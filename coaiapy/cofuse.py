import requests
from requests.auth import HTTPBasicAuth
from coaiamodule import read_config
import datetime
import yaml
import json

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

def create_prompt(prompt_name, content):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/prompts"
    data = {"name": prompt_name, "text": content}
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

def create_dataset(dataset_name):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/datasets"
    data = {"name": dataset_name}
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

def add_trace(trace_id, user_id=None, session_id=None, name=None):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    now = datetime.datetime.utcnow().isoformat()
    data = {
        "batch": [
            {
                "type": "trace",
                "id": trace_id,
                "timestamp": now
            }
        ]
    }
    if session_id:
        data["batch"][0]["sessionId"] = session_id
    if name:
        data["batch"][0]["name"] = name
    metadata = {}
    if user_id:
        metadata["userId"] = user_id
    if metadata:
        data["batch"][0]["metadata"] = metadata
    url = f"{c['langfuse_base_url']}/api/public/ingestion"
    r = requests.post(url, json=data, auth=auth)
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
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/scores"
    data = {
        "traceId": trace_id,
        "scoreId": score_id,
        "value": score_value
    }
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

def create_dataset_item(dataset_name, input_data, expected_output=None, metadata=None):
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
        data["metadata"] = json.loads(metadata)
    r = requests.post(url, json=data, auth=auth)
    return r.text