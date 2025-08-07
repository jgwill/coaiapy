#!/bin/bash
# Run real Langfuse integration tests using .env.tests
# This validates the actual .env functionality with live Langfuse API

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "${BLUE}🔗 CoaiaPy Real Langfuse Integration Tests${NC}"
echo "=================================================="

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if .env.tests exists
if [[ ! -f "${PROJECT_DIR}/.env.tests" ]]; then
    print_error ".env.tests file not found in project root"
    print_error "Create .env.tests with your Langfuse test credentials:"
    echo "LANGFUSE_SECRET_KEY=sk-lf-your-test-secret-key"
    echo "LANGFUSE_PUBLIC_KEY=pk-lf-your-test-public-key"
    echo "LANGFUSE_HOST=https://us.cloud.langfuse.com"
    exit 1
fi

print_status ".env.tests file found"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Build the test image if it doesn't exist
if ! docker image inspect coaiapy-test > /dev/null 2>&1; then
    print_status "Building Docker test image..."
    if docker build -f "${SCRIPT_DIR}/Dockerfile.test" -t coaiapy-test "${PROJECT_DIR}"; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
else
    print_status "Using existing Docker test image"
fi

# Run the real Langfuse integration tests
print_status "Running real Langfuse integration tests..."
print_status "Using .env.tests for actual Langfuse API testing"

# Prepare Docker command
DOCKER_CMD="docker run --rm"

# Mount .env.tests as .env
DOCKER_CMD="$DOCKER_CMD -v ${PROJECT_DIR}/.env.tests:/app/.env:ro"

# Mount the tests directory
DOCKER_CMD="$DOCKER_CMD -v ${SCRIPT_DIR}:/app/tests:ro"

# Set environment variable
DOCKER_CMD="$DOCKER_CMD -e TEST_SCENARIO=real-langfuse"

# Run only the real Langfuse integration tests
DOCKER_CMD="$DOCKER_CMD coaiapy-test python test_real_langfuse_integration.py"

print_status "Executing: $DOCKER_CMD"

if eval "$DOCKER_CMD"; then
    print_success "✅ Real Langfuse integration tests PASSED"
    echo "=================================================="
    print_status "All Langfuse operations validated:"
    print_status "• Configuration loading from .env.tests"
    print_status "• coaia fuse prompts list (table and JSON)"
    print_status "• coaia fuse datasets list"
    print_status "• coaia fuse traces list"
    echo "=================================================="
    exit 0
else
    print_error "❌ Real Langfuse integration tests FAILED"
    echo "=================================================="
    print_error "Possible issues:"
    print_error "• Invalid Langfuse credentials in .env.tests"
    print_error "• Network connectivity to Langfuse API"
    print_error "• API rate limits or service issues"
    echo "=================================================="
    exit 1
fi