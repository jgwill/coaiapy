import argparse
import os

import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash, abstract_process_send

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

def process_send(process_name, input_message):
    result = abstract_process_send(process_name, input_message)
    print(f"{result}")

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

    # Update 'summarize' subparser
    parser_summarize = subparsers.add_parser('summarize', help='Summarize text from stdin or a file.')
    parser_summarize.add_argument('filename', type=str, nargs='?', help="Optional filename containing text to summarize.")

    # Subparser for 'p' command
    parser_p = subparsers.add_parser('p', help='Process input message with abstract_process_send.')
    parser_p.add_argument('process_name', type=str, help="The process tag for abstract_process_send.")
    parser_p.add_argument('input_message', type=str, nargs='?', help="The input message to process.")

    args = parser.parse_args()

    if args.command == 'p':
        if not sys.stdin.isatty():
            input_message = sys.stdin.read()
        elif args.input_message:
            input_message = args.input_message
        else:
            print("Error: No input provided.")
            return
        process_send(args.process_name, input_message)
    elif args.command == 'tash':
        if args.f:
            tash_key_val_from_file(args.key, args.f)
        elif args.value:
            tash_key_val(args.key, args.value)
        else:
            print("Error: You must provide a value or use the --f flag to read from a file.")
    elif args.command == 'transcribe':
        transcribed_text = transcribe_audio(args.file_path)
        print(f"{transcribed_text}")
    elif args.command == 'summarize':
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        elif args.filename:
            if not os.path.isfile(args.filename):
                print(f"Error: File '{args.filename}' does not exist.")
                return
            with open(args.filename, 'r') as file:
                text = file.read()
        else:
            print("Error: No input provided.")
            return
        summary = summarizer(text)
        print(f"{summary}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()