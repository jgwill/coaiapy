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
        prompts = json.loads(prompts_json) if isinstance(prompts_json, str) else prompts_json
        if not prompts:
            return "No prompts found."
        
        # Table headers
        headers = ["Name", "Version", "Created", "Tags/Labels"]
        
        # Calculate column widths
        max_name = max([len(p.get('name', '')) for p in prompts] + [len(headers[0])])
        max_version = max([len(str(p.get('version', ''))) for p in prompts] + [len(headers[1])])
        max_created = max([len(p.get('createdAt', '')[:10]) for p in prompts] + [len(headers[2])])
        max_tags = max([len(', '.join(p.get('labels', []))) for p in prompts] + [len(headers[3])])
        
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
            name = prompt.get('name', 'N/A')[:max_name]
            version = str(prompt.get('version', 'N/A'))[:max_version]
            created = prompt.get('createdAt', 'N/A')[:10]  # Just date part
            labels = ', '.join(prompt.get('labels', []))[:max_tags] or 'None'
            
            row = f"| {name:<{max_name}} | {version:<{max_version}} | {created:<{max_created}} | {labels:<{max_tags}} |"
            table_lines.append(row)
        
        table_lines.append(separator)
        table_lines.append(f"Total prompts: {len(prompts)}")
        
        return '\n'.join(table_lines)
        
    except Exception as e:
        return f"Error formatting prompts table: {str(e)}\n\nRaw JSON:\n{prompts_json}"

def get_prompt(prompt_name):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/prompts/{prompt_name}"
    r = requests.get(url, auth=auth)
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