#!/bin/bash

# AbSequenceAlign Unified Development Script
# Replaces: dev-new.sh, start-dev.sh, and other redundant dev scripts

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to find an available port
find_available_port() {
    local port=$1
    while true; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return
        fi
        ((port++))
    done
}

# Function to cleanup background processes
cleanup() {
    print_status "Cleaning up processes..."
    lsof -ti:$VITE_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    pkill -f vite 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    pkill -f "python.*uvicorn" 2>/dev/null || true
    sleep 2
}

# Set up trap to cleanup on exit
trap cleanup INT TERM EXIT

print_header "AbSequenceAlign Development Environment"

# Check if we're in the right directory
if [ ! -f "Makefile" ]; then
    print_error "Makefile not found. Please run this script from the project root."
    exit 1
fi

# Find available ports
VITE_PORT=$(find_available_port 5678)
BACKEND_PORT=$(find_available_port 8000)

print_status "Using ports: Frontend=$VITE_PORT, Backend=$BACKEND_PORT"

# Export ports for other processes to use
export VITE_PORT=$VITE_PORT
export BACKEND_PORT=$BACKEND_PORT

# Check if conda environment exists
if ! conda env list | grep -q "^AbSequenceAlign "; then
    print_warning "Conda environment 'AbSequenceAlign' not found."
    print_status "Setting up development environment..."
    make install
fi

# Check if frontend dependencies are installed
if [ ! -d "app/frontend/node_modules" ]; then
    print_warning "Frontend dependencies not found."
    print_status "Installing frontend dependencies..."
    cd app/frontend && npm install && cd ../..
fi

print_status "Environment check complete"

# Initial cleanup
cleanup

print_header "Starting Development Servers"

# Start backend server
print_status "Starting backend server on port $BACKEND_PORT..."
cd app/backend
PYTHONPATH="$(pwd)/.." conda run -n AbSequenceAlign python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
cd ../..

# Wait for backend to be ready
print_status "Waiting for backend server..."
MAX_RETRIES=30
COUNT=0
while ! curl -s http://localhost:$BACKEND_PORT/health >/dev/null; do
    ((COUNT++))
    if [ $COUNT -eq $MAX_RETRIES ]; then
        print_error "Backend server failed to start"
        exit 1
    fi
    sleep 1
done

print_status "Backend server is ready at http://localhost:$BACKEND_PORT"

# Start frontend server
print_status "Starting frontend server on port $VITE_PORT..."
cd app/frontend
VITE_PORT=$VITE_PORT npm run dev:port &
FRONTEND_PID=$!
cd ../..

# Wait for frontend to be ready
print_status "Waiting for frontend server..."
MAX_RETRIES=30
COUNT=0
while ! curl -s http://localhost:$VITE_PORT >/dev/null; do
    ((COUNT++))
    if [ $COUNT -eq $MAX_RETRIES ]; then
        print_error "Frontend server failed to start"
        exit 1
    fi
    sleep 1
done

print_status "Frontend server is ready at http://localhost:$VITE_PORT"

print_header "Development Environment Ready"
echo -e "${GREEN}✅ Backend API:${NC} http://localhost:$BACKEND_PORT"
echo -e "${GREEN}✅ API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}✅ Frontend:${NC} http://localhost:$VITE_PORT"
echo -e "${GREEN}✅ Health Check:${NC} http://localhost:$BACKEND_PORT/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
