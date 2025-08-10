#!/bin/bash

# AbSequenceAlign Development Script - New Version

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AbSequenceAlign Development Environment${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "Makefile" ]; then
    echo -e "${RED}❌ Error: Makefile not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check if conda environment exists
if ! conda env list | grep -q "^AbSequenceAlign "; then
    echo -e "${YELLOW}⚠️  Conda environment 'AbSequenceAlign' not found.${NC}"
    echo -e "${YELLOW}Setting up development environment...${NC}"
    make setup
fi

# Check if frontend dependencies are installed
if [ ! -d "app/frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not found.${NC}"
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd app/frontend && npm install && cd ../..
fi

echo -e "${GREEN}✅ Environment check complete${NC}"
echo ""
echo -e "${YELLOW}Starting development servers...${NC}"
echo -e "${YELLOW}Backend will be available at: http://localhost:8000${NC}"
echo -e "${YELLOW}Frontend will be available at: http://localhost:5173${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping development servers...${NC}"
    kill %1 %2 2>/dev/null || true
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup INT TERM

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
if conda env list | grep -q "^AbSequenceAlign "; then
    cd app/backend && conda run -n AbSequenceAlign uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
else
    cd app/backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
fi
BACKEND_PID=$!

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd app/frontend && npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID


