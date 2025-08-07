# CoaiaPy Docker Test Suite

Comprehensive Docker-based testing for coaiapy package in isolated environments.

## Overview

This test suite validates:
- ✅ **Environment Variable Support**: New `.env` file functionality 
- ✅ **Configuration Loading**: Priority order (.env → system env → config files)
- ✅ **CLI Functionality**: All command-line interfaces work correctly
- ✅ **Package Integration**: Imports, dependencies, and core features
- ✅ **Python 3.6 Compatibility**: Ensures Pythonista iOS compatibility

## Quick Start

Run all tests:
```bash
./run_docker_tests.sh
```

## Test Scenarios

### 1. Minimal Configuration
- **File**: `sample.env.minimal`
- **Tests**: Basic Langfuse keys only
- **Purpose**: Verify minimal .env functionality

### 2. Langfuse Complete
- **File**: `sample.env.langfuse` 
- **Tests**: Full Langfuse configuration
- **Purpose**: Validate Langfuse-specific environment loading

### 3. Full Configuration
- **File**: `sample.env.full`
- **Tests**: All service configurations (AWS, Redis, OpenAI, Langfuse)
- **Purpose**: Comprehensive integration testing

### 4. **Real Langfuse Integration** 🔥
- **File**: `../.env.tests`
- **Tests**: Actual Langfuse API calls with real credentials
- **Purpose**: End-to-end validation with live Langfuse environment
- **Operations Tested**:
  - `coaia fuse prompts list` (table and JSON formats)
  - `coaia fuse datasets list`
  - `coaia fuse traces list`
  - Configuration loading and authentication

### 5. No .env File
- **File**: None
- **Tests**: System environment variables only
- **Purpose**: Fallback behavior validation

## Files Structure

```
tests/
├── Dockerfile.test           # Docker image definition
├── run_docker_tests.sh       # Main orchestration script
├── test_suite.py            # Comprehensive test suite
├── test_env_functionality.py # .env specific tests
├── sample.env.minimal        # Minimal test configuration
├── sample.env.langfuse       # Langfuse test configuration
├── sample.env.full          # Complete test configuration
└── README.md               # This file
```

## Docker Image

**Base Image**: `jgwill/ubuntu:py3.6`
- Python 3.6 for Pythonista compatibility
- Minimal Ubuntu environment
- No external config files (pure environment testing)

## Test Features

### Environment Variable Testing
- `.env` file parsing with comments and quotes
- Priority order: system env > .env file > config defaults
- Configuration merging and override behavior
- Missing file handling

### CLI Testing  
- Command-line help functionality
- Subcommand argument parsing
- Basic command execution
- Error handling and exit codes

### Integration Testing
- Module imports and dependencies
- Configuration loading from multiple sources
- Python 3.6 compatibility validation
- Package installation verification

## Usage Examples

### Run specific scenario manually:
```bash
# Test with Langfuse config
docker run --rm \
  -v $(pwd)/sample.env.langfuse:/app/.env:ro \
  -v $(pwd):/app/tests:ro \
  coaiapy-test

# Test with REAL Langfuse environment
docker run --rm \
  -v $(pwd)/../.env.tests:/app/.env:ro \
  -v $(pwd):/app/tests:ro \
  coaiapy-test python test_real_langfuse_integration.py

# Test without .env file
docker run --rm \
  -v $(pwd):/app/tests:ro \
  coaiapy-test
```

### Build test image manually:
```bash
docker build -f Dockerfile.test -t coaiapy-test ..
```

## Integration with Main Build System

Available in main `Makefile`:
```make
test-docker:
	cd tests && ./run_docker_tests.sh

test-langfuse-real:
	cd tests && ./run_real_langfuse_tests.sh

test-docker-clean:
	docker rmi coaiapy-test || true
```

### Quick Commands:
```bash
# Run all test scenarios (mock + real)
make test-docker

# Run ONLY real Langfuse tests
make test-langfuse-real

# Clean up Docker images
make test-docker-clean
```

## Expected Output

```
🐳 CoaiaPy Docker Test Suite
==================================================
[INFO] Building Docker test image...
[SUCCESS] Docker image built successfully

==================================================
[INFO] Running test scenario: minimal
[INFO] Description: Basic .env functionality with minimal config
==================================================
[INFO] Mounting: sample.env.minimal -> /app/.env
[SUCCESS] ✅ Test scenario 'minimal' PASSED

... (additional scenarios) ...

==================================================
[SUCCESS] 🎉 ALL TEST SCENARIOS PASSED (4/4)
==================================================
```

## Troubleshooting

### Docker Build Issues
- Ensure Docker daemon is running
- Check base image availability: `docker pull jgwill/ubuntu:py3.6`
- Verify file permissions on test scripts

### Test Failures
- Check `.env` file format (no spaces around `=`)
- Verify Python 3.6 compatibility of any new dependencies
- Review Docker container logs for detailed error messages

### Python Import Errors
- Ensure package is properly installed in container
- Check Python path and module structure
- Verify all dependencies are available in Python 3.6

## Contributing

When adding new tests:
1. Add test functions to `test_suite.py` or `test_env_functionality.py`
2. Create appropriate `.env` sample files if needed
3. Update test scenarios in `run_docker_tests.sh`
4. Document new functionality in this README

## Maintenance

- **Base Image**: Keep `jgwill/ubuntu:py3.6` for Pythonista compatibility
- **Dependencies**: Pin versions compatible with Python 3.6
- **Test Coverage**: Maintain comprehensive coverage of core functionality
- **Documentation**: Keep README updated with any new test scenarios