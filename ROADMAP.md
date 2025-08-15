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
- `[x]` **Add Observation**: (`coaia fuse traces add-observation`) Add single observation to existing trace.
- `[x]` **Batch Observations**: (`coaia fuse traces add-observations`) Add multiple observations to trace from file/stdin.
  - `[x]` Alias support: `add-obs` for single, `add-observations` for batch operations.
  - `[x]` JSON and YAML input format support.
  - `[x]` Parent-child observation relationships.
  - `[x]` Multiple observation types: EVENT, SPAN, GENERATION.

### Other Integrations

- `[x]` **Sessions**: Create and manage sessions.
- `[x]` **Scores**: Create and apply scores to traces.
- `[x]` **Comments**: List and post comments.
- `[x]` **Projects**: List projects.

## Planned Features

### V1.0: Fine-Tuning Management

- `[ ]` **`coaia fuse finetune create`**: Upload a dataset file to start a new fine-tuning job.
- `[ ]` **`coaia fuse finetune list`**: List all active fine-tuning jobs.
- `[ ]` **`coaia fuse finetune status <job_id>`**: Check the status of a specific job.
- `[ ]` **`coaia fuse finetune cancel <job_id>`**: Cancel an ongoing job.

### V1.1: Advanced CLI Features

- `[ ]` **Interactive Mode**: An interactive shell for running commands.
- `[ ]` **Direct Model Execution**: A `coaia run <prompt_name>` command to execute prompts directly against AI models.
- `[ ]` **Testing Suite**: A full `pytest` suite for robust testing.