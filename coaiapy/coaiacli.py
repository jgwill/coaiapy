import argparse
import os

import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash, abstract_process_send, initial_setup

EPILOG = """
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

To add a new process tag, define "TAG_instruction" and "TAG_temperature" in config.json.

Usage:
    coaia p TAG "My user input"
    cat myfile.txt | coaia p TAG
"""

def tash_key_val(key, value,ttl=-1):
    tash(key, value)
    print(f"Key: {key}, Value: {value} stashed successfully.")

def tash_key_val_from_file(key, file_path,ttl=-1):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    with open(file_path, 'r') as file:
        value = file.read()
    tash_key_val(key, value,ttl)

def process_send(process_name, input_message):
    result = abstract_process_send(process_name, input_message)
    print(f"{result}")

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for audio transcription, summarization, stashing to Redis and other processTag.", 
        epilog=EPILOG,
        usage="coaia <command> [<args>]",
        prog="coaia",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command')

    # Subparser for 'tash' command
    parser_tash = subparsers.add_parser('tash',aliases="m", help='Stash a key/value pair to Redis.')
    parser_tash.add_argument('key', type=str, help="The key to stash.")
    parser_tash.add_argument('value', type=str, nargs='?', help="The value to stash.")
    parser_tash.add_argument('-F','--file', type=str, help="Read the value from a file.")
    #--ttl
    parser_tash.add_argument('-T','--ttl', type=int, help="Time to live in seconds.")

    # Subparser for 'transcribe' command
    parser_transcribe = subparsers.add_parser('transcribe',aliases="t", help='Transcribe an audio file to text.')
    parser_transcribe.add_argument('file_path', type=str, help="The path to the audio file.")
    parser_transcribe.add_argument('-O','--output', type=str, help="Filename to save the output.")

    # Update 'summarize' subparser
    parser_summarize = subparsers.add_parser('summarize',aliases="s", help='Summarize text from stdin or a file.')
    parser_summarize.add_argument('filename', type=str, nargs='?', help="Optional filename containing text to summarize.")
    parser_summarize.add_argument('-O','--output', type=str, help="Filename to save the output.")

    # Subparser for 'p' command
    parser_p = subparsers.add_parser('p', help='Process input message with a custom process tag.')
    parser_p.add_argument('process_name', type=str, help="The process tag defined in the config.")
    parser_p.add_argument('input_message', type=str, nargs='?', help="The input message to process.")
    parser_p.add_argument('-O','--output', type=str, help="Filename to save the output.")
    parser_p.add_argument('-F', '--file', type=str, help="Read the input message from a file.")

    # Subparser for 'init' command
    parser_init = subparsers.add_parser('init', help='Create a sample config file in $HOME/coaia.json.')

    args = parser.parse_args()

    if args.command == 'init':
        initial_setup()
    elif args.command == 'p':
        if args.file:
            with open(args.file, 'r') as f:
                input_message = f.read()
        elif not sys.stdin.isatty():
            input_message = sys.stdin.read()
        elif args.input_message:
            input_message = args.input_message
        else:
            print("Error: No input provided.")
            return
        result = abstract_process_send(args.process_name, input_message)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
        else:
            print(f"{result}")
    elif args.command == 'tash' or args.command == 'm':
        if args.file:
            tash_key_val_from_file(args.key, args.file)
        elif args.value:
            tash_key_val(args.key, args.value,args.ttl)
        else:
            print("Error: You must provide a value or use the --file flag to read from a file.")
    elif args.command == 'transcribe' or args.command == 't':
        transcribed_text = transcribe_audio(args.file_path)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(transcribed_text)
        else:
            print(f"{transcribed_text}")
    elif args.command == 'summarize' or args.command == 's':
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
        if args.output:
            with open(args.output, 'w') as f:
                f.write(summary)
        else:
            print(f"{summary}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()