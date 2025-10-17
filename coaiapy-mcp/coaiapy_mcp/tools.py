"""
MCP Tools implementation for coaiapy

This module provides tool wrappers that execute coaia CLI commands via subprocess.
All tools are async to comply with MCP server requirements.
"""

import subprocess
import json
from typing import Dict, Any, List, Optional


# ============================================================================
# Redis Operations
# ============================================================================

async def coaia_tash(key: str, value: str) -> Dict[str, Any]:
    """
    Stash key-value pair to Redis via coaia CLI.
    
    Args:
        key: Redis key
        value: Value to store
        
    Returns:
        Dict with success status and message
    """
    result = subprocess.run(
        ["coaia", "tash", key, value],
        capture_output=True,
        text=True,
        check=False
    )
    return {
        "success": result.returncode == 0,
        "message": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    }


async def coaia_fetch(key: str) -> Dict[str, Any]:
    """
    Fetch value from Redis via coaia CLI.
    
    Args:
        key: Redis key to fetch
        
    Returns:
        Dict with success status, value, and optional error
    """
    result = subprocess.run(
        ["coaia", "fetch", key],
        capture_output=True,
        text=True,
        check=False
    )
    return {
        "success": result.returncode == 0,
        "value": result.stdout.strip() if result.returncode == 0 else None,
        "error": result.stderr.strip() if result.returncode != 0 else None
    }


# ============================================================================
# Langfuse Traces
# ============================================================================

async def coaia_fuse_trace_create(
    trace_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create Langfuse trace via coaia CLI with JSON output.
    
    Args:
        trace_id: Unique trace identifier
        user_id: Optional user identifier
        session_id: Optional session identifier
        name: Optional trace name
        metadata: Optional metadata dictionary
        
    Returns:
        Dict with success status, trace_id, and details
    """
    cmd = ["coaia", "fuse", "traces", "create", trace_id]

    if user_id:
        cmd.extend(["-u", user_id])
    if session_id:
        cmd.extend(["-s", session_id])
    if name:
        cmd.extend(["-n", name])
    if metadata:
        cmd.extend(["-m", json.dumps(metadata)])
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "trace_id": trace_id,
                "message": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


async def coaia_fuse_add_observation(
    observation_id: str,
    trace_id: str,
    name: str,
    type: Optional[str] = None,
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add observation to Langfuse trace via coaia CLI.
    
    Args:
        observation_id: Unique observation identifier
        trace_id: Parent trace identifier
        name: Observation name
        type: Optional observation type (SPAN, EVENT, GENERATION)
        parent_id: Optional parent observation ID
        metadata: Optional metadata dictionary
        
    Returns:
        Dict with success status and observation_id
    """
    cmd = ["coaia", "fuse", "traces", "add-observation", observation_id, trace_id, "-n", name]
    
    if type:
        cmd.extend(["-t", type])
    if parent_id:
        cmd.extend(["--parent", parent_id])
    if metadata:
        cmd.extend(["-m", json.dumps(metadata)])
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        return {
            "success": True,
            "observation_id": observation_id,
            "message": result.stdout.strip()
        }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


async def coaia_fuse_add_observations_batch(
    trace_id: str,
    observations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Batch add observations to Langfuse trace via coaia CLI.
    
    Args:
        trace_id: Parent trace identifier
        observations: List of observation dictionaries
        
    Returns:
        Dict with success status, count, and optional errors
    """
    # Create temporary JSON file with observations
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(observations, f)
        temp_file = f.name
    
    try:
        cmd = ["coaia", "fuse", "traces", "add-observations", trace_id, "-f", temp_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            return {
                "success": True,
                "count": len(observations),
                "message": result.stdout.strip()
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip()
            }
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


async def coaia_fuse_trace_view(trace_id: str) -> Dict[str, Any]:
    """
    View Langfuse trace tree via coaia CLI with JSON output.
    
    Args:
        trace_id: Trace identifier to view
        
    Returns:
        Dict with trace data and observations
    """
    cmd = ["coaia", "fuse", "traces", "trace-view", trace_id, "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "trace_id": trace_id,
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


# ============================================================================
# Langfuse Prompts
# ============================================================================

async def coaia_fuse_prompts_list() -> Dict[str, Any]:
    """
    List all Langfuse prompts via coaia CLI with JSON output.

    Returns:
        Dict with prompts list
    """
    cmd = ["coaia", "fuse", "prompts", "list", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            # coaia fuse prompts list --json returns array directly
            if isinstance(data, list):
                return {
                    "success": True,
                    "prompts": data
                }
            # Handle dict format (fallback)
            return data if isinstance(data, dict) else {"success": True, "data": data}
        except json.JSONDecodeError:
            return {
                "success": True,
                "prompts": [],
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


async def coaia_fuse_prompts_get(name: str, label: Optional[str] = None) -> Dict[str, Any]:
    """
    Get specific Langfuse prompt via coaia CLI with JSON output.
    
    Args:
        name: Prompt name
        label: Optional prompt label/version
        
    Returns:
        Dict with prompt data
    """
    cmd = ["coaia", "fuse", "prompts", "get", name, "--json"]
    
    if label:
        cmd.extend(["--label", label])
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "name": name,
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


# ============================================================================
# Langfuse Datasets
# ============================================================================

async def coaia_fuse_datasets_list() -> Dict[str, Any]:
    """
    List all Langfuse datasets via coaia CLI with JSON output.
    
    Returns:
        Dict with datasets list
    """
    cmd = ["coaia", "fuse", "datasets", "list", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "datasets": [],
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


async def coaia_fuse_datasets_get(name: str) -> Dict[str, Any]:
    """
    Get specific Langfuse dataset via coaia CLI with JSON output.
    
    Args:
        name: Dataset name
        
    Returns:
        Dict with dataset data
    """
    cmd = ["coaia", "fuse", "datasets", "get", name, "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "name": name,
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


# ============================================================================
# Langfuse Score Configurations
# ============================================================================

async def coaia_fuse_score_configs_list() -> Dict[str, Any]:
    """
    List all Langfuse score configurations via coaia CLI.
    
    Returns:
        Dict with score configs list
    """
    cmd = ["coaia", "fuse", "score-configs", "list"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        # Try to parse as JSON, fallback to plain text
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "configs": [],
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


async def coaia_fuse_score_configs_get(name: str) -> Dict[str, Any]:
    """
    Get specific Langfuse score configuration via coaia CLI.
    
    Args:
        name: Score configuration name
        
    Returns:
        Dict with score config data
    """
    cmd = ["coaia", "fuse", "score-configs", "get", name]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode == 0:
        # Try to parse as JSON, fallback to plain text
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": True,
                "name": name,
                "output": result.stdout.strip()
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }


# ============================================================================
# Tool Registry
# ============================================================================

# All available tools for MCP server registration
TOOLS = {
    # Redis Operations
    "coaia_tash": coaia_tash,
    "coaia_fetch": coaia_fetch,
    
    # Langfuse Traces
    "coaia_fuse_trace_create": coaia_fuse_trace_create,
    "coaia_fuse_add_observation": coaia_fuse_add_observation,
    "coaia_fuse_add_observations_batch": coaia_fuse_add_observations_batch,
    "coaia_fuse_trace_view": coaia_fuse_trace_view,
    
    # Langfuse Prompts
    "coaia_fuse_prompts_list": coaia_fuse_prompts_list,
    "coaia_fuse_prompts_get": coaia_fuse_prompts_get,
    
    # Langfuse Datasets
    "coaia_fuse_datasets_list": coaia_fuse_datasets_list,
    "coaia_fuse_datasets_get": coaia_fuse_datasets_get,
    
    # Langfuse Score Configurations
    "coaia_fuse_score_configs_list": coaia_fuse_score_configs_list,
    "coaia_fuse_score_configs_get": coaia_fuse_score_configs_get,
}
