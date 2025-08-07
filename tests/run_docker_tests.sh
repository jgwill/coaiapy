#!/bin/bash
# Docker test orchestration script for coaiapy
# Tests .env functionality and comprehensive package features in isolated environment

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

echo -e "${BLUE}🐳 CoaiaPy Docker Test Suite${NC}"
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

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Build the test image
print_status "Building Docker test image..."
if docker build -f "${SCRIPT_DIR}/Dockerfile.test" -t coaiapy-test "${PROJECT_DIR}"; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Test scenarios
declare -a TEST_SCENARIOS=(
    "minimal:sample.env.minimal:Basic .env functionality with minimal config"
    "langfuse:sample.env.langfuse:Langfuse-specific configuration testing"
    "full:sample.env.full:Complete configuration with all services"
    "real-langfuse:../.env.tests:Real Langfuse integration testing"
    "none::Testing without .env file (environment variables only)"
)

# Run test scenarios
FAILED_TESTS=0
TOTAL_TESTS=${#TEST_SCENARIOS[@]}

for scenario in "${TEST_SCENARIOS[@]}"; do
    IFS=':' read -r name env_file description <<< "$scenario"
    
    echo ""
    echo "=================================================="
    print_status "Running test scenario: $name"
    print_status "Description: $description"
    echo "=================================================="
    
    # Prepare Docker run command
    DOCKER_CMD="docker run --rm"
    
    # Mount .env file if specified
    if [[ -n "$env_file" ]]; then
        ENV_FILE_PATH="${SCRIPT_DIR}/${env_file}"
        if [[ -f "$ENV_FILE_PATH" ]]; then
            DOCKER_CMD="$DOCKER_CMD -v ${ENV_FILE_PATH}:/app/.env:ro"
            print_status "Mounting: $env_file -> /app/.env"
        else
            print_warning "Environment file not found: $env_file"
        fi
    else
        print_status "Running without .env file"
    fi
    
    # Add test scenario as environment variable
    DOCKER_CMD="$DOCKER_CMD -e TEST_SCENARIO=$name"
    
    # Mount the tests directory
    DOCKER_CMD="$DOCKER_CMD -v ${SCRIPT_DIR}:/app/tests:ro"
    
    # Run the container
    DOCKER_CMD="$DOCKER_CMD coaiapy-test"
    
    print_status "Executing: $DOCKER_CMD"
    
    if eval "$DOCKER_CMD"; then
        print_success "✅ Test scenario '$name' PASSED"
    else
        print_error "❌ Test scenario '$name' FAILED"
        ((FAILED_TESTS++))
    fi
done

# Final results
echo ""
echo "=================================================="
if [[ $FAILED_TESTS -eq 0 ]]; then
    print_success "🎉 ALL TEST SCENARIOS PASSED ($TOTAL_TESTS/$TOTAL_TESTS)"
    echo "=================================================="
    exit 0
else
    print_error "💥 $FAILED_TESTS/$TOTAL_TESTS TEST SCENARIOS FAILED"
    echo "=================================================="
    exit 1
fi