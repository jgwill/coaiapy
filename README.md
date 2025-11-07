# CoAiAPy

CoAiAPy is a comprehensive Python package for AI workflow automation and observability. It provides audio transcription, synthesis, and tagging capabilities using AWS services, along with revolutionary pipeline templates and environment management for automated AI workflows. Features complete Langfuse integration for AI pipeline observability, prompt management, and dataset operations.

* With a constraint to be compatible for python 3.6 (pythonista)
## Features

### 🚀 Pipeline Templates & Environment Management (NEW)
**Revolutionary Workflow Automation**: Transform 30+ minute manual setups into 30-second automated pipelines.

- **Pipeline Templates**: 5 built-in templates (simple-trace, data-pipeline, llm-chain, parallel-processing, error-handling)
- **Jinja2 Templating**: Variable substitution, validation, and conditional steps
- **Template Hierarchy**: Project → Global → Built-in discovery with customization support  
- **Environment Management**: Persistent cross-session variables with `.coaia-env` files
- **Shell Integration**: Export commands for bash automation and environment persistence
- **One-Command Workflows**: Complete trace/observation hierarchies created instantly

### Core Audio & Data Processing
- **Audio Transcription**: Convert audio files to text using AWS services
- **Audio Synthesis**: Generate audio files from text input
- **MP3 Tagging**: Add metadata tags to MP3 files for better organization and identification
- **Redis Stashing**: Stash key-value pairs to a Redis service

### Langfuse AI Observability (`coaia fuse`)
**Langfuse Integration**: Complete command-line interface for [Langfuse](https://langfuse.com/) - the open-source AI engineering platform for observability, analytics, and prompt management.

- **Prompt Management**: Create, list, and retrieve AI prompts with version control
- **Dataset Management**: Manage datasets with fine-tuning export (OpenAI/Gemini formats)  
- **Trace & Observation Workflows**: Production-ready AI pipeline observability
  - Auto-generated observation IDs and environment variable export
  - Pipeline integration with bash automation (`--export-env`)
  - Parent-child relationships with SPAN, EVENT, GENERATION observations
  - Shorthand type selection (`-te`, `-ts`, `-tg`)
  - Batch observation processing from JSON/YAML files
- **Session Management**: Create and manage user sessions with metadata
- **Project Integration**: Full Langfuse project and workspace support

## Installation

To install the package, you can use pip:

```bash
pip install coaiapy
```

## Usage

### CLI Tool

CoAiAPy provides a CLI tool for audio transcription, summarization, and stashing to Redis.

#### Help

To see the available commands and options, use the `--help` flag:

```bash
coaia --help
```

#### Setup

**Quick Start with Environment Variables**:

CoAiAPy supports multiple configuration methods. The easiest way is using environment variables or a `.env` file:

```bash
# Upstash Redis (Recommended)
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# AWS (for Polly text-to-speech)
AWS_KEY_ID=your_aws_key_id
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

**Using a .env file** (recommended for projects):

1. Copy `.env.example` to `.env` in your project directory
2. Fill in your credentials
3. CoAiAPy will automatically load these values

**Alternative Redis Configuration**:

If you're using a traditional Redis instance instead of Upstash:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_SSL=false
```

**Configuration Priority**: 
1. System environment variables (highest)
2. `.env` file in current directory
3. `~/.coaia.json` configuration file
4. Default values (lowest)

For detailed configuration instructions, see [REDIS_CONFIGURATION.md](REDIS_CONFIGURATION.md).
#### Transcribe Audio

To transcribe an audio file to text:

```bash
coaia transcribe <file_path>
```

Example:

```bash
coaia transcribe path/to/audio/file.mp3
```

#### Summarize Text

To summarize a text:

```bash
coaia summarize <text>
```

Example:

```bash
coaia summarize "This is a long text that needs to be summarized."
```

To summarize text from a file:

```bash
coaia summarize --f <file_path>
```

Example:

```bash
coaia summarize --f path/to/text/file.txt
```

#### Stash Key-Value Pair to Redis

To stash a key-value pair to Redis:

```bash
coaia tash <key> <value>
```

Example:

```bash
coaia tash my_key "This is the value to stash."
```

To stash a key-value pair from a file:

```bash
coaia tash <key> --f <file_path>
```

Example:

```bash
coaia tash my_key --f path/to/value/file.txt
```

#### Fetch Value from Redis

To fetch a value from Redis by key:

```bash
coaia fetch <key>
```

Example:

```bash
coaia fetch my_key
```

To fetch a value from Redis and save it to a file:

```bash
coaia fetch <key> --output <file_path>
```

Example:

```bash
coaia fetch my_key --output path/to/output/file.txt
```

#### Process Custom Tags

Enable custom quick addons for assistants or bots using process tags. To add a new process tag to `coaia.json`, include entries like:
```
	"dictkore_temperature":0.2,
	"dictkore_instruction": "You do : Receive a dictated text that requires correction and clarification.\n\n# Corrections\n\n- In the dictated text, spoken corrections are made. You make them and remove the text related to that to keep the essence of what is discussed.\n\n# Output\n\n- You keep all the essence of the text (same length).\n- You keep the same style.\n- You ensure annotated dictation errors in the text are fixed.",
```
```bash
coaia p dictkore "my text to correct"
```

## 🚀 Pipeline Templates & Environment Management

### Revolutionary Workflow Automation

CoAiAPy transforms complex AI pipeline creation from 30+ minute manual processes into 30-second automated workflows using templates and persistent environment management.

### Pipeline Templates

#### Built-in Templates (5 Available)

1. **simple-trace**: Basic monitoring with single observation
2. **data-pipeline**: Multi-step data processing workflow with validation
3. **llm-chain**: LLM interaction pipeline with input/output tracking
4. **parallel-processing**: Concurrent task execution with synchronization
5. **error-handling**: Robust error management with retry mechanisms

#### Template Commands

```bash
# List all available templates
coaia pipeline list
coaia pipeline list --path --json

# Inspect template details and variables
coaia pipeline show simple-trace
coaia pipeline show data-pipeline --preview

# Create pipeline from template (automatic trace/observation creation)
coaia pipeline create simple-trace --var trace_name="My Process" --var user_id="john"
coaia pipeline create data-pipeline --var pipeline_name="ETL Process" --export-env

# Create new custom template
coaia pipeline init my-template
coaia pipeline init custom-workflow --from data-pipeline --location project
```

#### Template Features

- **Variable Substitution**: Jinja2-powered with validation and built-in functions
- **Conditional Steps**: Include/exclude steps based on variable conditions
- **Parent-Child Relationships**: Automatic SPAN observation hierarchies
- **Template Hierarchy**: Project → Global → Built-in discovery system
- **Auto-Generation**: Trace IDs, observation IDs, timestamps generated automatically

### Environment Management

#### Persistent Cross-Session Variables

Environment files (`.coaia-env`) provide persistent variable storage across shell sessions:

```bash
# Initialize environment with defaults
coaia env init                    # Creates .coaia-env (project)
coaia env init --global          # Creates ~/.coaia/global.env
coaia env init --name dev        # Creates .coaia-env.dev

# Manage variables
coaia env set COAIA_USER_ID "john"     # Persist to file
coaia env set DEBUG_MODE "true" --temp # Session only
coaia env get COAIA_TRACE_ID           # Get variable value
coaia env unset OLD_VARIABLE           # Remove variable

# List and inspect environments  
coaia env list                    # Show all environments
coaia env list --name dev        # Show specific environment
coaia env list --json           # JSON output

# Shell integration
eval $(coaia env source --export)     # Load variables into shell
coaia env save --name "my-context"    # Save current state
```

#### Advanced Workflow Examples

**One-Command Pipeline Creation:**
```bash
# Before: Complex manual setup (30+ minutes)
export TRACE_ID=$(uuidgen)
export SESSION_ID=$(uuidgen) 
coaia fuse traces create $TRACE_ID -u john -s $SESSION_ID
export OBS_ID=$(uuidgen)
coaia fuse traces add-observation $OBS_ID $TRACE_ID -ts -n "Step 1"
# ... repeat for each step ...

# After: One-command automation (< 30 seconds)
coaia pipeline create data-pipeline \
  --var user_id="john" \
  --var pipeline_name="ETL Process" \
  --export-env

# Automatic: trace creation, observation hierarchy, environment setup
```

**Cross-Session Workflow Persistence:**
```bash
# Session 1: Start pipeline and persist state
coaia pipeline create llm-chain --var model="gpt-4" --export-env
coaia env save --name "llm-session"

# Session 2: Resume from saved state (hours/days later)
eval $(coaia env source --name llm-session --export)
coaia fuse traces add-observation $COAIA_TRACE_ID -n "Continued processing"
```

**Custom Template Creation:**
```bash
# Create project-specific template
coaia pipeline init company-etl --from data-pipeline --location project
# Edit ./.coaia/templates/company-etl.json with custom variables and steps

# Use custom template
coaia pipeline create company-etl --var data_source="production_db"
```

#### Environment File Formats

**JSON Format** (`.coaia-env`):
```json
{
  "COAIA_TRACE_ID": "uuid-here",
  "COAIA_USER_ID": "john",
  "CUSTOM_VARIABLE": "value"
}
```

**.env Format** (`.coaia-env`):
```bash
COAIA_TRACE_ID="uuid-here"
COAIA_USER_ID="john"
CUSTOM_VARIABLE="value"
```

### Building and Publishing

Use the provided `Makefile` to build and distribute the package. Typical tasks:

```bash
make build        # create sdist and wheel
make dist         # alias for make build
make upload-test  # upload the distribution to Test PyPI
make test-release # bump patch version, clean, build, and upload to Test PyPI
```

Both upload tasks use:
`twine upload --repository testpypi dist/*`
`make test-release` automatically sources `$HOME/.env` so `TWINE_USERNAME` and `TWINE_PASSWORD` are available.
If you need the variables in your shell, run:
```bash
export $(grep -v '^#' $HOME/.env | xargs)
```
It also bumps the patch version using `bump.py` before uploading.


## Langfuse Integration (`fuse`)

CoAiAPy integrates with Langfuse to manage prompts, datasets, and traces.

### Listing Prompts

To see a formatted table of all available prompts:
```bash
coaia fuse prompts list
```

### Getting a Specific Prompt

Retrieve a prompt by name. By default, it fetches the version with the `latest` label.
```bash
coaia fuse prompts get <prompt_name>
```

**Options:**
- `--label <label>`: Fetch the version with a specific label (e.g., `dev`, `staging`).
- `--prod`: A convenient shortcut for `--label production`.
- `--json`: Output the raw JSON response.
- `-c`, `--content-only`: Output only the raw prompt content, ideal for scripting.
- `-e`, `--escaped`: Output the prompt content as a single, JSON-escaped line. This is useful for embedding the content in other scripts or commands. Using `-e` implies `-c`.

**Examples:**
```bash
# Get the latest version of a prompt
coaia fuse prompts get MyPrompt

# Get the production version of a prompt
coaia fuse prompts get MyPrompt --prod

# Get only the content of a prompt
coaia fuse prompts get MyPrompt -c

# Get the content as an escaped, single line
coaia fuse prompts get MyPrompt -e
```

### Managing Datasets

#### Listing Datasets
To see a formatted table of all available datasets:
```bash
coaia fuse datasets list
```

#### Getting a Specific Dataset and its Items
Retrieve a dataset's metadata and all of its items in a formatted display.
```bash
coaia fuse datasets get <dataset_name>
```

**Options:**
- `--json`: Output the raw JSON for the dataset and its items.
- `-oft`, `--openai-ft`: Format the dataset for OpenAI fine-tuning (JSONL).
- `-gft`, `--gemini-ft`: Format the dataset for Gemini fine-tuning (JSONL).
- `--system-instruction "<text>"`: Customize the system instruction for fine-tuning formats. The default is "You are a helpful assistant".

**Examples:**
```bash
# Get a formatted view of a dataset and its items
coaia fuse datasets get MyDataset

# Get the raw JSON for a dataset
coaia fuse datasets get MyDataset --json

# Export a dataset for OpenAI fine-tuning
coaia fuse datasets get MyDataset -oft > training_data.jsonl

# Export for Gemini with a custom system instruction
coaia fuse datasets get MyDataset -gft --system-instruction "You are a creative writing assistant."
```

#### Creating a New Dataset
You can create a new, empty dataset directly from the CLI.
```bash
coaia fuse datasets create <new_dataset_name>
```

#### Adding Items to a Dataset
You can add new items (with an input and an optional expected output) to an existing dataset.
```bash
coaia fuse dataset-items create <dataset_name> --input "User question or prompt." --expected "Ideal model response."
```

### Traces & Observations - Enhanced AI Pipeline Support

CoAiAPy provides comprehensive support for Langfuse traces and observations with enhanced pipeline integration.

#### Creating Traces

Create a new trace with session, user metadata, and optional environment variable export:
```bash
coaia fuse traces create <trace_id> -s <session_id> -u <user_id> -n "Trace Name"
```

**Pipeline Integration Example:**
```bash
# Create trace and export environment variables for pipeline use
eval $(coaia fuse traces create $(uuidgen) -s $(uuidgen) -u pipeline-user -n "AI Workflow" --export-env)
echo "Created trace: $COAIA_TRACE_ID"
```

#### Adding Observations

Add single observations to traces with auto-generated IDs and enhanced CLI options:

**Basic Usage:**
```bash
# Observation ID is auto-generated if not provided
coaia fuse traces add-observation <trace_id> -n "Processing Step" -i '{"input":"data"}' -o '{"result":"output"}'

# With explicit observation ID
coaia fuse traces add-observation <trace_id> <observation_id> -n "Custom Step"
```

**Observation Types with Shortcuts:**
```bash
# EVENT (default) - discrete events
coaia fuse traces add-observation <trace_id> -te -n "Data Loaded"

# SPAN - operations with duration  
coaia fuse traces add-observation <trace_id> -ts -n "Main Processing"

# GENERATION - AI model calls
coaia fuse traces add-observation <trace_id> -tg -n "LLM Response" --model "gpt-4"
```

**Parent-Child Relationships:**
```bash
# Create parent SPAN
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -ts -n "Main Workflow" --export-env)
parent_span=$COAIA_LAST_OBSERVATION_ID

# Add child observations under the SPAN
coaia fuse traces add-observation $COAIA_TRACE_ID -n "Step 1" --parent $parent_span
coaia fuse traces add-observation $COAIA_TRACE_ID -n "Step 2" --parent $parent_span
```

**Pipeline Workflow Example:**
```bash
#!/bin/bash
# Complete AI pipeline with automatic ID propagation

# Step 1: Create trace and export environment
eval $(coaia fuse traces create $(uuidgen) -s $(uuidgen) -u ai-pipeline --export-env)

# Step 2: Create main SPAN observation
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -ts -n "AI Processing Pipeline" --export-env)
main_span=$COAIA_LAST_OBSERVATION_ID

# Step 3: Add processing steps under the main SPAN
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -n "Data Loading" --parent $main_span --export-env)
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -tg -n "Model Inference" --parent $main_span --model "gpt-4" --export-env)
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -n "Results Processing" --parent $main_span --export-env)

echo "Pipeline complete! Trace: $COAIA_TRACE_ID"
```

#### Batch Observations

Add multiple observations from JSON or YAML files:
```bash
# From file
coaia fuse traces add-observations <trace_id> -f observations.json

# From stdin with YAML format
cat observations.yaml | coaia fuse traces add-observations <trace_id> --format yaml

# Dry run to preview what would be created
coaia fuse traces add-observations <trace_id> -f observations.json --dry-run
```

**Example JSON format for batch observations:**
```json
[
  {
    "name": "Data Processing",
    "type": "SPAN",
    "input": {"dataset": "user_data.csv"},
    "output": {"processed_rows": 1000}
  },
  {
    "name": "Model Training", 
    "type": "GENERATION",
    "parent_observation_id": "previous-observation-id",
    "model": "gpt-4",
    "usage": {"tokens": 150, "cost": 0.003}
  }
]
```

#### Environment Variables for Pipelines

CoAiAPy exports standard environment variables for seamless pipeline integration:

- `COAIA_TRACE_ID`: Current trace identifier
- `COAIA_SESSION_ID`: Current session identifier  
- `COAIA_USER_ID`: Current user identifier
- `COAIA_LAST_OBSERVATION_ID`: Most recently created observation ID
- `COAIA_PARENT_OBSERVATION_ID`: Parent observation ID (when using --parent)

**Usage Pattern:**
```bash
# Commands with --export-env output only shell export statements (no JSON)
eval $(coaia fuse traces create $(uuidgen) --export-env)
eval $(coaia fuse traces add-observation $COAIA_TRACE_ID -ts -n "Process" --export-env)

# Use the exported variables in subsequent steps
coaia fuse traces add-observation $COAIA_TRACE_ID -n "Child" --parent $COAIA_LAST_OBSERVATION_ID
```

#### Advanced Features

**Datetime Format Support:**
- ISO format: `2025-08-17T14:30:22Z`
- TLID format: `250817143022` (yyMMddHHmmss)
- Short TLID: `2508171430` (yyMMddHHmm, seconds default to 00)

**Usage Information:**
```bash
coaia fuse traces add-observation <trace_id> -tg -n "LLM Call" \
  --model "gpt-4" \
  --usage '{"prompt_tokens": 100, "completion_tokens": 50, "total_cost": 0.0025}'
```

**Metadata and Levels:**
```bash
coaia fuse traces add-observation <trace_id> -n "Error Handling" \
  --level ERROR \
  --metadata '{"error_type": "timeout", "retry_count": 3}'
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Links

- [GitHub Repository](https://github.com/jgwill/coaiapy)
- [PyPI Package](https://pypi.org/project/coaiapy/)
- [llms.txt (AI Documentation)](https://coaiapy.jgwill.com/llms.txt)
- [Documentation Wiki](https://github.com/jgwill/coaiapy/wiki)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
