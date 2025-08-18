# Changelog

All notable changes to this project will be documented in this file.

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
- **`coaia env init/list/set/get/unset/source/clear/save`**: Complete environment variable management system

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
- **Cross-Session**: `coaia env save --name "context"` and `eval $(coaia env source --name context --export)`

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
