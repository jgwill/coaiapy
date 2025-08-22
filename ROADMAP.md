# CoAiAPy Project Roadmap

This document outlines the features of CoAiAPy, marking them as completed, in progress, or planned.

## Core Features

- `[x]` **Audio Transcription**: (`coaia transcribe`) Convert audio files to text.
- `[x]` **Text Summarization**: (`coaia summarize`) Summarize text from files or stdin.
- `[x]` **Redis Caching**: (`coaia tash`, `coaia fetch`) Store and retrieve key-value pairs from Redis.
- `[x]` **Custom Processing**: (`coaia p`) Run custom, user-defined processing pipelines.
- `[x]` **Configuration**: (`coaia init`) Initialize a local configuration file.

## Langfuse Integration (`fuse`)

### Prompt Management

- `[x]` **List Prompts**: (`coaia fuse prompts list`) Display all prompts in a formatted table.
- `[x]` **Get Prompt**: (`coaia fuse prompts get`) Retrieve a specific prompt.
  - `[x]` Fetch by label (`--label`, `--prod`).
  - `[x]` Default to `latest` label.
  - `[x]` JSON output (`--json`).
  - `[x]` Content-only output (`-c`, `--content-only`).
  - `[x]` Escaped, single-line output (`-e`, `--escaped`).
- `[x]` **Create Prompt**: (`coaia fuse prompts create`) Create a new prompt.

### Dataset Management

- `[x]` **List Datasets**: (`coaia fuse datasets list`) Display all datasets in a formatted table.
- `[x]` **Get Dataset**: (`coaia fuse datasets get`) Retrieve a dataset's metadata and items.
- `[x]` **Create Dataset**: (`coaia fuse datasets create`) Create a new dataset.
- `[x]` **Add Dataset Item**: (`coaia fuse dataset-items create`) Add a new item to a dataset.
- `[x]` **Fine-Tuning Export**:
  - `[x]` OpenAI format (`-oft`, `--openai-ft`).
  - `[x]` Gemini format (`-gft`, `--gemini-ft`).
  - `[x]` Custom system instruction (`--system-instruction`).

### Trace & Observation Management

- `[x]` **List Traces**: (`coaia fuse traces`) Display all traces in a formatted table.
- `[x]` **Create Trace**: (`coaia fuse traces create`) Create a new trace with session, user, and metadata.
  - `[x]` Environment variable export (`--export-env`) for pipeline workflows.
- `[x]` **Add Observation**: (`coaia fuse traces add-observation`) Add single observation to existing trace.
  - `[x]` Auto-generated observation IDs when not provided.
  - `[x]` Improved argument order: `trace_id` (required) → `observation_id` (optional).
  - `[x]` Shorthand type flags: `-te` (EVENT), `-ts` (SPAN), `-tg` (GENERATION).
  - `[x]` Environment variable export (`--export-env`) for pipeline workflows.
  - `[x]` Clean API response format with actual IDs (not internal event IDs).
- `[x]` **Batch Observations**: (`coaia fuse traces add-observations`) Add multiple observations to trace from file/stdin.
  - `[x]` Alias support: `add-obs` for single, `add-observations` for batch operations.
  - `[x]` JSON and YAML input format support.
  - `[x]` Parent-child observation relationships.
  - `[x]` Multiple observation types: EVENT, SPAN, GENERATION.
  - `[x]` TLID datetime format support (yyMMddHHmmss and yyMMddHHmm).

### Other Integrations

- `[x]` **Sessions**: Create and manage sessions.
- `[x]` **Scores**: Create and apply scores to traces.
- `[x]` **Comments**: List and post comments.
- `[x]` **Projects**: List projects.

## Pipeline Integration ✅ **COMPLETED**

### Environment Variable Workflow Support

- `[x]` **Shell Export Integration**: `--export-env` flag outputs shell variables for bash pipelines.
- `[x]` **Variable Standards**: `COAIA_TRACE_ID`, `COAIA_SESSION_ID`, `COAIA_LAST_OBSERVATION_ID`, `COAIA_PARENT_OBSERVATION_ID`.
- `[x]` **Pipeline Compatibility**: Clean output format for `eval $()` command substitution.
- `[x]` **Multi-Step Workflows**: Support for complex AI observability pipelines with automatic ID propagation.

### Enhanced CLI Experience

- `[x]` **UUID Auto-Generation**: Observation IDs automatically generated when not provided.
- `[x]` **Shorthand Options**: Quick type selection with `-te`, `-ts`, `-tg` flags.
- `[x]` **Response Cleanup**: API responses show actual IDs instead of internal event identifiers.
- `[x]` **Enhanced Help**: Detailed parameter descriptions and usage examples.

## Pipeline Templates & Environment Management ✅ **COMPLETED**

### Pipeline Template System

- `[x]` **List Templates**: (`coaia pipeline list`) Display all available templates with metadata.
- `[x]` **Show Template**: (`coaia pipeline show`) Inspect template details, variables, and steps.
- `[x]` **Create Pipeline**: (`coaia pipeline create`) Generate complete trace/observation workflows from templates.
- `[x]` **Initialize Template**: (`coaia pipeline init`) Create new custom templates with optional base templates.
- `[x]` **Template Features**:
  - `[x]` 5 built-in templates: simple-trace, data-pipeline, llm-chain, parallel-processing, error-handling.
  - `[x]` Jinja2 variable substitution with validation and built-in functions.
  - `[x]` Conditional step inclusion based on variables.
  - `[x]` Parent-child observation relationships with SPAN support.
  - `[x]` Template hierarchy: Project → Global → Built-in discovery.

### Environment Management System

- `[x]` **Initialize Environment**: (`coaia env init`) Create environment files with default variables.
- `[x]` **List Environments**: (`coaia env list`) Show available environment files and variables.
- `[x]` **Variable Management**: (`coaia env set/get/unset`) Manage environment variables.
- `[x]` **Source Environment**: (`coaia env source`) Load variables into current session.
- `[x]` **Clear Environment**: (`coaia env clear`) Remove environment files.
- `[x]` **Save Context**: (`coaia env save`) Save current environment as template.
- `[x]` **Environment Features**:
  - `[x]` Cross-session variable persistence with `.coaia-env` files.
  - `[x]` JSON and .env file format support.
  - `[x]` Shell export command generation for bash automation.
  - `[x]` Hierarchical environment resolution (OS → Project → Global).

## Planned Features

### V1.0: Fine-Tuning Management

- `[ ]` **`coaia fuse finetune create`**: Upload a dataset file to start a new fine-tuning job.
- `[ ]` **`coaia fuse finetune list`**: List all active fine-tuning jobs.
- `[ ]` **`coaia fuse finetune status <job_id>`**: Check the status of a specific job.
- `[ ]` **`coaia fuse finetune cancel <job_id>`**: Cancel an ongoing job.

### V1.1: Advanced Pipeline Features ✅ **COMPLETED**

- `[x]` **Environment File Management**: Persistent environment file (`.coaia-env`) for cross-session workflows.
- `[x]` **Pipeline Templates**: Pre-built templates for common AI workflow patterns (5 built-in templates).
- `[x]` **Template Hierarchy**: Project → Global → Built-in template discovery system.
- `[x]` **Jinja2 Templating**: Variable substitution, validation, and conditional steps.
- `[x]` **Cross-Session Persistence**: Environment variables persist across shell sessions.
- `[x]` **One-Command Workflows**: Complete pipeline creation from templates in seconds.

### V1.2: Advanced Automation & Integration

- `[ ]` **Template Sharing**: Community template repository and sharing system.
- `[ ]` **Bash Completion**: Shell completion for commands and parameters.
- `[ ]` **Multi-Environment Support**: Support for development, staging, production environment configurations.
- `[ ]` **Workflow Orchestration**: Automated pipeline scheduling and execution.
- `[ ]` **CI/CD Integration**: Template deployment and validation in CI/CD pipelines.

### V1.3: Enterprise Features

- `[ ]` **Encrypted Environment Files**: Secure credential storage with encryption.
- `[ ]` **Interactive Setup**: Interactive `coaia init --interactive` configuration.
- `[ ]` **Template Validation**: Testing framework for pipeline templates.
- `[ ]` **Performance Monitoring**: Pipeline execution monitoring and optimization.
- `[ ]` **Cross-Service Integration**: Unified configuration for AWS, Redis, OpenAI services.

### V1.4: Advanced CLI Features

- `[ ]` **Interactive Mode**: An interactive shell for running commands.
- `[ ]` **Direct Model Execution**: A `coaia run <prompt_name>` command to execute prompts directly against AI models.
- `[ ]` **Testing Suite**: A full `pytest` suite for robust testing.

## V2.0: Separation into Modules Refactoring

### Fuse Module

* submodule for Langfuse integration into 'git@github.com:jgwill/cofuse.git'
* Consideration to think about for the whole 'configuration' layer that cofuse will use that is probably embedded into 'coaiamodule' that obviously if this coaiapy package depends on this new 'cofuse' module package, it wont have access to the configuration layer but do we need it in cofule ? Would that be ok if it just look for common langfuse environment variables ? Try to load in .env, otherwise in $HOME/.env and config error if not, that is it.  It seems the right way todo it for now, simple therefore, any package that needs the 'cofuse' features (which is quite extensive) will benefits with its whole logics without having to worry about the configuration layer.  I am just worried about the 'template' of the 'coaia fuse pipeline' which we might have to think about how that could be abstracted adequatly.  Having a common 'configuration_layer' module that both 'cofuse' and 'coaiamodule' could use would be the best solution but I am not sure how to do it yet. jgwill/jgtcore will need the 'cofuse' feature that is for sure, no dependencies to boto3 and all these other dependencies that 'coaiamodule' has.


