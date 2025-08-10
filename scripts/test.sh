#!/bin/bash

# AbSequenceAlign Unified Test Script
# Handles: Backend tests, Frontend tests, E2E tests, and Docker tests

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend          Run backend tests only"
    echo "  --frontend         Run frontend tests only"
    echo "  --e2e              Run E2E tests only"
    echo "  --quick            Run quick UI tests only"
    echo "  --parallel         Run E2E tests in parallel"
    echo "  --docker           Run Docker build tests"
    echo "  --all              Run all tests (default)"
    echo "  --coverage         Run with coverage reporting"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Run all tests"
    echo "  $0 --backend       # Run only backend tests"
    echo "  $0 --e2e --quick   # Run E2E and quick tests"
    echo "  $0 --coverage      # Run all tests with coverage"
}

# Parse command line arguments
RUN_BACKEND=false
RUN_FRONTEND=false
RUN_E2E=false
RUN_QUICK=false
RUN_PARALLEL=false
RUN_DOCKER=false
RUN_COVERAGE=false

if [ $# -eq 0 ]; then
    RUN_BACKEND=true
    RUN_FRONTEND=true
    RUN_E2E=true
    RUN_DOCKER=true
else
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend)
                RUN_BACKEND=true
                shift
                ;;
            --frontend)
                RUN_FRONTEND=true
                shift
                ;;
            --e2e)
                RUN_E2E=true
                shift
                ;;
            --quick)
                RUN_QUICK=true
                shift
                ;;
            --parallel)
                RUN_PARALLEL=true
                shift
                ;;
            --docker)
                RUN_DOCKER=true
                shift
                ;;
            --all)
                RUN_BACKEND=true
                RUN_FRONTEND=true
                RUN_E2E=true
                RUN_DOCKER=true
                shift
                ;;
            --coverage)
                RUN_COVERAGE=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
fi

print_header "AbSequenceAlign Test Suite"

# Check if we're in the right directory
if [ ! -f "Makefile" ]; then
    print_error "Makefile not found. Please run this script from the project root."
    exit 1
fi

# Check if conda environment exists
if ! conda env list | grep -q "^AbSequenceAlign "; then
    print_warning "Conda environment 'AbSequenceAlign' not found."
    print_status "Setting up development environment..."
    make install
fi

# Backend Tests
if [ "$RUN_BACKEND" = true ]; then
    print_header "Running Backend Tests"
    cd app/backend
    
    if [ "$RUN_COVERAGE" = true ]; then
        print_status "Running backend tests with coverage..."
        PYTHONPATH="$(pwd)/.." conda run -n AbSequenceAlign python -m pytest tests/ -v --cov=backend --cov-report=xml --cov-report=term-missing
    else
        print_status "Running backend tests..."
        PYTHONPATH="$(pwd)/.." conda run -n AbSequenceAlign python -m pytest tests/ -v
    fi
    
    cd ../..
fi

# Frontend Tests
if [ "$RUN_FRONTEND" = true ]; then
    print_header "Running Frontend Tests"
    cd app/frontend
    
    print_status "Running frontend tests..."
    npm run test -- --run
    
    print_status "Running type checking..."
    npm run type-check
    
    print_status "Running linting..."
    npm run lint
    
    cd ../..
fi

# E2E Tests
if [ "$RUN_E2E" = true ]; then
    print_header "Running E2E Tests"
    cd app/frontend
    
    print_status "Running full E2E test suite..."
    ./scripts/run-e2e.sh
    
    cd ../..
fi

# Quick Tests
if [ "$RUN_QUICK" = true ]; then
    print_header "Running Quick UI Tests"
    cd app/frontend
    
    print_status "Running quick UI tests..."
    ./scripts/quick-test.sh
    
    cd ../..
fi

# Parallel Tests
if [ "$RUN_PARALLEL" = true ]; then
    print_header "Running Parallel E2E Tests"
    cd app/frontend
    
    print_status "Running E2E tests in parallel..."
    ./scripts/run-parallel-tests.sh
    
    cd ../..
fi

# Docker Tests
if [ "$RUN_DOCKER" = true ]; then
    print_header "Running Docker Build Tests"
    
    print_status "Testing backend Docker build..."
    docker build -f app/backend/Dockerfile -t absequencealign-backend-test .
    
    print_status "Testing frontend Docker build..."
    docker build -f app/frontend/Dockerfile -t absequencealign-frontend-test app/frontend
    
    print_status "Cleaning up test images..."
    docker rmi absequencealign-backend-test absequencealign-frontend-test 2>/dev/null || true
fi

print_header "Test Suite Complete"
print_status "All tests completed successfully!"
