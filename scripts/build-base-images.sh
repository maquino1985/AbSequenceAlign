#!/bin/bash

# Build Base Images Script
# This script builds base images for frontend and backend with dependency change detection
# Supports multi-architecture builds (ARM64 and AMD64) using Docker Buildx

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_BASE_IMAGE="absequencealign-backend-base"
FRONTEND_BASE_IMAGE="absequencealign-frontend-base"
BACKEND_TAG="latest"
FRONTEND_TAG="latest"

# Multi-architecture configuration
PLATFORMS="linux/amd64,linux/arm64"
BUILDX_BUILDER="absequencealign-multiarch"

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

# Function to setup buildx builder
setup_buildx() {
    print_status "Setting up Docker Buildx for multi-architecture builds..."
    
    # Check if buildx is available
    if ! docker buildx version >/dev/null 2>&1; then
        print_error "Docker Buildx is not available. Please install Docker Buildx."
        exit 1
    fi
    
    # Create a new builder instance if it doesn't exist
    if ! docker buildx inspect "$BUILDX_BUILDER" >/dev/null 2>&1; then
        print_status "Creating new buildx builder: $BUILDX_BUILDER"
        docker buildx create --name "$BUILDX_BUILDER" --use
    else
        print_status "Using existing buildx builder: $BUILDX_BUILDER"
        docker buildx use "$BUILDX_BUILDER"
    fi
    
    # Bootstrap the builder
    print_status "Bootstrapping buildx builder..."
    docker buildx inspect --bootstrap
    
    print_status "Buildx setup complete!"
}

# Function to calculate hash of dependency files
calculate_dependency_hash() {
    local dir=$1
    local hash_file="$dir/.dependency-hash"
    
    if [ "$dir" = "app/backend" ]; then
        # For backend, hash environment.yml
        if [ -f "$dir/environment.yml" ]; then
            cat "$dir/environment.yml" | sha256sum | cut -d' ' -f1
        else
            echo "no-deps"
        fi
    elif [ "$dir" = "app/frontend" ]; then
        # For frontend, hash package.json and package-lock.json
        if [ -f "$dir/package.json" ] && [ -f "$dir/package-lock.json" ]; then
            cat "$dir/package.json" "$dir/package-lock.json" | sha256sum | cut -d' ' -f1
        else
            echo "no-deps"
        fi
    else
        echo "unknown"
    fi
}

# Function to check if base image needs rebuilding
needs_rebuild() {
    local dir=$1
    local image_name=$2
    local hash_file="$dir/.dependency-hash"
    local current_hash=$(calculate_dependency_hash "$dir")
    
    # Check if hash file exists and matches current hash
    if [ -f "$hash_file" ]; then
        local stored_hash=$(cat "$hash_file")
        if [ "$current_hash" = "$stored_hash" ]; then
            # For multi-architecture builds, we can't easily check if the image exists
            # So we'll rely on the hash file for now
            return 1  # No rebuild needed
        fi
    fi
    
    return 0  # Rebuild needed
}

# Function to build backend base image with buildx
build_backend_base() {
    print_header "Building Backend Base Image (Multi-Architecture)"
    
    if needs_rebuild "app/backend" "$BACKEND_BASE_IMAGE" || [ "$FORCE_REBUILD" = true ]; then
        print_status "Dependencies changed or image missing. Building backend base image..."
        print_status "Target platforms: $PLATFORMS"
        
        # Build multi-architecture image
        docker buildx build \
            --platform "$PLATFORMS" \
            --file "$PROJECT_ROOT/app/backend/Dockerfile.base" \
            --tag "$BACKEND_BASE_IMAGE:$BACKEND_TAG" \
            --progress=plain \
            "$PROJECT_ROOT"
        
        # Store the new hash
        calculate_dependency_hash "app/backend" > "$PROJECT_ROOT/app/backend/.dependency-hash"
        
        print_status "Backend base image built successfully for multiple architectures!"
    else
        print_status "Backend base image is up to date."
    fi
}

# Function to build frontend base image with buildx
build_frontend_base() {
    print_header "Building Frontend Base Image (Multi-Architecture)"
    
    if needs_rebuild "app/frontend" "$FRONTEND_BASE_IMAGE" || [ "$FORCE_REBUILD" = true ]; then
        print_status "Dependencies changed or image missing. Building frontend base image..."
        print_status "Target platforms: $PLATFORMS"
        
        # Build multi-architecture image
        docker buildx build \
            --platform "$PLATFORMS" \
            --file "$PROJECT_ROOT/app/frontend/Dockerfile.base" \
            --tag "$FRONTEND_BASE_IMAGE:$FRONTEND_TAG" \
            --progress=plain \
            "$PROJECT_ROOT/app/frontend"
        
        # Store the new hash
        calculate_dependency_hash "app/frontend" > "$PROJECT_ROOT/app/frontend/.dependency-hash"
        
        print_status "Frontend base image built successfully for multiple architectures!"
    else
        print_status "Frontend base image is up to date."
    fi
}

# Function to show image architecture information
show_image_info() {
    print_header "Image Architecture Information"
    
    echo "Backend Base Image:"
    docker buildx imagetools inspect "$BACKEND_BASE_IMAGE:$BACKEND_TAG" 2>/dev/null || echo "  Not available"
    
    echo ""
    echo "Frontend Base Image:"
    docker buildx imagetools inspect "$FRONTEND_BASE_IMAGE:$FRONTEND_TAG" 2>/dev/null || echo "  Not available"
}

# Function to create local single-architecture images for development
create_local_images() {
    print_header "Creating Local Single-Architecture Images for Development"
    
    local platform="linux/$(uname -m | sed 's/x86_64/amd64/')"
    print_status "Creating local images for platform: $platform"
    
    # Create local backend image
    docker buildx build \
        --platform "$platform" \
        --file "$PROJECT_ROOT/app/backend/Dockerfile.base" \
        --tag "$BACKEND_BASE_IMAGE:$BACKEND_TAG" \
        --load \
        --progress=plain \
        "$PROJECT_ROOT"
    
    # Create local frontend image
    docker buildx build \
        --platform "$platform" \
        --file "$PROJECT_ROOT/app/frontend/Dockerfile.base" \
        --tag "$FRONTEND_BASE_IMAGE:$FRONTEND_TAG" \
        --load \
        --progress=plain \
        "$PROJECT_ROOT/app/frontend"
    
    print_status "Local single-architecture images created successfully!"
}

# Function to clean up old base images
cleanup_old_images() {
    print_header "Cleaning Up Old Base Images"
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old base images (keep only the latest)
    docker images | grep "$BACKEND_BASE_IMAGE" | grep -v "$BACKEND_TAG" | awk '{print $3}' | xargs -r docker rmi -f
    docker images | grep "$FRONTEND_BASE_IMAGE" | grep -v "$FRONTEND_TAG" | awk '{print $3}' | xargs -r docker rmi -f
    
    print_status "Cleanup completed."
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend-only    Build only backend base image"
    echo "  --frontend-only   Build only frontend base image"
    echo "  --force           Force rebuild even if dependencies haven't changed"
    echo "  --cleanup         Clean up old base images"
    echo "  --platforms       Specify target platforms (default: linux/amd64,linux/arm64)"
    echo "  --local           Create local single-architecture images for development"
    echo "  --info            Show image architecture information"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build both base images for multiple architectures"
    echo "  $0 --backend-only     # Build only backend base image"
    echo "  $0 --force            # Force rebuild both images"
    echo "  $0 --platforms linux/amd64  # Build only for AMD64"
    echo "  $0 --local            # Create local single-architecture images"
    echo "  $0 --cleanup          # Clean up old images"
    echo "  $0 --info             # Show image architecture information"
}

# Parse command line arguments
BUILD_BACKEND=true
BUILD_FRONTEND=true
FORCE_REBUILD=false
CLEANUP_ONLY=false
SHOW_INFO=false
CREATE_LOCAL=false

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
        --force)
            FORCE_REBUILD=true
            shift
            ;;
        --cleanup)
            CLEANUP_ONLY=true
            shift
            ;;
        --platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        --local)
            CREATE_LOCAL=true
            shift
            ;;
        --info)
            SHOW_INFO=true
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
print_header "AbSequenceAlign Multi-Architecture Base Image Builder"

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

# Show image info if requested
if [ "$SHOW_INFO" = true ]; then
    show_image_info
    exit 0
fi

# Setup buildx for multi-architecture builds
if [ "$CREATE_LOCAL" = false ]; then
    setup_buildx
fi

if [ "$CLEANUP_ONLY" = true ]; then
    cleanup_old_images
    exit 0
fi

# Force rebuild by removing hash files
if [ "$FORCE_REBUILD" = true ]; then
    print_warning "Force rebuild requested. Removing dependency hash files..."
    rm -f app/backend/.dependency-hash app/frontend/.dependency-hash
fi

# Build base images
if [ "$CREATE_LOCAL" = true ]; then
    create_local_images
else
    if [ "$BUILD_BACKEND" = true ]; then
        build_backend_base
    fi

    if [ "$BUILD_FRONTEND" = true ]; then
        build_frontend_base
    fi
fi

# Cleanup old images
cleanup_old_images

# Show final image information
show_image_info

print_header "Multi-Architecture Base Image Build Complete"
print_status "All base images are ready for use on multiple architectures!"
print_status "Supported platforms: $PLATFORMS"
