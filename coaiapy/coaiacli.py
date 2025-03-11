import argparse
import os
import json
import sys
import warnings
#ignore : RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer).
warnings.filterwarnings("ignore", message="Unable to find acceptable character detection dependency")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash, abstract_process_send, initial_setup
from cofuse import (
    get_comments, post_comment,
    create_session_and_save, add_trace_node_and_save,
    load_session_file,
    create_score, apply_score_to_trace,
    list_prompts, get_prompt, create_prompt,
    list_datasets, get_dataset, create_dataset,
    list_traces, list_projects, create_dataset_item,
    add_trace
)

EPILOG1 = """
coaiacli is a command line interface for audio transcription, summarization, and stashing to Redis.

setup these environment variables:
OPENAI_API_KEY AWS_KEY_ID AWS_SECRET_KEY AWS_REGION REDIS_HOST REDIS_PORT REDIS_PASSWORD REDIS_SSL

To add a new process tag, define "TAG_instruction" and "TAG_temperature" in config.json.

Usage:
    coaia p TAG "My user input"
    cat myfile.txt | coaia p TAG
"""
EPILOG = "SEE: https://github.com/jgwill/coaiapy/wiki  (not happy about its content, contribute to it)"

def tash_key_val(key, value,ttl=None):
    tash(key, value,ttl)
    print(f"Key: {key}  stashed successfully.")

def tash_key_val_from_file(key, file_path,ttl=None):
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
    parser_tash.add_argument('-T','--ttl', type=int, help="Time to live in seconds.",default=5555)

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

    # Subparser for 'fuse' command
    parser_fuse = subparsers.add_parser('fuse', help='Manage Langfuse integrations.')
    sub_fuse = parser_fuse.add_subparsers(dest='fuse_command', help="Subcommands for Langfuse")

    parser_fuse_base = sub_fuse.add_parser('comments', help="List or post comments to Langfuse")
    parser_fuse_base.add_argument('action', choices=['list','post'], help="Action to perform.")
    parser_fuse_base.add_argument('comment', nargs='?', help="Text for comment creation.")
    
    parser_fuse_prompts = sub_fuse.add_parser('prompts', help="Manage prompts in Langfuse (list, get, create)")
    parser_fuse_prompts.add_argument('action', choices=['list','get','create'], help="Action to perform.")
    parser_fuse_prompts.add_argument('name', nargs='?', help="Prompt name.")
    parser_fuse_prompts.add_argument('content', nargs='?', help="Prompt text.")

    parser_fuse_ds = sub_fuse.add_parser('datasets', help="Manage datasets in Langfuse (list, get, create)")
    parser_fuse_ds.add_argument('action', choices=['list','get','create'], help="Action to perform.")
    parser_fuse_ds.add_argument('name', nargs='?', help="Dataset name.")

    parser_fuse_sessions = sub_fuse.add_parser('sessions', help="Manage sessions in Langfuse (create, add node, view)")
    parser_fuse_sessions_sub = parser_fuse_sessions.add_subparsers(dest='sessions_action')

    parser_fuse_sessions_create = parser_fuse_sessions_sub.add_parser('create')
    parser_fuse_sessions_create.add_argument('session_id')
    parser_fuse_sessions_create.add_argument('user_id')
    parser_fuse_sessions_create.add_argument('-n','--name', default="New Session")
    parser_fuse_sessions_create.add_argument('-f','--file', default="session.yml")

    parser_fuse_sessions_add = parser_fuse_sessions_sub.add_parser('addnode')
    parser_fuse_sessions_add.add_argument('session_id')
    parser_fuse_sessions_add.add_argument('trace_id')
    parser_fuse_sessions_add.add_argument('user_id')
    parser_fuse_sessions_add.add_argument('-n','--name', default="Child Node")
    parser_fuse_sessions_add.add_argument('-f','--file', default="session.yml")

    parser_fuse_sessions_view = parser_fuse_sessions_sub.add_parser('view')
    parser_fuse_sessions_view.add_argument('-f','--file', default="session.yml")

    parser_fuse_sc = sub_fuse.add_parser('scores', aliases=['sc'], help="Manage scores in Langfuse (create or apply)")
    sub_fuse_sc = parser_fuse_sc.add_subparsers(dest='scores_action')

    parser_fuse_sc_create = sub_fuse_sc.add_parser('create')
    parser_fuse_sc_create.add_argument('score_id')
    parser_fuse_sc_create.add_argument('-n','--name', default="New Score")
    parser_fuse_sc_create.add_argument('-v','--value', type=float, default=1.0)

    parser_fuse_sc_apply = sub_fuse_sc.add_parser('apply')
    parser_fuse_sc_apply.add_argument('trace_id')
    parser_fuse_sc_apply.add_argument('score_id')
    parser_fuse_sc_apply.add_argument('-v','--value', type=float, default=1.0)

    parser_fuse_traces = sub_fuse.add_parser('traces', help="List or add traces in Langfuse")
    sub_fuse_traces = parser_fuse_traces.add_subparsers(dest='trace_action')

    parser_fuse_traces_add = sub_fuse_traces.add_parser('add', help='Add a new trace')
    parser_fuse_traces_add.add_argument('trace_id', help="Trace ID")
    parser_fuse_traces_add.add_argument('-s','--session', required=True, help="Session ID")
    parser_fuse_traces_add.add_argument('-u','--user', required=True, help="User ID") 
    parser_fuse_traces_add.add_argument('-n','--name', required=True, help="Trace name")
    parser_fuse_traces_add.add_argument('-d','--data', help="Additional trace data as JSON string")

    parser_fuse_projects = sub_fuse.add_parser('projects', help="List projects in Langfuse")
    parser_fuse_ds_items = sub_fuse.add_parser('dataset-items', help="Manage dataset items (create) in Langfuse")
    parser_fuse_ds_items_sub = parser_fuse_ds_items.add_subparsers(dest='ds_items_action')
    parser_ds_items_create = parser_fuse_ds_items_sub.add_parser('create')
    parser_ds_items_create.add_argument('datasetName')
    parser_ds_items_create.add_argument('-i','--input', required=True)
    parser_ds_items_create.add_argument('-e','--expected', help="Expected output")
    parser_ds_items_create.add_argument('-m','--metadata', help="Optional metadata as JSON string")

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
            tash_key_val_from_file(args.key, args.file,args.ttl)
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
    elif args.command == 'fuse':
        if args.fuse_command == 'comments':
            if args.action == 'list':
                print(get_comments())
            elif args.action == 'post':
                if not args.comment:
                    print("Error: comment text missing.")
                    return
                print(post_comment(args.comment))
        elif args.fuse_command == 'prompts':
            if args.action == 'list':
                print(list_prompts())
            elif args.action == 'get':
                if not args.name:
                    print("Error: prompt name missing.")
                    return
                print(get_prompt(args.name))
            elif args.action == 'create':
                if not args.name or not args.content:
                    print("Error: name or content missing.")
                    return
                print(create_prompt(args.name, args.content))
        elif args.fuse_command == 'datasets':
            if args.action == 'list':
                print(list_datasets())
            elif args.action == 'get':
                if not args.name:
                    print("Error: dataset name missing.")
                    return
                print(get_dataset(args.name))
            elif args.action == 'create':
                if not args.name:
                    print("Error: dataset name missing.")
                    return
                print(create_dataset(args.name))
        elif args.fuse_command == 'sessions':
            if args.sessions_action == 'create':
                print(create_session_and_save(args.file, args.session_id, args.user_id, args.name))
            elif args.sessions_action == 'addnode':
                print(add_trace_node_and_save(args.file, args.session_id, args.trace_id, args.user_id, args.name))
            elif args.sessions_action == 'view':
                data = load_session_file(args.file)
                print(data)
        elif args.fuse_command == 'scores' or args.fuse_command == 'sc':
            if args.scores_action == 'create':
                print(create_score(args.score_id, args.name, args.value))
            elif args.scores_action == 'apply':
                print(apply_score_to_trace(args.trace_id, args.score_id, args.value))
        elif args.fuse_command == 'traces':
            if args.trace_action == 'add':
                data = json.loads(args.data) if args.data else None
                print(add_trace(args.trace_id, args.user, args.session, args.name, data))
            else:
                print(list_traces())
        elif args.fuse_command == 'projects':
            print(list_projects())
        elif args.fuse_command == 'dataset-items':
            if args.ds_items_action == 'create':
                md = args.metadata if args.metadata else None
                print(create_dataset_item(args.datasetName, args.input, args.expected, md))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
