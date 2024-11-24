import argparse
import os

import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash

EPILOG="""
coaiacli is a command line interface for audio transcription, summarization, and stashing to Redis.

setup these environment variables:
OPENAI_API_KEY
AWS_KEY_ID
AWS_SECRET_KEY
AWS_REGION
REDIS_HOST
REDIS_PORT
REDIS_PASSWORD
REDIS_SSL
"""

def tash_key_val(key, value):
    tash(key, value)
    print(f"Key: {key}, Value: {value} stashed successfully.")

def tash_key_val_from_file(key, file_path):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    with open(file_path, 'r') as file:
        value = file.read()
    tash_key_val(key, value)

def main():
    parser = argparse.ArgumentParser(description="CLI tool for audio transcription, summarization, and stashing to Redis.", epilog=EPILOG,prog="coaia")
    subparsers = parser.add_subparsers(dest='command')

    # Subparser for 'tash' command
    parser_tash = subparsers.add_parser('tash', help='Stash a key/value pair to Redis.')
    parser_tash.add_argument('key', type=str, help="The key to stash.")
    parser_tash.add_argument('value', type=str, nargs='?', help="The value to stash.")
    parser_tash.add_argument('--f', type=str, help="Read the value from a file.")

    # Subparser for 'transcribe' command
    parser_transcribe = subparsers.add_parser('transcribe', help='Transcribe an audio file to text.')
    parser_transcribe.add_argument('file_path', type=str, help="The path to the audio file.")

    # Subparser for 'summarize' command
    parser_summarize = subparsers.add_parser('summarize', help='Summarize a text.')
    parser_summarize.add_argument('text', type=str, help="The text to summarize.")
    parser_summarize.add_argument('--f', type=str, help="Read the text from a file.")

    args = parser.parse_args()

    if args.command == 'tash':
        if args.f:
            tash_key_val_from_file(args.key, args.f)
        elif args.value:
            tash_key_val(args.key, args.value)
        else:
            print("Error: You must provide a value or use the --f flag to read from a file.")
    elif args.command == 'transcribe':
        transcribed_text = transcribe_audio(args.file_path)
        print(f"Transcribed Text: {transcribed_text}")
    elif args.command == 'summarize':
        if args.f:
            if not os.path.isfile(args.f):
                print(f"Error: File '{args.f}' does not exist.")
                return
            with open(args.f, 'r') as file:
                text = file.read()
        else:
            text = args.text
        summary = summarizer(text)
        print(f"Summary: {summary}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()