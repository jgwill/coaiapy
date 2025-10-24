"""
Unit tests for coaiapy-mcp tools.

Tests the tool implementations using direct library imports.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coaiapy_mcp import tools


# ============================================================================
# Redis Tools Tests
# ============================================================================

@pytest.mark.asyncio
async def test_coaia_tash_basic():
    """Test basic Redis stash operation."""
    result = await tools.coaia_tash("test_key", "test_value")
    
    assert isinstance(result, dict)
    assert "success" in result
    
    # If Redis is available, should succeed
    if tools.REDIS_AVAILABLE:
        assert result["success"] is True
        assert "message" in result
    else:
        # If Redis not available, should fail gracefully
        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_coaia_fetch_basic():
    """Test basic Redis fetch operation."""
    # First stash a value (if Redis available)
    if tools.REDIS_AVAILABLE:
        await tools.coaia_tash("fetch_test_key", "fetch_test_value")
    
    # Try to fetch
    result = await tools.coaia_fetch("fetch_test_key")
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if tools.REDIS_AVAILABLE:
        # Should succeed and return the value
        assert result["success"] is True
        assert result.get("value") == "fetch_test_value"
    else:
        # Should fail gracefully
        assert result["success"] is False


@pytest.mark.asyncio
async def test_coaia_fetch_nonexistent():
    """Test fetching a non-existent key."""
    result = await tools.coaia_fetch("nonexistent_key_12345")
    
    assert isinstance(result, dict)
    
    if tools.REDIS_AVAILABLE:
        # Should fail with not found
        assert result["success"] is False
        assert "not found" in result.get("error", "").lower()


# ============================================================================
# Langfuse Tools Tests
# ============================================================================

@pytest.mark.asyncio
async def test_coaia_fuse_trace_create_basic():
    """Test basic Langfuse trace creation."""
    result = await tools.coaia_fuse_trace_create(
        trace_id="test-trace-001",
        user_id="test_user",
        name="Test Trace"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if tools.LANGFUSE_AVAILABLE:
        # Should succeed
        assert result["success"] is True
        assert result.get("trace_id") == "test-trace-001"
    else:
        # Should fail gracefully
        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_coaia_fuse_add_observation_basic():
    """Test adding observation to trace."""
    # First create a trace
    if tools.LANGFUSE_AVAILABLE:
        await tools.coaia_fuse_trace_create(
            trace_id="test-trace-002",
            name="Test Trace for Observation"
        )
    
    # Add observation
    result = await tools.coaia_fuse_add_observation(
        observation_id="test-obs-001",
        trace_id="test-trace-002",
        name="Test Observation"
    )
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if tools.LANGFUSE_AVAILABLE:
        assert result.get("observation_id") == "test-obs-001"


@pytest.mark.asyncio
async def test_coaia_fuse_prompts_list():
    """Test listing Langfuse prompts."""
    result = await tools.coaia_fuse_prompts_list()
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if tools.LANGFUSE_AVAILABLE:
        # Should have prompts key
        assert "prompts" in result


@pytest.mark.asyncio
async def test_coaia_fuse_datasets_list():
    """Test listing Langfuse datasets."""
    result = await tools.coaia_fuse_datasets_list()
    
    assert isinstance(result, dict)
    assert "success" in result


@pytest.mark.asyncio
async def test_coaia_fuse_score_configs_list():
    """Test listing score configurations."""
    result = await tools.coaia_fuse_score_configs_list()
    
    assert isinstance(result, dict)
    assert "success" in result


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skipif(not tools.REDIS_AVAILABLE, reason="Redis not available")
async def test_redis_roundtrip():
    """Test full Redis stash and fetch roundtrip."""
    key = "roundtrip_test_key"
    value = "roundtrip_test_value"
    
    # Stash
    stash_result = await tools.coaia_tash(key, value)
    assert stash_result["success"] is True
    
    # Fetch
    fetch_result = await tools.coaia_fetch(key)
    assert fetch_result["success"] is True
    assert fetch_result["value"] == value


@pytest.mark.asyncio
@pytest.mark.skipif(not tools.LANGFUSE_AVAILABLE, reason="Langfuse not available")
async def test_langfuse_trace_workflow():
    """Test full Langfuse trace creation workflow."""
    trace_id = "workflow-test-trace"
    
    # Create trace
    trace_result = await tools.coaia_fuse_trace_create(
        trace_id=trace_id,
        user_id="workflow_test_user",
        name="Workflow Test"
    )
    assert trace_result["success"] is True
    
    # Add observation
    obs_result = await tools.coaia_fuse_add_observation(
        observation_id="workflow-obs-001",
        trace_id=trace_id,
        name="First Step"
    )
    assert obs_result["success"] is True


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_tool_handles_invalid_parameters():
    """Test that tools handle invalid parameters gracefully."""
    # This should not crash, but return an error
    try:
        result = await tools.coaia_tash("", "")  # Empty strings
        assert isinstance(result, dict)
    except Exception as e:
        # Should not raise exception, should return error dict
        pytest.fail(f"Tool raised exception instead of returning error: {e}")


def test_tool_registry():
    """Test that all tools are registered in TOOLS dict."""
    expected_tools = [
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
    
    for tool_name in expected_tools:
        assert tool_name in tools.TOOLS, f"Tool {tool_name} not in TOOLS registry"


def test_tool_functions_are_async():
    """Test that all tool functions are async."""
    import inspect
    
    for tool_name, tool_func in tools.TOOLS.items():
        assert inspect.iscoroutinefunction(tool_func), \
            f"Tool {tool_name} is not an async function"
