import argparse
import os
import json
import sys
import warnings
import uuid
#ignore : RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer).
warnings.filterwarnings("ignore", message="Unable to find acceptable character detection dependency")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash, abstract_process_send, initial_setup, fetch_key_val
from cofuse import (
    get_comments, post_comment,
    create_session_and_save, add_trace_node_and_save,
    load_session_file,
    create_score, apply_score_to_trace, create_score_for_target, list_scores, format_scores_table,
    list_score_configs, get_score_config, create_score_config, export_score_configs, format_score_configs_table,
    import_score_configs, format_import_preview, apply_score_config, list_available_configs, validate_score_value, get_config_with_auto_refresh,
    list_presets, get_preset_by_name, format_presets_table, format_preset_display, install_preset, install_presets_interactive,
    list_prompts, get_prompt, create_prompt, format_prompts_table, format_prompt_display,
    list_datasets, get_dataset, create_dataset, format_datasets_table,
    list_dataset_items, format_dataset_display, format_dataset_for_finetuning,
    list_traces, list_projects, create_dataset_item, format_traces_table,
    add_trace, add_observation, add_observations_batch, patch_trace_output,
    get_trace_with_observations, format_trace_tree,
    get_observation, format_observation_display
)
from .pipeline import TemplateLoader, TemplateRenderer, PipelineTemplate, PipelineVariable, PipelineStep
from .environment import EnvironmentManager, format_environment_table

# Security validation functions
def validate_uuid(value, field_name="ID"):
    """Validate UUID format to prevent injection attacks"""
    if not value:
        return None  # Allow None/empty values
    
    try:
        # Attempt to parse as UUID - will raise ValueError if invalid
        uuid_obj = uuid.UUID(value)
        # Return string representation to ensure consistent format
        return str(uuid_obj)
    except ValueError:
        raise ValueError(f"Invalid {field_name} format. Must be a valid UUID (e.g., 12345678-1234-1234-1234-123456789abc)")

def validate_identifier(value, field_name="identifier", max_length=100):
    """Validate general string identifiers for security"""
    if not value:
        return None
    
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    value = value.strip()
    if not value:
        return None
    
    if len(value) > max_length:
        raise ValueError(f"{field_name} too long (max {max_length} characters)")
    
    # Check for suspicious patterns
    suspicious_patterns = ['../', '..\\', '<script', 'javascript:', 'data:', 'file:']
    for pattern in suspicious_patterns:
        if pattern.lower() in value.lower():
            raise ValueError(f"{field_name} contains potentially dangerous content")
    
    return value

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

def tash_key_val(key, value, ttl=None, verbose=False):
    tash(key, value, ttl, verbose=verbose)
    print(f"Key: {key}  was just saved to memory.")

def tash_key_val_from_file(key, file_path, ttl=None, verbose=False):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    with open(file_path, 'r') as file:
        value = file.read()
    tash_key_val(key, value, ttl, verbose=verbose)

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
    parser_tash.add_argument('-v', '--verbose', action='store_true', help="Show detailed Redis connection information.")

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
    parser_fuse_sc_apply.add_argument('--trace-id', help="Trace ID to apply score to")
    parser_fuse_sc_apply.add_argument('--session-id', help="Session ID to apply score to")
    parser_fuse_sc_apply.add_argument('--observation-id', help="Optional observation ID (for trace scores only)")
    parser_fuse_sc_apply.add_argument('--name', help="Score name")
    parser_fuse_sc_apply.add_argument('--score-id', help="Score ID (alternative to name)")
    parser_fuse_sc_apply.add_argument('-v','--value', type=float, default=1.0, help="Score value")
    parser_fuse_sc_apply.add_argument('-c', '--comment', help="Optional comment for the score")

    parser_fuse_sc_list = sub_fuse_sc.add_parser('list')
    parser_fuse_sc_list.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")

    parser_fuse_scc = sub_fuse.add_parser('score-configs', aliases=['scc'], help="Manage score configurations in Langfuse (list, get, create)")
    sub_fuse_scc = parser_fuse_scc.add_subparsers(dest='score_configs_action')

    parser_fuse_scc_list = sub_fuse_scc.add_parser('list')
    parser_fuse_scc_list.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")

    parser_fuse_scc_get = sub_fuse_scc.add_parser('get')
    parser_fuse_scc_get.add_argument('config_id', help="Score config ID")
    parser_fuse_scc_get.add_argument('--json', action='store_true', help="Output in JSON format (default: formatted display)")

    parser_fuse_scc_create = sub_fuse_scc.add_parser('create')
    parser_fuse_scc_create.add_argument('name', help="Name of the score config")
    parser_fuse_scc_create.add_argument('data_type', choices=['NUMERIC', 'CATEGORICAL', 'BOOLEAN'], help="Data type for the score config")
    parser_fuse_scc_create.add_argument('--description', help="Description of the score config")
    parser_fuse_scc_create.add_argument('--min-value', type=float, help="Minimum value for numeric scores")
    parser_fuse_scc_create.add_argument('--max-value', type=float, help="Maximum value for numeric scores")
    parser_fuse_scc_create.add_argument('--categories', help="Categories for categorical scores (JSON format: [{\"label\": \"Good\", \"value\": 1}])")

    parser_fuse_scc_export = sub_fuse_scc.add_parser('export')
    parser_fuse_scc_export.add_argument('-o', '--output', help="Output file path (optional, defaults to stdout)")
    parser_fuse_scc_export.add_argument('--no-metadata', action='store_true', help="Exclude Langfuse metadata (cleaner for sharing)")

    parser_fuse_scc_import = sub_fuse_scc.add_parser('import', help="Import score configs from JSON file")
    parser_fuse_scc_import.add_argument('file', help="JSON file to import from")
    parser_fuse_scc_import.add_argument('--select', nargs='*', help="Select specific config names to import")
    parser_fuse_scc_import.add_argument('--allow-duplicates', action='store_true', help="Allow importing configs with existing names (creates additional configs, does NOT replace)")
    parser_fuse_scc_import.add_argument('--no-guidance', action='store_true', help="Skip guidance messages about duplicate handling")
    parser_fuse_scc_import.add_argument('--preview', action='store_true', help="Preview what would be imported without actually importing")

    parser_fuse_scc_presets = sub_fuse_scc.add_parser('presets', help="Manage built-in score configuration presets")
    sub_fuse_scc_presets = parser_fuse_scc_presets.add_subparsers(dest='presets_action')
    
    parser_fuse_scc_presets_list = sub_fuse_scc_presets.add_parser('list', help="List available presets")
    parser_fuse_scc_presets_list.add_argument('--category', choices=['narrative', 'ai', 'general', 'technical', 'specialized', 'numeric', 'boolean'], 
                                            help="Filter by category")
    parser_fuse_scc_presets_list.add_argument('--json', action='store_true', help="Output in JSON format")
    
    parser_fuse_scc_presets_show = sub_fuse_scc_presets.add_parser('show', help="Show detailed preset information")
    parser_fuse_scc_presets_show.add_argument('preset_name', help="Name of the preset to show")
    
    parser_fuse_scc_presets_install = sub_fuse_scc_presets.add_parser('install', help="Install one or more presets")
    parser_fuse_scc_presets_install.add_argument('preset_names', nargs='*', help="Preset names to install (if none provided, installs all)")
    parser_fuse_scc_presets_install.add_argument('--category', choices=['narrative', 'ai', 'general', 'technical', 'specialized', 'numeric', 'boolean'], 
                                               help="Install all presets from a specific category")
    parser_fuse_scc_presets_install.add_argument('--allow-duplicates', action='store_true', help="Allow installing presets with existing names (creates additional configs, does NOT replace)")
    parser_fuse_scc_presets_install.add_argument('--interactive', action='store_true', help="Interactive mode with duplicate checking")

    parser_fuse_scc_apply = sub_fuse_scc.add_parser('apply', help="Apply a score using score configuration with validation")
    parser_fuse_scc_apply.add_argument('config_name_or_id', help="Score config name or ID")
    parser_fuse_scc_apply.add_argument('--trace-id', help="Trace ID to apply score to")
    parser_fuse_scc_apply.add_argument('--session-id', help="Session ID to apply score to")
    parser_fuse_scc_apply.add_argument('--observation-id', help="Optional observation ID (for trace scores only)")
    parser_fuse_scc_apply.add_argument('-v', '--value', required=True, help="Score value to apply")
    parser_fuse_scc_apply.add_argument('-c', '--comment', help="Optional comment for the score")

    parser_fuse_scc_available = sub_fuse_scc.add_parser('available', help="List available score configs with optional filtering")
    parser_fuse_scc_available.add_argument('--category', help="Filter by category (searches in name and description)")
    parser_fuse_scc_available.add_argument('--cached-only', action='store_true', help="Only show cached configs")
    parser_fuse_scc_available.add_argument('--json', action='store_true', help="Output in JSON format")

    parser_fuse_scc_show = sub_fuse_scc.add_parser('show', help="Show detailed config information with validation requirements")
    parser_fuse_scc_show.add_argument('config_name_or_id', help="Score config name or ID")
    parser_fuse_scc_show.add_argument('--requirements', action='store_true', help="Show detailed validation requirements")
    parser_fuse_scc_show.add_argument('--json', action='store_true', help="Output in JSON format")

    parser_fuse_traces = sub_fuse.add_parser('traces', help="List or manage traces and observations in Langfuse")
    parser_fuse_traces.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    parser_fuse_traces.add_argument('--include-observations', action='store_true', help="Include detailed observation data for each trace")
    sub_fuse_traces = parser_fuse_traces.add_subparsers(dest='trace_action')

    parser_fuse_traces_add = sub_fuse_traces.add_parser('create', help='Create a new trace')
    parser_fuse_traces_add.add_argument('trace_id', help="Trace ID")
    parser_fuse_traces_add.add_argument('-s','--session', help="Session ID")
    parser_fuse_traces_add.add_argument('-u','--user', help="User ID") 
    parser_fuse_traces_add.add_argument('-n','--name', help="Trace name")
    parser_fuse_traces_add.add_argument('-i','--input', help="Input data (JSON string or plain text)")
    parser_fuse_traces_add.add_argument('-o','--output', help="Output data (JSON string or plain text)")
    parser_fuse_traces_add.add_argument('-m','--metadata', help="Additional metadata as JSON string")
    parser_fuse_traces_add.add_argument('--export-env', action='store_true', help="Export shell environment variables for pipeline workflows")

    parser_fuse_obs_add = sub_fuse_traces.add_parser('add-observation', help='Add an observation to a trace')
    parser_fuse_obs_add.add_argument('trace_id', help="Trace ID to add observation to")
    parser_fuse_obs_add.add_argument('observation_id', nargs='?', help="Observation ID (auto-generated UUID if not provided)")
    parser_fuse_obs_add.add_argument('-t','--type', choices=['EVENT', 'SPAN', 'GENERATION'], default='EVENT', 
                                   help="Observation type: EVENT (default), SPAN (with duration), GENERATION (model call)")
    parser_fuse_obs_add.add_argument('-te', action='store_const', dest='type', const='EVENT', help="Shorthand for --type EVENT")
    parser_fuse_obs_add.add_argument('-ts', action='store_const', dest='type', const='SPAN', help="Shorthand for --type SPAN") 
    parser_fuse_obs_add.add_argument('-tg', action='store_const', dest='type', const='GENERATION', help="Shorthand for --type GENERATION")
    parser_fuse_obs_add.add_argument('-n','--name', help="Observation name (descriptive label)")
    parser_fuse_obs_add.add_argument('-i','--input', help="Input data (JSON string or plain text)")
    parser_fuse_obs_add.add_argument('-o','--output', help="Output data (JSON string or plain text)")
    parser_fuse_obs_add.add_argument('-m','--metadata', help="Metadata as JSON string")
    parser_fuse_obs_add.add_argument('-p','--parent', help="Parent observation ID (for nested observations under SPAN)")
    parser_fuse_obs_add.add_argument('--start-time', help="Start time (ISO format, tlid format yyMMddHHmmss, or short tlid yyMMddHHmm)")
    parser_fuse_obs_add.add_argument('--end-time', help="End time (ISO format, tlid format yyMMddHHmmss, or short tlid yyMMddHHmm)")
    parser_fuse_obs_add.add_argument('--level', choices=['DEBUG', 'DEFAULT', 'WARNING', 'ERROR'], default='DEFAULT', 
                                   help="Observation level/severity")
    parser_fuse_obs_add.add_argument('--model', help="Model name (for GENERATION observations)")
    parser_fuse_obs_add.add_argument('--usage', help="Usage information as JSON string (tokens, cost, etc.)")
    parser_fuse_obs_add.add_argument('--export-env', action='store_true', 
                                   help="Export COAIA_TRACE_ID, COAIA_LAST_OBSERVATION_ID environment variables")

    

    parser_fuse_traces_session_view = sub_fuse_traces.add_parser('session-view', aliases=['sv'], help='View a specific session by ID from Langfuse')
    parser_fuse_traces_session_view.add_argument('session_id', help="ID of the session to view")
    parser_fuse_traces_session_view.add_argument('--json', action='store_true', help="Output in JSON format")

    parser_fuse_traces_trace_view = sub_fuse_traces.add_parser('trace-view', aliases=['tv'], help='View a specific trace with its observations in tree format')
    parser_fuse_traces_trace_view.add_argument('trace_id', help="ID of the trace to view")
    parser_fuse_traces_trace_view.add_argument('--json', action='store_true', help="Output in JSON format")

    parser_fuse_obs_get = sub_fuse_traces.add_parser('get-observation', aliases=['obs-get', 'get-obs'], help='Get a specific observation by ID')
    parser_fuse_obs_get.add_argument('observation_id', help="Observation ID to retrieve")
    parser_fuse_obs_get.add_argument('--json', action='store_true', help="Output in JSON format")

    # Add batch observations command with aliases
    parser_fuse_obs_batch = sub_fuse_traces.add_parser('add-observations', aliases=['add-obs-batch'], help='Add multiple observations to a trace from file or stdin')
    parser_fuse_obs_batch.add_argument('trace_id', help="Trace ID to add observations to")
    parser_fuse_obs_batch.add_argument('-f','--file', help="File containing observations (JSON or YAML format)")
    parser_fuse_obs_batch.add_argument('--format', choices=['json', 'yaml'], default='json', help="Input format (default: json)")
    parser_fuse_obs_batch.add_argument('--dry-run', action='store_true', help="Show what would be created without actually creating")

    # Add patch-output command to update trace output
    parser_fuse_patch_output = sub_fuse_traces.add_parser('patch-output', help='Update the output field of an existing trace')
    parser_fuse_patch_output.add_argument('trace_id', help="Trace ID to update")
    parser_fuse_patch_output.add_argument('output_data', nargs='?', help="Output data (JSON string or plain text, or read from stdin if not provided)")
    parser_fuse_patch_output.add_argument('-f','--file', help="File containing output data (JSON)")
    parser_fuse_patch_output.add_argument('--json', action='store_true', help="Treat output_data as JSON (default: auto-detect)")

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
    parser_fetch.add_argument('-v', '--verbose', action='store_true', help="Show detailed Redis connection information.")

    # Pipeline template management commands
    parser_pipeline = subparsers.add_parser('pipeline', help='Manage pipeline templates for automated workflows')
    sub_pipeline = parser_pipeline.add_subparsers(dest='pipeline_action')
    
    parser_pipeline_list = sub_pipeline.add_parser('list', help='List available pipeline templates')
    parser_pipeline_list.add_argument('--path', action='store_true', help='Include template file paths')
    parser_pipeline_list.add_argument('--json', action='store_true', help='Output in JSON format')
    
    parser_pipeline_show = sub_pipeline.add_parser('show', help='Show template details and variables')
    parser_pipeline_show.add_argument('template_name', help='Name of the template to show')
    parser_pipeline_show.add_argument('--preview', action='store_true', help='Show rendered output preview with example variables')
    
    parser_pipeline_create = sub_pipeline.add_parser('create', help='Create a pipeline from template')
    parser_pipeline_create.add_argument('template_name', help='Name of the template to use')
    parser_pipeline_create.add_argument('--var', action='append', nargs=2, metavar=('KEY', 'VALUE'), 
                                       help='Template variables as key-value pairs (can be used multiple times)')
    parser_pipeline_create.add_argument('--trace-id', help='Trace ID to use (auto-generated if not provided)')
    parser_pipeline_create.add_argument('--session-id', help='Session ID for the trace')
    parser_pipeline_create.add_argument('--user-id', help='User ID for the trace')
    parser_pipeline_create.add_argument('--export-env', action='store_true', help='Export environment variables for pipeline workflows')
    parser_pipeline_create.add_argument('--dry-run', action='store_true', help='Show what would be created without actually creating')
    parser_pipeline_create.add_argument('--enable-judge', action='store_true', help='Enable LLM-as-a-Judge API integration for evaluation steps')
    
    parser_pipeline_init = sub_pipeline.add_parser('init', help='Create a new pipeline template')
    parser_pipeline_init.add_argument('template_name', help='Name for the new template')
    parser_pipeline_init.add_argument('--from', dest='base_template', help='Base template to extend from')
    parser_pipeline_init.add_argument('--location', choices=['user', 'project'], default='user',
                                     help='Where to save the template (user: ~/.coaia/templates, project: ./.coaia/templates)')
    parser_pipeline_init.add_argument('--format', choices=['json', 'yaml'], default='json', help='Template file format')

    # Environment variable management commands
    parser_env = subparsers.add_parser('env', help='Manage environment variables for pipeline workflows')
    sub_env = parser_env.add_subparsers(dest='env_action')
    
    parser_env_init = sub_env.add_parser('init', help='Initialize environment file with default variables')
    parser_env_init.add_argument('--name', help='Environment name (default environment if not specified)')
    parser_env_init.add_argument('--location', choices=['project', 'global'], default='project', 
                                help='Environment location (project: .coaia-env, global: ~/.coaia/global.env)')
    parser_env_init.add_argument('--format', choices=['json', 'env'], default='json', help='Environment file format')
    
    parser_env_list = sub_env.add_parser('list', help='List available environment files and their variables')
    parser_env_list.add_argument('--name', help='Show specific environment')
    parser_env_list.add_argument('--location', choices=['project', 'global'], help='Filter by location')
    parser_env_list.add_argument('--json', action='store_true', help='Output in JSON format')
    
    parser_env_source = sub_env.add_parser('source', help='Load environment variables into current session')
    parser_env_source.add_argument('--name', help='Environment name to source')
    parser_env_source.add_argument('--location', choices=['project', 'global'], default='project', help='Environment location')
    parser_env_source.add_argument('--export', action='store_true', help='Output shell export commands')
    
    parser_env_set = sub_env.add_parser('set', help='Set an environment variable')
    parser_env_set.add_argument('key', help='Variable name')
    parser_env_set.add_argument('value', help='Variable value')
    parser_env_set.add_argument('--name', help='Environment name')
    parser_env_set.add_argument('--location', choices=['project', 'global'], default='project', help='Environment location')
    parser_env_set.add_argument('--format', choices=['json', 'env'], default='json', help='File format')
    parser_env_set.add_argument('--temp', action='store_true', help="Don't persist to file, just set for current session")
    
    parser_env_get = sub_env.add_parser('get', help='Get an environment variable value')
    parser_env_get.add_argument('key', help='Variable name')
    parser_env_get.add_argument('--name', help='Environment name')
    parser_env_get.add_argument('--location', choices=['project', 'global'], default='project', help='Environment location')
    
    parser_env_unset = sub_env.add_parser('unset', help='Remove an environment variable')
    parser_env_unset.add_argument('key', help='Variable name')
    parser_env_unset.add_argument('--name', help='Environment name')
    parser_env_unset.add_argument('--location', choices=['project', 'global'], default='project', help='Environment location')
    parser_env_unset.add_argument('--format', choices=['json', 'env'], default='json', help='File format')
    parser_env_unset.add_argument('--temp', action='store_true', help="Don't persist to file, just unset for current session")
    
    parser_env_clear = sub_env.add_parser('clear', help='Clear/remove environment file')
    parser_env_clear.add_argument('--name', help='Environment name to clear')
    parser_env_clear.add_argument('--location', choices=['project', 'global'], default='project', help='Environment location')
    parser_env_clear.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    parser_env_save = sub_env.add_parser('save', help='Save current context as environment template')
    parser_env_save.add_argument('--name', help='Environment name to save as')
    parser_env_save.add_argument('--location', choices=['project', 'global'], default='project', help='Environment location')
    parser_env_save.add_argument('--context-name', help='Descriptive name for this context')

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
        verbose = getattr(args, 'verbose', False)
        if args.file:
            tash_key_val_from_file(args.key, args.file, args.ttl, verbose=verbose)
        elif args.value:
            tash_key_val(args.key, args.value, args.ttl, verbose=verbose)
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
        verbose = getattr(args, 'verbose', False)
        fetch_key_val(args.key, args.output, verbose=verbose)
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
                try:
                    session_id = validate_uuid(args.session_id, "Session ID")
                    user_id = validate_identifier(args.user_id, "User ID") if args.user_id else None
                    name = validate_identifier(args.name, "Name") if args.name else None
                    print(create_session_and_save(args.file, session_id, user_id, name))
                except ValueError as e:
                    print(f"Error: {e}")
                    return
            elif args.sessions_action == 'addnode':
                try:
                    session_id = validate_uuid(args.session_id, "Session ID")
                    trace_id = validate_uuid(args.trace_id, "Trace ID")
                    user_id = validate_identifier(args.user_id, "User ID") if args.user_id else None
                    name = validate_identifier(args.name, "Name") if args.name else None
                    print(add_trace_node_and_save(args.file, session_id, trace_id, user_id, name))
                except ValueError as e:
                    print(f"Error: {e}")
                    return
            elif args.sessions_action == 'view':
                data = load_session_file(args.file)
                print(data)
        elif args.fuse_command == 'scores' or args.fuse_command == 'sc':
            if args.scores_action == 'create':
                print(create_score(args.score_id, args.name, args.value))
            elif args.scores_action == 'apply':
                try:
                    # Validate that exactly one target is specified
                    targets = [args.trace_id, args.session_id]
                    specified_targets = [t for t in targets if t is not None]
                    
                    if len(specified_targets) != 1:
                        print("Error: Must specify exactly one of --trace-id or --session-id")
                        return
                    
                    # Validate and determine target type
                    if args.trace_id:
                        target_type = "trace"
                        target_id = validate_uuid(args.trace_id, "Trace ID")
                    else:
                        target_type = "session"
                        target_id = validate_uuid(args.session_id, "Session ID")
                    
                    # Validate other IDs
                    score_id = validate_identifier(args.score_id, "Score ID") if args.score_id else None
                    observation_id = validate_uuid(args.observation_id, "Observation ID") if args.observation_id else None
                    score_name = validate_identifier(args.name, "Score Name") if args.name else None
                    comment = validate_identifier(args.comment, "Comment", max_length=500) if args.comment else None
                    
                    # Apply score using create_score_for_target
                    result = create_score_for_target(
                        target_type=target_type,
                        target_id=target_id,
                        score_id=score_id,
                        score_value=args.value,
                        score_name=score_name,
                        observation_id=observation_id,
                        comment=comment
                    )
                except ValueError as e:
                    print(f"Error: {e}")
                    return
                print(result)
            elif args.scores_action == 'list':
                scores_data = list_scores()
                if args.json:
                    print(scores_data)
                else:
                    print(format_scores_table(scores_data))
        elif args.fuse_command == 'score-configs' or args.fuse_command == 'scc':
            if args.score_configs_action == 'list':
                configs_data = list_score_configs()
                if args.json:
                    print(configs_data)
                else:
                    print(format_score_configs_table(configs_data))
            elif args.score_configs_action == 'get':
                config_data = get_score_config(args.config_id)
                if args.json:
                    print(config_data)
                else:
                    # For now, just print JSON formatted for get action
                    try:
                        parsed = json.loads(config_data)
                        print(json.dumps(parsed, indent=2))
                    except json.JSONDecodeError:
                        print(config_data)
            elif args.score_configs_action == 'create':
                # Parse categories if provided
                categories = None
                if args.categories:
                    try:
                        categories = json.loads(args.categories)
                    except json.JSONDecodeError:
                        print("Error: Invalid JSON format for categories")
                        return
                
                result = create_score_config(
                    name=args.name,
                    data_type=args.data_type,
                    description=args.description,
                    categories=categories,
                    min_value=getattr(args, 'min_value', None),
                    max_value=getattr(args, 'max_value', None)
                )
                print(result)
            elif args.score_configs_action == 'export':
                include_metadata = not args.no_metadata  # Invert the flag
                result = export_score_configs(
                    output_file=args.output,
                    include_metadata=include_metadata
                )
                if not args.output:  # If no output file, print to stdout
                    print(result)
                else:
                    print(f"Score configs exported to {args.output}")
            elif args.score_configs_action == 'import':
                if args.preview:
                    # Show preview only
                    result = format_import_preview(args.file)
                    print(result)
                else:
                    # Perform actual import
                    result = import_score_configs(
                        import_file=args.file,
                        show_guidance=not getattr(args, 'no_guidance', False),
                        allow_duplicates=getattr(args, 'allow_duplicates', False),
                        selected_configs=args.select
                    )
                    print(result)
            elif args.score_configs_action == 'presets':
                if args.presets_action == 'list':
                    presets = list_presets(category=args.category)
                    if args.json:
                        print(json.dumps(presets, indent=2))
                    else:
                        print(format_presets_table(presets))
                elif args.presets_action == 'show':
                    preset = get_preset_by_name(args.preset_name)
                    print(format_preset_display(preset))
                elif args.presets_action == 'install':
                    if args.preset_names:
                        # Install specific presets
                        if len(args.preset_names) == 1:
                            # Single preset installation
                            result = install_preset(
                                args.preset_names[0], 
                                check_duplicates=not getattr(args, 'allow_duplicates', False),
                                interactive=args.interactive
                            )
                            print(result)
                        else:
                            # Multiple preset installation
                            result = install_presets_interactive(
                                preset_names=args.preset_names
                            )
                            print(result)
                    elif args.category:
                        # Install by category
                        result = install_presets_interactive(category=args.category)
                        print(result)
                    else:
                        # Install all presets (interactive by default)
                        result = install_presets_interactive()
                        print(result)
            elif args.score_configs_action == 'apply':
                # Validate that exactly one target is specified
                targets = [args.trace_id, args.session_id]
                specified_targets = [t for t in targets if t is not None]
                
                if len(specified_targets) != 1:
                    print("Error: Must specify exactly one of --trace-id or --session-id")
                    return
                
                # Determine target type
                if args.trace_id:
                    target_type = "trace"
                    target_id = args.trace_id
                else:
                    target_type = "session"
                    target_id = args.session_id
                
                result = apply_score_config(
                    config_name_or_id=args.config_name_or_id,
                    target_type=target_type,
                    target_id=target_id,
                    value=args.value,
                    observation_id=args.observation_id,
                    comment=args.comment
                )
                print(result)
            elif args.score_configs_action == 'available':
                configs = list_available_configs(
                    category=args.category,
                    cached_only=args.cached_only
                )
                if args.json:
                    print(json.dumps(configs, indent=2))
                else:
                    print(format_score_configs_table(json.dumps(configs)))
            elif args.score_configs_action == 'show':
                config = get_config_with_auto_refresh(args.config_name_or_id)
                if not config:
                    print(f"Config '{args.config_name_or_id}' not found")
                    return
                
                if args.json:
                    print(json.dumps(config, indent=2))
                else:
                    # Format detailed display
                    print(f"Score Config: {config.get('name', 'N/A')}")
                    print(f"ID: {config.get('id', 'N/A')}")
                    print(f"Type: {config.get('dataType', 'N/A')}")
                    print(f"Description: {config.get('description', 'N/A')}")
                    
                    if args.requirements:
                        print("\nValidation Requirements:")
                        data_type = config.get('dataType', '').upper()
                        
                        if data_type == 'BOOLEAN':
                            print("  - Accepts: true/false, 1/0, yes/no, on/off")
                        elif data_type == 'CATEGORICAL':
                            categories = config.get('categories', [])
                            if categories:
                                print("  - Valid options:")
                                for cat in categories:
                                    print(f"    • '{cat.get('label')}' (value: {cat.get('value')})")
                        elif data_type == 'NUMERIC':
                            min_val = config.get('minValue')
                            max_val = config.get('maxValue')
                            if min_val is not None and max_val is not None:
                                print(f"  - Range: {min_val} to {max_val}")
                            elif min_val is not None:
                                print(f"  - Minimum: {min_val}")
                            elif max_val is not None:
                                print(f"  - Maximum: {max_val}")
                            else:
                                print("  - Any numeric value")
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
                
                # Handle environment variable export
                if getattr(args, 'export_env', False):
                    print(f"export COAIA_TRACE_ID='{args.trace_id}'")
                    if args.session:
                        print(f"export COAIA_SESSION_ID='{args.session}'")
                    if args.user:
                        print(f"export COAIA_USER_ID='{args.user}'")
                else:
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
                
                # Auto-generate observation_id if not provided
                observation_id = args.observation_id if args.observation_id else str(uuid.uuid4())
                
                result = add_observation(
                    observation_id,
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
                
                # Handle environment variable export
                if getattr(args, 'export_env', False):
                    print(f"export COAIA_TRACE_ID='{args.trace_id}'")
                    print(f"export COAIA_LAST_OBSERVATION_ID='{observation_id}'")
                    if args.parent:
                        print(f"export COAIA_PARENT_OBSERVATION_ID='{args.parent}'")
                else:
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
            elif args.trace_action == 'patch-output':
                # Handle trace output patching
                output_data = None

                # Get output data from various sources
                if args.file:
                    # Read from file
                    if not os.path.isfile(args.file):
                        print(f"Error: File '{args.file}' does not exist.")
                        return
                    with open(args.file, 'r') as f:
                        output_data = f.read().strip()
                elif args.output_data:
                    # Use provided argument
                    output_data = args.output_data
                elif not sys.stdin.isatty():
                    # Read from stdin
                    output_data = sys.stdin.read().strip()
                else:
                    print("Error: No output data provided. Provide as argument, --file, or via stdin.")
                    return

                if not output_data:
                    print("Error: No output data provided.")
                    return

                # Parse as JSON if flag is set or if it looks like JSON
                parsed_output = output_data
                if args.json or (output_data.startswith('{') or output_data.startswith('[')):
                    try:
                        parsed_output = json.loads(output_data)
                    except json.JSONDecodeError:
                        if args.json:
                            print(f"Error: Failed to parse output as JSON: {output_data}")
                            return
                        # Fall back to string if JSON parsing failed and not explicitly requested
                        parsed_output = output_data

                # Validate trace_id
                try:
                    validate_identifier(args.trace_id, "trace_id")
                except ValueError as e:
                    print(f"Error: {e}")
                    return

                # Patch the trace output
                result = patch_trace_output(args.trace_id, parsed_output)
                print(result)
            elif args.trace_action in ['session-view', 'sv']:
                session_id = args.session_id
                traces_data = list_traces(session_id=session_id, include_observations=getattr(args, 'include_observations', False))
                if args.json:
                    print(traces_data)
                else:
                    print(format_traces_table(traces_data))
            elif args.trace_action in ['trace-view', 'tv']:
                trace_id = args.trace_id
                trace_data = get_trace_with_observations(trace_id)
                if args.json:
                    print(trace_data)
                else:
                    print(format_trace_tree(trace_data))
            elif args.trace_action in ['get-observation', 'obs-get', 'get-obs']:
                observation_id = args.observation_id
                obs_data = get_observation(observation_id)
                if args.json:
                    print(obs_data)
                else:
                    print(format_observation_display(obs_data))
            else:
                traces_data = list_traces(include_observations=getattr(args, 'include_observations', False))
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
    elif args.command == 'pipeline':
        loader = TemplateLoader()
        renderer = TemplateRenderer()
        
        if args.pipeline_action == 'list':
            templates = loader.list_templates(include_path=args.path)
            if args.json:
                print(json.dumps(templates, indent=2))
            else:
                # Format as table
                if not templates:
                    print("No templates found.")
                    return
                
                # Calculate column widths
                max_name = max([len(t.get('name', '')) for t in templates] + [len('Name')])
                max_desc = max([len(t.get('description', '') or '') for t in templates] + [len('Description')])
                max_version = max([len(t.get('version', '') or '') for t in templates] + [len('Version')])
                max_author = max([len(t.get('author', '') or '') for t in templates] + [len('Author')])
                
                # Print header
                separator = f"+{'-' * (max_name + 2)}+{'-' * (max_desc + 2)}+{'-' * (max_version + 2)}+{'-' * (max_author + 2)}+"
                print(separator)
                print(f"| {'Name':<{max_name}} | {'Description':<{max_desc}} | {'Version':<{max_version}} | {'Author':<{max_author}} |")
                print(separator)
                
                # Print templates
                for template in templates:
                    name = (template.get('name', '') or '')[:max_name]
                    desc = (template.get('description', '') or '')[:max_desc]
                    version = (template.get('version', '') or '')[:max_version]
                    author = (template.get('author', '') or '')[:max_author]
                    print(f"| {name:<{max_name}} | {desc:<{max_desc}} | {version:<{max_version}} | {author:<{max_author}} |")
                
                print(separator)
                print(f"Total templates: {len(templates)}")
                
                if args.path:
                    print("\nTemplate locations:")
                    for template in templates:
                        if 'path' in template:
                            print(f"  {template['name']}: {template['path']}")
        
        elif args.pipeline_action == 'show':
            template = loader.load_template(args.template_name)
            if not template:
                print(f"Template '{args.template_name}' not found.")
                return
            
            # Display template information
            print(f"Template: {template.name}")
            print(f"Version: {template.version}")
            print(f"Description: {template.description or 'No description'}")
            print(f"Author: {template.author or 'Unknown'}")
            if template.extends:
                print(f"Extends: {template.extends}")
            print()
            
            # Display variables
            print("Variables:")
            if not template.variables:
                print("  (No variables defined)")
            else:
                for var in template.variables:
                    required_text = "required" if var.required else "optional"
                    default_text = f" (default: {var.default})" if var.default is not None else ""
                    choices_text = f" (choices: {var.choices})" if var.choices else ""
                    print(f"  {var.name} ({var.type}, {required_text}){default_text}{choices_text}")
                    if var.description:
                        print(f"    {var.description}")
            print()
            
            # Display steps
            print("Pipeline Steps:")
            for i, step in enumerate(template.steps, 1):
                step_info = f"{i}. {step.name} ({step.observation_type})"
                if step.parent:
                    step_info += f" → parent: {step.parent}"
                if step.conditional:
                    step_info += f" → conditional: {step.conditional}"
                print(f"  {step_info}")
                if step.description:
                    print(f"     {step.description}")
            
            # Show preview if requested
            if args.preview:
                print("\n" + "="*50)
                print("PREVIEW (with example variables)")
                print("="*50)
                
                # Create example variables
                example_vars = {}
                for var in template.variables:
                    if var.default is not None:
                        example_vars[var.name] = var.default
                    elif var.choices:
                        example_vars[var.name] = var.choices[0]
                    elif var.type == "string":
                        example_vars[var.name] = f"example_{var.name}"
                    elif var.type == "number":
                        example_vars[var.name] = 42
                    elif var.type == "boolean":
                        example_vars[var.name] = True
                    elif var.type == "list":
                        example_vars[var.name] = ["item1", "item2"]
                
                try:
                    # For preview, always show judge integration capabilities if template has judge steps
                    has_judge_steps = any('judge' in step.name.lower() or 'evaluation' in step.name.lower() 
                                        for step in template.steps)
                    if has_judge_steps:
                        rendered_observations = renderer.render_with_judge_integration(template, example_vars, enable_judge_calls=False)
                    else:
                        rendered_observations = renderer.render_template(template, example_vars)
                    print(f"Example variables: {json.dumps(example_vars, indent=2)}")
                    print(f"\nRendered observations:")
                    for obs in rendered_observations:
                        print(f"  {obs['name']} ({obs['type']})")
                        if obs.get('parent'):
                            print(f"    → parent: {obs['parent']}")
                        if obs.get('variables'):
                            print(f"    → variables: {json.dumps(obs['variables'])}")
                except Exception as e:
                    print(f"Preview error: {str(e)}")
        
        elif args.pipeline_action == 'create':
            template = loader.load_template(args.template_name)
            if not template:
                print(f"Template '{args.template_name}' not found.")
                return
            
            # Parse variables
            variables = {}
            if args.var:
                for key, value in args.var:
                    # Try to parse as JSON, fallback to string
                    try:
                        variables[key] = json.loads(value)
                    except json.JSONDecodeError:
                        variables[key] = value
            
            # Validate variables
            try:
                errors = template.validate_variables(variables)
                if errors:
                    print(f"Template validation failed:")
                    for error in errors:
                        print(f"  - {error}")
                    return
                
                # Render template with optional judge integration
                enable_judge = getattr(args, 'enable_judge', False)
                if enable_judge:
                    rendered_observations = renderer.render_with_judge_integration(template, variables, enable_judge_calls=True)
                else:
                    rendered_observations = renderer.render_template(template, variables)
                
                if args.dry_run:
                    print(f"DRY RUN: Would create {len(rendered_observations)} observations")
                    print(f"Template: {template.name}")
                    print(f"Variables: {json.dumps(variables, indent=2)}")
                    print("\nObservations to create:")
                    for obs in rendered_observations:
                        print(f"  - {obs['name']} ({obs['type']})")
                        if obs.get('parent'):
                            print(f"    → parent: {obs['parent']}")
                    return
                
                # Generate trace ID if not provided
                trace_id = args.trace_id if args.trace_id else str(uuid.uuid4())
                
                # Create trace first
                trace_result = add_trace(
                    trace_id=trace_id,
                    user_id=args.user_id,
                    session_id=args.session_id,
                    name=f"Pipeline: {template.name}",
                    metadata={
                        "template_name": template.name,
                        "template_version": template.version,
                        "variables": variables
                    }
                )
                
                print(f"Created trace: {trace_id}")
                
                # Create observations
                observation_ids = {}  # Track created observations for parent references
                
                for obs_data in rendered_observations:
                    # Generate observation ID
                    obs_id = str(uuid.uuid4())
                    
                    # Resolve parent reference
                    parent_id = None
                    if obs_data.get('parent'):
                        parent_name = obs_data['parent']
                        if parent_name in observation_ids:
                            parent_id = observation_ids[parent_name]
                    
                    # Create observation
                    obs_result = add_observation(
                        observation_id=obs_id,
                        trace_id=trace_id,
                        observation_type=obs_data['type'],
                        name=obs_data['name'],
                        input_data=obs_data['variables'].get('input') if obs_data.get('variables') else None,
                        output_data=obs_data['variables'].get('output') if obs_data.get('variables') else None,
                        metadata=obs_data.get('metadata'),
                        parent_observation_id=parent_id
                    )
                    
                    # Store observation ID for future parent references
                    observation_ids[obs_data['name']] = obs_id
                    print(f"Created observation: {obs_data['name']} ({obs_id})")
                
                # Export environment variables if requested
                if args.export_env:
                    print(f"export COAIA_TRACE_ID='{trace_id}'")
                    if args.session_id:
                        print(f"export COAIA_SESSION_ID='{args.session_id}'")
                    if args.user_id:
                        print(f"export COAIA_USER_ID='{args.user_id}'")
                    # Export last created observation ID
                    if observation_ids:
                        last_obs_id = list(observation_ids.values())[-1]
                        print(f"export COAIA_LAST_OBSERVATION_ID='{last_obs_id}'")
                
            except Exception as e:
                print(f"Error creating pipeline: {str(e)}")
        
        elif args.pipeline_action == 'init':
            # Create a new template
            base_template = None
            if args.base_template:
                base_template = loader.load_template(args.base_template)
                if not base_template:
                    print(f"Base template '{args.base_template}' not found.")
                    return
            
            # Create new template structure
            if base_template:
                # Extend from base template
                new_template = PipelineTemplate(
                    name=args.template_name,
                    description=f"Extended from {base_template.name}",
                    extends=base_template.name,
                    variables=base_template.variables.copy(),
                    steps=base_template.steps.copy(),
                    author="User-created"
                )
            else:
                # Create minimal template
                new_template = PipelineTemplate(
                    name=args.template_name,
                    description=f"Custom template: {args.template_name}",
                    author="User-created",
                    variables=[
                        PipelineVariable(
                            name="user_id",
                            type="string",
                            required=False,
                            description="User running the pipeline"
                        )
                    ],
                    steps=[
                        PipelineStep(
                            name=f"{args.template_name} Main Task",
                            observation_type="EVENT",
                            description=f"Main task for {args.template_name}",
                            variables={
                                "input": {"task": args.template_name},
                                "output": {"status": "complete"}
                            },
                            metadata={
                                "template": args.template_name,
                                "created_by": "{{user_id or 'system'}}"
                            }
                        )
                    ]
                )
            
            # Save template
            try:
                saved_path = loader.save_template(new_template, args.location, args.format)
                print(f"Template '{args.template_name}' created at: {saved_path}")
                print(f"Edit the template file to customize variables and steps.")
            except Exception as e:
                print(f"Error creating template: {str(e)}")
    
    elif args.command == 'env':
        env_manager = EnvironmentManager()
        
        if args.env_action == 'init':
            try:
                file_path = env_manager.init_environment(
                    env_name=args.name,
                    location=args.location,
                    format=args.format
                )
                print(f"Environment file initialized: {file_path}")
                print("Default variables created:")
                env_vars = env_manager.load_environment(args.name, args.location)
                print(format_environment_table(env_vars))
            except Exception as e:
                print(f"Error initializing environment: {str(e)}")
        
        elif args.env_action == 'list':
            if args.name:
                # Show specific environment
                try:
                    location = args.location or 'project'
                    env_vars = env_manager.load_environment(args.name, location)
                    if args.json:
                        print(json.dumps(env_vars, indent=2))
                    else:
                        env_name = args.name or 'default'
                        print(f"Environment: {env_name} ({location})")
                        print(format_environment_table(env_vars))
                except Exception as e:
                    print(f"Error loading environment '{args.name}': {str(e)}")
            else:
                # List all environments
                environments = env_manager.list_environments()
                
                if args.json:
                    print(json.dumps(environments, indent=2))
                else:
                    has_envs = False
                    for location, env_list in environments.items():
                        if env_list:
                            if not has_envs:
                                print("Available environments:")
                                has_envs = True
                            print(f"\n{location.title()}:")
                            for env_name in env_list:
                                try:
                                    env_vars = env_manager.load_environment(env_name if env_name != 'default' else None, location)
                                    var_count = len([k for k in env_vars.keys() if not k.startswith('_COAIA_ENV_')])
                                    print(f"  {env_name} ({var_count} variables)")
                                except:
                                    print(f"  {env_name} (error reading)")
                    
                    if not has_envs:
                        print("No environment files found.")
                        print("Run 'coaia env init' to create a default environment.")
        
        elif args.env_action == 'source':
            try:
                env_vars = env_manager.source_environment(args.name, args.location)
                if args.export:
                    # Output shell export commands
                    commands = env_manager.export_shell_commands(args.name, args.location)
                    for cmd in commands:
                        print(cmd)
                else:
                    print(f"Sourced {len(env_vars)} environment variables")
                    if env_vars:
                        print(format_environment_table(env_vars))
            except Exception as e:
                print(f"Error sourcing environment: {str(e)}")
        
        elif args.env_action == 'set':
            try:
                env_vars = env_manager.set_variable(
                    key=args.key,
                    value=args.value,
                    env_name=args.name,
                    location=args.location,
                    persist=not args.temp,
                    format=args.format
                )
                if args.temp:
                    print(f"Set {args.key}={args.value} (session only)")
                else:
                    print(f"Set {args.key}={args.value} (persisted)")
            except Exception as e:
                print(f"Error setting variable: {str(e)}")
        
        elif args.env_action == 'get':
            try:
                value = env_manager.get_variable(args.key, args.name, args.location)
                if value is not None:
                    print(value)
                else:
                    print(f"Variable '{args.key}' not found")
                    return 1
            except Exception as e:
                print(f"Error getting variable: {str(e)}")
                return 1
        
        elif args.env_action == 'unset':
            try:
                env_vars = env_manager.unset_variable(
                    key=args.key,
                    env_name=args.name,
                    location=args.location,
                    persist=not args.temp,
                    format=args.format
                )
                if args.temp:
                    print(f"Unset {args.key} (session only)")
                else:
                    print(f"Unset {args.key} (persisted)")
            except Exception as e:
                print(f"Error unsetting variable: {str(e)}")
        
        elif args.env_action == 'clear':
            env_name = args.name or 'default'
            if not args.confirm:
                response = input(f"Are you sure you want to clear environment '{env_name}' ({args.location})? [y/N]: ")
                if response.lower() not in ['y', 'yes']:
                    print("Cancelled")
                    return
            
            try:
                env_manager.clear_environment(args.name, args.location)
                print(f"Environment '{env_name}' ({args.location}) cleared")
            except Exception as e:
                print(f"Error clearing environment: {str(e)}")
        
        elif args.env_action == 'save':
            try:
                file_path = env_manager.save_current_context(
                    env_name=args.name,
                    location=args.location,
                    name=args.context_name
                )
                print(f"Current context saved to: {file_path}")
                
                # Show what was saved
                current_context = env_manager.get_current_context()
                active_vars = {k: v for k, v in current_context.items() if v is not None}
                if active_vars:
                    print("Saved variables:")
                    print(format_environment_table(active_vars))
                else:
                    print("No active COAIA variables found in current context")
            except Exception as e:
                print(f"Error saving context: {str(e)}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
