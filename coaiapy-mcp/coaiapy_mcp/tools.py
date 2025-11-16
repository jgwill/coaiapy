"""
MCP Tools implementation using direct library imports.

This module implements MCP tools by calling coaiapy, langfuse, and redis libraries directly
instead of using subprocess wrappers. This provides:
- Faster execution (no process creation overhead)
- Better error handling (typed exceptions)
- Shared configuration (load once, use everywhere)
- No environment variable propagation issues
"""

import os
from typing import Dict, Any, Optional, List
import redis
from langfuse import Langfuse

# Import from coaiapy
try:
    from coaiapy import coaiamodule
    from coaiapy.cofuse import (
        list_score_configs,
        get_score_config,
        list_prompts as cofuse_list_prompts,
        get_prompt as cofuse_get_prompt,
        list_datasets as cofuse_list_datasets,
        get_dataset as cofuse_get_dataset,
        add_trace,
        add_observation,
        patch_trace_output,
        get_observation,
        format_observation_display,
        get_comments,
        get_comment_by_id,
        post_comment,
        list_traces,
        list_projects,
        get_trace_with_observations,
        format_traces_table,
        format_trace_tree,
    )
    from coaiapy.pipeline import TemplateLoader
except ImportError as e:
    print(f"Warning: Could not import from coaiapy: {e}")
    print("Some tools may not be available.")

# Load configuration once on module import
# Support custom .env path via COAIAPY_ENV_PATH environment variable
try:
    env_path = os.getenv('COAIAPY_ENV_PATH')
    config = coaiamodule.read_config(env_path=env_path)
except Exception as e:
    print(f"Warning: Could not load config: {e}")
    config = {}

# Initialize Redis client
# Try direct URL first (handles SSL automatically), fall back to component config
redis_client = None
REDIS_AVAILABLE = False

# Check for direct Redis URL from environment
redis_url = os.getenv('REDIS_URL') or os.getenv('KV_URL')
if redis_url:
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        REDIS_AVAILABLE = True
    except Exception as e:
        print(f"Warning: Redis connection failed with URL: {e}")
        redis_client = None

# Fall back to component-based config if URL didn't work
if not REDIS_AVAILABLE:
    redis_config = config.get("jtaleconf", {})
    try:
        redis_client = redis.Redis(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=redis_config.get("db", 0),
            password=redis_config.get("password") if redis_config.get("password") else None,
            ssl=redis_config.get("ssl", False),
            ssl_cert_reqs="none" if redis_config.get("ssl") else "required",
            decode_responses=True,
        )
        # Test connection
        redis_client.ping()
        REDIS_AVAILABLE = True
    except (redis.RedisError, redis.ConnectionError) as e:
        print(f"Warning: Redis not available: {e}")
        redis_client = None
        REDIS_AVAILABLE = False

# Initialize Langfuse client
try:
    langfuse_client = Langfuse(
        secret_key=config.get("langfuse_secret_key", os.getenv("LANGFUSE_SECRET_KEY")),
        public_key=config.get("langfuse_public_key", os.getenv("LANGFUSE_PUBLIC_KEY")),
        host=config.get("langfuse_host", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")),
    )
    LANGFUSE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Langfuse not available: {e}")
    langfuse_client = None
    LANGFUSE_AVAILABLE = False

# Initialize Pipeline Template Loader
try:
    pipeline_loader = TemplateLoader()
    PIPELINE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Pipeline loader not available: {e}")
    pipeline_loader = None
    PIPELINE_AVAILABLE = False


# ============================================================================
# Redis Tools
# ============================================================================

async def coaia_tash(key: str, value: str) -> Dict[str, Any]:
    """
    Stash key-value pair to Redis via direct client call.
    
    Args:
        key: Redis key
        value: Value to store
        
    Returns:
        Dict with success status and message/error
    """
    if not REDIS_AVAILABLE:
        return {
            "success": False,
            "error": "Redis is not available. Check configuration and Redis server."
        }
    
    try:
        redis_client.set(key, value)
        return {
            "success": True,
            "message": f"Stored '{key}' in Redis"
        }
    except redis.RedisError as e:
        return {
            "success": False,
            "error": f"Redis error: {str(e)}"
        }


async def coaia_fetch(key: str) -> Dict[str, Any]:
    """
    Fetch value from Redis via direct client call.
    
    Args:
        key: Redis key to fetch
        
    Returns:
        Dict with success status and value/error
    """
    if not REDIS_AVAILABLE:
        return {
            "success": False,
            "error": "Redis is not available. Check configuration and Redis server."
        }
    
    try:
        value = redis_client.get(key)
        if value is None:
            return {
                "success": False,
                "error": f"Key '{key}' not found in Redis"
            }
        return {
            "success": True,
            "value": value
        }
    except redis.RedisError as e:
        return {
            "success": False,
            "error": f"Redis error: {str(e)}"
        }


# ============================================================================
# Langfuse Trace Tools
# ============================================================================

async def coaia_fuse_trace_create(
    trace_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    input_data: Optional[Any] = None,
    output_data: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Create Langfuse trace via direct SDK call.
    
    Args:
        trace_id: Unique trace identifier
        user_id: Optional user identifier
        session_id: Optional session identifier
        name: Optional trace name
        metadata: Optional metadata dictionary
        input_data: Optional input data
        output_data: Optional output data
        
    Returns:
        Dict with success status and trace details/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's add_trace function which handles the API call
        result = add_trace(
            trace_id=trace_id,
            user_id=user_id,
            session_id=session_id,
            name=name,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata,
        )
        
        return {
            "success": True,
            "trace_id": trace_id,
            "details": {
                "name": name,
                "user_id": user_id,
                "session_id": session_id,
                "metadata": metadata,
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse trace creation error: {str(e)}"
        }


async def coaia_fuse_add_observation(
    observation_id: str,
    trace_id: str,
    name: str,
    observation_type: str = "SPAN",
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    input_data: Optional[Any] = None,
    output_data: Optional[Any] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add observation to trace via direct SDK call.
    
    Args:
        observation_id: Unique observation identifier
        trace_id: Parent trace identifier
        name: Observation name
        observation_type: Type (SPAN, EVENT, GENERATION)
        parent_id: Optional parent observation ID
        metadata: Optional metadata dictionary
        input_data: Optional input data
        output_data: Optional output data
        start_time: Optional start timestamp
        end_time: Optional end timestamp
        
    Returns:
        Dict with success status and observation details/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's add_observation function
        result = add_observation(
            observation_id=observation_id,
            trace_id=trace_id,
            observation_type=observation_type,
            name=name,
            parent_observation_id=parent_id,
            metadata=metadata,
            input_data=input_data,
            output_data=output_data,
            start_time=start_time,
            end_time=end_time,
        )
        
        return {
            "success": True,
            "observation_id": observation_id,
            "trace_id": trace_id,
            "name": name,
            "type": observation_type,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse observation creation error: {str(e)}"
        }


async def coaia_fuse_trace_patch_output(
    trace_id: str,
    output_data: Any,
) -> Dict[str, Any]:
    """
    Update the output field of an existing trace.

    Args:
        trace_id: Trace identifier to update
        output_data: New output data (string, object, or any JSON-serializable data)

    Returns:
        Dict with success status and trace details/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        # Use coaiapy's patch_trace_output function
        result = patch_trace_output(
            trace_id=trace_id,
            output_data=output_data,
        )

        return {
            "success": True,
            "trace_id": trace_id,
            "message": f"Successfully patched output for trace {trace_id}",
            "details": {
                "output_data": output_data if not isinstance(output_data, str) or len(str(output_data)) < 100 else f"{str(output_data)[:100]}...",
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse trace output patch error: {str(e)}"
        }


async def coaia_fuse_trace_get(trace_id: str, json_output: bool = False) -> Dict[str, Any]:
    """
    Get a specific trace by ID from Langfuse with all its observations.

    Args:
        trace_id: Unique trace identifier
        json_output: If True, return raw JSON; if False, return formatted tree

    Returns:
        Dict with success status and trace data/error with proper Langfuse URL
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        # Fetch trace with observations
        trace_data = get_trace_with_observations(trace_id)

        import json
        parsed = json.loads(trace_data)
        if 'error' in parsed:
            return {
                "success": False,
                "error": parsed['error']
            }

        # Get project ID for constructing proper URL
        try:
            projects_json = list_projects()
            projects = json.loads(projects_json)
            # Projects response has structure: {"data": [{"id": "...", "name": "...", ...}]}
            project_id = None
            if isinstance(projects, dict) and 'data' in projects and isinstance(projects['data'], list) and len(projects['data']) > 0:
                project_id = projects['data'][0].get('id')

            # Construct proper Langfuse URL with project_id
            langfuse_host = config.get('langfuse_host', 'https://cloud.langfuse.com')
            trace_url = f"{langfuse_host}/project/{project_id}/traces/{trace_id}" if project_id else f"{langfuse_host}/traces/{trace_id}"
        except Exception as url_error:
            # Fallback if project fetch fails
            langfuse_host = config.get('langfuse_host', 'https://cloud.langfuse.com')
            trace_url = f"{langfuse_host}/traces/{trace_id}"

        if json_output:
            return {
                "success": True,
                "trace": parsed,
                "trace_url": trace_url,
                "json": trace_data
            }
        else:
            formatted = format_trace_tree(parsed)
            return {
                "success": True,
                "trace": parsed,
                "trace_url": trace_url,
                "formatted": formatted
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Trace retrieval error: {str(e)}"
        }


async def coaia_fuse_trace_view(trace_id: str, json_output: bool = False) -> Dict[str, Any]:
    """
    View trace details with observations from Langfuse (alias for coaia_fuse_trace_get).

    Args:
        trace_id: Trace identifier to fetch
        json_output: If True, return raw JSON; if False, return formatted tree

    Returns:
        Dict with success status and trace data/error
    """
    return await coaia_fuse_trace_get(trace_id, json_output)


async def coaia_fuse_observation_get(observation_id: str, json_output: bool = False) -> Dict[str, Any]:
    """
    Get a specific observation by ID from Langfuse.

    Args:
        observation_id: Unique observation identifier
        json_output: If True, return raw JSON; if False, return formatted display

    Returns:
        Dict with success status and observation data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        # Use coaiapy's get_observation function
        obs_data = get_observation(observation_id)

        import json
        parsed = json.loads(obs_data)
        if 'error' in parsed:
            return {
                "success": False,
                "error": parsed['error']
            }

        if json_output:
            return {
                "success": True,
                "observation": parsed,
                "json": obs_data
            }
        else:
            formatted = format_observation_display(parsed)
            return {
                "success": True,
                "observation": parsed,
                "formatted": formatted
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Observation retrieval error: {str(e)}"
        }


async def coaia_fuse_traces_session_view(session_id: str, json_output: bool = False) -> Dict[str, Any]:
    """
    View all traces for a specific session from Langfuse.

    Args:
        session_id: Session identifier to filter traces
        json_output: If True, return raw JSON data; if False, return formatted table

    Returns:
        Dict with success status and traces data or formatted table/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        import json

        # Get project ID for constructing proper URL
        try:
            projects_json = list_projects()
            projects = json.loads(projects_json)
            # Projects response has structure: {"data": [{"id": "...", "name": "...", ...}]}
            project_id = None
            if isinstance(projects, dict) and 'data' in projects and isinstance(projects['data'], list) and len(projects['data']) > 0:
                project_id = projects['data'][0].get('id')

            # Construct proper Langfuse URL with project_id
            langfuse_host = config.get('langfuse_host', 'https://cloud.langfuse.com')
            session_url = f"{langfuse_host}/project/{project_id}/sessions/{session_id}" if project_id else f"{langfuse_host}/sessions/{session_id}"
        except Exception as url_error:
            # Fallback if project fetch fails
            langfuse_host = config.get('langfuse_host', 'https://cloud.langfuse.com')
            session_url = f"{langfuse_host}/sessions/{session_id}"

        # Call list_traces with session_id filter
        traces_json = list_traces(session_id=session_id, include_observations=False)

        if json_output:
            # Return raw JSON
            traces_data = json.loads(traces_json) if isinstance(traces_json, str) else traces_json
            return {
                "success": True,
                "session_id": session_id,
                "session_url": session_url,
                "traces": traces_data
            }
        else:
            # Return formatted table
            table_output = format_traces_table(traces_json)
            return {
                "success": True,
                "session_id": session_id,
                "session_url": session_url,
                "table": table_output
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error viewing session traces: {str(e)}"
        }


# ============================================================================
# Langfuse Prompts Tools
# ============================================================================

async def coaia_fuse_prompts_list() -> Dict[str, Any]:
    """
    List all Langfuse prompts.
    
    Returns:
        Dict with success status and list of prompts/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's list_prompts function
        prompts_data = cofuse_list_prompts(debug=False)
        
        # Parse the response (it might be a formatted string or dict)
        if isinstance(prompts_data, str):
            # If it's a formatted string, we return it as-is
            return {
                "success": True,
                "prompts": prompts_data,
                "note": "Prompts returned as formatted string"
            }
        elif isinstance(prompts_data, (list, dict)):
            return {
                "success": True,
                "prompts": prompts_data
            }
        else:
            return {
                "success": True,
                "prompts": str(prompts_data)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse prompts list error: {str(e)}"
        }


async def coaia_fuse_prompts_get(name: str, label: Optional[str] = None) -> Dict[str, Any]:
    """
    Get specific Langfuse prompt.
    
    Args:
        name: Prompt name
        label: Optional prompt label/version
        
    Returns:
        Dict with success status and prompt data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's get_prompt function
        prompt_data = cofuse_get_prompt(prompt_name=name, label=label)
        
        return {
            "success": True,
            "prompt": prompt_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse prompt get error: {str(e)}"
        }


# ============================================================================
# Langfuse Datasets Tools
# ============================================================================

async def coaia_fuse_datasets_list() -> Dict[str, Any]:
    """
    List all Langfuse datasets.
    
    Returns:
        Dict with success status and list of datasets/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's list_datasets function
        datasets_data = cofuse_list_datasets()
        
        return {
            "success": True,
            "datasets": datasets_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse datasets list error: {str(e)}"
        }


async def coaia_fuse_datasets_get(name: str) -> Dict[str, Any]:
    """
    Get specific Langfuse dataset.
    
    Args:
        name: Dataset name
        
    Returns:
        Dict with success status and dataset data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's get_dataset function
        dataset_data = cofuse_get_dataset(dataset_name=name)
        
        return {
            "success": True,
            "dataset": dataset_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse dataset get error: {str(e)}"
        }


# ============================================================================
# Langfuse Score Configurations Tools
# ============================================================================

async def coaia_fuse_score_configs_list() -> Dict[str, Any]:
    """
    List all Langfuse score configurations using coaiapy's smart cache system.
    
    Returns:
        Dict with success status and list of configs/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's list_score_configs function
        configs_data = list_score_configs(debug=False)
        
        return {
            "success": True,
            "configs": configs_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse score configs list error: {str(e)}"
        }


async def coaia_fuse_score_configs_get(name_or_id: str) -> Dict[str, Any]:
    """
    Get specific score configuration using coaiapy's smart cache system.
    
    Args:
        name_or_id: Score config name or ID
        
    Returns:
        Dict with success status and config data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Use coaiapy's get_score_config function
        config_data = get_score_config(config_id=name_or_id)
        
        return {
            "success": True,
            "config": config_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse score config get error: {str(e)}"
        }


# ============================================================================
# Langfuse Comments Tools
# ============================================================================

async def coaia_fuse_comments_list(
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    author_user_id: Optional[str] = None,
    page: int = 1,
    limit: int = 50
) -> Dict[str, Any]:
    """
    List comments with optional filtering.

    Args:
        object_type: Filter by object type (trace, observation, session, prompt)
        object_id: Filter by specific object ID (requires object_type)
        author_user_id: Filter by author user ID
        page: Page number (starts at 1)
        limit: Items per page

    Returns:
        Dict with success status and list of comments/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        # Use coaiapy's get_comments function
        comments_data = get_comments(
            object_type=object_type,
            object_id=object_id,
            author_user_id=author_user_id,
            page=page,
            limit=limit
        )

        # Parse response if it's a string
        import json
        if isinstance(comments_data, str):
            try:
                parsed_data = json.loads(comments_data)
                return {
                    "success": True,
                    "comments": parsed_data
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "comments": comments_data,
                    "note": "Comments returned as raw string"
                }
        else:
            return {
                "success": True,
                "comments": comments_data
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse comments list error: {str(e)}"
        }


async def coaia_fuse_comments_get(comment_id: str) -> Dict[str, Any]:
    """
    Get a specific comment by ID.

    Args:
        comment_id: The unique Langfuse identifier of a comment

    Returns:
        Dict with success status and comment data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        # Use coaiapy's get_comment_by_id function
        comment_data = get_comment_by_id(comment_id)

        # Parse response if it's a string
        import json
        if isinstance(comment_data, str):
            try:
                parsed_data = json.loads(comment_data)
                return {
                    "success": True,
                    "comment": parsed_data
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "comment": comment_data,
                    "note": "Comment returned as raw string"
                }
        else:
            return {
                "success": True,
                "comment": comment_data
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse comment get error: {str(e)}"
        }


async def coaia_fuse_comments_create(
    text: str,
    object_type: str,
    object_id: str,
    author_user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a comment attached to an object (trace, observation, session, or prompt).

    Args:
        text: The comment text/content
        object_type: Type of object to attach comment to (trace, observation, session, prompt) - REQUIRED
        object_id: ID of the object to attach comment to - REQUIRED
        author_user_id: Optional user ID of the comment author

    Returns:
        Dict with success status and created comment data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }

    try:
        # Use coaiapy's post_comment function
        comment_data = post_comment(
            text=text,
            object_type=object_type,
            object_id=object_id,
            author_user_id=author_user_id
        )

        # Parse response if it's a string
        import json
        if isinstance(comment_data, str):
            try:
                parsed_data = json.loads(comment_data)
                return {
                    "success": True,
                    "comment": parsed_data
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "comment": comment_data,
                    "note": "Comment returned as raw string"
                }
        else:
            return {
                "success": True,
                "comment": comment_data
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse comment creation error: {str(e)}"
        }


# ============================================================================
# Tool Registry
# ============================================================================

# Export all tools
TOOLS = {
    # Redis tools
    "coaia_tash": coaia_tash,
    "coaia_fetch": coaia_fetch,

    # Langfuse trace tools
    "coaia_fuse_trace_create": coaia_fuse_trace_create,
    "coaia_fuse_add_observation": coaia_fuse_add_observation,
    "coaia_fuse_trace_patch_output": coaia_fuse_trace_patch_output,
    "coaia_fuse_trace_get": coaia_fuse_trace_get,
    "coaia_fuse_trace_view": coaia_fuse_trace_view,
    "coaia_fuse_observation_get": coaia_fuse_observation_get,
    "coaia_fuse_traces_session_view": coaia_fuse_traces_session_view,

    # Langfuse prompts tools
    "coaia_fuse_prompts_list": coaia_fuse_prompts_list,
    "coaia_fuse_prompts_get": coaia_fuse_prompts_get,

    # Langfuse datasets tools
    "coaia_fuse_datasets_list": coaia_fuse_datasets_list,
    "coaia_fuse_datasets_get": coaia_fuse_datasets_get,

    # Langfuse score configs tools
    "coaia_fuse_score_configs_list": coaia_fuse_score_configs_list,
    "coaia_fuse_score_configs_get": coaia_fuse_score_configs_get,

    # Langfuse comments tools
    "coaia_fuse_comments_list": coaia_fuse_comments_list,
    "coaia_fuse_comments_get": coaia_fuse_comments_get,
    "coaia_fuse_comments_create": coaia_fuse_comments_create,
}

__all__ = [
    "TOOLS",
    "coaia_tash",
    "coaia_fetch",
    "coaia_fuse_trace_create",
    "coaia_fuse_add_observation",
    "coaia_fuse_trace_patch_output",
    "coaia_fuse_trace_get",
    "coaia_fuse_trace_view",
    "coaia_fuse_observation_get",
    "coaia_fuse_traces_session_view",
    "coaia_fuse_prompts_list",
    "coaia_fuse_prompts_get",
    "coaia_fuse_datasets_list",
    "coaia_fuse_datasets_get",
    "coaia_fuse_score_configs_list",
    "coaia_fuse_score_configs_get",
    "coaia_fuse_comments_list",
    "coaia_fuse_comments_get",
    "coaia_fuse_comments_create",
]
