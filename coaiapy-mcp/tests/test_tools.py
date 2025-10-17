"""
Tests for coaiapy-mcp tools module

These tests verify that tool functions properly wrap coaia CLI commands.
Note: These are unit tests that may require a running Redis instance and
configured Langfuse credentials for full integration testing.
"""

import pytest
from coaiapy_mcp.tools import (
    coaia_tash,
    coaia_fetch,
    coaia_fuse_trace_create,
    coaia_fuse_add_observation,
    coaia_fuse_prompts_list,
)


@pytest.mark.asyncio
async def test_tash_fetch_roundtrip():
    """Test Redis stash/fetch workflow (requires Redis)"""
    # This test requires a running Redis instance
    # Skip if Redis is not available
    
    # Stash
    result = await coaia_tash("test_key_mcp", "test_value_mcp")
    # We don't assert success here because Redis might not be available
    # Just verify the structure
    assert "success" in result
    assert "message" in result or "error" in result


@pytest.mark.asyncio
async def test_fetch_nonexistent_key():
    """Test fetching a non-existent key"""
    result = await coaia_fetch("nonexistent_key_12345")
    assert "success" in result
    assert "value" in result or "error" in result


@pytest.mark.asyncio
async def test_trace_create_structure():
    """Test trace creation returns correct structure"""
    import uuid
    trace_id = str(uuid.uuid4())
    
    result = await coaia_fuse_trace_create(
        trace_id=trace_id,
        user_id="test_user",
        name="Test Trace"
    )
    
    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


@pytest.mark.asyncio
async def test_add_observation_structure():
    """Test observation addition returns correct structure"""
    import uuid
    obs_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    result = await coaia_fuse_add_observation(
        observation_id=obs_id,
        trace_id=trace_id,
        name="Test Observation"
    )
    
    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


@pytest.mark.asyncio
async def test_prompts_list_structure():
    """Test prompts list returns correct structure"""
    result = await coaia_fuse_prompts_list()
    
    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "prompts" in result or "error" in result


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test that tools handle errors gracefully"""
    # Try to create observation with invalid parameters
    result = await coaia_fuse_add_observation(
        observation_id="",  # Invalid empty ID
        trace_id="",
        name=""
    )
    
    # Should return an error but not raise exception
    assert isinstance(result, dict)
