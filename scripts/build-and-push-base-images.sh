#!/bin/bash

# Build and Push Base Images to GHCR
# This script builds base images for frontend and backend and pushes them to GitHub Container Registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY=${REGISTRY:-ghcr.io}
GITHUB_REPOSITORY_OWNER=${GITHUB_REPOSITORY_OWNER:-maquino1985}
BACKEND_BASE_IMAGE="${REGISTRY}/${GITHUB_REPOSITORY_OWNER}/absequencealign-backend-base"
FRONTEND_BASE_IMAGE="${REGISTRY}/${GITHUB_REPOSITORY_OWNER}/absequencealign-frontend-base"
TAG=${IMAGE_TAG:-latest}

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Function to build backend base image
build_backend_base() {
    print_header "Building Backend Base Image"
    
    print_status "Building backend base image: ${BACKEND_BASE_IMAGE}:${TAG}"
    docker build -f "$PROJECT_ROOT/app/backend/Dockerfile.base" -t "${BACKEND_BASE_IMAGE}:${TAG}" "$PROJECT_ROOT"
    
    print_status "Backend base image built successfully!"
}

# Function to build frontend base image
build_frontend_base() {
    print_header "Building Frontend Base Image"
    
    print_status "Building frontend base image: ${FRONTEND_BASE_IMAGE}:${TAG}"
    docker build -f "$PROJECT_ROOT/app/frontend/Dockerfile.base" -t "${FRONTEND_BASE_IMAGE}:${TAG}" "$PROJECT_ROOT/app/frontend"
    
    print_status "Frontend base image built successfully!"
}

# Function to push images to GHCR
push_images() {
    print_header "Pushing Images to GHCR"
    
    # Check if we're logged in to GHCR
    if ! docker info | grep -q "ghcr.io"; then
        print_warning "Not logged in to GHCR. Attempting to login..."
        if [ -n "$GITHUB_TOKEN" ]; then
            echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_REPOSITORY_OWNER" --password-stdin
        else
            print_error "GITHUB_TOKEN environment variable not set. Please login to GHCR manually:"
            print_error "echo \$GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_REPOSITORY_OWNER --password-stdin"
            exit 1
        fi
    fi
    
    print_status "Pushing backend base image..."
    docker push "${BACKEND_BASE_IMAGE}:${TAG}"
    
    print_status "Pushing frontend base image..."
    docker push "${FRONTEND_BASE_IMAGE}:${TAG}"
    
    print_status "All images pushed successfully!"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend-only    Build and push only backend base image"
    echo "  --frontend-only   Build and push only frontend base image"
    echo "  --build-only      Build images but don't push to registry"
    echo "  --push-only       Push existing images without building"
    echo "  --help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  REGISTRY                   Container registry (default: ghcr.io)"
    echo "  GITHUB_REPOSITORY_OWNER    GitHub username/org (default: maquino1985)"
    echo "  IMAGE_TAG                  Image tag (default: latest)"
    echo "  GITHUB_TOKEN               GitHub token for authentication"
    echo ""
    echo "Examples:"
    echo "  $0                         # Build and push both images"
    echo "  $0 --backend-only          # Build and push only backend"
    echo "  $0 --build-only            # Build both images locally"
}

# Parse command line arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
PUSH_IMAGES=true
BUILD_IMAGES=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BUILD_FRONTEND=false
            shift
            ;;
        --frontend-only)
            BUILD_BACKEND=false
            shift
            ;;
        --build-only)
            PUSH_IMAGES=false
            shift
            ;;
        --push-only)
            BUILD_IMAGES=false
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

# Main execution
print_header "AbSequenceAlign Base Image Builder and Publisher"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build base images
if [ "$BUILD_IMAGES" = true ]; then
    if [ "$BUILD_BACKEND" = true ]; then
        build_backend_base
    fi

    if [ "$BUILD_FRONTEND" = true ]; then
        build_frontend_base
    fi
fi

# Push images to GHCR
if [ "$PUSH_IMAGES" = true ]; then
    push_images
fi

print_header "Build and Push Complete"
print_status "Base images are ready and available at:"
if [ "$BUILD_BACKEND" = true ]; then
    print_status "  Backend: ${BACKEND_BASE_IMAGE}:${TAG}"
fi
if [ "$BUILD_FRONTEND" = true ]; then
    print_status "  Frontend: ${FRONTEND_BASE_IMAGE}:${TAG}"
fi
