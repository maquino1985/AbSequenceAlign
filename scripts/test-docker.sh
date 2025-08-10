#!/bin/bash

# AbSequenceAlign Docker Test Runner
# Runs all tests in isolated Docker containers

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
    echo "  --backend          Run backend tests in Docker"
    echo "  --frontend         Run frontend tests in Docker"
    echo "  --e2e              Run E2E tests in Docker"
    echo "  --integration      Run integration tests in Docker"
    echo "  --all              Run all tests in Docker (default)"
    echo "  --cleanup          Clean up Docker containers and images"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Run all tests in Docker"
    echo "  $0 --backend       # Run only backend tests in Docker"
    echo "  $0 --cleanup       # Clean up Docker resources"
}

# Parse command line arguments
RUN_BACKEND=false
RUN_FRONTEND=false
RUN_E2E=false
RUN_INTEGRATION=false
CLEANUP_ONLY=false

if [ $# -eq 0 ]; then
    RUN_BACKEND=true
    RUN_FRONTEND=true
    RUN_E2E=true
    RUN_INTEGRATION=true
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
            --integration)
                RUN_INTEGRATION=true
                shift
                ;;
            --all)
                RUN_BACKEND=true
                RUN_FRONTEND=true
                RUN_E2E=true
                RUN_INTEGRATION=true
                shift
                ;;
            --cleanup)
                CLEANUP_ONLY=true
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

print_header "AbSequenceAlign Docker Test Suite"

# Check if we're in the right directory
if [ ! -f "docker-compose.test.yml" ]; then
    print_error "docker-compose.test.yml not found. Please run this script from the project root."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Cleanup function
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker compose -f docker-compose.test.yml down -v --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    print_status "Cleanup complete"
}

# If cleanup only, do that and exit
if [ "$CLEANUP_ONLY" = true ]; then
    cleanup
    exit 0
fi

# Initial cleanup
cleanup

# Build base images first
print_header "Building Base Images"
print_status "Building backend and frontend base images..."
if ! ./scripts/build-base-images.sh; then
    print_error "Failed to build base images!"
    cleanup
    exit 1
fi
print_status "Base images built successfully!"

# Backend Tests
if [ "$RUN_BACKEND" = true ]; then
    print_header "Running Backend Tests in Docker"
    print_status "Building and running backend test container..."
    
    if docker compose -f docker-compose.test.yml up --build backend-test --exit-code-from backend-test; then
        print_status "Backend tests passed!"
    else
        print_error "Backend tests failed!"
        cleanup
        exit 1
    fi
fi

# Frontend Tests
if [ "$RUN_FRONTEND" = true ]; then
    print_header "Running Frontend Tests in Docker"
    print_status "Building and running frontend test container..."
    
    if docker compose -f docker-compose.test.yml up --build frontend-test --exit-code-from frontend-test; then
        print_status "Frontend tests passed!"
    else
        print_error "Frontend tests failed!"
        cleanup
        exit 1
    fi
fi

# Integration Tests
if [ "$RUN_INTEGRATION" = true ]; then
    print_header "Running Integration Tests in Docker"
    print_status "Building and running integration test container..."
    
    if docker compose -f docker-compose.test.yml up --build integration-test --exit-code-from integration-test; then
        print_status "Integration tests passed!"
    else
        print_error "Integration tests failed!"
        cleanup
        exit 1
    fi
fi

# E2E Tests
if [ "$RUN_E2E" = true ]; then
    print_header "Running E2E Tests in Docker"
    print_status "Building and running E2E test container..."
    
    if docker compose -f docker-compose.test.yml up --build e2e-test --exit-code-from e2e-test; then
        print_status "E2E tests passed!"
    else
        print_error "E2E tests failed!"
        cleanup
        exit 1
    fi
fi

# Final cleanup
cleanup

print_header "Docker Test Suite Complete"
print_status "All tests completed successfully in Docker containers!"
