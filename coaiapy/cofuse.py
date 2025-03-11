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

def list_prompts():
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    url = f"{c['langfuse_base_url']}/api/public/v2/prompts"
    r = requests.get(url, auth=auth)
    return r.text

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