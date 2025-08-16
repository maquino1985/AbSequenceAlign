#!/bin/bash

# AbSequenceAlign Simple Development Environment
# Starts both frontend and backend servers without health checks

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

# Function to initialize conda/micromamba
init_conda() {
    # Try to source shell configuration to get conda alias
    if [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc" 2>/dev/null || true
    fi
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc" 2>/dev/null || true
    fi
    
    # Check if conda is available, if not try micromamba
    if command -v conda >/dev/null 2>&1; then
        echo "conda"
    elif command -v micromamba >/dev/null 2>&1; then
        echo "micromamba"
    else
        print_error "Neither conda nor micromamba found. Please install micromamba or conda."
        exit 1
    fi
}

# Get the conda command
CONDA_CMD=$(init_conda)

# Function to find available port
find_available_port() {
    local port=$1
    while netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; do
        port=$((port + 1))
    done
    echo $port
}

# Function to cleanup background processes
cleanup() {
    print_status "Cleaning up processes..."
    # Kill processes on specific ports using netstat/ss instead of lsof
    netstat -tulpn 2>/dev/null | grep ":$VITE_PORT " | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 2>/dev/null || true
    netstat -tulpn 2>/dev/null | grep ":$BACKEND_PORT " | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 2>/dev/null || true
    # Fallback to ss if netstat not available
    ss -tulpn 2>/dev/null | grep ":$VITE_PORT " | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 2>/dev/null || true
    ss -tulpn 2>/dev/null | grep ":$BACKEND_PORT " | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 2>/dev/null || true
    # Kill by process name
    pkill -f vite 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    pkill -f "python.*uvicorn" 2>/dev/null || true
    sleep 2
}

# Set up trap to cleanup on exit
trap cleanup INT TERM EXIT

print_header "AbSequenceAlign Simple Development Environment"

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
if ! $CONDA_CMD env list | grep -q "AbSequenceAlign"; then
    print_warning "Conda environment 'AbSequenceAlign' not found."
    print_status "Setting up development environment..."
    (cd app/backend && source ~/.zshrc 2>/dev/null || true && $CONDA_CMD env create -f environment.yml || $CONDA_CMD env update -f environment.yml)
    (cd app/frontend && npm install)
fi

# Check if frontend dependencies are installed
if [ ! -d "app/frontend/node_modules" ]; then
    print_warning "Frontend dependencies not found."
    print_status "Installing frontend dependencies..."
    (cd app/frontend && npm install)
fi

print_status "Environment check complete"

# Initial cleanup
cleanup

print_header "Starting Development Servers"

# Start backend server
print_status "Starting backend server on port $BACKEND_PORT..."
(cd app/backend && PYTHONPATH="$(pwd)/.." $CONDA_CMD run -n AbSequenceAlign python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT) &
BACKEND_PID=$!

# Give backend a moment to start
sleep 3

# Start frontend server
print_status "Starting frontend server on port $VITE_PORT..."
(cd app/frontend && VITE_PORT=$VITE_PORT npm run dev:port) &
FRONTEND_PID=$!

# Give frontend a moment to start
sleep 3

print_header "Development Environment Ready"
echo -e "${GREEN}✅ Backend API:${NC} http://localhost:$BACKEND_PORT"
echo -e "${GREEN}✅ API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}✅ Frontend:${NC} http://localhost:$VITE_PORT"
echo -e "${GREEN}✅ Health Check:${NC} http://localhost:$BACKEND_PORT/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Wait for both processes with better error handling
print_status "Waiting for processes to complete..."
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || {
    print_warning "One or more processes exited unexpectedly"
    # Check if processes are still running
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_status "Backend process is still running"
    fi
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_status "Frontend process is still running"
    fi
}


