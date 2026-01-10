# Changelog

All notable changes to this project will be documented in this file.

## [0.4.4] - 2026-01-10 - Major Feature Release & Refactoring

### 🚀 Major Features
- **Comprehensive Langfuse Integration Enhancements**:
  - Expanded `cofuse.py` with significant updates for improved Langfuse observability.
  - Introduction of Media Upload functionality to enrich traces and observations with visual context.
  - Enhanced comments and scoring mechanisms within Langfuse integration.
- **MCP Overhaul (`coaiapy-mcp`)**:
  - Major refactoring and expansion of the Model Context Protocol (MCP) server and tools.
  - Improved configuration management for MCP.
- **CLI & Core Functionality Expansion**:
  - Extensive updates to `coaiapy.coaiacli.py` for new and improved CLI commands.
  - Introduction of `coaiapy.cogh.py` for GitHub-related functionalities.
- **Advanced LLM Tooling**:
  - Significant additions and modifications within the `__llms/` directory, indicating new LLM-specific tools and documentation (e.g., `llms-jgwill-miadi-issue-115-github-hooks-issues-subissues.md`).
- **Pipeline Templates & Environment Management**:
  - Further development and refinement of template-driven workflow automation and persistent environment variable management.

### 📚 Documentation Updates
- **`README.md`**: Updated to reflect new features, particularly Pipeline Templates & Environment Management, and Langfuse integration.
- **`REDIS_CONFIGURATION.md`**: Comprehensive updates for Redis configuration, debugging, and priority order.
- **`MEDIA_UPLOAD_GUIDE.md`**: New guide for media upload functionality.
- **`llms.txt`**: Updated version information and general content adjustments.
- Various other documentation files (`CLI_ENV_REFACTOR_SUMMARY.md`, `FIX_SUMMARY.md`, `ROADMAP_MEDIA_PIPELINE.md`, etc.) added or significantly updated.

### 🧪 Testing & Quality Assurance
- Added new test suites, particularly for media upload and Redis environment variable handling.

### ⬆️ Dependency Updates
- Updated `pyproject.toml` and `requirements.txt` to reflect new and modified dependencies.

## [0.2.84] - 2025-11-07 - Comprehensive Redis Configuration & Debugging

### ✨ Enhanced Features
- **Unified Redis Configuration**: Consolidated all Redis/Upstash/Vercel KV configuration documentation into `REDIS_CONFIGURATION.md`.
- **Expanded Environment Variable Support**: Added full support and documentation for Vercel KV variables (`KV_REST_API_URL`, `KV_REST_API_TOKEN`, `KV_URL`, `REDIS_URL`).
- **Refined Priority Order**: Clearly defined and documented the priority order for all Redis connection methods (Upstash Direct, Vercel KV, Traditional Redis, Config Files).
- **Verbose Debugging Mode**: Introduced `--verbose` flag for `coaia tash` and `coaia fetch` commands, providing detailed connection information for troubleshooting.
- **Improved Error Messages**: Enhanced error messages to guide users with specific troubleshooting steps and variable names.

### 🐛 Bug Fixes
- **Removed Non-Standard Variables**: Eliminated support for confusing and non-standard `UPSTASH_REST_API_*` variables, aligning with platform standards.

### 📚 Documentation Updates
- **REDIS_CONFIGURATION.md**: Completely overhauled to be a single source of truth for Redis configuration, including detailed examples, troubleshooting, and migration guides.
- **Removed Redundant Files**: Deleted `CHANGES_SUMMARY.md`, `ENVIRONMENT_VARIABLES_REFERENCE.md`, `FIX_SUMMARY_REDIS.md`, `REDIS_FIX_DOCUMENTATION.md`, `SUPPORTED_VARIABLES.txt`, `UPDATE_NOTES.md`, and `VISUAL_COMPARISON.md` after content consolidation.

## [0.2.83] - 2025-10-31 - Comment Support Enhancement & API Fixes

### ✨ Enhanced Features
- **Complete Comment Support**: Comprehensive Langfuse comment functionality with filtering and pagination
  - `get_comments()`: Enhanced with object_type, object_id, author_user_id filtering and pagination (page, limit)
  - `get_comment_by_id()`: New function for retrieving specific comments by ID
  - `post_comment()`: Enhanced to require object_type and object_id, with auto-detection of projectId

### 🔧 API Compliance Fixes
- **Uppercase Object Types**: Automatic conversion to uppercase (TRACE, OBSERVATION, SESSION, PROMPT) for API compliance
- **Project ID Auto-Detection**: Automatic retrieval of projectId from Langfuse API for comment creation
- **Field Name Corrections**: Changed `text` → `content` to match Langfuse API specification
- **Response Format Handling**: Fixed project list parsing to handle `{"data": [...]}` response format

### 🐛 Bug Fixes
- **Import Path Fix**: Corrected import from `coaiamodule` to `coaiapy.coaiamodule` for proper module resolution
- **Project Info Retrieval**: Fixed `get_current_project_info()` to properly extract project data from API response

### 📚 Documentation Updates
- **llms.txt Updated**: Comprehensive update with comment support documentation, MCP integration details, and current version numbers (v0.2.83)
- **Comment API Examples**: Added detailed usage examples for all comment operations with filtering and pagination

### 🔗 MCP Integration
- Full support for comment operations via coaiapy-mcp v0.1.9
- See coaiapy-mcp CHANGELOG for MCP-specific enhancements

## [0.2.54+] - 2025-08-18 - Pipeline Templates & Environment Management Revolution

### 🚀 Major Features Added
- **Pipeline Template System**: Complete template engine with 5 built-in templates (simple-trace, data-pipeline, llm-chain, parallel-processing, error-handling)
- **Environment Management**: Persistent cross-session variable storage with `.coaia-env` files supporting JSON and .env formats
- **Jinja2 Templating Engine**: Variable substitution, validation, conditional steps, and built-in functions (uuid4(), now(), timestamp())
- **Template Hierarchy**: Project → Global → Built-in discovery system with customization support
- **One-Command Workflows**: Transform 30+ minute manual setups into 30-second automated pipeline creation

### ⚡ Revolutionary CLI Commands
- **`coaia pipeline list`**: Display all available templates with metadata and optional path information
- **`coaia pipeline show <template>`**: Inspect template details, variables, steps with optional preview rendering
- **`coaia pipeline create <template>`**: Generate complete trace/observation workflows from templates with variable substitution
- **`coaia pipeline init <name>`**: Create new custom templates with optional base template extension
- **`coaia environment init/list/set/get/unset/source/clear/save`**: Complete environment variable management system

### 🔄 Cross-Session Persistence
- **Environment Files**: `.coaia-env` files for project-level and `~/.coaia/global.env` for global persistence
- **Variable Hierarchy**: OS environment → Project environment → Global environment → Template defaults
- **Shell Integration**: `--export` flag generates shell export commands for bash automation
- **Context Saving**: Save and restore complete pipeline contexts across sessions

### 🛠 Template System Features
- **Built-in Functions**: Jinja2 template engine with uuid4(), now(), timestamp() functions
- **Conditional Steps**: Include/exclude steps based on variable conditions  
- **Parent-Child Relationships**: Automatic SPAN observation hierarchies with nested children
- **Variable Validation**: Type checking, required field validation, and choice constraints
- **Template Extension**: Create custom templates based on existing ones with inheritance

### 📈 Workflow Transformation Examples
- **Before**: 30+ minute manual trace/observation setup with error-prone ID management
- **After**: `coaia pipeline create data-pipeline --var user_id="john" --export-env` (< 30 seconds)
- **Cross-Session**: `coaia environment save --name "context"` and `eval $(coaia environment source --name context --export)`

### 🔧 Technical Improvements
- **New Dependencies**: Added Jinja2>=2.10 for template rendering
- **New Modules**: `pipeline.py` (template engine) and `environment.py` (environment management)
- **Enhanced CLI**: Comprehensive help text for all pipeline and environment commands
- **Error Handling**: Template validation, variable type checking, and user-friendly error messages

## [0.2.54] - 2025-08-17

### Added
- **Observation Auto-Generation**: `observation_id` is now optional and auto-generated using UUID when not provided
- **Environment Variable Export**: Added `--export-env` flag to output shell variables (`COAIA_TRACE_ID`, `COAIA_LAST_OBSERVATION_ID`, `COAIA_PARENT_OBSERVATION_ID`) for pipeline workflows
- **Shorthand Observation Types**: Added convenience flags `-te` (EVENT), `-ts` (SPAN), `-tg` (GENERATION) as shortcuts for `--type`
- **Response Processing**: Implemented clean API response format showing actual observation/trace IDs instead of internal event IDs
- **Enhanced Help Text**: Improved CLI help descriptions for all observation parameters with detailed explanations

### Changed  
- **CLI Argument Order**: `trace_id` is now the first required argument, `observation_id` is second and optional for `add-observation` command
- **Pipeline Integration**: Commands with `--export-env` output only shell export statements (no JSON) for `eval $()` usage
- **Observation Types**: Enhanced help text explains EVENT (default), SPAN (with duration), GENERATION (model call) use cases

### Fixed
- **Response Format**: API responses now return actual observation/trace IDs instead of confusing internal event IDs suffixed with "-event"
- **Parent Relationships**: Proper handling of nested observations under SPAN parents
- **Environment Variables**: Clean shell export format compatible with bash `eval $()` command substitution

### Technical Improvements
- **UUID Import**: Added UUID module for reliable ID generation
- **Response Processor**: New `process_langfuse_response()` function cleans up Langfuse API responses
- **Pipeline Workflows**: Full support for complex multi-step AI observability pipelines

## [0.2.51] - 2025-08-03

### Added
- **Fine-Tuning Export**: `datasets get` command can now export datasets in formats compatible with OpenAI (`--openai-ft`, `-oft`) and Gemini (`--gemini-ft`, `-gft`) for fine-tuning.
- **Custom System Instruction**: Added `--system-instruction` flag to customize the system message in fine-tuning exports.
- **Dataset Item Display**: `datasets get` command now fetches and displays the items within a dataset in a formatted table.
- **Content-Only Prompt Output**: Added `-c` / `--content-only` flag to `prompts get` to output only the raw prompt content.
- **Escaped Prompt Output**: Added `-e` / `--escaped` flag to `prompts get` to output prompt content as a single, JSON-escaped line for scripting.
- **ROADMAP.md**: Created a roadmap to track future development.
- **CHANGELOG.md**: Created a changelog to track project history.

### Changed
- **Default Prompt Label**: `prompts get` now defaults to fetching the `latest` label when no specific label is provided.
- **Documentation**: Updated `README.md` to include all new features for prompts and datasets.

### Fixed
- **Prompt Fetching Logic**: Corrected an issue where the `production` label was being unintentionally used as a fallback.
- **Error Display**: Improved error handling to show clear messages from the Langfuse API when a prompt or dataset is not found.
- **Prompt Content Parsing**: Enhanced display functions to correctly handle both string and chat-based (list of objects) prompt formats.

## [0.2.47] - 2025-06-15

### Added
- **Langfuse Integration**: Initial integration with the Langfuse API under the `coaia fuse` command.
- **Prompt Management**: Added `prompts list`, `prompts get`, and `prompts create` commands.
- **Dataset Management**: Added `datasets list`, `datasets get`, and `datasets create` commands.
- **Formatted Output**: Implemented pretty-printed tables for `prompts list` and `datasets list`.
- **JSON Output**: Added `--json` flag for raw API output.

### Fixed
- **API Pagination**: Implemented correct pagination handling for listing prompts.

## [0.2.40] - 2025-06-15

### Added
- **Redis `fetch` command**: Added `coaia fetch` to retrieve values from Redis.
- **CI/CD**: Set up GitHub Actions for continuous integration and testing.

### Changed
- **Configuration**: Migrated from `config.json` to `coaia.json` and improved config loading logic.

## [Initial Version]

### Added
- **Core Functionality**: Initial release with `transcribe`, `summarize`, `tash`, and custom process `p` commands.
- **AWS & Redis Integration**: Core integration with AWS for transcription and Redis for caching.
- **Build System**: `Makefile` for building and publishing the package.
