import requests
from requests.auth import HTTPBasicAuth
from coaiapy.coaiamodule import read_config
import datetime
import yaml
import json
import re
import os
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union

@dataclass
class ScoreCategory:
    """Represents a category in a categorical score configuration"""
    label: str
    value: Union[int, float]

@dataclass
class ScoreConfigMetadata:
    """Metadata for score configurations from Langfuse"""
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    project_id: Optional[str] = None
    is_archived: Optional[bool] = None

@dataclass 
class ScoreConfig:
    """Represents a score configuration with all its properties"""
    name: str
    data_type: str  # "NUMERIC", "CATEGORICAL", "BOOLEAN"
    description: Optional[str] = None
    categories: Optional[List[ScoreCategory]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    metadata: Optional[ScoreConfigMetadata] = None
    
    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format suitable for JSON export/import"""
        result = {
            "name": self.name,
            "dataType": self.data_type,
            "description": self.description,
            "minValue": self.min_value,
            "maxValue": self.max_value
        }
        
        # Convert categories to dict format
        if self.categories:
            result["categories"] = [
                {"label": cat.label, "value": cat.value} 
                for cat in self.categories
            ]
        else:
            result["categories"] = None
        
        # Include metadata if requested
        if include_metadata and self.metadata:
            result["metadata"] = {
                "id": self.metadata.id,
                "createdAt": self.metadata.created_at,
                "updatedAt": self.metadata.updated_at,
                "projectId": self.metadata.project_id,
                "isArchived": self.metadata.is_archived
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScoreConfig':
        """Create ScoreConfig from dictionary (e.g., from JSON import)"""
        # Parse categories
        categories = None
        if data.get("categories"):
            categories = [
                ScoreCategory(label=cat["label"], value=cat["value"])
                for cat in data["categories"]
            ]
        
        # Parse metadata if present
        metadata = None
        if data.get("metadata"):
            meta_data = data["metadata"]
            metadata = ScoreConfigMetadata(
                id=meta_data.get("id"),
                created_at=meta_data.get("createdAt"),
                updated_at=meta_data.get("updatedAt"),
                project_id=meta_data.get("projectId"),
                is_archived=meta_data.get("isArchived")
            )
        
        return cls(
            name=data["name"],
            data_type=data["dataType"],
            description=data.get("description"),
            categories=categories,
            min_value=data.get("minValue"),
            max_value=data.get("maxValue"),
            metadata=metadata
        )
    
    def to_create_command(self) -> str:
        """Generate CLI command to create this score config"""
        cmd_parts = [
            "coaia fuse score-configs create",
            f'"{self.name}"',
            self.data_type
        ]
        
        if self.description:
            cmd_parts.append(f'--description "{self.description}"')
        
        if self.min_value is not None:
            cmd_parts.append(f'--min-value {self.min_value}')
            
        if self.max_value is not None:
            cmd_parts.append(f'--max-value {self.max_value}')
        
        if self.categories:
            categories_json = json.dumps([
                {"label": cat.label, "value": cat.value} 
                for cat in self.categories
            ])
            cmd_parts.append(f"--categories '{categories_json}'")
        
        return " ".join(cmd_parts)

@dataclass
class ScoreConfigExport:
    """Represents an export file containing multiple score configurations"""
    version: str = "1.0"
    exported_at: Optional[str] = None
    total_configs: Optional[int] = None
    configs: List[ScoreConfig] = field(default_factory=list)
    
    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for JSON export"""
        return {
            "version": self.version,
            "exportedAt": self.exported_at or datetime.datetime.utcnow().isoformat() + 'Z',
            "totalConfigs": len(self.configs),
            "configs": [config.to_dict(include_metadata) for config in self.configs]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScoreConfigExport':
        """Create from dictionary (e.g., from JSON import)"""
        configs = [
            ScoreConfig.from_dict(config_data) 
            for config_data in data.get("configs", [])
        ]
        
        return cls(
            version=data.get("version", "1.0"),
            exported_at=data.get("exportedAt"),
            total_configs=data.get("totalConfigs"),
            configs=configs
        )

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

def get_comments(object_type=None, object_id=None, author_user_id=None, page=1, limit=50):
    """
    Get comments with optional filtering.

    Args:
        object_type: Filter by object type (trace, observation, session, prompt)
        object_id: Filter by specific object ID (requires object_type)
        author_user_id: Filter by author user ID
        page: Page number (starts at 1)
        limit: Items per page

    Returns:
        JSON response with comments data
    """
    config = read_config()
    auth = HTTPBasicAuth(config['langfuse_public_key'], config['langfuse_secret_key'])
    url = f"{config['langfuse_base_url']}/api/public/comments"

    # Build query parameters
    params = {}
    if page:
        params['page'] = page
    if limit:
        params['limit'] = limit
    if object_type:
        params['objectType'] = object_type.upper()  # API expects uppercase (TRACE, OBSERVATION, SESSION, PROMPT)
    if object_id:
        params['objectId'] = object_id
    if author_user_id:
        params['authorUserId'] = author_user_id

    response = requests.get(url, auth=auth, params=params)
    return response.text

def get_comment_by_id(comment_id):
    """
    Get a specific comment by ID.

    Args:
        comment_id: The unique Langfuse identifier of a comment

    Returns:
        JSON response with comment data
    """
    config = read_config()
    auth = HTTPBasicAuth(config['langfuse_public_key'], config['langfuse_secret_key'])
    url = f"{config['langfuse_base_url']}/api/public/comments/{comment_id}"
    response = requests.get(url, auth=auth)
    return response.text

def post_comment(text, object_type, object_id, author_user_id=None):
    """
    Create a comment attached to an object (trace, observation, session, or prompt).

    Args:
        text: The comment text/content
        object_type: Type of object to attach comment to (trace, observation, session, prompt) - REQUIRED
        object_id: ID of the object to attach comment to - REQUIRED
        author_user_id: Optional user ID of the comment author

    Returns:
        JSON response with created comment data
    """
    config = read_config()
    auth = HTTPBasicAuth(config['langfuse_public_key'], config['langfuse_secret_key'])
    url = f"{config['langfuse_base_url']}/api/public/comments"

    # Get current project ID (required by API)
    project_info = get_current_project_info()
    if not project_info or not project_info.get('id'):
        raise ValueError("Could not determine project ID. Ensure Langfuse credentials are configured.")

    # Build request data with API-expected field names
    data = {
        "projectId": project_info['id'],
        "content": text,  # API expects "content", not "text"
        "objectType": object_type.upper(),  # API expects uppercase (TRACE, OBSERVATION, SESSION, PROMPT)
        "objectId": object_id
    }

    if author_user_id:
        data['authorUserId'] = author_user_id

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
        headers = ["Name", "User ID", "Started", "Status", "Session ID", "Trace ID", "Release", "Version", "Observations"]
        
        # Calculate column widths
        # Ensure UUIDs are fully displayed (36 chars for UUID + 2 for padding)
        UUID_LEN = 36
        
        max_name = max([len((t.get('name', '') or '')) for t in traces] + [len(headers[0])])
        max_user = max([len((t.get('userId', '') or '')) for t in traces] + [len(headers[1])])
        max_started = max([len((t.get('timestamp', '') or '')[:16]) for t in traces] + [len(headers[2])])
        max_status = max([len(str(t.get('level', '') or '')) for t in traces] + [len(headers[3])])
        max_session = max([len((t.get('sessionId', '') or '')) for t in traces] + [len(headers[4])])
        max_trace = max([len((t.get('id', '') or '')) for t in traces] + [len(headers[5])])
        max_release = max([len((t.get('release', '') or '')) for t in traces] + [len(headers[6])])
        max_version = max([len((t.get('version', '') or '')) for t in traces] + [len(headers[7])])
        max_observations = max([len(f"{len(t.get('observations', []))} observations") if t.get('observations') else len('N/A') for t in traces] + [len(headers[8])])
        
        # Minimum widths
        max_name = max(max_name, 15)
        max_user = max(max_user, 8)
        max_started = max(max_started, 16)
        max_status = max(max_status, 8)
        max_session = max(max_session, UUID_LEN) # Ensure full UUID
        max_trace = max(max_trace, UUID_LEN)   # Ensure full UUID
        max_release = max(max_release, 8)
        max_version = max(max_version, 8)
        max_observations = max(max_observations, 12)
        
        # Format table
        separator = f"+{'-' * (max_name + 2)}+{'-' * (max_user + 2)}+{'-' * (max_started + 2)}+{'-' * (max_status + 2)}+{'-' * (max_session + 2)}+{'-' * (max_trace + 2)}+{'-' * (max_release + 2)}+{'-' * (max_version + 2)}+{'-' * (max_observations + 2)}+"
        header_row = f"| {headers[0]:<{max_name}} | {headers[1]:<{max_user}} | {headers[2]:<{max_started}} | {headers[3]:<{max_status}} | {headers[4]:<{max_session}} | {headers[5]:<{max_trace}} | {headers[6]:<{max_release}} | {headers[7]:<{max_version}} | {headers[8]:<{max_observations}} |"
        
        table_lines = [separator, header_row, separator]
        
        for trace in traces:
            name = (trace.get('name', '') or 'Unnamed')[:max_name]
            user = (trace.get('userId', '') or 'N/A')[:max_user]
            started = (trace.get('timestamp', '') or 'N/A')[:16]  # YYYY-MM-DD HH:MM
            status = str(trace.get('level', '') or 'N/A')[:max_status]
            session = (trace.get('sessionId', '') or 'N/A') # No truncation for session ID
            trace_id = (trace.get('id', '') or 'N/A') # No truncation for trace ID
            release = (trace.get('release', '') or 'N/A')
            version = (trace.get('version', '') or 'N/A')
            observations_count = f"{len(trace.get('observations', []))} observations" if trace.get('observations') else 'N/A'
            
            row = f"| {name:<{max_name}} | {user:<{max_user}} | {started:<{max_started}} | {status:<{max_status}} | {session:<{max_session}} | {trace_id:<{max_trace}} | {release:<{max_release}} | {version:<{max_version}} | {observations_count:<{max_observations}} |"
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

def patch_trace_output(trace_id, output_data):
    """
    Update the output field of an existing trace in Langfuse.

    This sends a new trace-create event with the same trace ID but different event ID,
    allowing Langfuse to merge/update the output field of the existing trace.

    Args:
        trace_id: ID of the trace to update
        output_data: New output data (can be string, object, or any JSON-serializable data)

    Returns:
        Processed response with success/error status
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    # Build minimal trace body with just ID and output
    # Langfuse will merge this with the existing trace
    body = {
        "id": trace_id,
        "timestamp": now,
        "output": output_data
    }

    # Create unique event ID for this patch operation
    # Using timestamp-based suffix to make it deterministic but unique
    event_id = f"{trace_id}-patch-{uuid.uuid4().hex[:8]}"

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
    return process_langfuse_response(r.text, trace_id, "trace output patch")

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

# Built-in preset library of unified score configurations
BUILT_IN_PRESETS = [
    # Narrative & Storytelling Category
    {
        "name": "Narrative Coherence",
        "dataType": "CATEGORICAL",
        "description": "Evaluates how well story elements connect and flow together logically.",
        "categories": [
            {"label": "Incoherent", "value": 1},
            {"label": "Loosely Connected", "value": 2},
            {"label": "Coherent", "value": 3},
            {"label": "Well-Structured", "value": 4},
            {"label": "Masterfully Woven", "value": 5}
        ]
    },
    {
        "name": "Character Development",
        "dataType": "CATEGORICAL",
        "description": "Measures the depth and growth of characters throughout the narrative.",
        "categories": [
            {"label": "Flat/Static", "value": 1},
            {"label": "Basic Development", "value": 2},
            {"label": "Moderate Growth", "value": 3},
            {"label": "Rich Development", "value": 4},
            {"label": "Complex Evolution", "value": 5}
        ]
    },
    {
        "name": "Emotional Resonance",
        "dataType": "CATEGORICAL",
        "description": "Evaluates the emotional impact and connection with the audience.",
        "categories": [
            {"label": "No Emotional Impact", "value": 1},
            {"label": "Mild Resonance", "value": 2},
            {"label": "Moderate Impact", "value": 3},
            {"label": "Strong Emotional Connection", "value": 4},
            {"label": "Deeply Moving", "value": 5}
        ]
    },
    {
        "name": "Originality",
        "dataType": "CATEGORICAL",
        "description": "Evaluates the uniqueness and freshness of the ideas or expression.",
        "categories": [
            {"label": "Unoriginal", "value": 1},
            {"label": "Low Originality", "value": 2},
            {"label": "Moderate Originality", "value": 3},
            {"label": "High Originality", "value": 4},
            {"label": "Highly Original", "value": 5}
        ]
    },
    {
        "name": "Thematic Depth",
        "dataType": "CATEGORICAL",
        "description": "Measures the depth and sophistication of underlying themes.",
        "categories": [
            {"label": "Surface Level", "value": 1},
            {"label": "Basic Themes", "value": 2},
            {"label": "Developed Themes", "value": 3},
            {"label": "Rich Thematic Content", "value": 4},
            {"label": "Profound Depth", "value": 5}
        ]
    },
    # AI Response Evaluation Category
    {
        "name": "Helpfulness",
        "dataType": "CATEGORICAL",
        "description": "Measures how well the response addresses the user's needs and provides value.",
        "categories": [
            {"label": "Not Helpful", "value": 1},
            {"label": "Slightly Helpful", "value": 2},
            {"label": "Moderately Helpful", "value": 3},
            {"label": "Very Helpful", "value": 4},
            {"label": "Extremely Helpful", "value": 5}
        ]
    },
    {
        "name": "Accuracy",
        "dataType": "CATEGORICAL",
        "description": "Evaluates the factual correctness and precision of the information provided.",
        "categories": [
            {"label": "Inaccurate", "value": 1},
            {"label": "Mostly Inaccurate", "value": 2},
            {"label": "Partially Accurate", "value": 3},
            {"label": "Mostly Accurate", "value": 4},
            {"label": "Completely Accurate", "value": 5}
        ]
    },
    {
        "name": "Safety",
        "dataType": "CATEGORICAL",
        "description": "Assesses whether the content is safe, appropriate, and free from harmful elements.",
        "categories": [
            {"label": "Unsafe/Harmful", "value": 1},
            {"label": "Potentially Unsafe", "value": 2},
            {"label": "Neutral/Safe", "value": 3},
            {"label": "Very Safe", "value": 4},
            {"label": "Exemplarily Safe", "value": 5}
        ]
    },
    {
        "name": "Relevance",
        "dataType": "CATEGORICAL",
        "description": "Measures how well the response relates to and addresses the specific query or context.",
        "categories": [
            {"label": "Irrelevant", "value": 1},
            {"label": "Slightly Relevant", "value": 2},
            {"label": "Moderately Relevant", "value": 3},
            {"label": "Highly Relevant", "value": 4},
            {"label": "Perfectly Relevant", "value": 5}
        ]
    },
    {
        "name": "Completeness",
        "dataType": "CATEGORICAL",
        "description": "Evaluates whether the response fully addresses all aspects of the query or task.",
        "categories": [
            {"label": "Incomplete", "value": 1},
            {"label": "Partially Complete", "value": 2},
            {"label": "Mostly Complete", "value": 3},
            {"label": "Very Complete", "value": 4},
            {"label": "Comprehensive", "value": 5}
        ]
    },
    # General Content Evaluation Category
    {
        "name": "Clarity",
        "dataType": "CATEGORICAL",
        "description": "Measures how easy it is to understand the content.",
        "categories": [
            {"label": "Unclear", "value": 1},
            {"label": "Moderately Clear", "value": 2},
            {"label": "Clear", "value": 3},
            {"label": "Very Clear", "value": 4},
            {"label": "Excellent Clarity", "value": 5}
        ]
    },
    {
        "name": "Engagement",
        "dataType": "CATEGORICAL",
        "description": "Evaluates how well the content captures and holds the audience's attention.",
        "categories": [
            {"label": "Disengaging", "value": 1},
            {"label": "Slightly Engaging", "value": 2},
            {"label": "Engaging", "value": 3},
            {"label": "Very Engaging", "value": 4},
            {"label": "Highly Engaging", "value": 5}
        ]
    },
    {
        "name": "Tone Appropriateness",
        "dataType": "CATEGORICAL",
        "description": "Assesses whether the tone matches the context and audience expectations.",
        "categories": [
            {"label": "Inappropriate Tone", "value": 1},
            {"label": "Somewhat Inappropriate", "value": 2},
            {"label": "Acceptable Tone", "value": 3},
            {"label": "Well-Matched Tone", "value": 4},
            {"label": "Perfect Tone", "value": 5}
        ]
    },
    {
        "name": "Conciseness",
        "dataType": "CATEGORICAL",
        "description": "Evaluates the efficiency of communication - saying more with fewer words.",
        "categories": [
            {"label": "Verbose/Wordy", "value": 1},
            {"label": "Somewhat Verbose", "value": 2},
            {"label": "Balanced", "value": 3},
            {"label": "Concise", "value": 4},
            {"label": "Perfectly Concise", "value": 5}
        ]
    },
    # Technical Quality Category
    {
        "name": "Structure & Organization",
        "dataType": "CATEGORICAL",
        "description": "Evaluates the logical organization and structural quality of the content.",
        "categories": [
            {"label": "Disorganized", "value": 1},
            {"label": "Basic Structure", "value": 2},
            {"label": "Well-Organized", "value": 3},
            {"label": "Excellent Structure", "value": 4},
            {"label": "Masterful Organization", "value": 5}
        ]
    },
    {
        "name": "Language Quality",
        "dataType": "CATEGORICAL",
        "description": "Assesses grammar, vocabulary usage, and overall linguistic competence.",
        "categories": [
            {"label": "Poor Language", "value": 1},
            {"label": "Fair Language", "value": 2},
            {"label": "Good Language", "value": 3},
            {"label": "Excellent Language", "value": 4},
            {"label": "Exceptional Language", "value": 5}
        ]
    },
    # Specialized Assessment Category
    {
        "name": "Critical Thinking",
        "dataType": "CATEGORICAL",
        "description": "Measures the depth of analysis, reasoning, and intellectual rigor.",
        "categories": [
            {"label": "No Critical Analysis", "value": 1},
            {"label": "Basic Analysis", "value": 2},
            {"label": "Sound Reasoning", "value": 3},
            {"label": "Strong Critical Thinking", "value": 4},
            {"label": "Exceptional Analysis", "value": 5}
        ]
    },
    {
        "name": "Evidence Support",
        "dataType": "CATEGORICAL",
        "description": "Evaluates the use and quality of supporting evidence, examples, or citations.",
        "categories": [
            {"label": "No Evidence", "value": 1},
            {"label": "Weak Evidence", "value": 2},
            {"label": "Adequate Evidence", "value": 3},
            {"label": "Strong Evidence", "value": 4},
            {"label": "Compelling Evidence", "value": 5}
        ]
    },
    {
        "name": "Innovation",
        "dataType": "CATEGORICAL",
        "description": "Assesses creativity, novel approaches, and fresh perspectives in problem-solving.",
        "categories": [
            {"label": "Conventional", "value": 1},
            {"label": "Slightly Creative", "value": 2},
            {"label": "Moderately Innovative", "value": 3},
            {"label": "Highly Innovative", "value": 4},
            {"label": "Groundbreaking", "value": 5}
        ]
    },
    # Numeric Assessment Category
    {
        "name": "Overall Quality",
        "dataType": "NUMERIC",
        "description": "General numeric assessment of overall content quality.",
        "minValue": 0.0,
        "maxValue": 10.0
    },
    {
        "name": "Performance Score",
        "dataType": "NUMERIC",
        "description": "Numeric performance evaluation score.",
        "minValue": 0,
        "maxValue": 100
    },
    # Boolean Assessment Category
    {
        "name": "Meets Requirements",
        "dataType": "BOOLEAN",
        "description": "Binary assessment of whether content meets specified requirements."
    }
]

def get_built_in_presets():
    """Return the list of built-in preset score configurations"""
    return BUILT_IN_PRESETS.copy()

def list_presets(category=None):
    """
    List available preset score configurations
    
    Args:
        category: Optional category filter (e.g., 'narrative', 'ai', 'general', 'technical', 'specialized', 'numeric', 'boolean')
    
    Returns:
        List of presets matching the filter criteria
    """
    presets = get_built_in_presets()
    
    if not category:
        return presets
    
    # Category mapping based on the preset library structure
    category_mapping = {
        'narrative': ['Narrative Coherence', 'Character Development', 'Emotional Resonance', 'Originality', 'Thematic Depth'],
        'ai': ['Helpfulness', 'Accuracy', 'Safety', 'Relevance', 'Completeness'],
        'general': ['Clarity', 'Engagement', 'Tone Appropriateness', 'Conciseness'],
        'technical': ['Structure & Organization', 'Language Quality'],
        'specialized': ['Critical Thinking', 'Evidence Support', 'Innovation'],
        'numeric': ['Overall Quality', 'Performance Score'],
        'boolean': ['Meets Requirements']
    }
    
    category_names = category_mapping.get(category.lower(), [])
    if category_names:
        return [p for p in presets if p['name'] in category_names]
    
    return presets

def format_presets_table(presets):
    """
    Format presets list as a readable table
    
    Args:
        presets: List of preset configurations
    
    Returns:
        Formatted table string
    """
    if not presets:
        return "No presets found."
    
    # Table headers
    headers = ["Name", "Type", "Categories/Range", "Description"]
    
    # Calculate column widths
    max_name = max([len(p['name']) for p in presets] + [len(headers[0])])
    max_type = max([len(p['dataType']) for p in presets] + [len(headers[1])])
    max_range = 20  # Fixed width for range/categories summary
    max_desc = max([len((p.get('description', '')[:50])) for p in presets] + [len(headers[3])])
    
    # Minimum widths
    max_name = max(max_name, 15)
    max_type = max(max_type, 10)
    max_desc = max(max_desc, 30)
    
    # Format table
    separator = f"+{'-' * (max_name + 2)}+{'-' * (max_type + 2)}+{'-' * (max_range + 2)}+{'-' * (max_desc + 2)}+"
    header_row = f"| {headers[0]:<{max_name}} | {headers[1]:<{max_type}} | {headers[2]:<{max_range}} | {headers[3]:<{max_desc}} |"
    
    table_lines = [separator, header_row, separator]
    
    for preset in presets:
        name = preset['name'][:max_name]
        data_type = preset['dataType'][:max_type]
        description = (preset.get('description', '') or 'N/A')[:max_desc]
        
        # Format range/categories summary
        if preset['dataType'] == 'CATEGORICAL' and preset.get('categories'):
            range_info = f"{len(preset['categories'])} categories"
        elif preset['dataType'] == 'NUMERIC':
            min_val = preset.get('minValue', 'N/A')
            max_val = preset.get('maxValue', 'N/A')
            range_info = f"{min_val}-{max_val}"
        elif preset['dataType'] == 'BOOLEAN':
            range_info = "True/False"
        else:
            range_info = "N/A"
        
        range_info = range_info[:max_range]
        
        row = f"| {name:<{max_name}} | {data_type:<{max_type}} | {range_info:<{max_range}} | {description:<{max_desc}} |"
        table_lines.append(row)
    
    table_lines.append(separator)
    table_lines.append(f"Total presets: {len(presets)}")
    
    return '\n'.join(table_lines)

def install_preset(preset_name, check_duplicates=True, interactive=False):
    """
    Install a preset score configuration
    
    Args:
        preset_name: Name of the preset to install
        check_duplicates: Whether to check for existing configs with the same name
        interactive: Whether to prompt for confirmation in case of duplicates
    
    Returns:
        Installation result message
    """
    # Find the preset
    presets = get_built_in_presets()
    preset = next((p for p in presets if p['name'].lower() == preset_name.lower()), None)
    
    if not preset:
        available_names = [p['name'] for p in presets]
        return f"Preset '{preset_name}' not found.\n\nAvailable presets:\n" + "\n".join(f"  - {name}" for name in available_names)
    
    # Check for duplicates if requested
    if check_duplicates:
        existing_configs = json.loads(list_score_configs())
        duplicate = next((c for c in existing_configs if c['name'].lower() == preset['name'].lower()), None)
        
        if duplicate:
            duplicate_msg = f"Score config '{preset['name']}' already exists (ID: {duplicate.get('id', 'unknown')})."
            
            if interactive:
                # In a real CLI, this would prompt the user
                # For now, we'll return a message indicating what would happen
                return f"{duplicate_msg}\n\n⚠️  Note: --allow-duplicates creates additional configs with same names, not replacements.\nTo install anyway, use: coaia fuse score-configs presets install '{preset_name}' --allow-duplicates"
            else:
                return f"{duplicate_msg}\n\n⚠️  Langfuse API does not support replacing configs.\nSkipping installation. Use --allow-duplicates to create additional config with same name."
    
    # Install the preset
    try:
        result = create_score_config(
            name=preset['name'],
            data_type=preset['dataType'],
            description=preset.get('description'),
            categories=preset.get('categories'),
            min_value=preset.get('minValue'),
            max_value=preset.get('maxValue')
        )
        
        # Check if installation was successful
        result_data = json.loads(result)
        if 'id' in result_data:
            return f"✅ Successfully installed preset '{preset['name']}' (ID: {result_data['id']})"
        else:
            return f"❌ Failed to install preset '{preset['name']}': {result}"
            
    except Exception as e:
        return f"❌ Error installing preset '{preset['name']}': {str(e)}"

def get_preset_by_name(preset_name):
    """
    Get a specific preset configuration by name
    
    Args:
        preset_name: Name of the preset to retrieve
    
    Returns:
        Preset configuration dictionary or None if not found
    """
    presets = get_built_in_presets()
    return next((p for p in presets if p['name'].lower() == preset_name.lower()), None)

def format_preset_display(preset):
    """
    Format a single preset as a detailed display
    
    Args:
        preset: Preset configuration dictionary
    
    Returns:
        Formatted display string
    """
    if not preset:
        return "Preset not found."
    
    display_lines = []
    
    # Header
    header = f"🎯 PRESET: {preset['name']}"
    display_lines.append("=" * len(header))
    display_lines.append(header)
    display_lines.append("=" * len(header))
    display_lines.append("")
    
    # Basic info
    display_lines.append("📋 CONFIGURATION:")
    display_lines.append(f"   Data Type: {preset['dataType']}")
    
    if preset.get('description'):
        display_lines.append(f"   Description: {preset['description']}")
    
    # Type-specific details
    if preset['dataType'] == 'CATEGORICAL' and preset.get('categories'):
        display_lines.append(f"   Categories: {len(preset['categories'])} options")
        display_lines.append("")
        display_lines.append("📝 CATEGORIES:")
        for i, cat in enumerate(preset['categories'], 1):
            display_lines.append(f"   {i}. {cat['label']} (value: {cat['value']})")
    
    elif preset['dataType'] == 'NUMERIC':
        if preset.get('minValue') is not None or preset.get('maxValue') is not None:
            min_val = preset.get('minValue', 'No minimum')
            max_val = preset.get('maxValue', 'No maximum')
            display_lines.append(f"   Range: {min_val} to {max_val}")
    
    elif preset['dataType'] == 'BOOLEAN':
        display_lines.append("   Values: True or False")
    
    display_lines.append("")
    
    # Installation command
    display_lines.append("🚀 INSTALLATION:")
    display_lines.append(f"   coaia fuse score-configs presets install '{preset['name']}'")
    
    return '\n'.join(display_lines)

def install_presets_interactive(preset_names=None, category=None):
    """
    Interactively install multiple presets with duplicate checking
    
    Args:
        preset_names: Optional list of specific preset names to install
        category: Optional category filter for bulk installation
    
    Returns:
        Installation results summary
    """
    # Get presets to install
    if preset_names:
        # Install specific presets
        presets_to_install = []
        for name in preset_names:
            preset = get_preset_by_name(name)
            if preset:
                presets_to_install.append(preset)
            else:
                return f"Preset '{name}' not found."
    elif category:
        # Install by category
        presets_to_install = list_presets(category)
        if not presets_to_install:
            return f"No presets found for category '{category}'."
    else:
        # Install all presets (with confirmation)
        presets_to_install = get_built_in_presets()
    
    # Check for duplicates
    existing_configs = json.loads(list_score_configs())
    existing_names = {c['name'].lower(): c for c in existing_configs}
    
    duplicates = []
    new_installs = []
    
    for preset in presets_to_install:
        if preset['name'].lower() in existing_names:
            duplicates.append({
                'preset': preset,
                'existing': existing_names[preset['name'].lower()]
            })
        else:
            new_installs.append(preset)
    
    # Build results
    results = []
    
    if duplicates:
        results.append(f"⚠️  Found {len(duplicates)} duplicate(s):")
        for dup in duplicates:
            results.append(f"   - '{dup['preset']['name']}' (existing ID: {dup['existing'].get('id', 'unknown')})")
        results.append("")
    
    if new_installs:
        results.append(f"✅ Installing {len(new_installs)} new preset(s):")
        
        installed_count = 0
        failed_count = 0
        
        for preset in new_installs:
            try:
                result = create_score_config(
                    name=preset['name'],
                    data_type=preset['dataType'],
                    description=preset.get('description'),
                    categories=preset.get('categories'),
                    min_value=preset.get('minValue'),
                    max_value=preset.get('maxValue')
                )
                
                result_data = json.loads(result)
                if 'id' in result_data:
                    results.append(f"   ✅ '{preset['name']}' (ID: {result_data['id']})")
                    installed_count += 1
                else:
                    results.append(f"   ❌ '{preset['name']}' - Installation failed")
                    failed_count += 1
            except Exception as e:
                results.append(f"   ❌ '{preset['name']}' - Error: {str(e)}")
                failed_count += 1
        
        results.append("")
        results.append(f"📊 SUMMARY: {installed_count} installed, {failed_count} failed, {len(duplicates)} skipped (duplicates)")
    else:
        if duplicates:
            results.append("No new presets to install (all already exist).")
        else:
            results.append("No presets selected for installation.")
    
    return "\n".join(results)

def export_score_configs(output_file=None, include_metadata=True):
    """
    Export all score configs to JSON format
    
    Args:
        output_file: Optional file path to save the export
        include_metadata: Whether to include Langfuse-specific metadata (id, timestamps, etc.)
    
    Returns:
        JSON string of exported score configs
    """
    configs_data = list_score_configs()
    configs = json.loads(configs_data)
    
    # Clean up the data for export
    exported_configs = []
    for config in configs:
        exported_config = {
            "name": config.get("name"),
            "dataType": config.get("dataType"),
            "description": config.get("description"),
            "categories": config.get("categories"),
            "minValue": config.get("minValue"),
            "maxValue": config.get("maxValue")
        }
        
        # Include metadata if requested
        if include_metadata:
            exported_config["metadata"] = {
                "id": config.get("id"),
                "createdAt": config.get("createdAt"),
                "updatedAt": config.get("updatedAt"),
                "projectId": config.get("projectId"),
                "isArchived": config.get("isArchived")
            }
        
        exported_configs.append(exported_config)
    
    # Create export structure
    export_data = {
        "version": "1.0",
        "exportedAt": datetime.datetime.utcnow().isoformat() + 'Z',
        "totalConfigs": len(exported_configs),
        "configs": exported_configs
    }
    
    result_json = json.dumps(export_data, indent=2)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(result_json)
    
    return result_json

def import_score_configs(import_file, show_guidance=True, allow_duplicates=False, selected_configs=None):
    """
    Import score configs from JSON file
    
    Args:
        import_file: Path to JSON file containing score configs
        show_guidance: Whether to show guidance about handling duplicates (formerly 'interactive')
        allow_duplicates: Whether to create new configs even if names already exist (formerly 'force')
                         WARNING: This creates additional configs with same names, not replacements!
        selected_configs: Optional list of config names to import
    
    Returns:
        Import results summary
    """
    try:
        with open(import_file, 'r') as f:
            import_data = json.load(f)
    except FileNotFoundError:
        return f"❌ Import file '{import_file}' not found."
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON in import file: {str(e)}"
    
    # Parse import data structure
    if isinstance(import_data, dict) and 'configs' in import_data:
        # ScoreConfigExport format
        configs_to_import = import_data['configs']
        import_metadata = {
            'version': import_data.get('version', 'unknown'),
            'exported_at': import_data.get('exportedAt', 'unknown'),
            'total_configs': import_data.get('totalConfigs', len(configs_to_import))
        }
    elif isinstance(import_data, list):
        # Direct list of configs
        configs_to_import = import_data
        import_metadata = {
            'version': 'unknown',
            'exported_at': 'unknown', 
            'total_configs': len(configs_to_import)
        }
    else:
        return "❌ Invalid import file format. Expected export file with 'configs' array or direct config array."
    
    if not configs_to_import:
        return "❌ No score configs found in import file."
    
    # Convert to ScoreConfig objects for validation
    try:
        parsed_configs = []
        for i, config_data in enumerate(configs_to_import):
            try:
                score_config = ScoreConfig.from_dict(config_data)
                parsed_configs.append(score_config)
            except Exception as e:
                return f"❌ Invalid config at index {i}: {str(e)}"
    except Exception as e:
        return f"❌ Error parsing configs: {str(e)}"
    
    # Filter configs if specific ones were selected
    if selected_configs:
        selected_names = set(name.lower() for name in selected_configs)
        filtered_configs = [c for c in parsed_configs if c.name.lower() in selected_names]
        not_found = [name for name in selected_configs if name.lower() not in {c.name.lower() for c in parsed_configs}]
        if not_found:
            return f"❌ Configs not found in import file: {', '.join(not_found)}"
        configs_to_process = filtered_configs
    else:
        configs_to_process = parsed_configs
    
    # Check for duplicates with existing configs
    existing_configs = json.loads(list_score_configs())
    existing_names = {c['name'].lower(): c for c in existing_configs}
    
    duplicates = []
    new_imports = []
    
    for config in configs_to_process:
        if config.name.lower() in existing_names:
            duplicates.append({
                'import_config': config,
                'existing': existing_names[config.name.lower()]
            })
        else:
            new_imports.append(config)
    
    # Build results
    results = []
    
    # Show import file info
    results.append(f"📁 IMPORT FILE: {import_file}")
    results.append(f"   Version: {import_metadata['version']}")
    results.append(f"   Exported: {import_metadata['exported_at']}")
    results.append(f"   Total configs in file: {import_metadata['total_configs']}")
    results.append("")
    
    if duplicates and not allow_duplicates:
        results.append(f"⚠️  Found {len(duplicates)} duplicate name(s):")
        for dup in duplicates:
            results.append(f"   - '{dup['import_config'].name}' (existing ID: {dup['existing'].get('id', 'unknown')})")
        results.append("")
        
        if show_guidance and not selected_configs:
            results.append("⚠️  IMPORTANT: Langfuse API does NOT support replacing/updating score configs!")
            results.append("")
            results.append("Available options:")
            results.append("   1. Skip duplicates (default) - import only new configs")
            results.append("   2. Create duplicates (--allow-duplicates) - creates new configs with same names")
            results.append("   3. Select specific configs (--select) to import only certain configs")
            results.append("")
            results.append("⚠️  Using --allow-duplicates will create ADDITIONAL configs with the same names,")
            results.append("    not replace existing ones. This may cause confusion in your Langfuse project.")
            results.append("")
            results.append("Use --allow-duplicates to proceed anyway, or --select to specify configs to import.")
    
    if new_imports or allow_duplicates:
        configs_to_create = new_imports if not allow_duplicates else configs_to_process
        
        if allow_duplicates and duplicates:
            results.append("⚠️  WARNING: Creating duplicate configs (same names, different IDs)!")
            results.append("")
        
        results.append(f"✅ Importing {len(configs_to_create)} config(s):")
        
        imported_count = 0
        failed_count = 0
        
        for config in configs_to_create:
            try:
                result = create_score_config(
                    name=config.name,
                    data_type=config.data_type,
                    description=config.description,
                    categories=None if not config.categories else [
                        {"label": cat.label, "value": cat.value} for cat in config.categories
                    ],
                    min_value=config.min_value,
                    max_value=config.max_value
                )
                
                result_data = json.loads(result)
                if 'id' in result_data:
                    results.append(f"   ✅ '{config.name}' (ID: {result_data['id']})")
                    imported_count += 1
                else:
                    results.append(f"   ❌ '{config.name}' - Import failed")
                    failed_count += 1
            except Exception as e:
                results.append(f"   ❌ '{config.name}' - Error: {str(e)}")
                failed_count += 1
        
        results.append("")
        results.append(f"📊 SUMMARY: {imported_count} imported, {failed_count} failed, {len(duplicates)} skipped (duplicates)")
    else:
        if duplicates:
            results.append("No new configs to import (all names already exist).")
            results.append("Use --allow-duplicates to create additional configs with the same names,")
            results.append("or --select to choose specific configs to import.")
        else:
            results.append("No configs selected for import.")
    
    return "\n".join(results)

def import_score_configs_legacy(import_file, interactive=True, force=False, selected_configs=None):
    """
    DEPRECATED: Legacy wrapper for backwards compatibility.
    Use import_score_configs() with new parameter names instead.
    
    This function maps old parameter names to new ones:
    - interactive -> show_guidance (but interactive mode was never actually implemented)
    - force -> allow_duplicates (but force doesn't replace, it creates duplicates!)
    """
    import warnings
    warnings.warn(
        "import_score_configs_legacy() is deprecated. "
        "Use import_score_configs() with show_guidance/allow_duplicates parameters. "
        "Note: 'force' creates duplicates, doesn't replace configs!",
        DeprecationWarning,
        stacklevel=2
    )
    
    return import_score_configs(
        import_file=import_file,
        show_guidance=interactive,
        allow_duplicates=force,
        selected_configs=selected_configs
    )

def format_import_preview(import_file):
    """
    Preview what would be imported from a JSON file without actually importing
    
    Args:
        import_file: Path to JSON file containing score configs
    
    Returns:
        Preview summary string
    """
    try:
        with open(import_file, 'r') as f:
            import_data = json.load(f)
    except FileNotFoundError:
        return f"❌ Import file '{import_file}' not found."
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON in import file: {str(e)}"
    
    # Parse import data structure
    if isinstance(import_data, dict) and 'configs' in import_data:
        configs_to_import = import_data['configs']
        import_metadata = {
            'version': import_data.get('version', 'unknown'),
            'exported_at': import_data.get('exportedAt', 'unknown'),
            'total_configs': import_data.get('totalConfigs', len(configs_to_import))
        }
    elif isinstance(import_data, list):
        configs_to_import = import_data
        import_metadata = {
            'version': 'unknown',
            'exported_at': 'unknown',
            'total_configs': len(configs_to_import)
        }
    else:
        return "❌ Invalid import file format."
    
    if not configs_to_import:
        return "❌ No score configs found in import file."
    
    # Build preview
    results = []
    results.append(f"📁 IMPORT PREVIEW: {import_file}")
    results.append(f"   Version: {import_metadata['version']}")
    results.append(f"   Exported: {import_metadata['exported_at']}")
    results.append(f"   Total configs: {import_metadata['total_configs']}")
    results.append("")
    
    # Preview table of configs
    results.append("📋 CONFIGS TO IMPORT:")
    headers = ["Name", "Type", "Categories/Range", "Description"]
    
    # Calculate column widths
    max_name = max([len(c.get('name', '')) for c in configs_to_import] + [len(headers[0])])
    max_type = max([len(c.get('dataType', '')) for c in configs_to_import] + [len(headers[1])])
    max_range = 20  # Fixed width
    max_desc = max([len((c.get('description', '') or '')[:40]) for c in configs_to_import] + [len(headers[3])])
    
    # Minimum widths
    max_name = max(max_name, 15)
    max_type = max(max_type, 10)
    max_desc = max(max_desc, 25)
    
    # Format table
    separator = f"+{'-' * (max_name + 2)}+{'-' * (max_type + 2)}+{'-' * (max_range + 2)}+{'-' * (max_desc + 2)}+"
    header_row = f"| {headers[0]:<{max_name}} | {headers[1]:<{max_type}} | {headers[2]:<{max_range}} | {headers[3]:<{max_desc}} |"
    
    results.append(separator)
    results.append(header_row)
    results.append(separator)
    
    for config in configs_to_import:
        name = (config.get('name', '') or 'N/A')[:max_name]
        data_type = (config.get('dataType', '') or 'N/A')[:max_type]
        description = (config.get('description', '') or 'N/A')[:max_desc]
        
        # Format range/categories summary
        if config.get('dataType') == 'CATEGORICAL' and config.get('categories'):
            range_info = f"{len(config['categories'])} categories"
        elif config.get('dataType') == 'NUMERIC':
            min_val = config.get('minValue', 'N/A')
            max_val = config.get('maxValue', 'N/A')
            range_info = f"{min_val}-{max_val}"
        elif config.get('dataType') == 'BOOLEAN':
            range_info = "True/False"
        else:
            range_info = "N/A"
        
        range_info = range_info[:max_range]
        
        row = f"| {name:<{max_name}} | {data_type:<{max_type}} | {range_info:<{max_range}} | {description:<{max_desc}} |"
        results.append(row)
    
    results.append(separator)
    results.append("")
    
    # Check for potential duplicates
    existing_configs = json.loads(list_score_configs())
    existing_names = {c['name'].lower() for c in existing_configs}
    
    potential_duplicates = [c for c in configs_to_import if c.get('name', '').lower() in existing_names]
    
    if potential_duplicates:
        results.append(f"⚠️  POTENTIAL DUPLICATES ({len(potential_duplicates)}):")
        for config in potential_duplicates:
            results.append(f"   - '{config.get('name', 'unknown')}'")
        results.append("")
        results.append("Use --force to replace duplicates during import.")
    else:
        results.append("✅ No duplicate conflicts detected.")
    
    return "\n".join(results)

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

def list_traces(include_observations=False, session_id=None):
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base_url = c['langfuse_base_url']

    traces_url = f"{base_url}/api/public/traces"

    # Add session_id filter if provided
    params = {}
    if session_id:
        params['sessionId'] = session_id

    r = requests.get(traces_url, auth=auth, params=params)

    if r.status_code != 200:
        return r.text # Return error if traces cannot be fetched

    traces_data = json.loads(r.text)

    # Handle nested structure from Langfuse API
    if isinstance(traces_data, dict) and 'data' in traces_data:
        traces = traces_data['data']
    else:
        traces = traces_data
        
    if include_observations:
        observations_url = f"{base_url}/api/public/observations"
        for trace in traces:
            trace_id = trace.get('id')
            if trace_id:
                # Fetch observations for each trace
                obs_r = requests.get(f"{observations_url}?traceId={trace_id}", auth=auth)
                if obs_r.status_code == 200:
                    obs_data = json.loads(obs_r.text)
                    if isinstance(obs_data, dict) and 'data' in obs_data:
                        trace['observations'] = obs_data['data']
                    else:
                        trace['observations'] = obs_data
                else:
                    trace['observations'] = [] # No observations or error fetching
            else:
                trace['observations'] = [] # No trace ID
                
    return json.dumps(traces, indent=2)

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


# ============================================================================
# Project-Aware Smart Caching System for Score Configs (Phase 2)
# ============================================================================

def get_current_project_info():
    """Get current project ID and name from Langfuse API"""
    try:
        projects_json = list_projects()
        response = json.loads(projects_json)

        # Handle both {"data": [...]} and direct array formats
        projects = response.get('data', response) if isinstance(response, dict) else response

        # Return the first project (assumes single project per API key)
        if projects and isinstance(projects, list) and len(projects) > 0:
            project = projects[0]
            return {
                'id': project.get('id'),
                'name': project.get('name', 'unknown')
            }
        else:
            return None
    except Exception as e:
        print(f"Warning: Could not get project info: {e}")
        return None


def get_project_cache_path(project_id):
    """Generate project-specific cache file path with security validation"""
    import re
    
    # Sanitize project_id to prevent path traversal attacks
    if not project_id or not isinstance(project_id, str):
        raise ValueError("Project ID must be a non-empty string")
    
    # Check for path traversal attempts before sanitization
    if '..' in project_id or '/' in project_id or '\\' in project_id:
        raise ValueError(f"Project ID contains path traversal characters: {project_id}")
    
    # Remove dangerous characters and path components
    sanitized_id = re.sub(r'[^a-zA-Z0-9_-]', '_', project_id.strip())
    
    # Prevent empty or dangerous names after sanitization
    if not sanitized_id or sanitized_id in ['.', '..', '_', '__']:
        raise ValueError(f"Invalid project ID after sanitization: {project_id}")
    
    # Limit length to prevent filesystem issues
    if len(sanitized_id) > 100:
        sanitized_id = sanitized_id[:100]
    
    cache_dir = Path.home() / '.coaia' / 'score-configs'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f'{sanitized_id}.json'


def is_cache_stale(cached_config, max_age_hours=24):
    """Check if cached config is stale based on age"""
    try:
        cached_at = datetime.datetime.fromisoformat(cached_config.get('cached_at', '').replace('Z', '+00:00'))
        age_hours = (datetime.datetime.now(datetime.timezone.utc) - cached_at).total_seconds() / 3600
        return age_hours > max_age_hours
    except Exception:
        return True  # Treat invalid timestamps as stale


def load_project_cache(project_id):
    """Load existing cache file for a project with validation"""
    cache_path = get_project_cache_path(project_id)
    
    try:
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            # Validate cache structure to prevent malformed data attacks
            if not isinstance(data, dict):
                print(f"Warning: Invalid cache structure (not dict) in {cache_path}")
                return None
            
            # Validate required fields and types
            if 'configs' in data and not isinstance(data['configs'], list):
                print(f"Warning: Invalid configs field (not list) in {cache_path}")
                return None
            
            # Validate each config entry
            if 'configs' in data:
                for i, config in enumerate(data['configs']):
                    if not isinstance(config, dict):
                        print(f"Warning: Invalid config entry {i} (not dict) in {cache_path}")
                        return None
                    
                    # Validate required config fields
                    if 'name' not in config and 'id' not in config:
                        print(f"Warning: Config entry {i} missing name/id in {cache_path}")
                        return None
            
            return data
        else:
            return None
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in cache {cache_path}: {e}")
        return None
    except Exception as e:
        print(f"Warning: Could not load cache from {cache_path}: {e}")
        return None


def save_project_cache(project_id, cache_data):
    """Save cache data to project-specific cache file"""
    cache_path = get_project_cache_path(project_id)
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Could not save cache to {cache_path}: {e}")
        return False


def cache_score_config(cache_path, config):
    """Store a single config in the project cache with atomic writes"""
    import tempfile
    import shutil
    
    try:
        # Validate input config
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        
        if not config.get('name') and not config.get('id'):
            raise ValueError("Config must have either name or id")
        
        # Load existing cache with validation
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            # Validate loaded data structure
            if not isinstance(cache_data, dict):
                print(f"Warning: Corrupted cache file {cache_path}, reinitializing")
                cache_data = {'configs': []}
            elif 'configs' not in cache_data or not isinstance(cache_data['configs'], list):
                print(f"Warning: Invalid cache structure in {cache_path}, reinitializing")
                cache_data = {'configs': []}
        else:
            cache_data = {'configs': []}
        
        # Add cached_at timestamp to config (create copy to avoid modifying input)
        config_copy = config.copy()
        config_copy['cached_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Update or add config in cache
        existing_index = None
        for i, cached_config in enumerate(cache_data['configs']):
            if (cached_config.get('id') and cached_config.get('id') == config_copy.get('id')) or \
               (cached_config.get('name') and cached_config.get('name') == config_copy.get('name')):
                existing_index = i
                break
        
        if existing_index is not None:
            cache_data['configs'][existing_index] = config_copy
        else:
            cache_data['configs'].append(config_copy)
        
        # Update cache metadata
        cache_data['last_sync'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Atomic write using temporary file to prevent corruption
        cache_dir = cache_path.parent
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tmp', dir=cache_dir, delete=False) as tmp_file:
            json.dump(cache_data, tmp_file, indent=2)
            tmp_file.flush()
            # Ensure data is written to disk before rename
            import os
            os.fsync(tmp_file.fileno())
            tmp_path = tmp_file.name
        
        # Atomic rename (only works if tmp and target on same filesystem)
        try:
            shutil.move(tmp_path, cache_path)
        except Exception as rename_error:
            # Fallback: copy and remove (less atomic but more compatible)
            try:
                shutil.copy2(tmp_path, cache_path)
                os.unlink(tmp_path)
            except Exception as fallback_error:
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                raise fallback_error
        
        return True
    except Exception as e:
        print(f"Warning: Could not cache config: {e}")
        return False


def get_config_with_auto_refresh(config_name_or_id):
    """
    Smart cache-first retrieval with transparent auto-refresh.
    Returns config data with automatic cache management.
    
    Args:
        config_name_or_id: Either config name (string) or config ID
        
    Returns:
        dict: Config data from cache or API, or None if not found
    """
    # Get current project info
    project_info = get_current_project_info()
    if not project_info:
        print("Warning: Could not determine current project, falling back to API")
        return _fetch_config_from_api(config_name_or_id)
    
    project_id = project_info['id']
    project_name = project_info['name']
    
    # Load project cache
    cache_data = load_project_cache(project_id)
    
    # Search cache first if available
    if cache_data:
        for cached_config in cache_data.get('configs', []):
            # Match by ID or name
            if (cached_config.get('id') == config_name_or_id or 
                cached_config.get('name') == config_name_or_id):
                
                # Check if cache is stale
                if not is_cache_stale(cached_config):
                    print(f"Cache hit for config '{config_name_or_id}' in project '{project_name}'")
                    return cached_config
                else:
                    print(f"Cache stale for config '{config_name_or_id}', refreshing from API")
                    break
    
    # Cache miss or stale - fetch from API
    print(f"Fetching config '{config_name_or_id}' from API for project '{project_name}'")
    
    # Try to find config by name first (list all configs)
    try:
        all_configs_json = list_score_configs()
        all_configs = json.loads(all_configs_json)
        
        target_config = None
        for config in all_configs:
            if config.get('id') == config_name_or_id or config.get('name') == config_name_or_id:
                target_config = config
                break
        
        if not target_config:
            print(f"Config '{config_name_or_id}' not found")
            return None
        
        # Initialize cache structure if needed
        if not cache_data:
            cache_data = {
                'project_id': project_id,
                'project_name': project_name,
                'last_sync': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'configs': []
            }
        
        # Add to cache
        cache_path = get_project_cache_path(project_id)
        if cache_score_config(cache_path, target_config):
            print(f"Cached config '{config_name_or_id}' for project '{project_name}'")
        
        return target_config
        
    except Exception as e:
        print(f"Error fetching config '{config_name_or_id}': {e}")
        return None


def _fetch_config_from_api(config_name_or_id):
    """Fallback function to fetch config directly from API without caching"""
    try:
        # First try to get by ID if it looks like an ID
        if isinstance(config_name_or_id, str) and (len(config_name_or_id) > 20 or config_name_or_id.startswith('cm')):
            config_json = get_score_config(config_name_or_id)
            return json.loads(config_json)
        
        # Otherwise search by name in all configs
        all_configs_json = list_score_configs()
        all_configs = json.loads(all_configs_json)
        
        for config in all_configs:
            if config.get('name') == config_name_or_id:
                return config
                
        return None
    except Exception as e:
        print(f"Error fetching config from API: {e}")
        return None


def validate_score_value(config, value):
    """
    Validate a score value against its configuration constraints.
    
    Args:
        config: Score config dictionary from API
        value: Value to validate (can be string, int, float, or bool)
        
    Returns:
        tuple: (is_valid: bool, processed_value: any, error_message: str)
    """
    if not config:
        return False, None, "Config not found"
    
    data_type = config.get('dataType', '').upper()
    
    if data_type == 'BOOLEAN':
        # Accept various boolean representations
        if isinstance(value, bool):
            return True, value, None
        elif isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True, True, None
            elif value.lower() in ['false', '0', 'no', 'off']:
                return True, False, None
            else:
                return False, None, f"Invalid boolean value '{value}'. Use true/false, 1/0, yes/no, or on/off"
        elif isinstance(value, (int, float)):
            if value in [0, 1]:
                return True, bool(value), None
            else:
                return False, None, f"Invalid boolean value '{value}'. Use 1 for true or 0 for false"
        else:
            return False, None, f"Invalid boolean value '{value}'. Use true/false, 1/0, yes/no, or on/off"
    
    elif data_type == 'CATEGORICAL':
        categories = config.get('categories', [])
        if not categories:
            return False, None, "No categories defined for categorical score"
        
        # Convert value to appropriate type for comparison
        try:
            # Try to convert to int/float first
            if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                if '.' in value:
                    numeric_value = float(value)
                else:
                    numeric_value = int(value)
            else:
                numeric_value = value
        except:
            numeric_value = value
        
        # Check if value matches any category value or label
        valid_values = []
        valid_labels = []
        for category in categories:
            cat_value = category.get('value')
            cat_label = category.get('label', '')
            valid_values.append(cat_value)
            valid_labels.append(cat_label)
            
            # Match by value (exact)
            if cat_value == numeric_value or cat_value == value:
                return True, cat_value, None
            
            # Match by label (case-insensitive)
            if isinstance(value, str) and cat_label.lower() == value.lower():
                return True, cat_value, None
        
        # Format error message with valid options
        valid_options = []
        for category in categories:
            valid_options.append(f"'{category.get('label')}' ({category.get('value')})")
        
        return False, None, f"Invalid categorical value '{value}'. Valid options: {', '.join(valid_options)}"
    
    elif data_type == 'NUMERIC':
        # Convert to numeric with robust edge case handling
        try:
            if isinstance(value, (int, float)):
                numeric_value = float(value)
            elif isinstance(value, str):
                # Strip whitespace and validate format
                value = value.strip()
                if not value:
                    return False, None, "Numeric value cannot be empty"
                
                # Check for invalid patterns
                if value in ['inf', '-inf', 'nan', '+inf']:
                    return False, None, f"Invalid numeric value '{value}'. Infinity and NaN not allowed"
                
                # Handle scientific notation safely
                if 'e' in value.lower():
                    try:
                        numeric_value = float(value)
                        # Check if result is finite
                        if not (numeric_value == numeric_value and abs(numeric_value) != float('inf')):
                            return False, None, f"Numeric value '{value}' results in invalid number"
                    except (ValueError, OverflowError):
                        return False, None, f"Invalid numeric value '{value}'. Invalid scientific notation"
                else:
                    # Regular numeric parsing with overflow protection
                    try:
                        if '.' in value:
                            numeric_value = float(value)
                            # Check for overflow/underflow
                            if abs(numeric_value) > 1e308:
                                return False, None, f"Numeric value '{value}' is too large"
                        else:
                            # Try int first, fallback to float for large numbers
                            try:
                                int_value = int(value)
                                # Check for extremely large integers that might cause issues
                                if abs(int_value) > 9223372036854775807:  # sys.maxsize on 64-bit
                                    numeric_value = float(int_value)
                                else:
                                    numeric_value = int_value
                            except ValueError:
                                numeric_value = float(value)
                    except (ValueError, OverflowError):
                        return False, None, f"Invalid numeric value '{value}'. Must be a valid number"
                
                # Final validation - ensure result is finite
                if isinstance(numeric_value, float) and not (numeric_value == numeric_value and abs(numeric_value) != float('inf')):
                    return False, None, f"Numeric value '{value}' results in invalid number"
                    
            else:
                # Try to convert other types
                numeric_value = float(value)
                
        except (ValueError, TypeError, OverflowError) as e:
            return False, None, f"Invalid numeric value '{value}'. Must be a valid number"
        
        # Check min/max constraints
        min_value = config.get('minValue')
        max_value = config.get('maxValue')
        
        if min_value is not None and numeric_value < min_value:
            range_info = f"minimum: {min_value}"
            if max_value is not None:
                range_info = f"range: {min_value} to {max_value}"
            return False, None, f"Value {numeric_value} is below minimum. Valid {range_info}"
        
        if max_value is not None and numeric_value > max_value:
            range_info = f"maximum: {max_value}"
            if min_value is not None:
                range_info = f"range: {min_value} to {max_value}"
            return False, None, f"Value {numeric_value} is above maximum. Valid {range_info}"
        
        return True, numeric_value, None
    
    else:
        return False, None, f"Unknown data type '{data_type}'. Expected BOOLEAN, CATEGORICAL, or NUMERIC"


def apply_score_config(config_name_or_id, target_type, target_id, value, observation_id=None, comment=None):
    """
    Apply a score using a score configuration with value validation.
    
    Args:
        config_name_or_id: Name or ID of the score config
        target_type: "trace" or "session"
        target_id: ID of the trace or session
        value: Score value to apply
        observation_id: Optional observation ID for trace scores
        comment: Optional comment for the score
        
    Returns:
        str: API response or error message
    """
    # Get the config using smart caching
    config = get_config_with_auto_refresh(config_name_or_id)
    if not config:
        return f"Error: Score config '{config_name_or_id}' not found"
    
    # Validate the value
    is_valid, processed_value, error_message = validate_score_value(config, value)
    if not is_valid:
        return f"Error: {error_message}"
    
    # Apply the score using the existing function
    try:
        result = create_score_for_target(
            target_type=target_type,
            target_id=target_id,
            score_id=None,  # Use config instead
            score_value=processed_value,
            score_name=None,  # Use config instead
            observation_id=observation_id,
            config_id=config['id'],
            comment=comment
        )
        
        config_name = config.get('name', config_name_or_id)
        target_desc = f"{target_type} '{target_id}'"
        if observation_id:
            target_desc += f" (observation '{observation_id}')"
        
        print(f"Applied score config '{config_name}' with value {processed_value} to {target_desc}")
        return result
        
    except Exception as e:
        return f"Error applying score: {e}"


def list_available_configs(category=None, cached_only=False):
    """
    List available score configurations with optional filtering.
    
    Args:
        category: Optional category filter (matches description content)
        cached_only: If True, only return cached configs
        
    Returns:
        list: List of score config dictionaries
    """
    if cached_only:
        # Get from cache only
        project_info = get_current_project_info()
        if not project_info:
            return []
        
        cache_data = load_project_cache(project_info['id'])
        if not cache_data:
            return []
        
        configs = cache_data.get('configs', [])
    else:
        # Get from API
        try:
            configs_json = list_score_configs()
            configs = json.loads(configs_json)
        except Exception as e:
            print(f"Error fetching configs: {e}")
            return []
    
    # Apply category filter if specified
    if category:
        filtered_configs = []
        for config in configs:
            description = config.get('description', '').lower()
            config_name = config.get('name', '').lower()
            if category.lower() in description or category.lower() in config_name:
                filtered_configs.append(config)
        configs = filtered_configs
    
    return configs

def get_trace_with_observations(trace_id):
    """Get a specific trace with all its observations"""
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base_url = c['langfuse_base_url']

    # Get the trace
    trace_url = f"{base_url}/api/public/traces/{trace_id}"
    r = requests.get(trace_url, auth=auth)

    if r.status_code != 200:
        return json.dumps({"error": f"Trace not found: {r.text}"}, indent=2)

    trace = json.loads(r.text)

    # Get observations for this trace
    observations_url = f"{base_url}/api/public/observations"
    obs_r = requests.get(f"{observations_url}?traceId={trace_id}", auth=auth)

    if obs_r.status_code == 200:
        obs_data = json.loads(obs_r.text)
        if isinstance(obs_data, dict) and 'data' in obs_data:
            trace['observations'] = obs_data['data']
        else:
            trace['observations'] = obs_data
    else:
        trace['observations'] = []

    return json.dumps(trace, indent=2)

def format_trace_tree(trace_json):
    """Format a trace with its observations as an ASCII tree"""
    try:
        trace = json.loads(trace_json) if isinstance(trace_json, str) else trace_json

        if 'error' in trace:
            return f"Error: {trace['error']}"

        # Tree symbols
        BRANCH = "├── "
        LAST_BRANCH = "└── "
        VERTICAL = "│   "
        SPACE = "    "

        lines = []

        # Trace header with key info
        trace_name = trace.get('name', 'Unnamed')
        trace_id = trace.get('id', 'N/A')
        user_id = trace.get('userId', 'N/A')
        session_id = trace.get('sessionId', 'N/A')
        timestamp = trace.get('timestamp', 'N/A')[:19] if trace.get('timestamp') else 'N/A'

        lines.append(f"🔗 Trace: {trace_name}")
        lines.append(f"├── 🆔 ID: {trace_id}")
        lines.append(f"├── 👤 User: {user_id}")
        lines.append(f"├── 🔗 Session: {session_id}")
        lines.append(f"├── ⏰ Time: {timestamp}")

        # Add metadata if present
        metadata = trace.get('metadata', {})
        if metadata:
            lines.append(f"├── 📋 Metadata:")
            metadata_items = list(metadata.items())
            for i, (key, value) in enumerate(metadata_items):
                is_last_meta = i == len(metadata_items) - 1
                prefix = LAST_BRANCH if is_last_meta else BRANCH
                lines.append(f"│   {prefix}{key}: {value}")

        # Process observations
        observations = trace.get('observations', [])
        if not observations:
            lines.append(f"└── 📝 No observations")
            return '\n'.join(lines)

        lines.append(f"└── 📝 Observations ({len(observations)}):")

        # Build observation hierarchy
        obs_by_id = {obs.get('id'): obs for obs in observations}
        root_observations = [obs for obs in observations if not obs.get('parentObservationId')]

        def add_observation_tree(obs_list, prefix="    ", is_last_group=True):
            for i, obs in enumerate(obs_list):
                is_last = i == len(obs_list) - 1
                obs_name = obs.get('name', f"Observation {obs.get('id', 'Unknown')[:8]}")
                obs_type = obs.get('type', 'unknown').upper()
                obs_status = obs.get('level', 'N/A')
                obs_time = obs.get('startTime', 'N/A')[:19] if obs.get('startTime') else 'N/A'

                # Choose symbol
                if is_last:
                    symbol = LAST_BRANCH
                    next_prefix = prefix + SPACE
                else:
                    symbol = BRANCH
                    next_prefix = prefix + VERTICAL

                obs_id_full = obs.get('id', 'N/A')

                # Add beautiful glyphs for different observation types
                type_glyphs = {
                    'SPAN': '🔗',        # Link/chain for spans
                    'GENERATION': '🤖',   # Robot for AI generation
                    'EVENT': '⚡',        # Lightning for events
                    'SCORE': '📊',        # Chart for scoring
                    'TRACE': '🛤️',        # Railway track for traces
                    'DEFAULT': '📦',      # Package for default/unknown
                }

                glyph = type_glyphs.get(obs_type, type_glyphs['DEFAULT'])
                lines.append(f"{prefix}{symbol}{glyph} [{obs_type}] {obs_name} ({obs_id_full})")
                lines.append(f"{next_prefix}├── ⏰ {obs_time}")
                if obs_status != 'N/A':
                    lines.append(f"{next_prefix}├── 📊 {obs_status}")

                # Add input/output if present with proper line formatting
                if obs.get('input'):
                    input_text = str(obs['input']).replace('\n', ' ').replace('\r', ' ')
                    if len(input_text) > 90:
                        input_text = input_text[:90] + "..."
                    lines.append(f"{next_prefix}├── 📥 Input: {input_text}")

                if obs.get('output'):
                    output_text = str(obs['output']).replace('\n', ' ').replace('\r', ' ')
                    if len(output_text) > 90:
                        output_text = output_text[:90] + "..."
                    lines.append(f"{next_prefix}├── 📤 Output: {output_text}")

                # Find child observations
                children = [child for child in observations if child.get('parentObservationId') == obs.get('id')]
                if children:
                    lines.append(f"{next_prefix}└── 🌿 Children ({len(children)}):")
                    add_observation_tree(children, next_prefix + "    ", True)
                else:
                    # Remove the last ├── and make it └── for better formatting
                    if lines[-1].startswith(next_prefix + "├──"):
                        lines[-1] = lines[-1].replace("├──", "└──", 1)

        if root_observations:
            add_observation_tree(root_observations)
        else:
            lines.append("    └── (No root observations found)")

        return '\n'.join(lines)

    except Exception as e:
        return f"Error formatting trace tree: {str(e)}\n\nRaw JSON:\n{trace_json}"

def get_observation(observation_id):
    """
    Get a specific observation by ID from Langfuse

    Args:
        observation_id: Unique identifier of the observation

    Returns:
        JSON string with observation details or error message
    """
    c = read_config()
    auth = HTTPBasicAuth(c['langfuse_public_key'], c['langfuse_secret_key'])
    base_url = c['langfuse_base_url']

    url = f"{base_url}/api/public/observations/{observation_id}"
    r = requests.get(url, auth=auth)

    if r.status_code != 200:
        error_msg = f"Failed to retrieve observation {observation_id}: {r.status_code}"
        try:
            error_detail = r.json()
            error_msg += f"\nDetails: {json.dumps(error_detail, indent=2)}"
        except:
            error_msg += f"\n{r.text}"
        return json.dumps({"error": error_msg}, indent=2)

    return r.text

def format_observation_display(obs_json):
    """
    Format a single observation for display with tree structure

    Args:
        obs_json: JSON string or dict containing observation data

    Returns:
        Formatted string with observation details
    """
    try:
        obs = json.loads(obs_json) if isinstance(obs_json, str) else obs_json

        if 'error' in obs:
            return f"Error: {obs['error']}"

        # Type glyphs for different observation types
        type_glyphs = {
            'SPAN': '🔗',
            'GENERATION': '🤖',
            'EVENT': '⚡',
            'DEFAULT': '📦'
        }

        obs_type = obs.get('type', 'UNKNOWN').upper()
        glyph = type_glyphs.get(obs_type, type_glyphs['DEFAULT'])

        # Format timestamp
        timestamp = obs.get('timestamp', 'N/A')
        if timestamp and timestamp != 'N/A':
            timestamp = timestamp[:19]

        # Start building output
        lines = []
        lines.append(f"{glyph} Observation: {obs.get('name', 'Unnamed')}")
        lines.append(f"├── 🆔 ID: {obs.get('id', 'N/A')}")
        lines.append(f"├── 📝 Type: {obs_type}")
        lines.append(f"├── 🔗 Trace ID: {obs.get('traceId', 'N/A')}")

        # Parent observation if exists
        if obs.get('parentObservationId'):
            lines.append(f"├── 👨‍👩‍👧 Parent ID: {obs.get('parentObservationId')}")

        # Status info
        status = obs.get('statusMessage')
        if status:
            lines.append(f"├── 📊 Status: {status}")

        # Timing
        lines.append(f"├── ⏰ Time: {timestamp}")

        # Duration if available
        if obs.get('duration'):
            duration_ms = obs.get('duration', 0) / 1000000  # Convert from nanoseconds to ms
            lines.append(f"├── ⏱️  Duration: {duration_ms:.2f}ms")

        # Model info if it's a GENERATION
        if obs_type == 'GENERATION':
            if obs.get('model'):
                lines.append(f"├── 🤖 Model: {obs.get('model')}")
            if obs.get('tokenCount'):
                lines.append(f"├── 🔢 Tokens: {obs.get('tokenCount')}")
            if obs.get('completionTokenCount'):
                lines.append(f"├── ✅ Completion Tokens: {obs.get('completionTokenCount')}")

        # Input
        if obs.get('input'):
            input_text = str(obs['input']).replace('\n', ' ').replace('\r', ' ')
            if len(input_text) > 100:
                input_text = input_text[:100] + "..."
            lines.append(f"├── 📥 Input: {input_text}")

        # Output
        if obs.get('output'):
            output_text = str(obs['output']).replace('\n', ' ').replace('\r', ' ')
            if len(output_text) > 100:
                output_text = output_text[:100] + "..."
            lines.append(f"├── 📤 Output: {output_text}")

        # Metadata
        metadata = obs.get('metadata', {})
        if metadata:
            lines.append(f"├── 📋 Metadata:")
            metadata_items = list(metadata.items())
            for i, (key, value) in enumerate(metadata_items):
                is_last = i == len(metadata_items) - 1
                prefix = "│   └──" if is_last else "│   ├──"
                lines.append(f"{prefix} {key}: {value}")

        # Level
        if obs.get('level'):
            lines.append(f"└── 📌 Level: {obs.get('level')}")

        return '\n'.join(lines)

    except Exception as e:
        return f"Error formatting observation: {str(e)}\n\nRaw JSON:\n{obs_json}"