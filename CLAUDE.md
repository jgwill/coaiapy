# CLAUDE.md - CoaiaPy Package Documentation

**Status**: Fully Automated Build & Distribution System Complete  
**Current Version**: 0.2.44  
**Python Compatibility**: >=3.6 (Pythonista compatible)  
**Date**: 2025-07-31

---

## 📦 Package Overview

CoaiaPy is a Python package for audio transcription, synthesis, and tagging using Boto3, with Redis integration for data stashing and Langfuse integration for prompt management.

### Core Features
- **Audio Processing**: Transcription and synthesis via AWS Polly
- **Redis Integration**: Data stashing and retrieval (`tash`, `fetch` commands)
- **Langfuse Integration**: Prompt management with pagination support
- **Process Tags**: Custom text processing with configurable instructions
- **Config Management**: Multiple config file locations with environment variable overrides

### CLI Commands
```bash
coaia transcribe <file>     # Transcribe audio to text
coaia summarize <text>      # Summarize text input
coaia tash <key> <value>    # Stash to Redis
coaia fetch <key>           # Fetch from Redis
coaia fuse                  # Manage Langfuse integrations
coaia p <tag> <text>        # Process with custom tags
coaia init                  # Create sample config
```

---

## 🔧 Development Environment

### Python Compatibility
- **Minimum**: Python >=3.6
- **Reason**: Pythonista iOS app compatibility requirement
- **Dependencies**: Pinned for Python 3.6 compatibility
  - `boto3<=1.26.137` (last version supporting Python 3.6)
  - `mutagen<=1.45.1` (last version supporting Python 3.6)
  - `redis==5.1.1` (pinned for compatibility)

### Key Files
- `pyproject.toml` - Modern Python packaging configuration
- `setup.py` - Legacy setup for compatibility  
- `requirements.txt` - Runtime dependencies
- `Makefile` - Automated build/release workflows
- `bump.py` - Automatic version management

---

## 🚀 Automated Build & Distribution System

### Make Commands

#### **Single Operations**
```bash
make clean          # Remove build artifacts (build/, dist/, *.egg-info)
make bump           # Auto-increment patch version in setup.py & pyproject.toml
make build          # Create wheel and source distributions
make upload         # Upload to production PyPI
make upload-test    # Upload to TestPyPI
```

#### **Combined Workflows**
```bash
make test-release   # FULL AUTOMATION: bump + clean + build + upload to TestPyPI
make dist          # Alias for build
```

### Version Management
- **Script**: `bump.py` automatically increments patch version
- **Files Updated**: Both `setup.py` and `pyproject.toml` simultaneously
- **Usage**: `python bump.py` or `python bump.py 1.2.3` for specific version

### Environment Setup
- **Credentials**: Stored in `~/.env` (auto-loaded by Makefile)
- **Required Variables**: `TWINE_USERNAME`, `TWINE_PASSWORD` for PyPI uploads
- **Config**: Uses `~/.pypirc` for twine configuration

### Build Validation
- **Twine Check**: All packages validated before upload
- **Distribution Types**: Both wheel (.whl) and source (.tar.gz) created
- **Clean Process**: Removes all artifacts between builds

---

## 📁 Project Structure

```
coaiapy/
├── coaiapy/                    # Main package directory
│   ├── __init__.py
│   ├── coaiacli.py            # CLI entry point
│   ├── coaiamodule.py         # Core functionality
│   ├── cofuse.py              # Langfuse integration
│   ├── syntation.py           # Text processing
│   └── test_cli_fetch.py      # Tests
├── codex/                     # Development logs
│   └── ledgers/               # Build/release history
├── pyproject.toml             # Modern packaging config
├── setup.py                   # Legacy setup
├── requirements.txt           # Dependencies
├── Makefile                   # Build automation
├── bump.py                    # Version management
├── README.md                  # Package documentation
└── CLAUDE.md                  # This file
```

---

## ⚠️ Critical Dependency Information

### Python 3.6 Compatibility Requirements
**IMPORTANT**: This package MUST maintain Python 3.6 compatibility for Pythonista iOS app.

#### Dependency Version Constraints
- **boto3**: `<=1.26.137` - Last version supporting Python 3.6 (support dropped 2025-04-22)
- **mutagen**: `<=1.45.1` - Last version supporting Python 3.6 (support dropped in v1.46.0)
- **redis**: `==5.1.1` - Pinned for stability

#### When Updating Dependencies
1. **Always verify Python 3.6 compatibility** before updating any dependency
2. **Test on Python 3.6** if available, or check PyPI compatibility tables
3. **Never update boto3 or mutagen** beyond specified versions
4. **Pin specific versions** for critical dependencies

---

## 🔄 Common Development Workflows

### Quick Release to TestPyPI
```bash
make test-release
# Automatically: bumps version, cleans, builds, uploads to TestPyPI
```

### Production Release
```bash
make test-release              # Test on TestPyPI first
# Verify everything works, then:
make upload                    # Upload to production PyPI
```

### Manual Version Management
```bash
python bump.py                 # Auto-increment patch
python bump.py 1.2.3          # Set specific version
```

### Development Testing
```bash
make clean && make build       # Clean build
twine check dist/*             # Validate packages
pip install -e .               # Editable install for testing
```

---

## 🐛 Known Issues & Solutions

### Upload Errors
- **"File already exists"**: Version already uploaded to PyPI/TestPyPI
- **Solution**: Run `make bump` to increment version, then retry upload
- **Note**: PyPI/TestPyPI don't allow re-uploading same version

### Setup.py Deprecation Warnings
- **Status**: Non-blocking warnings about license format and setup.py usage
- **Impact**: Build still succeeds, package works correctly
- **Future**: Will need SPDX license format migration before 2026-02-18

### Python Version Conflicts
- **Issue**: Dependencies may not support Python 3.6
- **Check**: Always verify compatibility before updating
- **Solution**: Use pinned versions specified above

---

## 📋 Fresh Session Checklist

### For New Claude Instance Working on CoaiaPy:

#### **Essential Context**
1. **Python 3.6 Compatibility**: CRITICAL requirement for Pythonista iOS app
2. **Pinned Dependencies**: boto3<=1.26.137, mutagen<=1.45.1, redis==5.1.1
3. **Automated Build System**: Use `make test-release` for full workflow

#### **Key Commands to Remember**
```bash
make test-release    # Full automated release to TestPyPI
make clean          # Always clean before fresh builds
make bump           # Auto-increment version
coaia --help        # Verify CLI functionality
```

#### **Before Making Changes**
1. **Test current functionality**: `coaia --help` and basic commands
2. **Check dependencies**: Ensure Python 3.6 compatibility maintained
3. **Use automation**: Don't manually manage versions or builds

#### **Testing Workflow**
1. **Local testing**: `pip install -e .` for editable install
2. **Build testing**: `make clean && make build && twine check dist/*`
3. **Release testing**: `make test-release` (uploads to TestPyPI)
4. **Production**: `make upload` (only after TestPyPI verification)

#### **Common Tasks**
- **Add new dependency**: Check Python 3.6 compatibility first
- **Update version**: Use `make bump` or `python bump.py`
- **Fix build issues**: Check dependency compatibility
- **Release new version**: Use `make test-release` workflow

---

## 🎯 Current Status

✅ **Fully Automated Build System**: Complete and tested  
✅ **Python 3.6 Compatibility**: Maintained with pinned dependencies  
✅ **TestPyPI Integration**: Working (latest: v0.2.53)  
✅ **Version Management**: Automated via bump.py  
✅ **Clean Build Process**: Artifacts properly managed  
✅ **Dependency Validation**: Twine checks pass  
✅ **Environment Variable Support**: Complete .env integration with Langfuse (PR #27)
✅ **Docker Test Suite**: Comprehensive testing including real API validation
✅ **Real Langfuse Integration**: Live API testing with `.env.tests` credentials

**Ready for**: Enhanced Langfuse operations, multi-environment support, advanced testing scenarios

---

## 🚀 Next Steps for Future Instances

**Priority 1: Enhanced Langfuse Operations**
- Implement `coaia fuse traces create` command
- Add dataset CRUD operations (`create`, `update`, `delete`)
- Enhance scoring and evaluation features
- Expand real API integration testing

**Priority 2: Advanced Configuration Features**  
- Multi-environment support (`.env.development`, `.env.production`)
- Encrypted .env file support for secure credential storage
- Configuration validation and schema enforcement
- Interactive setup with `coaia init --interactive`

**Priority 3: Integration & Automation**
- Langfuse workflow automation and batch operations
- Cross-service integration (AWS, Redis, OpenAI unified config)
- CI/CD pipeline integration for automated testing
- Performance monitoring and optimization

**See**: [NEXT_STEPS.md](./NEXT_STEPS.md) for detailed implementation roadmap  
**See**: [tests/NEXT_TESTING_ROADMAP.md](./tests/NEXT_TESTING_ROADMAP.md) for testing expansion plans

---

**Last Updated**: 2025-08-07  
**Next Action**: Implement enhanced Langfuse operations with real API testing