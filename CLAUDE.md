# CLAUDE.md - CoaiaPy Package Documentation

**Status**: Project-Aware Smart Caching System Complete  
**Current Version**: 0.2.54+  
**Python Compatibility**: >=3.6 (Pythonista compatible)  
**Date**: 2025-08-24

---

## 📦 Package Overview

CoaiaPy is a Python package for audio transcription, synthesis, and tagging using Boto3, with Redis integration for data stashing and Langfuse integration for prompt management.

### Core Features
- **Audio Processing**: Transcription and synthesis via AWS Polly
- **Redis Integration**: Data stashing and retrieval (`tash`, `fetch` commands)
- **Langfuse Integration**: Comprehensive observability with traces, observations, and batch operations
- **Smart Caching**: Project-aware score-config caching with auto-refresh (`~/.coaia/score-configs/`)
- **Pipeline Templates**: Automated workflow creation from reusable templates (5 built-in templates)
- **Environment Management**: Persistent environment variables across sessions with `.coaia-env` files
- **Process Tags**: Custom text processing with configurable instructions
- **Config Management**: Multiple config file locations with environment variable overrides

### CLI Commands
```bash
# Core Operations
coaia transcribe <file>     # Transcribe audio to text
coaia summarize <text>      # Summarize text input
coaia tash <key> <value>    # Stash to Redis
coaia fetch <key>           # Fetch from Redis
coaia p <tag> <text>        # Process with custom tags
coaia init                  # Create sample config

# Langfuse Integration
coaia fuse traces create <id>              # Create new trace
coaia fuse traces add-observation <obs> <trace>  # Add single observation
coaia fuse traces add-observations <trace> # Batch add observations from file/stdin
coaia fuse prompts list                    # List prompts
coaia fuse datasets create <name>          # Create datasets

# Pipeline Templates (NEW)
coaia pipeline list                        # List available templates
coaia pipeline show <template>             # Show template details
coaia pipeline create <template> --var key=value  # Create pipeline from template
coaia pipeline init <name>                 # Create new template

# Environment Management (NEW)
coaia env init                             # Initialize environment file
coaia env list                             # List environments
coaia env set <key> <value>                # Set environment variable
coaia env get <key>                        # Get environment variable
coaia env source --export                  # Export shell commands
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
- `requirements.txt` - Runtime dependencies (includes Jinja2>=2.10)
- `Makefile` - Automated build/release workflows
- `bump.py` - Automatic version management
- `pipeline.py` - Pipeline template engine
- `environment.py` - Environment variable management
- `templates/` - Built-in pipeline templates (5 templates)

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
│   ├── pipeline.py            # Pipeline template engine (NEW)
│   ├── environment.py         # Environment management (NEW)
│   ├── templates/             # Built-in pipeline templates (NEW)
│   │   ├── simple-trace.json
│   │   ├── data-pipeline.json
│   │   ├── llm-chain.json
│   │   ├── parallel-processing.json
│   │   └── error-handling.json
│   ├── syntation.py           # Text processing
│   └── test_cli_fetch.py      # Tests
├── codex/                     # Development logs
│   └── ledgers/               # Build/release history
├── pyproject.toml             # Modern packaging config
├── setup.py                   # Legacy setup
├── requirements.txt           # Dependencies (includes Jinja2)
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
- **jinja2**: `>=2.10` - Template rendering engine for pipeline templates (NEW)

#### When Updating Dependencies
1. **Always verify Python 3.6 compatibility** before updating any dependency
2. **Test on Python 3.6** if available, or check PyPI compatibility tables
3. **Never update boto3 or mutagen** beyond specified versions
4. **Pin specific versions** for critical dependencies

---

## 🚀 Pipeline Templates & Environment Management

### **Revolutionary Workflow Transformation**
CoaiaPy now transforms complex 30+ minute manual setups into **one-command pipeline creation** with persistent environment management.

### **Pipeline Template System**

#### **Built-in Templates (5 Available)**
1. **simple-trace**: Basic monitoring with single observation
2. **data-pipeline**: Multi-step data processing workflow with validation
3. **llm-chain**: LLM interaction pipeline with input/output tracking
4. **parallel-processing**: Concurrent task execution with synchronization
5. **error-handling**: Robust error management with retry mechanisms

#### **Template Hierarchy & Discovery**
Templates are discovered in priority order:
1. **Project templates** (highest priority): `./.coaia/templates/`
2. **User global templates**: `~/.coaia/templates/`
3. **Built-in templates** (lowest priority): Package installation

#### **Template Management Commands**
```bash
# List all available templates
coaia pipeline list
coaia pipeline list --path --json

# Inspect template details and variables
coaia pipeline show simple-trace
coaia pipeline show llm-chain --preview

# Create pipeline from template
coaia pipeline create simple-trace --var trace_name="My Process" --var user_id="john"
coaia pipeline create data-pipeline --trace-id $(uuidgen) --export-env

# Create new custom template
coaia pipeline init my-custom-template
coaia pipeline init advanced-workflow --from data-pipeline
```

#### **Template Features**
- **Variable Substitution**: Jinja2-powered templating with validation
- **Built-in Functions**: `uuid4()`, `now()`, `timestamp()` available
- **Conditional Steps**: Include/exclude steps based on variables
- **Parent-Child Relationships**: SPAN observations with nested children
- **Metadata Enrichment**: Automatic template tracking and context

### **Environment Management System**

#### **Persistent Cross-Session Variables**
Environment files (`.coaia-env`) provide persistent variable storage across shell sessions:

```bash
# Initialize environment with defaults
coaia env init                    # Creates .coaia-env (project)
coaia env init --global          # Creates ~/.coaia/global.env
coaia env init --name dev        # Creates .coaia-env.dev

# Manage variables
coaia env set COAIA_USER_ID "john" --persist
coaia env set DEBUG_MODE "true" --temp  # Session only
coaia env get COAIA_TRACE_ID
coaia env unset OLD_VARIABLE

# List and inspect environments  
coaia env list                    # All environments
coaia env list --name dev        # Specific environment
coaia env list --json           # JSON output

# Shell integration
eval $(coaia env source --export)  # Load into shell
coaia env save --name "my-context" # Save current state
```

#### **Environment File Formats**
Supports both JSON and .env formats:

**JSON Format** (`.coaia-env`):
```json
{
  "COAIA_TRACE_ID": "uuid-here",
  "COAIA_USER_ID": "john",
  "_COAIA_ENV_CREATED": "1692123456"
}
```

**.env Format** (`.coaia-env`):
```bash
COAIA_TRACE_ID="uuid-here"
COAIA_USER_ID="john"
# Metadata hidden from display
```

#### **Hierarchy & Priority**
Environment variables resolve in order:
1. **Current OS environment** (highest priority)
2. **Project environment** (`.coaia-env`)
3. **Global environment** (`~/.coaia/global.env`)
4. **Template defaults** (lowest priority)

### **Advanced Pipeline Workflows**

#### **One-Command Pipeline Creation**
```bash
# Before: Complex manual setup (30+ minutes)
export TRACE_ID=$(uuidgen)
coaia fuse traces create $TRACE_ID -u john -s session123
export OBS_ID=$(uuidgen)  
coaia fuse traces add-observation $OBS_ID $TRACE_ID -n "Step 1" -ts
# ... repeat for each step ...

# After: One-command automation (< 30 seconds)
coaia pipeline create data-pipeline \
  --var user_id="john" \
  --var pipeline_name="ETL Process" \
  --export-env

# Automatic trace creation, observation hierarchy, environment setup
```

#### **Cross-Session Workflow Persistence**
```bash
# Session 1: Start pipeline and persist state
coaia pipeline create llm-chain --var model="gpt-4" --export-env
eval $(coaia env save --name "llm-session")

# Session 2: Resume from saved state
eval $(coaia env source --name llm-session --export)
coaia fuse traces add-observation $COAIA_TRACE_ID -n "Continued processing"
```

#### **Template Extension & Customization**
```bash
# Create project-specific template based on built-in
coaia pipeline init company-etl --from data-pipeline --location project

# Edit template with custom variables and steps
# File created: ./.coaia/templates/company-etl.json

# Use custom template
coaia pipeline create company-etl --var data_source="sales_db"
```

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
✅ **TestPyPI Integration**: Working (latest: v0.2.54+)  
✅ **Version Management**: Automated via bump.py  
✅ **Clean Build Process**: Artifacts properly managed  
✅ **Dependency Validation**: Twine checks pass  
✅ **Environment Variable Support**: Complete .env integration with Langfuse
✅ **Docker Test Suite**: Comprehensive testing including real API validation
✅ **Real Langfuse Integration**: Live API testing with validated credentials
✅ **Enhanced Observation Workflows**: Production-ready AI pipeline observability
✅ **Pipeline Template System**: 5 built-in templates with Jinja2 rendering ✨ **NEW**
✅ **Environment Management**: Persistent cross-session variable storage ✨ **NEW**
✅ **One-Command Pipelines**: 30+ minute setups reduced to 30 seconds ✨ **NEW**
✅ **Template Hierarchy**: Project → Global → Built-in discovery system ✨ **NEW**
✅ **Shell Integration**: Export commands and bash automation support ✨ **NEW**
✅ **Smart Caching System**: Project-aware score-config caching with auto-refresh ✨ **NEW**

**Ready for**: Advanced automation workflows, template sharing, CI/CD integration

---

## 🧠 Smart Caching System for Score Configs (Phase 2)

### **Revolutionary Performance Enhancement**
CoaiaPy now features a sophisticated project-aware caching system that dramatically improves score-config retrieval performance and reduces API calls.

### **Key Features**
- **Project-Aware Structure**: Separate cache files per Langfuse project (`~/.coaia/score-configs/{project_id}.json`)
- **Auto-Detection**: Automatically detects current project via existing `list_projects()` API
- **Smart Auto-Refresh**: Cache-first with transparent refresh on miss/staleness (24-hour default)
- **No Manual Sync**: Completely automatic - no user intervention required
- **Robust Error Handling**: Graceful fallback to direct API calls when needed

### **Cache Structure**
```json
{
  "project_id": "cm6m5rrk6001vvkbq7zovttji",
  "project_name": "depotoire2502", 
  "last_sync": "2025-08-24T10:30:00Z",
  "configs": [
    {
      "id": "config-123",
      "name": "Helpfulness", 
      "dataType": "CATEGORICAL",
      "categories": [...],
      "cached_at": "2025-08-24T10:30:00Z"
    }
  ]
}
```

### **Core Functions**
- **`get_config_with_auto_refresh(config_name_or_id)`**: Main API - smart cache-first retrieval
- **`get_current_project_info()`**: Auto-detect current project from Langfuse
- **`load_project_cache(project_id)`**: Load project-specific cache
- **`is_cache_stale(cached_config, max_age_hours=24)`**: Check cache freshness
- **`cache_score_config(cache_path, config)`**: Store/update configs in cache

### **Usage Scenarios**
1. **Fresh Cache Hit**: Config found in cache (< 24h old) → Instant return
2. **Cache Miss**: Config not in cache → API fetch + cache storage
3. **Stale Cache**: Config > 24h old → API refresh + cache update  
4. **Error Handling**: API/cache failures → Graceful fallback to direct API

### **Performance Impact**
- **Cache Hit**: ~1ms vs ~200-500ms API call (200-500x faster)
- **Reduced API Load**: Minimizes Langfuse API calls through intelligent caching
- **Cross-Session Persistence**: Cache survives across CLI invocations and sessions

---

## 🚀 Next Steps for Future Instances

**Priority 1: Pipeline Templates & Environment Management** ✅ **COMPLETED (v0.2.54+)**
- ✅ Implement pipeline template system with 5 built-in templates
- ✅ Add Jinja2-powered variable substitution and validation
- ✅ Create environment file management (`.coaia-env`) for persistent workflows
- ✅ Add template hierarchy: project → global → built-in discovery
- ✅ Implement shell integration with export commands
- ✅ Add conditional steps and parent-child relationships
- ✅ Create template initialization and customization system
- ✅ Add cross-session workflow persistence

**Priority 2: Advanced Automation & Integration**  
- Template sharing and community repository
- Bash completion and enhanced shell integration
- Multi-environment support (`.env.development`, `.env.production`)
- Automated workflow orchestration and scheduling
- CI/CD pipeline integration for template deployment
- Template validation and testing framework

**Priority 3: Enterprise Features & Security**
- Encrypted .env file support for secure credential storage
- Configuration validation and schema enforcement
- Interactive setup with `coaia init --interactive`
- Cross-service integration (AWS, Redis, OpenAI unified config)
- Performance monitoring and optimization
- Template versioning and dependency management

**See**: [NEXT_STEPS.md](./NEXT_STEPS.md) for detailed implementation roadmap  
**See**: [tests/NEXT_TESTING_ROADMAP.md](./tests/NEXT_TESTING_ROADMAP.md) for testing expansion plans

---

## 🎉 Major Release: v0.2.54+ - Pipeline Templates & Environment Management Revolution

### **Breakthrough Features Delivered**

✨ **Pipeline Templates**: 5 built-in templates transform 30+ minute setups into 30-second automation  
✨ **Environment Management**: Persistent cross-session variables with `.coaia-env` files  
✨ **Template Hierarchy**: Project → Global → Built-in discovery system with customization  
✨ **Jinja2 Rendering**: Variable substitution, validation, and conditional steps  
✨ **Shell Integration**: Export commands and bash automation with environment persistence  

### **The Ultimate Workflow Revolution**
```bash
# Before: Complex multi-step manual setup (30+ minutes)
export TRACE_ID=$(uuidgen)
export SESSION_ID=$(uuidgen)
coaia fuse traces create $TRACE_ID -u john -s $SESSION_ID -n "Data Pipeline"
export OBS1_ID=$(uuidgen)
coaia fuse traces add-observation $OBS1_ID $TRACE_ID -ts -n "Data Validation"
export OBS2_ID=$(uuidgen)  
coaia fuse traces add-observation $OBS2_ID $TRACE_ID -n "Processing" --parent $OBS1_ID
# ... repeat for each step, prone to errors, no persistence ...

# After: One-command pipeline automation (< 30 seconds)
coaia pipeline create data-pipeline \
  --var user_id="john" \
  --var pipeline_name="ETL Process" \
  --var data_source="production_db" \
  --export-env

# Automatic: trace creation, observation hierarchy, environment setup, persistence
```

### **Cross-Session Persistence Magic**
```bash
# Session 1: Create and persist
coaia pipeline create llm-chain --var model="gpt-4" --export-env
coaia env save --name "llm-session"  # Persist state

# Session 2: Resume seamlessly (hours/days later)
eval $(coaia env source --name llm-session --export)
coaia fuse traces add-observation $COAIA_TRACE_ID -n "Resumed processing"
```

### **Template System Power**
```bash
# Inspect built-in templates
coaia pipeline list
coaia pipeline show data-pipeline --preview

# Create custom templates
coaia pipeline init company-workflow --from data-pipeline --location project
# Edit ./.coaia/templates/company-workflow.json with custom variables

# Use anywhere
coaia pipeline create company-workflow --var environment="production"
```

### **Impact & Benefits**
- **⚡ Speed**: 30+ minute workflows → 30 seconds (60x faster)
- **🔄 Persistence**: Cross-session state management with environment files  
- **🎯 Reliability**: Template validation eliminates configuration errors
- **📈 Scalability**: Template hierarchy supports team and enterprise workflows
- **🛠 Customization**: Jinja2 templating with conditional logic and built-in functions
- **🔗 Integration**: Shell export commands enable bash automation pipelines

**CoaiaPy is now the definitive solution for automated AI pipeline creation and management!**

---

**Last Updated**: 2025-08-18  
**Next Action**: Advanced template sharing and enterprise integration features