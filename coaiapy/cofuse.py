import requests
from requests.auth import HTTPBasicAuth
from coaiamodule import read_config
import datetime
import yaml
import json
import re

def parse_tlid_to_iso(tlid_str):
    """
    Parse tlid format to ISO 8601 format
    
    Supports:
    - yyMMddHHmmss (12 digits): Full format with seconds
    - yyMMddHHmm (10 digits): Short format, seconds default to 00
    
    Args:
        tlid_str: String in format 'yyMMddHHmmss' or 'yyMMddHHmm'
                 (e.g., '251216143022' or '2512161430' for 2025-12-16 14:30:22 or 2025-12-16 14:30:00)
    
    Returns:
        String in ISO 8601 format with Z suffix (e.g., '2025-12-16T14:30:22Z')
    
    Raises:
        ValueError: If the format is invalid
    """
    if not tlid_str or not isinstance(tlid_str, str):
        raise ValueError("tlid_str must be a non-empty string")
    
    # Check if it's 10 or 12 digits
    if re.match(r'^\d{12}$', tlid_str):
        # Full format: yyMMddHHmmss
        format_type = "full"
    elif re.match(r'^\d{10}$', tlid_str):
        # Short format: yyMMddHHmm
        format_type = "short"
    else:
        raise ValueError("tlid format must be 10 digits (yyMMddHHmm) or 12 digits (yyMMddHHmmss)")
    
    try:
        # Parse components
        yy = int(tlid_str[:2])
        mm = int(tlid_str[2:4])
        dd = int(tlid_str[4:6])
        hh = int(tlid_str[6:8])
        min_val = int(tlid_str[8:10])
        
        if format_type == "full":
            ss = int(tlid_str[10:12])
        else:
            ss = 0  # Default seconds to 0 for short format
        
        # Convert 2-digit year to 4-digit (assuming 2000s)
        yyyy = 2000 + yy
        
        # Create datetime object (this will validate the date/time)
        dt = datetime.datetime(yyyy, mm, dd, hh, min_val, ss)
        
        # Return ISO format with Z suffix
        return dt.isoformat() + 'Z'
        
    except ValueError as e:
        raise ValueError(f"Invalid date/time values in tlid '{tlid_str}': {str(e)}")

def process_langfuse_response(response_text, actual_id=None, operation_type="operation"):
    """
    Process Langfuse API response to return cleaner format with actual IDs
    
    Args:
        response_text: Raw response from Langfuse API
        actual_id: The actual ID we want to show (observation_id, trace_id, etc.)
        operation_type: Type of operation for error messages
    
    Returns:
        Processed response with actual IDs instead of internal event IDs
    """
    try:
        response_data = json.loads(response_text)
        
        if isinstance(response_data, dict):
            # Handle successful responses
            if 'successes' in response_data:
                processed_successes = []
                for success in response_data['successes']:
                    processed_success = success.copy()
                    # Replace event ID with actual ID if provided
                    if actual_id and success.get('id', '').endswith('-event'):
                        processed_success['id'] = actual_id
                    processed_successes.append(processed_success)
                
                response_data['successes'] = processed_successes
                return json.dumps(response_data, indent=2)
            
            # Handle error responses
            elif 'message' in response_data:
                return response_text
        
        return response_text
        
    except (json.JSONDecodeError, KeyError):
        # Return original response if we can't process it
        return response_text

def detect_and_parse_datetime(time_str):
    """
    Detect format and parse datetime string to ISO format
    
    Supports:
    - tlid format: yyMMddHHmmss (12 digits) or yyMMddHHmm (10 digits)
    - ISO format: already in correct format
    - Other formats: passed through as-is
    
    Args:
        time_str: Time string in various formats
        
    Returns:
        String in ISO 8601 format, or original string if not recognized
    """
    if not time_str:
        return None
    
    # Check if it's tlid format (10 or 12 digits)
    if re.match(r'^\d{10}$', time_str) or re.match(r'^\d{12}$', time_str):
        try:
            return parse_tlid_to_iso(time_str)
        except ValueError:
            # If tlid parsing fails, return original string
            return time_str
    
    # Check if it's already ISO format or similar
    if 'T' in time_str or time_str.endswith('Z'):
        return time_str
    
    # Return original string for other formats
    return time_str

def get_comments():
    config = read_config()
    auth = HTTPBasicAuth(config['langfuse_public_key'], config['langfuse_secret_key'])
    url = f"{config['langfuse_base_url']}/api/public/comments"
    response = requests.get(url, auth=auth)
    return response.text

def post_comment(text):
    config = read_config()
    auth = HTTPBasicAuth(config['langfuse_public_key'], config['langfuse_secret_key'])
    url = f"{config['langfuse_base_url']}/api/public/comments"
    data = {"text": text}
    response = requests.post(url, json=data, auth=auth)
    return response.text

def list_prompts(debug=False):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base = f"{c['langfuse_base_url']}/api/public/v2/prompts"
    page = 1
    all_prompts = []
    
    if debug:
        print(f"Starting pagination from: {base}")
    
    while True:
        url = f"{base}?page={page}"
        if debug:
            print(f"Fetching page {page}: {url}")
            
        r = requests.get(url, auth=auth)
        if r.status_code != 200:
            if debug:
                print(f"Request failed with status {r.status_code}: {r.text}")
            break
            
        try:
            data = r.json()
        except ValueError as e:
            if debug:
                print(f"JSON parsing error: {e}")
            break

        if debug:
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict):
                print(f"  data length: {len(data.get('data', [])) if data.get('data') else 'No data key'}")
                meta = data.get('meta', {})
                print(f"  meta: {meta}")
                if meta:
                    print(f"    page: {meta.get('page')}")
                    print(f"    limit: {meta.get('limit')}")
                    print(f"    totalPages: {meta.get('totalPages')}")
                    print(f"    totalItems: {meta.get('totalItems')}")
                # Also check for other pagination formats
                print(f"  hasNextPage: {data.get('hasNextPage')}")
                print(f"  nextPage: {data.get('nextPage')}")
                print(f"  totalPages: {data.get('totalPages')}")

        prompts = data.get('data') if isinstance(data, dict) else data
        if not prompts:
            if debug:
                print("No prompts found, breaking")
            break
            
        if isinstance(prompts, list):
            all_prompts.extend(prompts)
            if debug:
                print(f"Added {len(prompts)} prompts, total now: {len(all_prompts)}")
        else:
            all_prompts.append(prompts)
            if debug:
                print(f"Added 1 prompt, total now: {len(all_prompts)}")

        # Check pagination conditions
        should_continue = False
        if isinstance(data, dict):
            # Check for meta-based pagination (Langfuse v2 format)
            meta = data.get('meta', {})
            if meta and meta.get('totalPages'):
                current_page = meta.get('page', page)
                total_pages = meta.get('totalPages')
                if current_page < total_pages:
                    page += 1
                    should_continue = True
                    if debug:
                        print(f"Meta pagination: page {current_page} < totalPages {total_pages}, continuing to page {page}")
                else:
                    if debug:
                        print(f"Meta pagination: page {current_page} >= totalPages {total_pages}, stopping")
            # Fallback to other pagination formats
            elif data.get('hasNextPage'):
                page += 1
                should_continue = True
                if debug:
                    print(f"hasNextPage=True, continuing to page {page}")
            elif data.get('nextPage'):
                page = data['nextPage']
                should_continue = True
                if debug:
                    print(f"nextPage={page}, continuing")
            elif data.get('totalPages') and page < data['totalPages']:
                page += 1
                should_continue = True
                if debug:
                    print(f"page {page} < totalPages {data.get('totalPages')}, continuing")
            else:
                if debug:
                    print("No pagination indicators found, stopping")
        
        if not should_continue:
            break

    if debug:
        print(f"Final result: {len(all_prompts)} total prompts")
    
    return json.dumps(all_prompts, indent=2)

def format_prompts_table(prompts_json):
    """Format prompts data as a readable table"""
    try:
        data = json.loads(prompts_json) if isinstance(prompts_json, str) else prompts_json
        
        # Handle both direct array and nested structure from Langfuse API
        if isinstance(data, dict) and 'data' in data:
            prompts = data['data']
        elif isinstance(data, list):
            prompts = data
        else:
            prompts = data
            
        if not prompts:
            return "No prompts found."
        
        # Table headers
        headers = ["Name", "Version", "Created", "Tags/Labels"]
        
        # Calculate column widths
        max_name = max([len(p.get('name', '') or '') for p in prompts] + [len(headers[0])])
        max_version = max([len(str(p.get('version', '') or '')) for p in prompts] + [len(headers[1])])
        max_created = max([len((p.get('createdAt', '') or '')[:10]) for p in prompts] + [len(headers[2])])
        max_tags = max([len(', '.join(p.get('labels', []) or [])) for p in prompts] + [len(headers[3])])
        
        # Minimum widths
        max_name = max(max_name, 15)
        max_version = max(max_version, 8)  
        max_created = max(max_created, 10)
        max_tags = max(max_tags, 12)
        
        # Format table
        separator = f"+{'-' * (max_name + 2)}+{'-' * (max_version + 2)}+{'-' * (max_created + 2)}+{'-' * (max_tags + 2)}+"
        header_row = f"| {headers[0]:<{max_name}} | {headers[1]:<{max_version}} | {headers[2]:<{max_created}} | {headers[3]:<{max_tags}} |"
        
        table_lines = [separator, header_row, separator]
        
        for prompt in prompts:
            name = (prompt.get('name', '') or 'N/A')[:max_name]
            version = str(prompt.get('version', '') or 'N/A')[:max_version]
            created = (prompt.get('createdAt', '') or 'N/A')[:10]  # Just date part
            labels = ', '.join(prompt.get('labels', []) or [])[:max_tags] or 'None'
            
            row = f"| {name:<{max_name}} | {version:<{max_version}} | {created:<{max_created}} | {labels:<{max_tags}} |"
            table_lines.append(row)
        
        table_lines.append(separator)
        table_lines.append(f"Total prompts: {len(prompts)}")
        
        return '\n'.join(table_lines)
        
    except Exception as e:
        return f"Error formatting prompts table: {str(e)}\n\nRaw JSON:\n{prompts_json}"

def format_datasets_table(datasets_json):
    """Format datasets data as a readable table"""
    try:
        data = json.loads(datasets_json) if isinstance(datasets_json, str) else datasets_json
        
        # Handle nested structure from Langfuse API
        if isinstance(data, dict) and 'data' in data:
            datasets = data['data']
        else:
            datasets = data
            
        if not datasets:
            return "No datasets found."
        
        # Table headers
        headers = ["Name", "Created", "Items", "Description"]
        
        # Calculate column widths
        max_name = max([len(d.get('name', '')) for d in datasets] + [len(headers[0])])
        max_created = max([len((d.get('createdAt', '') or '')[:10]) for d in datasets] + [len(headers[1])])
        max_items = max([len(str(d.get('itemCount', 0))) for d in datasets] + [len(headers[2])])
        max_desc = max([len((d.get('description', '') or '')[:50]) for d in datasets] + [len(headers[3])])
        
        # Minimum widths
        max_name = max(max_name, 15)
        max_created = max(max_created, 10)
        max_items = max(max_items, 6)
        max_desc = max(max_desc, 20)
        
        # Format table
        separator = f"+{'-' * (max_name + 2)}+{'-' * (max_created + 2)}+{'-' * (max_items + 2)}+{'-' * (max_desc + 2)}+"
        header_row = f"| {headers[0]:<{max_name}} | {headers[1]:<{max_created}} | {headers[2]:<{max_items}} | {headers[3]:<{max_desc}} |"
        
        table_lines = [separator, header_row, separator]
        
        for dataset in datasets:
            name = (dataset.get('name', '') or 'N/A')[:max_name]
            created = (dataset.get('createdAt', '') or 'N/A')[:10]  # Just date part
            items = str(dataset.get('itemCount', 0))
            desc = (dataset.get('description', '') or 'No description')[:max_desc]
            
            row = f"| {name:<{max_name}} | {created:<{max_created}} | {items:<{max_items}} | {desc:<{max_desc}} |"
            table_lines.append(row)
        
        table_lines.append(separator)
        table_lines.append(f"Total datasets: {len(datasets)}")
        
        return '\n'.join(table_lines)
        
    except Exception as e:
        return f"Error formatting datasets table: {str(e)}\n\nRaw JSON:\n{datasets_json}"

def format_traces_table(traces_json):
    """Format traces data as a readable table"""
    try:
        data = json.loads(traces_json) if isinstance(traces_json, str) else traces_json
        
        # Handle nested structure from Langfuse API
        if isinstance(data, dict) and 'data' in data:
            traces = data['data']
        else:
            traces = data
            
        if not traces:
            return "No traces found."
        
        # Table headers
        headers = ["Name", "User ID", "Started", "Status", "Session"]
        
        # Calculate column widths
        max_name = max([len((t.get('name', '') or '')[:25]) for t in traces] + [len(headers[0])])
        max_user = max([len((t.get('userId', '') or '')[:15]) for t in traces] + [len(headers[1])])
        max_started = max([len((t.get('timestamp', '') or '')[:16]) for t in traces] + [len(headers[2])])
        max_status = max([len(str(t.get('level', '') or '')) for t in traces] + [len(headers[3])])
        max_session = max([len((t.get('sessionId', '') or '')[:20]) for t in traces] + [len(headers[4])])
        
        # Minimum widths
        max_name = max(max_name, 15)
        max_user = max(max_user, 8)
        max_started = max(max_started, 16)
        max_status = max(max_status, 8)
        max_session = max(max_session, 12)
        
        # Format table
        separator = f"+{'-' * (max_name + 2)}+{'-' * (max_user + 2)}+{'-' * (max_started + 2)}+{'-' * (max_status + 2)}+{'-' * (max_session + 2)}+"
        header_row = f"| {headers[0]:<{max_name}} | {headers[1]:<{max_user}} | {headers[2]:<{max_started}} | {headers[3]:<{max_status}} | {headers[4]:<{max_session}} |"
        
        table_lines = [separator, header_row, separator]
        
        for trace in traces:
            name = (trace.get('name', '') or 'Unnamed')[:max_name]
            user = (trace.get('userId', '') or 'N/A')[:max_user]
            started = (trace.get('timestamp', '') or 'N/A')[:16]  # YYYY-MM-DD HH:MM
            status = str(trace.get('level', '') or 'N/A')[:max_status]
            session = (trace.get('sessionId', '') or 'N/A')[:max_session]
            
            row = f"| {name:<{max_name}} | {user:<{max_user}} | {started:<{max_started}} | {status:<{max_status}} | {session:<{max_session}} |"
            table_lines.append(row)
        
        table_lines.append(separator)
        table_lines.append(f"Total traces: {len(traces)}")
        
        return '\n'.join(table_lines)
        
    except Exception as e:
        return f"Error formatting traces table: {str(e)}\n\nRaw JSON:\n{traces_json}"

def format_prompt_display(prompt_json):
    """Format a single prompt as a beautiful display"""
    try:
        prompt = json.loads(prompt_json) if isinstance(prompt_json, str) else prompt_json
        if not prompt:
            return "Prompt not found."

        # Handle API error messages gracefully
        if 'message' in prompt and 'error' in prompt:
            return f"Error: {prompt['message']} ({prompt['error']})"
        
        # Extract key information
        name = prompt.get('name', '') or 'Unnamed Prompt'
        version = prompt.get('version', '') or 'N/A'
        created_at = prompt.get('createdAt', '') or ''
        created = created_at[:19] if created_at else 'N/A'  # YYYY-MM-DD HH:MM:SS
        updated_at = prompt.get('updatedAt', '') or ''
        updated = updated_at[:19] if updated_at else 'N/A'
        labels = prompt.get('labels', []) or []
        
        # Handle different prompt content formats
        prompt_content = prompt.get('prompt', '')
        if isinstance(prompt_content, list):
            # Handle chat format: [{"role": "system", "content": "..."}]
            prompt_text = '\n'.join([msg.get('content', '') for msg in prompt_content if msg.get('content')])
        else:
            # Handle string format
            prompt_text = prompt_content or ''
            
        type_val = prompt.get('type', '') or 'text'
        is_active = prompt.get('isActive', False)
        
        # Handle config if present
        config = prompt.get('config', {})
        temperature = config.get('temperature', 'N/A') if config else 'N/A'
        max_tokens = config.get('max_tokens', 'N/A') if config else 'N/A'
        
        # Additional metadata
        tags = prompt.get('tags', []) or []
        commit_message = prompt.get('commitMessage', '') or ''
        
        # Build display
        display_lines = []
        
        # Header with name and version
        header = f"🎯 PROMPT: {name}"
        if version != 'N/A':
            header += f" (v{version})"
        display_lines.append("=" * len(header))
        display_lines.append(header)
        display_lines.append("=" * len(header))
        display_lines.append("")
        
        # Metadata section
        display_lines.append("📋 METADATA:")
        display_lines.append(f"   Type: {type_val}")
        display_lines.append(f"   Active: {'✅ Yes' if is_active else '❌ No'}")
        display_lines.append(f"   Created: {created}")
        display_lines.append(f"   Updated: {updated}")
        if labels:
            display_lines.append(f"   Labels: {', '.join(labels)}")
        else:
            display_lines.append("   Labels: None")
        if tags:
            display_lines.append(f"   Tags: {', '.join(tags)}")
        if commit_message:
            display_lines.append(f"   Commit: {commit_message}")
        display_lines.append("")
        
        # Configuration section (if present)
        if config:
            display_lines.append("⚙️ CONFIGURATION:")
            if temperature != 'N/A':
                display_lines.append(f"   Temperature: {temperature}")
            if max_tokens != 'N/A':
                display_lines.append(f"   Max Tokens: {max_tokens}")
            # Add other config fields if present
            for key, value in config.items():
                if key not in ['temperature', 'max_tokens']:
                    display_lines.append(f"   {key.title()}: {value}")
            display_lines.append("")
        
        # Prompt content section
        display_lines.append("📝 PROMPT CONTENT:")
        display_lines.append("-" * 50)
        if prompt_text:
            # Split long content into readable lines
            for line in prompt_text.split('\n'):
                display_lines.append(line)
        else:
            display_lines.append("(No content)")
        display_lines.append("-" * 50)
        
        return '\n'.join(display_lines)
        
    except Exception as e:
        return f"Error formatting prompt display: {str(e)}\n\nRaw JSON:\n{prompt_json}"

def get_prompt(prompt_name, label=None):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    
    url = f"{c['langfuse_base_url']}/api/public/v2/prompts/{prompt_name}"
    params = {}
    if label:
        params['label'] = label
    
    r = requests.get(url, auth=auth, params=params)
    
    return r.text

def create_prompt(prompt_name, content, commit_message=None, labels=None, tags=None, prompt_type="text", config=None):
    """
    Create a prompt in Langfuse with enhanced features
    
    Args:
        prompt_name: Name of the prompt
        content: Prompt content (string for text prompts, list for chat prompts)
        commit_message: Optional commit message for version tracking
        labels: Optional list of deployment labels
        tags: Optional list of tags
        prompt_type: Type of prompt ("text" or "chat")
        config: Optional configuration object
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/prompts"
    
    # Build the request data based on prompt type
    data = {
        "type": prompt_type,
        "name": prompt_name,
        "prompt": content
    }
    
    # Add optional fields
    if commit_message:
        data["commitMessage"] = commit_message
        
    if labels:
        data["labels"] = labels if isinstance(labels, list) else [labels]
        
    if tags:
        data["tags"] = tags if isinstance(tags, list) else [tags]
        
    if config:
        data["config"] = config
    
    r = requests.post(url, json=data, auth=auth)
    return r.text

def list_datasets():
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/datasets"
    r = requests.get(url, auth=auth)
    return r.text

def get_dataset(dataset_name):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/datasets/{dataset_name}"
    r = requests.get(url, auth=auth)
    return r.text

def create_dataset(dataset_name, description=None, metadata=None):
    """
    Create a dataset in Langfuse with enhanced features
    
    Args:
        dataset_name: Name of the dataset
        description: Optional description of the dataset
        metadata: Optional metadata object
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/datasets"
    
    data = {"name": dataset_name}
    
    if description:
        data["description"] = description
        
    if metadata:
        if isinstance(metadata, str):
            try:
                data["metadata"] = json.loads(metadata)
            except json.JSONDecodeError:
                data["metadata"] = {"note": metadata}  # Treat as simple note if not JSON
        else:
            data["metadata"] = metadata
    
    r = requests.post(url, json=data, auth=auth)
    return r.text

def list_dataset_items(dataset_name, debug=False):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base = f"{c['langfuse_base_url']}/api/public/dataset-items"
    page = 1
    all_items = []
    
    while True:
        params = {'name': dataset_name, 'page': page}
        if debug:
            print(f"Fetching page {page} for dataset {dataset_name}: {base} with params {params}")
            
        r = requests.get(base, auth=auth, params=params)
        if r.status_code != 200:
            if debug:
                print(f"Request failed with status {r.status_code}: {r.text}")
            break
            
        try:
            data = r.json()
        except ValueError as e:
            if debug:
                print(f"JSON parsing error: {e}")
            break

        items = data.get('data') if isinstance(data, dict) else data
        if not items:
            if debug:
                print("No items found, breaking")
            break
            
        all_items.extend(items)

        meta = data.get('meta', {})
        if meta.get('page', page) >= meta.get('totalPages', 1):
            break
        page += 1

    return json.dumps(all_items, indent=2)

def format_dataset_display(dataset_json, items_json):
    """Format a single dataset and its items as a beautiful display"""
    try:
        dataset = json.loads(dataset_json)
        items = json.loads(items_json)

        if 'message' in dataset and 'error' in dataset:
            return f"Error fetching dataset: {dataset['message']} ({dataset['error']})"

        # Build display
        display_lines = []
        
        # Header with dataset name
        name = dataset.get('name', 'Unnamed Dataset')
        header = f"📦 DATASET: {name}"
        display_lines.append("=" * len(header))
        display_lines.append(header)
        display_lines.append("=" * len(header))
        display_lines.append(f"   Description: {dataset.get('description') or 'N/A'}")
        display_lines.append(f"   Created: {dataset.get('createdAt', 'N/A')[:19]}")
        display_lines.append(f"   Updated: {dataset.get('updatedAt', 'N/A')[:19]}")
        display_lines.append("")

        # Items table
        display_lines.append("📋 DATASET ITEMS:")
        if not items:
            display_lines.append("   (No items found in this dataset)")
            return '\n'.join(display_lines)

        headers = ["ID", "Input", "Expected Output"]
        
        # Truncate content for display
        def truncate(text, length):
            if not text:
                return "N/A"
            text = str(text).replace('\n', ' ')
            return text if len(text) <= length else text[:length-3] + "..."

        rows = [
            [
                item.get('id'),
                truncate(item.get('input'), 50),
                truncate(item.get('expectedOutput'), 50)
            ] for item in items
        ]

        max_id = max([len(r[0]) for r in rows] + [len(headers[0])])
        max_input = max([len(r[1]) for r in rows] + [len(headers[1])])
        max_output = max([len(r[2]) for r in rows] + [len(headers[2])])

        separator = f"+{'-' * (max_id + 2)}+{'-' * (max_input + 2)}+{'-' * (max_output + 2)}+"
        header_row = f"| {headers[0]:<{max_id}} | {headers[1]:<{max_input}} | {headers[2]:<{max_output}} |"
        
        display_lines.append(separator)
        display_lines.append(header_row)
        display_lines.append(separator)

        for row_data in rows:
            row = f"| {row_data[0]:<{max_id}} | {row_data[1]:<{max_input}} | {row_data[2]:<{max_output}} |"
            display_lines.append(row)
        
        display_lines.append(separator)
        display_lines.append(f"Total items: {len(items)}")

        return '\n'.join(display_lines)

    except Exception as e:
        return f"Error formatting dataset display: {str(e)}"

def format_dataset_for_finetuning(items_json, format_type, system_instruction):
    """Formats dataset items for fine-tuning."""
    try:
        items = json.loads(items_json)
        output_lines = []

        for item in items:
            input_content = item.get('input')
            output_content = item.get('expectedOutput')

            if not input_content or not output_content:
                continue

            if format_type == 'openai':
                record = {
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": input_content},
                        {"role": "assistant", "content": output_content}
                    ]
                }
            elif format_type == 'gemini':
                record = {
                    "systemInstruction": {
                        "role": "system",
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": [
                        {"role": "user", "parts": [{"text": input_content}]},
                        {"role": "model", "parts": [{"text": output_content}]}
                    ]
                }
            else:
                continue
            
            output_lines.append(json.dumps(record))

        return '\n'.join(output_lines)

    except Exception as e:
        return f"Error formatting for fine-tuning: {str(e)}"

def add_trace(trace_id, user_id=None, session_id=None, name=None, input_data=None, output_data=None, metadata=None):
    """
    Create a trace in Langfuse with enhanced features
    
    Args:
        trace_id: Unique identifier for the trace
        user_id: Optional user ID
        session_id: Optional session ID  
        name: Optional trace name
        input_data: Optional input data
        output_data: Optional output data
        metadata: Optional metadata object
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # Build the trace body
    body = {
        "id": trace_id,
        "timestamp": now
    }
    
    if session_id:
        body["sessionId"] = session_id
    if name:
        body["name"] = name
    if input_data:
        body["input"] = input_data
    if output_data:
        body["output"] = output_data
    if user_id:
        body["userId"] = user_id
    if metadata:
        body["metadata"] = metadata
    
    # Build the ingestion event
    event_id = trace_id + "-event"  # Create unique event ID
    data = {
        "batch": [
            {
                "id": event_id,
                "timestamp": now,
                "type": "trace-create",
                "body": body
            }
        ]
    }
    
    url = f"{c['langfuse_base_url']}/api/public/ingestion"
    r = requests.post(url, json=data, auth=auth)
    return process_langfuse_response(r.text, trace_id, "trace creation")

def add_observation(observation_id, trace_id, observation_type="EVENT", name=None, 
                   input_data=None, output_data=None, metadata=None, parent_observation_id=None,
                   start_time=None, end_time=None, level="DEFAULT", model=None, usage=None):
    """
    Create an observation (event, span, or generation) in Langfuse
    
    Args:
        observation_id: Unique identifier for the observation
        trace_id: ID of the trace this observation belongs to
        observation_type: Type of observation ("EVENT", "SPAN", "GENERATION")
        name: Optional observation name
        input_data: Optional input data
        output_data: Optional output data
        metadata: Optional metadata object
        parent_observation_id: Optional parent observation ID for nesting
        start_time: Optional start time (ISO format or tlid format yyMMddHHmmss)
        end_time: Optional end time (ISO format or tlid format yyMMddHHmmss)
        level: Observation level ("DEBUG", "DEFAULT", "WARNING", "ERROR")
        model: Optional model name
        usage: Optional usage information
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    
    # Auto-detect and parse datetime formats
    if start_time:
        start_time = detect_and_parse_datetime(start_time)
    else:
        start_time = datetime.datetime.utcnow().isoformat() + 'Z'
    
    if end_time:
        end_time = detect_and_parse_datetime(end_time)
    
    body = {
        "id": observation_id,
        "traceId": trace_id,
        "type": observation_type,
        "startTime": start_time,
        "level": level
    }
    
    if name:
        body["name"] = name
    if input_data:
        body["input"] = input_data
    if output_data:
        body["output"] = output_data
    if metadata:
        body["metadata"] = metadata
    if parent_observation_id:
        body["parentObservationId"] = parent_observation_id
    if end_time:
        body["endTime"] = end_time
    if model:
        body["model"] = model
    if usage:
        body["usage"] = usage
    
    # Build the ingestion event with proper envelope structure
    event_id = observation_id + "-event"  # Create unique event ID
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    data = {
        "batch": [
            {
                "id": event_id,
                "timestamp": now,
                "type": "observation-create",
                "body": body
            }
        ]
    }
    
    url = f"{c['langfuse_base_url']}/api/public/ingestion"
    r = requests.post(url, json=data, auth=auth)
    return process_langfuse_response(r.text, observation_id, "observation creation")

def add_observations_batch(trace_id, observations_data, format_type='json', dry_run=False):
    """
    Add multiple observations to a trace from structured data
    
    Args:
        trace_id: ID of the trace to add observations to
        observations_data: List of observation dictionaries or string data to parse.
                          start_time and end_time fields support ISO format, tlid format (yyMMddHHmmss), 
                          or short tlid format (yyMMddHHmm)
        format_type: Format of input data ('json' or 'yaml')
        dry_run: If True, show what would be created without actually creating
    
    Returns:
        Results from batch creation or dry run preview
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    
    # Parse input data if it's a string
    if isinstance(observations_data, str):
        try:
            if format_type == 'yaml':
                observations = yaml.safe_load(observations_data)
            else:
                observations = json.loads(observations_data)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            return f"Error parsing {format_type.upper()} data: {str(e)}"
    else:
        observations = observations_data
    
    # Ensure observations is a list
    if not isinstance(observations, list):
        observations = [observations]
    
    if dry_run:
        # Return preview of what would be created
        preview = {
            "trace_id": trace_id,
            "total_observations": len(observations),
            "observations_preview": []
        }
        
        for i, obs in enumerate(observations):
            obs_preview = {
                "index": i + 1,
                "id": obs.get('id', f"obs-{i+1}"),
                "type": obs.get('type', 'EVENT'),
                "name": obs.get('name', f"Observation {i+1}"),
                "has_input": bool(obs.get('input')),
                "has_output": bool(obs.get('output')),
                "parent": obs.get('parent_observation_id')
            }
            preview["observations_preview"].append(obs_preview)
        
        return json.dumps(preview, indent=2)
    
    # Build batch ingestion data
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    batch_events = []
    
    for i, obs in enumerate(observations):
        # Generate observation ID if not provided
        observation_id = obs.get('id', f"{trace_id}-obs-{i+1}")
        
        # Parse start_time with auto-detection
        start_time_val = obs.get('start_time')
        if start_time_val:
            start_time_val = detect_and_parse_datetime(start_time_val)
        else:
            start_time_val = now
            
        # Parse end_time with auto-detection
        end_time_val = obs.get('end_time')
        if end_time_val:
            end_time_val = detect_and_parse_datetime(end_time_val)
        
        # Build observation body
        body = {
            "id": observation_id,
            "traceId": trace_id,
            "type": obs.get('type', 'EVENT'),
            "startTime": start_time_val,
            "level": obs.get('level', 'DEFAULT')
        }
        
        # Add optional fields
        if obs.get('name'):
            body["name"] = obs['name']
        if obs.get('input'):
            body["input"] = obs['input']
        if obs.get('output'):
            body["output"] = obs['output']
        if obs.get('metadata'):
            body["metadata"] = obs['metadata']
        if obs.get('parent_observation_id'):
            body["parentObservationId"] = obs['parent_observation_id']
        if end_time_val:
            body["endTime"] = end_time_val
        if obs.get('model'):
            body["model"] = obs['model']
        if obs.get('usage'):
            body["usage"] = obs['usage']
        
        # Create event
        event_id = f"{observation_id}-event"
        event = {
            "id": event_id,
            "timestamp": now,
            "type": "observation-create",
            "body": body
        }
        
        batch_events.append(event)
    
    # Send batch request
    data = {"batch": batch_events}
    url = f"{c['langfuse_base_url']}/api/public/ingestion"
    r = requests.post(url, json=data, auth=auth)
    # For batch operations, we don't have a single ID to clean up, so return as-is
    return r.text

def create_session(session_id, user_id, session_name="New Session"):
    return add_trace(trace_id=session_id, user_id=user_id, session_id=session_id, name=session_name)

def add_trace_node(session_id, trace_id, user_id, node_name="Child Node"):
    return add_trace(trace_id=trace_id, user_id=user_id, session_id=session_id, name=node_name)

def create_score(score_id, score_name="New Score", score_value=1.0):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/scores"
    data = {
        "id": score_id,
        "name": score_name,
        "value": score_value
    }
    r = requests.post(url, json=data, auth=auth)
    return r.text

def apply_score_to_trace(trace_id, score_id, score_value=1.0):
    """Apply a score to a trace (legacy function, kept for compatibility)"""
    return create_score_for_target(
        target_type="trace",
        target_id=trace_id,
        score_id=score_id,
        score_value=score_value
    )

def create_score_for_target(target_type, target_id, score_id, score_value=1.0, score_name=None, observation_id=None, config_id=None, comment=None):
    """
    Create a score for a trace or session
    
    Args:
        target_type: "trace" or "session"
        target_id: ID of the trace or session
        score_id: ID for the score (if not using config_id)
        score_value: Value of the score
        score_name: Name of the score (if not using config_id)
        observation_id: Optional observation ID for trace scores
        config_id: Optional config ID to use instead of score_id/score_name
        comment: Optional comment for the score
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/scores"
    
    # Build the request data
    data = {
        "value": score_value
    }
    
    # Add target-specific fields
    if target_type == "trace":
        data["traceId"] = target_id
        if observation_id:
            data["observationId"] = observation_id
    elif target_type == "session":
        data["sessionId"] = target_id
    else:
        raise ValueError("target_type must be 'trace' or 'session'")
    
    # Add score identification (either by config or by id/name)
    if config_id:
        data["configId"] = config_id
    else:
        if score_id:
            data["id"] = score_id
        if score_name:
            data["name"] = score_name
    
    # Add optional fields
    if comment:
        data["comment"] = comment
    
    r = requests.post(url, json=data, auth=auth)
    return r.text

def list_scores(debug=False, user_id=None, name=None, from_timestamp=None, to_timestamp=None, config_id=None):
    """List all scores from Langfuse with optional filtering"""
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base = f"{c['langfuse_base_url']}/api/public/v2/scores"
    page = 1
    all_scores = []
    
    if debug:
        print(f"Starting pagination from: {base}")
    
    while True:
        # Build query parameters
        params = {"page": page}
        if user_id:
            params["userId"] = user_id
        if name:
            params["name"] = name
        if from_timestamp:
            params["fromTimestamp"] = from_timestamp
        if to_timestamp:
            params["toTimestamp"] = to_timestamp
        if config_id:
            params["configId"] = config_id
            
        if debug:
            print(f"Fetching page {page}: {base} with params {params}")
            
        r = requests.get(base, params=params, auth=auth)
        if r.status_code != 200:
            if debug:
                print(f"Request failed with status {r.status_code}: {r.text}")
            break
            
        try:
            data = r.json()
        except ValueError as e:
            if debug:
                print(f"JSON parsing error: {e}")
            break

        if debug:
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict):
                print(f"  data length: {len(data.get('data', [])) if data.get('data') else 'No data key'}")
                meta = data.get('meta', {})
                print(f"  meta: {meta}")

        scores = data.get('data') if isinstance(data, dict) else data
        if not scores:
            if debug:
                print("No scores found, breaking")
            break
            
        if isinstance(scores, list):
            all_scores.extend(scores)
            if debug:
                print(f"Added {len(scores)} scores, total now: {len(all_scores)}")
        else:
            all_scores.append(scores)
            if debug:
                print(f"Added 1 score, total now: {len(all_scores)}")

        # Check pagination conditions
        should_continue = False
        if isinstance(data, dict):
            # Check for meta-based pagination (Langfuse v2 format)
            meta = data.get('meta', {})
            if meta and meta.get('totalPages'):
                current_page = meta.get('page', page)
                total_pages = meta.get('totalPages')
                if current_page < total_pages:
                    page += 1
                    should_continue = True
                    if debug:
                        print(f"Meta pagination: page {current_page} < totalPages {total_pages}, continuing to page {page}")
                else:
                    if debug:
                        print(f"Meta pagination: page {current_page} >= totalPages {total_pages}, stopping")
            # Fallback to other pagination formats
            elif data.get('hasNextPage'):
                page += 1
                should_continue = True
                if debug:
                    print(f"hasNextPage=True, continuing to page {page}")
            elif data.get('nextPage'):
                page = data['nextPage']
                should_continue = True
                if debug:
                    print(f"nextPage={page}, continuing")
            elif data.get('totalPages') and page < data['totalPages']:
                page += 1
                should_continue = True
                if debug:
                    print(f"page {page} < totalPages {data.get('totalPages')}, continuing")
            else:
                if debug:
                    print("No pagination indicators found, stopping")
        
        if not should_continue:
            break

    if debug:
        print(f"Final result: {len(all_scores)} total scores")
    
    return json.dumps(all_scores, indent=2)

def format_scores_table(scores_json):
    """Format scores data as a readable table"""
    try:
        data = json.loads(scores_json) if isinstance(scores_json, str) else scores_json
        
        # Handle nested structure from Langfuse API
        if isinstance(data, dict) and 'data' in data:
            scores = data['data']
        elif isinstance(data, list):
            scores = data
        else:
            scores = data
            
        if not scores:
            return "No scores found."
        
        # Table headers
        headers = ["ID", "Name", "Value", "Created", "Trace ID"]
        
        # Calculate column widths
        max_id = max([len((s.get('id', '') or '')[:20]) for s in scores] + [len(headers[0])])
        max_name = max([len(s.get('name', '') or '') for s in scores] + [len(headers[1])])
        max_value = max([len(str(s.get('value', '') or '')) for s in scores] + [len(headers[2])])
        max_created = max([len((s.get('timestamp', '') or '')[:16]) for s in scores] + [len(headers[3])])
        max_trace = max([len((s.get('traceId', '') or '')[:20]) for s in scores] + [len(headers[4])])
        
        # Minimum widths
        max_id = max(max_id, 8)
        max_name = max(max_name, 15)
        max_value = max(max_value, 8)
        max_created = max(max_created, 16)
        max_trace = max(max_trace, 12)
        
        # Format table
        separator = f"+{'-' * (max_id + 2)}+{'-' * (max_name + 2)}+{'-' * (max_value + 2)}+{'-' * (max_created + 2)}+{'-' * (max_trace + 2)}+"
        header_row = f"| {headers[0]:<{max_id}} | {headers[1]:<{max_name}} | {headers[2]:<{max_value}} | {headers[3]:<{max_created}} | {headers[4]:<{max_trace}} |"
        
        table_lines = [separator, header_row, separator]
        
        for score in scores:
            score_id = (score.get('id', '') or 'N/A')[:max_id]
            name = (score.get('name', '') or 'N/A')[:max_name]
            value = str(score.get('value', '') or 'N/A')[:max_value]
            created = (score.get('timestamp', '') or 'N/A')[:16]  # YYYY-MM-DD HH:MM
            trace_id = (score.get('traceId', '') or 'N/A')[:max_trace]
            
            row = f"| {score_id:<{max_id}} | {name:<{max_name}} | {value:<{max_value}} | {created:<{max_created}} | {trace_id:<{max_trace}} |"
            table_lines.append(row)
        
        table_lines.append(separator)
        table_lines.append(f"Total scores: {len(scores)}")
        
        return '\n'.join(table_lines)
        
    except Exception as e:
        return f"Error formatting scores table: {str(e)}\n\nRaw JSON:\n{scores_json}"

def list_score_configs(debug=False):
    """List all score configs from Langfuse"""
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base = f"{c['langfuse_base_url']}/api/public/score-configs"
    page = 1
    all_configs = []
    
    if debug:
        print(f"Starting pagination from: {base}")
    
    while True:
        url = f"{base}?page={page}"
        if debug:
            print(f"Fetching page {page}: {url}")
            
        r = requests.get(url, auth=auth)
        if r.status_code != 200:
            if debug:
                print(f"Request failed with status {r.status_code}: {r.text}")
            break
            
        try:
            data = r.json()
        except ValueError as e:
            if debug:
                print(f"JSON parsing error: {e}")
            break

        if debug:
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict):
                print(f"  data length: {len(data.get('data', [])) if data.get('data') else 'No data key'}")
                meta = data.get('meta', {})
                print(f"  meta: {meta}")

        configs = data.get('data') if isinstance(data, dict) else data
        if not configs:
            if debug:
                print("No score configs found, breaking")
            break
            
        if isinstance(configs, list):
            all_configs.extend(configs)
            if debug:
                print(f"Added {len(configs)} score configs, total now: {len(all_configs)}")
        else:
            all_configs.append(configs)
            if debug:
                print(f"Added 1 score config, total now: {len(all_configs)}")

        # Check pagination conditions
        should_continue = False
        if isinstance(data, dict):
            # Check for meta-based pagination (Langfuse v2 format)
            meta = data.get('meta', {})
            if meta and meta.get('totalPages'):
                current_page = meta.get('page', page)
                total_pages = meta.get('totalPages')
                if current_page < total_pages:
                    page += 1
                    should_continue = True
                    if debug:
                        print(f"Meta pagination: page {current_page} < totalPages {total_pages}, continuing to page {page}")
                else:
                    if debug:
                        print(f"Meta pagination: page {current_page} >= totalPages {total_pages}, stopping")
            # Fallback to other pagination formats
            elif data.get('hasNextPage'):
                page += 1
                should_continue = True
                if debug:
                    print(f"hasNextPage=True, continuing to page {page}")
            elif data.get('nextPage'):
                page = data['nextPage']
                should_continue = True
                if debug:
                    print(f"nextPage={page}, continuing")
            elif data.get('totalPages') and page < data['totalPages']:
                page += 1
                should_continue = True
                if debug:
                    print(f"page {page} < totalPages {data.get('totalPages')}, continuing")
            else:
                if debug:
                    print("No pagination indicators found, stopping")
        
        if not should_continue:
            break

    if debug:
        print(f"Final result: {len(all_configs)} total score configs")
    
    return json.dumps(all_configs, indent=2)

def format_score_configs_table(configs_json):
    """Format score configs data as a readable table"""
    try:
        data = json.loads(configs_json) if isinstance(configs_json, str) else configs_json
        
        # Handle nested structure from Langfuse API
        if isinstance(data, dict) and 'data' in data:
            configs = data['data']
        elif isinstance(data, list):
            configs = data
        else:
            configs = data
            
        if not configs:
            return "No score configs found."
        
        # Table headers
        headers = ["ID", "Name", "Data Type", "Description", "Created"]
        
        # Calculate column widths
        max_id = max([len((c.get('id', '') or '')[:20]) for c in configs] + [len(headers[0])])
        max_name = max([len(c.get('name', '') or '') for c in configs] + [len(headers[1])])
        max_datatype = max([len(str(c.get('dataType', '') or '')) for c in configs] + [len(headers[2])])
        max_desc = max([len((c.get('description', '') or '')[:40]) for c in configs] + [len(headers[3])])
        max_created = max([len((c.get('createdAt', '') or '')[:16]) for c in configs] + [len(headers[4])])
        
        # Minimum widths
        max_id = max(max_id, 8)
        max_name = max(max_name, 15)
        max_datatype = max(max_datatype, 10)
        max_desc = max(max_desc, 20)
        max_created = max(max_created, 16)
        
        # Format table
        separator = f"+{'-' * (max_id + 2)}+{'-' * (max_name + 2)}+{'-' * (max_datatype + 2)}+{'-' * (max_desc + 2)}+{'-' * (max_created + 2)}+"
        header_row = f"| {headers[0]:<{max_id}} | {headers[1]:<{max_name}} | {headers[2]:<{max_datatype}} | {headers[3]:<{max_desc}} | {headers[4]:<{max_created}} |"
        
        table_lines = [separator, header_row, separator]
        
        for config in configs:
            config_id = (config.get('id', '') or 'N/A')[:max_id]
            name = (config.get('name', '') or 'N/A')[:max_name]
            data_type = str(config.get('dataType', '') or 'N/A')[:max_datatype]
            description = (config.get('description', '') or 'N/A')[:max_desc]
            created = (config.get('createdAt', '') or 'N/A')[:16]  # YYYY-MM-DD HH:MM
            
            row = f"| {config_id:<{max_id}} | {name:<{max_name}} | {data_type:<{max_datatype}} | {description:<{max_desc}} | {created:<{max_created}} |"
            table_lines.append(row)
        
        table_lines.append(separator)
        table_lines.append(f"Total score configs: {len(configs)}")
        
        return '\n'.join(table_lines)
        
    except Exception as e:
        return f"Error formatting score configs table: {str(e)}\n\nRaw JSON:\n{configs_json}"

def get_score_config(config_id):
    """Get a specific score config by ID"""
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/score-configs/{config_id}"
    r = requests.get(url, auth=auth)
    return r.text

def create_score_config(name, data_type, description=None, categories=None, min_value=None, max_value=None):
    """
    Create a score config in Langfuse
    
    Args:
        name: Name of the score config
        data_type: Type of score data ("NUMERIC", "CATEGORICAL", "BOOLEAN")
        description: Optional description of the score config
        categories: Optional list of categories for categorical scores (list of dicts with 'label' and 'value')
        min_value: Optional minimum value for numerical scores
        max_value: Optional maximum value for numerical scores
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/score-configs"
    
    # Build the request data
    data = {
        "name": name,
        "dataType": data_type
    }
    
    # Add optional fields
    if description:
        data["description"] = description
        
    if categories:
        data["categories"] = categories
        
    if min_value is not None:
        data["minValue"] = min_value
        
    if max_value is not None:
        data["maxValue"] = max_value
    
    r = requests.post(url, json=data, auth=auth)
    return r.text

def load_session_file(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except:
        return {"session_id": None, "nodes": []}

def save_session_file(path, session_data):
    with open(path, 'w') as f:
        yaml.safe_dump(session_data, f, default_flow_style=False)

def create_session_and_save(session_file, session_id, user_id, session_name="New Session"):
    result = create_session(session_id, user_id, session_name)
    data = load_session_file(session_file)
    data["session_id"] = session_id
    if "nodes" not in data:
        data["nodes"] = []
    save_session_file(session_file, data)
    return result

def add_trace_node_and_save(session_file, session_id, trace_id, user_id, node_name="Child Node"):
    result = add_trace_node(session_id, trace_id, user_id, node_name)
    data = load_session_file(session_file)
    if "nodes" not in data:
        data["nodes"] = []
    data["nodes"].append({"trace_id": trace_id, "name": node_name})
    save_session_file(session_file, data)
    return result

def list_traces():
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/traces"
    r = requests.get(url, auth=auth)
    return r.text

def list_projects():
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/projects"
    r = requests.get(url, auth=auth)
    return r.text

def create_dataset_item(dataset_name, input_data, expected_output=None, metadata=None, 
                       source_trace_id=None, source_observation_id=None, item_id=None, status=None):
    """
    Create a dataset item in Langfuse with enhanced features
    
    Args:
        dataset_name: Name of the dataset
        input_data: Input data for the item
        expected_output: Optional expected output
        metadata: Optional metadata (string or object)
        source_trace_id: Optional source trace ID
        source_observation_id: Optional source observation ID 
        item_id: Optional custom ID (items are upserted on their id)
        status: Optional status (DatasetStatus enum)
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/dataset-items"
    
    data = {
        "datasetName": dataset_name,
        "input": input_data
    }
    
    if expected_output:
        data["expectedOutput"] = expected_output
        
    if metadata:
        if isinstance(metadata, str):
            try:
                data["metadata"] = json.loads(metadata)
            except json.JSONDecodeError:
                data["metadata"] = {"note": metadata}  # Treat as simple note if not JSON
        else:
            data["metadata"] = metadata
            
    if source_trace_id:
        data["sourceTraceId"] = source_trace_id
        
    if source_observation_id:
        data["sourceObservationId"] = source_observation_id
        
    if item_id:
        data["id"] = item_id
        
    if status:
        data["status"] = status
    
    r = requests.post(url, json=data, auth=auth)
    return r.text