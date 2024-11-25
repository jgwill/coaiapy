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

#### Process Custom Tags

Enable custom quick addons for assistants or bots using process tags. To add a new process tag to `config.json`, include entries like:
```
	"dictkore_temperature":0.2,
	"dictkore_instruction": "You do : Receive a dictated text that requires correction and clarification.\n\n# Corrections\n\n- In the dictated text, spoken corrections are made. You make them and remove the text related to that to keep the essence of what is discussed.\n\n# Output\n\n- You keep all the essence of the text (same length).\n- You keep the same style.\n- You ensure annotated dictation errors in the text are fixed.",
```
```bash
coaia p dictkore "my text to correct"
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

