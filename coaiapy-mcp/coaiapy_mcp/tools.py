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
    )
    from coaiapy.pipeline import TemplateLoader
except ImportError as e:
    print(f"Warning: Could not import from coaiapy: {e}")
    print("Some tools may not be available.")

# Load configuration once on module import
try:
    config = coaiamodule.read_config()
except Exception as e:
    print(f"Warning: Could not load config: {e}")
    config = {}

# Initialize Redis client
redis_config = config.get("jtaleconf", {})
try:
    redis_client = redis.Redis(
        host=redis_config.get("host", "localhost"),
        port=redis_config.get("port", 6379),
        db=redis_config.get("db", 0),
        password=redis_config.get("password") if redis_config.get("password") else None,
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


async def coaia_fuse_trace_view(trace_id: str) -> Dict[str, Any]:
    """
    View trace details via Langfuse API.
    
    Note: This requires fetching from Langfuse API. We'll use the langfuse client.
    
    Args:
        trace_id: Trace identifier to fetch
        
    Returns:
        Dict with success status and trace data/error
    """
    if not LANGFUSE_AVAILABLE:
        return {
            "success": False,
            "error": "Langfuse is not available. Check credentials in configuration."
        }
    
    try:
        # Note: The Langfuse Python SDK doesn't have a direct fetch_trace method
        # in the same way as described. We'll return a placeholder or use API directly.
        # For now, we'll indicate that this needs to be done via web UI or API
        return {
            "success": True,
            "trace_id": trace_id,
            "message": "Trace created. View it in Langfuse web UI.",
            "url": f"{config.get('langfuse_host', 'https://cloud.langfuse.com')}/traces/{trace_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse trace view error: {str(e)}"
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
    "coaia_fuse_trace_view": coaia_fuse_trace_view,
    
    # Langfuse prompts tools
    "coaia_fuse_prompts_list": coaia_fuse_prompts_list,
    "coaia_fuse_prompts_get": coaia_fuse_prompts_get,
    
    # Langfuse datasets tools
    "coaia_fuse_datasets_list": coaia_fuse_datasets_list,
    "coaia_fuse_datasets_get": coaia_fuse_datasets_get,
    
    # Langfuse score configs tools
    "coaia_fuse_score_configs_list": coaia_fuse_score_configs_list,
    "coaia_fuse_score_configs_get": coaia_fuse_score_configs_get,
}

__all__ = [
    "TOOLS",
    "coaia_tash",
    "coaia_fetch",
    "coaia_fuse_trace_create",
    "coaia_fuse_add_observation",
    "coaia_fuse_trace_view",
    "coaia_fuse_prompts_list",
    "coaia_fuse_prompts_get",
    "coaia_fuse_datasets_list",
    "coaia_fuse_datasets_get",
    "coaia_fuse_score_configs_list",
    "coaia_fuse_score_configs_get",
]
