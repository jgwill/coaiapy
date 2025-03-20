# CoAiAPy

CoAiAPy is a Python package that provides a CLI tool for audio transcription, text summarization, and Redis stashing. It leverages OpenAI for text processing and Redis for data storage.

## Features

- **Audio Transcription**: Converts audio files to text using the OpenAI Whisper API.
- **Text Summarization**: Summarizes text using the OpenAI API.
- **Redis Stashing**: Stores key-value pairs in a Redis database.
- **Custom Process Tags**: Enables custom text processing using configurations defined in `coaia.json`.
- **Langfuse Integration**: Supports tracing and monitoring using Langfuse.

## Installation

To install the package, use pip:

```bash
pip install coaiapy
```

## Configuration

Before using CoAiAPy, you need to set up a configuration file (`coaia.json`) in your home directory or the current working directory. You can create a sample configuration file by running:

```bash
coaia init
```

This will create a `coaia.json` file in your home directory (`~/.config/jgwill/coaia.json` or `~/coaia.json`) with placeholder values. You need to replace these placeholders with your actual API keys and Redis credentials.

### Environment Variables

The following environment variables can be used to override the values in the `coaia.json` file:

- `OPENAI_API_KEY`: OpenAI API key.
- `AWS_KEY_ID`: AWS key ID for Polly service.
- `AWS_SECRET_KEY`: AWS secret key for Polly service.
- `AWS_REGION`: AWS region for Polly service.
- `REDIS_HOST`: Redis host.
- `REDIS_PORT`: Redis port.
- `REDIS_PASSWORD`: Redis password.
- `REDIS_SSL`: Redis SSL setting.
- `UPSTASH_HOST`: Upstash host (alternative to Redis).
- `UPSTASH_PASSWORD`: Upstash password (alternative to Redis).

## Usage

### CLI Tool

CoAiAPy provides a command-line interface (`coaia`) for various tasks.

#### Help

To display help information, use the `--help` flag:

```bash
coaia --help
```

#### Transcribe Audio

To transcribe an audio file to text:

```bash
coaia transcribe <file_path> [-O <output_file>]
```

- `<file_path>`: Path to the audio file.
- `-O <output_file>`: Optional output file to save the transcribed text. If not specified, the text will be printed to the console.

Example:

```bash
coaia transcribe audio.mp3 -O output.txt
```

#### Summarize Text

To summarize text from a file or standard input:

```bash
coaia summarize [<file_path>] [-O <output_file>]
```

- `<file_path>`: Optional path to a file containing the text to summarize. If not specified, the text will be read from standard input.
- `-O <output_file>`: Optional output file to save the summarized text. If not specified, the text will be printed to the console.

Examples:

```bash
coaia summarize text.txt -O summary.txt
cat text.txt | coaia summarize -O summary.txt
coaia summarize -O summary.txt < text.txt
```

#### Stash Key-Value Pair to Redis

To stash a key-value pair to Redis:

```bash
coaia tash <key> <value> [-T <ttl>]
coaia tash <key> -F <file_path> [-T <ttl>]
```

- `<key>`: The key to stash.
- `<value>`: The value to stash.
- `-F <file_path>`: Read the value from a file.
- `-T <ttl>`: Time-to-live in seconds for the key. Defaults to 5555.

Examples:

```bash
coaia tash my_key "This is the value" -T 3600
coaia tash my_key -F value.txt -T 3600
```

#### Process with Custom Tag

To process input with a custom tag defined in `coaia.json`:

```bash
coaia p <process_name> <input_message> [-O <output_file>] [-F <file_path>]
```

- `<process_name>`: The name of the process tag defined in `coaia.json`.
- `<input_message>`: The input message to process.
- `-O <output_file>`: Optional output file to save the processed text. If not specified, the text will be printed to the console.
- `-F <file_path>`: Read the input message from a file.

Example:

```bash
coaia p dictkore "correct my dictation" -O corrected.txt
coaia p dictkore -F input.txt -O corrected.txt
```

Ensure that the `coaia.json` file contains the necessary configurations for the process tag, including `process_name_instruction` and `process_name_temperature`.

#### Langfuse Integration

CoAiAPy supports integration with Langfuse for tracing and monitoring. The `fuse` command provides subcommands for managing comments, prompts, datasets, sessions, scores, and traces.

##### Comments

```bash
coaia fuse comments <list|post> [<comment_text>]
```

- `list`: List comments.
- `post`: Post a comment.
- `<comment_text>`: The comment text to post.

##### Prompts

```bash
coaia fuse prompts <list|get|create> [<name>] [<content>]
```

- `list`: List prompts.
- `get`: Get a prompt by name.
- `create`: Create a prompt.
- `<name>`: The prompt name.
- `<content>`: The prompt content.

##### Datasets

```bash
coaia fuse datasets <list|get|create> [<name>]
```

- `list`: List datasets.
- `get`: Get a dataset by name.
- `create`: Create a dataset.
- `<name>`: The dataset name.

##### Sessions

```bash
coaia fuse sessions <create|addnode|view> ...
```

- `create`: Create a session.
  ```bash
  coaia fuse sessions create <session_id> <user_id> [-n <name>] [-f <file>]
  ```
- `addnode`: Add a node to a session.
  ```bash
  coaia fuse sessions addnode <session_id> <trace_id> <user_id> [-n <name>] [-f <file>]
  ```
- `view`: View a session.
  ```bash
  coaia fuse sessions view [-f <file>]
  ```
  - `-f <file>`: YAML file to store session data (default: `session.yml`).

##### Scores

```bash
coaia fuse scores <create|apply> ...
```

- `create`: Create a score.
  ```bash
  coaia fuse scores create <score_id> [-n <name>] [-v <value>]
  ```
- `apply`: Apply a score to a trace.
  ```bash
  coaia fuse scores apply <trace_id> <score_id> [-v <value>]
  ```

##### Traces

```bash
coaia fuse traces <list|add> ...
```

- `list`: List traces.
- `add`: Add a trace.
  ```bash
  coaia fuse traces add <trace_id> -s <session_id> -u <user_id> -n <name> [-d <data>]
  ```
  - `-d <data>`: Additional trace data as JSON string.

##### Projects

```bash
coaia fuse projects
```

- List projects.

##### Dataset Items

```bash
coaia fuse dataset-items create <datasetName> -i <input> [-e <expected>] [-m <metadata>]
```

- `create`: Create a dataset item.
  - `-i <input>`: Input data.
  - `-e <expected>`: Expected output.
  - `-m <metadata>`: Optional metadata as JSON string.

#### Init

To create a default coaia.json file

```bash
coaia init
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

