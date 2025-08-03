# CoAiAPy

CoAiAPy is a Python package that provides functionality for audio transcription, synthesis, and tagging of MP3 files using Boto3 and the Mutagen library. This package is designed to facilitate the processing of audio files for various applications.

## Features

- **Audio Transcription**: Convert audio files to text using AWS services.
- **Audio Synthesis**: Generate audio files from text input.
- **MP3 Tagging**: Add metadata tags to MP3 files for better organization and identification.
- **Redis Stashing**: Stash key-value pairs to a Redis service.

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

Set these environment variables to use the AWS transcription service:

```bash
OPENAI_API_KEY
AWS_KEY_ID
AWS_SECRET_KEY
AWS_REGION
REDIS_HOST
REDIS_PORT
REDIS_PASSWORD
REDIS_SSL
```
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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
