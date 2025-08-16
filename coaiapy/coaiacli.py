import argparse
import os
import json
import sys
import warnings
#ignore : RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer).
warnings.filterwarnings("ignore", message="Unable to find acceptable character detection dependency")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash, abstract_process_send, initial_setup, fetch_key_val
from cofuse import (
    get_comments, post_comment,
    create_session_and_save, add_trace_node_and_save,
    load_session_file,
    create_score, apply_score_to_trace,
    list_prompts, get_prompt, create_prompt, format_prompts_table, format_prompt_display,
    list_datasets, get_dataset, create_dataset, format_datasets_table,
    list_dataset_items, format_dataset_display, format_dataset_for_finetuning,
    list_traces, list_projects, create_dataset_item, format_traces_table,
    add_trace, add_observation, add_observations_batch
)

EPILOG = """see: https://github.com/jgwill/coaiapy/wiki for more details."""
EPILOG1 = """
coaiacli is a command line interface for audio transcription, summarization, and stashing to Redis.

setup these environment variables:
OPENAI_API_KEY,AWS_KEY_ID,AWS_SECRET_KEY,AWS_REGION
REDIS_HOST,REDIS_PORT,REDIS_PASSWORD,REDIS_SSL

To add a new process tag, define "TAG_instruction" and "TAG_temperature" in coaia.json.

Usage:
    coaia p TAG "My user input"
    cat myfile.txt | coaia p TAG
"""

def tash_key_val(key, value,ttl=None):
    tash(key, value,ttl)
    print(f"Key: {key}  was just saved to memory.")

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
    parser_fuse_prompts.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    parser_fuse_prompts.add_argument('--debug', action='store_true', help="Show debug information for pagination")
    parser_fuse_prompts.add_argument('--label', type=str, help="Specify a label to fetch.")
    parser_fuse_prompts.add_argument('--prod', action='store_true', help="Shortcut to fetch the 'production' label.")
    parser_fuse_prompts.add_argument('-c', '--content-only', action='store_true', help="Output only the prompt content.")
    parser_fuse_prompts.add_argument('-e', '--escaped', action='store_true', help="Output the prompt content as a single, escaped line.")
    # Enhanced prompt creation arguments
    parser_fuse_prompts.add_argument('--commit-message', type=str, help="Commit message for this prompt version")
    parser_fuse_prompts.add_argument('--labels', type=str, nargs='*', help="Deployment labels (space-separated)")
    parser_fuse_prompts.add_argument('--tags', type=str, nargs='*', help="Tags (space-separated)")
    parser_fuse_prompts.add_argument('--type', type=str, choices=['text', 'chat'], default='text', help="Prompt type (text or chat)")
    parser_fuse_prompts.add_argument('-f', '--file', type=str, help="Read prompt content from file")

    parser_fuse_ds = sub_fuse.add_parser('datasets', help="Manage datasets in Langfuse (list, get, create)")
    parser_fuse_ds.add_argument('action', choices=['list','get','create'], help="Action to perform.")
    parser_fuse_ds.add_argument('name', nargs='?', help="Dataset name.")
    parser_fuse_ds.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    parser_fuse_ds.add_argument('-oft', '--openai-ft', action='store_true', help="Format output for OpenAI fine-tuning.")
    parser_fuse_ds.add_argument('-gft', '--gemini-ft', action='store_true', help="Format output for Gemini fine-tuning.")
    parser_fuse_ds.add_argument('--system-instruction', type=str, default="You are a helpful assistant", help="System instruction for fine-tuning formats.")
    # Enhanced dataset creation arguments
    parser_fuse_ds.add_argument('--description', type=str, help="Description for the dataset")
    parser_fuse_ds.add_argument('--metadata', type=str, help="Metadata for the dataset (JSON string or simple text)")

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

    parser_fuse_traces = sub_fuse.add_parser('traces', help="List or manage traces and observations in Langfuse")
    parser_fuse_traces.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    sub_fuse_traces = parser_fuse_traces.add_subparsers(dest='trace_action')

    parser_fuse_traces_add = sub_fuse_traces.add_parser('create', help='Create a new trace')
    parser_fuse_traces_add.add_argument('trace_id', help="Trace ID")
    parser_fuse_traces_add.add_argument('-s','--session', help="Session ID")
    parser_fuse_traces_add.add_argument('-u','--user', help="User ID") 
    parser_fuse_traces_add.add_argument('-n','--name', help="Trace name")
    parser_fuse_traces_add.add_argument('-i','--input', help="Input data (JSON string or plain text)")
    parser_fuse_traces_add.add_argument('-o','--output', help="Output data (JSON string or plain text)")
    parser_fuse_traces_add.add_argument('-m','--metadata', help="Additional metadata as JSON string")

    parser_fuse_obs_add = sub_fuse_traces.add_parser('add-observation', help='Add an observation to a trace')
    parser_fuse_obs_add.add_argument('observation_id', help="Observation ID")
    parser_fuse_obs_add.add_argument('trace_id', help="Trace ID")
    parser_fuse_obs_add.add_argument('-t','--type', choices=['EVENT', 'SPAN', 'GENERATION'], default='EVENT', help="Observation type")
    parser_fuse_obs_add.add_argument('-n','--name', help="Observation name")
    parser_fuse_obs_add.add_argument('-i','--input', help="Input data (JSON string or plain text)")
    parser_fuse_obs_add.add_argument('-o','--output', help="Output data (JSON string or plain text)")
    parser_fuse_obs_add.add_argument('-m','--metadata', help="Metadata as JSON string")
    parser_fuse_obs_add.add_argument('-p','--parent', help="Parent observation ID")
    parser_fuse_obs_add.add_argument('--start-time', help="Start time (ISO format or tlid format yyMMddHHmmss)")
    parser_fuse_obs_add.add_argument('--end-time', help="End time (ISO format or tlid format yyMMddHHmmss)")
    parser_fuse_obs_add.add_argument('--level', choices=['DEBUG', 'DEFAULT', 'WARNING', 'ERROR'], default='DEFAULT', help="Observation level")
    parser_fuse_obs_add.add_argument('--model', help="Model name")
    parser_fuse_obs_add.add_argument('--usage', help="Usage information as JSON string")

    # Add batch observations command with aliases
    parser_fuse_obs_batch = sub_fuse_traces.add_parser('add-observations', aliases=['add-obs-batch'], help='Add multiple observations to a trace from file or stdin')
    parser_fuse_obs_batch.add_argument('trace_id', help="Trace ID to add observations to")
    parser_fuse_obs_batch.add_argument('-f','--file', help="File containing observations (JSON or YAML format)")
    parser_fuse_obs_batch.add_argument('--format', choices=['json', 'yaml'], default='json', help="Input format (default: json)")
    parser_fuse_obs_batch.add_argument('--dry-run', action='store_true', help="Show what would be created without actually creating")

    parser_fuse_projects = sub_fuse.add_parser('projects', help="List projects in Langfuse")
    parser_fuse_ds_items = sub_fuse.add_parser('dataset-items', help="Manage dataset items (create) in Langfuse")
    parser_fuse_ds_items_sub = parser_fuse_ds_items.add_subparsers(dest='ds_items_action')
    parser_ds_items_create = parser_fuse_ds_items_sub.add_parser('create')
    parser_ds_items_create.add_argument('datasetName')
    parser_ds_items_create.add_argument('-i','--input', required=True)
    parser_ds_items_create.add_argument('-e','--expected', help="Expected output")
    parser_ds_items_create.add_argument('-m','--metadata', help="Optional metadata as JSON string")
    # Enhanced dataset item creation arguments
    parser_ds_items_create.add_argument('--source-trace', help="Source trace ID")
    parser_ds_items_create.add_argument('--source-observation', help="Source observation ID")
    parser_ds_items_create.add_argument('--id', help="Custom item ID (for upserts)")
    parser_ds_items_create.add_argument('--status', help="Item status")

    # Subparser for 'fetch' command
    parser_fetch = subparsers.add_parser('fetch', help='Fetch a value from Redis by key.')
    parser_fetch.add_argument('key', type=str, help="The key to fetch.")
    parser_fetch.add_argument('-O', '--output', type=str, help="Filename to save the fetched value.")

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
    elif args.command == 'fetch':
        fetch_key_val(args.key, args.output)
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
                prompts_data = list_prompts(debug=getattr(args, 'debug', False))
                if args.json:
                    print(prompts_data)
                else:
                    print(format_prompts_table(prompts_data))
            elif args.action == 'get':
                if not args.name:
                    print("Error: prompt name missing.")
                    return
                
                label = 'latest' # Default to latest
                if args.prod:
                    label = 'production'
                if args.label:
                    label = args.label

                prompt_data = get_prompt(args.name, label=label)

                if args.content_only or args.escaped:
                    try:
                        prompt_json = json.loads(prompt_data)
                        prompt_content = prompt_json.get('prompt', '')
                        if isinstance(prompt_content, list):
                            # Handle chat format
                            content = '\n'.join([msg.get('content', '') for msg in prompt_content if msg.get('content')])
                        else:
                            # Handle string format
                            content = prompt_content
                        
                        if args.escaped:
                            print(json.dumps(content))
                        else:
                            print(content)

                    except json.JSONDecodeError:
                        print(f"Error: Could not parse prompt data as JSON.\n{prompt_data}")
                    return

                if args.json:
                    print(prompt_data)
                else:
                    print(format_prompt_display(prompt_data))
            elif args.action == 'create':
                if not args.name:
                    print("Error: prompt name missing.")
                    return
                    
                # Get content from file or argument
                content = None
                if args.file:
                    if not os.path.isfile(args.file):
                        print(f"Error: File '{args.file}' does not exist.")
                        return
                    with open(args.file, 'r') as f:
                        content = f.read()
                elif args.content:
                    content = args.content
                else:
                    print("Error: content missing. Provide either content argument or --file.")
                    return
                
                # Handle chat prompts (JSON format expected)
                if args.type == 'chat' and content:
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        print("Error: Chat prompt content must be valid JSON format.")
                        return
                
                result = create_prompt(
                    args.name, 
                    content,
                    commit_message=getattr(args, 'commit_message', None),
                    labels=getattr(args, 'labels', None),
                    tags=getattr(args, 'tags', None),
                    prompt_type=getattr(args, 'type', 'text')
                )
                print(result)
        elif args.fuse_command == 'datasets':
            if args.action == 'list':
                datasets_data = list_datasets()
                if args.json:
                    print(datasets_data)
                else:
                    print(format_datasets_table(datasets_data))
            elif args.action == 'get':
                if not args.name:
                    print("Error: dataset name missing.")
                    return
                
                dataset_json = get_dataset(args.name)
                items_json = list_dataset_items(args.name)

                if args.openai_ft:
                    print(format_dataset_for_finetuning(items_json, 'openai', args.system_instruction))
                elif args.gemini_ft:
                    print(format_dataset_for_finetuning(items_json, 'gemini', args.system_instruction))
                elif args.json:
                    dataset_data = json.loads(dataset_json)
                    items_data = json.loads(items_json)
                    dataset_data['items'] = items_data
                    print(json.dumps(dataset_data, indent=2))
                else:
                    print(format_dataset_display(dataset_json, items_json))
            elif args.action == 'create':
                if not args.name:
                    print("Error: dataset name missing.")
                    return
                result = create_dataset(
                    args.name, 
                    description=getattr(args, 'description', None),
                    metadata=getattr(args, 'metadata', None)
                )
                print(result)
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
            if args.trace_action == 'create':
                # Parse JSON data, fallback to plain text if not JSON
                input_data = None
                if args.input:
                    try:
                        input_data = json.loads(args.input)
                    except json.JSONDecodeError:
                        input_data = args.input  # Use as plain text
                
                output_data = None
                if args.output:
                    try:
                        output_data = json.loads(args.output)
                    except json.JSONDecodeError:
                        output_data = args.output  # Use as plain text
                
                metadata = None
                if args.metadata:
                    try:
                        metadata = json.loads(args.metadata)
                    except json.JSONDecodeError:
                        print(f"Warning: metadata must be valid JSON, got: {args.metadata}")
                        return
                
                result = add_trace(
                    args.trace_id, 
                    user_id=args.user,
                    session_id=args.session,
                    name=args.name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata
                )
                print(result)
            elif args.trace_action == 'add-observation':
                # Parse JSON data, fallback to plain text if not JSON
                input_data = None
                if args.input:
                    try:
                        input_data = json.loads(args.input)
                    except json.JSONDecodeError:
                        input_data = args.input  # Use as plain text
                
                output_data = None
                if args.output:
                    try:
                        output_data = json.loads(args.output)
                    except json.JSONDecodeError:
                        output_data = args.output  # Use as plain text
                
                metadata = None
                if args.metadata:
                    try:
                        metadata = json.loads(args.metadata)
                    except json.JSONDecodeError:
                        print(f"Warning: metadata must be valid JSON, got: {args.metadata}")
                        return
                
                usage = None
                if args.usage:
                    try:
                        usage = json.loads(args.usage)
                    except json.JSONDecodeError:
                        print(f"Warning: usage must be valid JSON, got: {args.usage}")
                        return
                
                result = add_observation(
                    args.observation_id,
                    args.trace_id,
                    observation_type=args.type,
                    name=args.name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata,
                    parent_observation_id=args.parent,
                    start_time=getattr(args, 'start_time', None),
                    end_time=getattr(args, 'end_time', None),
                    level=args.level,
                    model=args.model,
                    usage=usage
                )
                print(result)
            elif args.trace_action == 'add-observations' or args.trace_action == 'add-obs-batch':
                # Handle batch observation creation
                observations_data = None
                
                if args.file:
                    # Read from file
                    if not os.path.isfile(args.file):
                        print(f"Error: File '{args.file}' does not exist.")
                        return
                    with open(args.file, 'r') as f:
                        observations_data = f.read()
                elif not sys.stdin.isatty():
                    # Read from stdin
                    observations_data = sys.stdin.read()
                else:
                    print("Error: No input provided. Use --file or pipe data via stdin.")
                    return
                
                if not observations_data.strip():
                    print("Error: No observation data provided.")
                    return
                
                result = add_observations_batch(
                    args.trace_id,
                    observations_data,
                    format_type=args.format,
                    dry_run=args.dry_run
                )
                print(result)
            else:
                traces_data = list_traces()
                if args.json:
                    print(traces_data)
                else:
                    print(format_traces_table(traces_data))
        elif args.fuse_command == 'projects':
            print(list_projects())
        elif args.fuse_command == 'dataset-items':
            if args.ds_items_action == 'create':
                result = create_dataset_item(
                    args.datasetName, 
                    args.input, 
                    expected_output=args.expected,
                    metadata=args.metadata,
                    source_trace_id=getattr(args, 'source_trace', None),
                    source_observation_id=getattr(args, 'source_observation', None),
                    item_id=getattr(args, 'id', None),
                    status=getattr(args, 'status', None)
                )
                print(result)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
