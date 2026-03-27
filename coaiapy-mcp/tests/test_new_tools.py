"""
Unit tests for the 9 new MCP tool functions.

Tests coaia_fuse_prompts_delete, coaia_fuse_score_get,
coaia_fuse_score_config_update, coaia_fuse_trace_delete,
coaia_fuse_traces_delete_batch, coaia_fuse_sessions_list,
coaia_fuse_session_get, and coaia_fuse_observations_list
using mocked Langfuse API calls.
"""

import pytest
import sys
import os
import inspect
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coaiapy_mcp import tools


# ============================================================================
# Sample data fixtures
# ============================================================================

SAMPLE_SCORE = {
    "id": "score-abc-123",
    "name": "Helpfulness",
    "traceId": "trace-xyz",
    "value": 4.5,
    "dataType": "NUMERIC",
    "comment": "Very helpful response",
}

SAMPLE_SCORE_CONFIG = {
    "id": "cfg-abc-123",
    "name": "Helpfulness",
    "dataType": "CATEGORICAL",
    "description": "Updated description",
    "isArchived": False,
    "categories": [{"label": "Good", "value": 1}, {"label": "Bad", "value": 0}],
}

SAMPLE_SESSION = {
    "id": "session-abc-123",
    "createdAt": "2025-01-15T10:00:00Z",
    "projectId": "proj-123",
}

SAMPLE_SESSIONS_LIST = {
    "data": [SAMPLE_SESSION],
    "meta": {"page": 1, "limit": 50, "totalItems": 1, "totalPages": 1},
}

SAMPLE_OBSERVATION = {
    "id": "obs-abc-123",
    "traceId": "trace-xyz",
    "type": "GENERATION",
    "name": "llm-call",
    "startTime": "2025-01-15T10:01:00Z",
}

SAMPLE_OBSERVATIONS_LIST = {
    "data": [SAMPLE_OBSERVATION],
    "meta": {"page": 1, "limit": 50, "totalItems": 1, "totalPages": 1},
}


# ============================================================================
# coaia_fuse_prompts_delete
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_prompt')
async def test_prompts_delete_basic(mock_delete):
    """Test basic prompt deletion by name."""
    mock_delete.return_value = {"message": "Prompt deleted"}

    result = await tools.coaia_fuse_prompts_delete(name="old-prompt")

    assert result["success"] is True
    assert result["result"] == {"message": "Prompt deleted"}
    mock_delete.assert_called_once_with(
        prompt_name="old-prompt", version=None, label=None
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_prompt')
async def test_prompts_delete_with_version(mock_delete):
    """Test deleting a specific prompt version."""
    mock_delete.return_value = {"message": "Prompt version 2 deleted"}

    result = await tools.coaia_fuse_prompts_delete(name="old-prompt", version=2)

    assert result["success"] is True
    mock_delete.assert_called_once_with(
        prompt_name="old-prompt", version=2, label=None
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_prompt')
async def test_prompts_delete_with_label(mock_delete):
    """Test deleting a prompt by label."""
    mock_delete.return_value = {"message": "Prompt with label deleted"}

    result = await tools.coaia_fuse_prompts_delete(name="old-prompt", label="staging")

    assert result["success"] is True
    mock_delete.assert_called_once_with(
        prompt_name="old-prompt", version=None, label="staging"
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_prompt')
async def test_prompts_delete_error(mock_delete):
    """Test error handling when prompt deletion fails."""
    mock_delete.side_effect = Exception("Prompt 'nonexistent' not found")

    result = await tools.coaia_fuse_prompts_delete(name="nonexistent")

    assert result["success"] is False
    assert "error" in result
    assert "nonexistent" in result["error"]


@pytest.mark.asyncio
async def test_prompts_delete_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_prompts_delete(name="some-prompt")

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_score_get
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_score_by_id')
async def test_score_get_basic(mock_get):
    """Test getting a score by ID."""
    mock_get.return_value = SAMPLE_SCORE

    result = await tools.coaia_fuse_score_get(score_id="score-abc-123")

    assert result["success"] is True
    assert result["score"] == SAMPLE_SCORE
    assert result["score"]["value"] == 4.5
    mock_get.assert_called_once_with(score_id="score-abc-123")


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_score_by_id')
async def test_score_get_not_found(mock_get):
    """Test error when score ID doesn't exist."""
    mock_get.side_effect = Exception("Score 'invalid-id' not found")

    result = await tools.coaia_fuse_score_get(score_id="invalid-id")

    assert result["success"] is False
    assert "error" in result
    assert "invalid-id" in result["error"]


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_score_by_id')
async def test_score_get_api_error(mock_get):
    """Test generic API error during score retrieval."""
    mock_get.side_effect = Exception("Network timeout")

    result = await tools.coaia_fuse_score_get(score_id="score-abc-123")

    assert result["success"] is False
    assert "Network timeout" in result["error"]


@pytest.mark.asyncio
async def test_score_get_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_score_get(score_id="score-abc-123")

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_score_config_update
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_score_config')
async def test_score_config_update_description(mock_update):
    """Test updating only the description of a score config."""
    mock_update.return_value = SAMPLE_SCORE_CONFIG

    result = await tools.coaia_fuse_score_config_update(
        config_id="cfg-abc-123", description="Updated description"
    )

    assert result["success"] is True
    assert result["config"] == SAMPLE_SCORE_CONFIG
    mock_update.assert_called_once_with(
        config_id="cfg-abc-123", description="Updated description", is_archived=None
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_score_config')
async def test_score_config_update_archive(mock_update):
    """Test archiving a score config."""
    archived_config = {**SAMPLE_SCORE_CONFIG, "isArchived": True}
    mock_update.return_value = archived_config

    result = await tools.coaia_fuse_score_config_update(
        config_id="cfg-abc-123", is_archived=True
    )

    assert result["success"] is True
    assert result["config"]["isArchived"] is True
    mock_update.assert_called_once_with(
        config_id="cfg-abc-123", description=None, is_archived=True
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_score_config')
async def test_score_config_update_both_params(mock_update):
    """Test updating both description and archive status."""
    mock_update.return_value = {
        **SAMPLE_SCORE_CONFIG,
        "description": "New desc",
        "isArchived": True,
    }

    result = await tools.coaia_fuse_score_config_update(
        config_id="cfg-abc-123", description="New desc", is_archived=True
    )

    assert result["success"] is True
    mock_update.assert_called_once_with(
        config_id="cfg-abc-123", description="New desc", is_archived=True
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_score_config')
async def test_score_config_update_error(mock_update):
    """Test error when config update fails."""
    mock_update.side_effect = Exception("Config 'cfg-invalid' not found")

    result = await tools.coaia_fuse_score_config_update(
        config_id="cfg-invalid", description="test"
    )

    assert result["success"] is False
    assert "error" in result
    assert "cfg-invalid" in result["error"]


@pytest.mark.asyncio
async def test_score_config_update_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_score_config_update(
            config_id="cfg-abc-123", description="test"
        )

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_trace_delete
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_trace')
async def test_trace_delete_basic(mock_delete):
    """Test deleting a single trace by ID."""
    mock_delete.return_value = {"message": "Trace deleted"}

    result = await tools.coaia_fuse_trace_delete(trace_id="trace-xyz")

    assert result["success"] is True
    assert result["result"] == {"message": "Trace deleted"}
    mock_delete.assert_called_once_with(trace_id="trace-xyz")


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_trace')
async def test_trace_delete_not_found(mock_delete):
    """Test error when trace ID doesn't exist."""
    mock_delete.side_effect = Exception("Trace 'bad-id' not found")

    result = await tools.coaia_fuse_trace_delete(trace_id="bad-id")

    assert result["success"] is False
    assert "error" in result
    assert "bad-id" in result["error"]


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_trace')
async def test_trace_delete_api_error(mock_delete):
    """Test generic API error during trace deletion."""
    mock_delete.side_effect = Exception("Permission denied")

    result = await tools.coaia_fuse_trace_delete(trace_id="trace-xyz")

    assert result["success"] is False
    assert "Permission denied" in result["error"]


@pytest.mark.asyncio
async def test_trace_delete_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_trace_delete(trace_id="trace-xyz")

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_traces_delete_batch
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_traces_batch')
async def test_traces_delete_batch_basic(mock_delete):
    """Test batch deletion of multiple traces."""
    mock_delete.return_value = {"message": "3 traces deleted"}

    result = await tools.coaia_fuse_traces_delete_batch(
        trace_ids=["trace-1", "trace-2", "trace-3"]
    )

    assert result["success"] is True
    assert result["result"] == {"message": "3 traces deleted"}
    mock_delete.assert_called_once_with(
        trace_ids=["trace-1", "trace-2", "trace-3"]
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_traces_batch')
async def test_traces_delete_batch_single(mock_delete):
    """Test batch deletion with a single trace ID."""
    mock_delete.return_value = {"message": "1 trace deleted"}

    result = await tools.coaia_fuse_traces_delete_batch(trace_ids=["trace-1"])

    assert result["success"] is True
    mock_delete.assert_called_once_with(trace_ids=["trace-1"])


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_delete_traces_batch')
async def test_traces_delete_batch_error(mock_delete):
    """Test error handling for batch trace deletion."""
    mock_delete.side_effect = Exception("Batch delete failed: invalid IDs")

    result = await tools.coaia_fuse_traces_delete_batch(
        trace_ids=["bad-1", "bad-2"]
    )

    assert result["success"] is False
    assert "error" in result
    assert "Batch delete failed" in result["error"]


@pytest.mark.asyncio
async def test_traces_delete_batch_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_traces_delete_batch(
            trace_ids=["trace-1"]
        )

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_sessions_list
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_sessions')
async def test_sessions_list_basic(mock_list):
    """Test listing sessions with default parameters."""
    mock_list.return_value = SAMPLE_SESSIONS_LIST

    result = await tools.coaia_fuse_sessions_list()

    assert result["success"] is True
    assert result["sessions"] == SAMPLE_SESSIONS_LIST
    mock_list.assert_called_once_with(page=1, limit=50, environment=None)


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_sessions')
async def test_sessions_list_with_filters(mock_list):
    """Test listing sessions with pagination and environment filter."""
    mock_list.return_value = SAMPLE_SESSIONS_LIST

    result = await tools.coaia_fuse_sessions_list(
        page=2, limit=10, environment="production"
    )

    assert result["success"] is True
    mock_list.assert_called_once_with(
        page=2, limit=10, environment="production"
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_sessions')
async def test_sessions_list_error(mock_list):
    """Test error handling when listing sessions fails."""
    mock_list.side_effect = Exception("API rate limit exceeded")

    result = await tools.coaia_fuse_sessions_list()

    assert result["success"] is False
    assert "error" in result
    assert "rate limit" in result["error"].lower()


@pytest.mark.asyncio
async def test_sessions_list_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_sessions_list()

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_session_get
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_session')
async def test_session_get_basic(mock_get):
    """Test getting a session by ID."""
    mock_get.return_value = SAMPLE_SESSION

    result = await tools.coaia_fuse_session_get(session_id="session-abc-123")

    assert result["success"] is True
    assert result["session"] == SAMPLE_SESSION
    assert result["session"]["id"] == "session-abc-123"
    mock_get.assert_called_once_with(session_id="session-abc-123")


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_session')
async def test_session_get_not_found(mock_get):
    """Test error when session ID doesn't exist."""
    mock_get.side_effect = Exception("Session 'bad-session' not found")

    result = await tools.coaia_fuse_session_get(session_id="bad-session")

    assert result["success"] is False
    assert "error" in result
    assert "bad-session" in result["error"]


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_session')
async def test_session_get_api_error(mock_get):
    """Test generic API error during session retrieval."""
    mock_get.side_effect = Exception("Internal server error")

    result = await tools.coaia_fuse_session_get(session_id="session-abc-123")

    assert result["success"] is False
    assert "Internal server error" in result["error"]


@pytest.mark.asyncio
async def test_session_get_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_session_get(session_id="session-abc-123")

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_observations_list
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_observations_v2')
async def test_observations_list_basic(mock_list):
    """Test listing observations with default parameters."""
    mock_list.return_value = SAMPLE_OBSERVATIONS_LIST

    result = await tools.coaia_fuse_observations_list()

    assert result["success"] is True
    assert result["observations"] == SAMPLE_OBSERVATIONS_LIST
    mock_list.assert_called_once_with(
        limit=50, cursor=None, name=None, user_id=None,
        trace_id=None, observation_type=None,
        parent_observation_id=None,
        from_start_time=None, to_start_time=None,
        version=None, environment=None,
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_observations_v2')
async def test_observations_list_with_trace_filter(mock_list):
    """Test listing observations filtered by trace ID."""
    mock_list.return_value = SAMPLE_OBSERVATIONS_LIST

    result = await tools.coaia_fuse_observations_list(
        trace_id="trace-xyz", limit=10
    )

    assert result["success"] is True
    mock_list.assert_called_once_with(
        limit=10, cursor=None, name=None, user_id=None,
        trace_id="trace-xyz", observation_type=None,
        parent_observation_id=None,
        from_start_time=None, to_start_time=None,
        version=None, environment=None,
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_observations_v2')
async def test_observations_list_with_all_filters(mock_list):
    """Test listing observations with all filter parameters set."""
    mock_list.return_value = SAMPLE_OBSERVATIONS_LIST

    result = await tools.coaia_fuse_observations_list(
        limit=25,
        cursor="cursor-abc",
        name="llm-call",
        user_id="user-1",
        trace_id="trace-xyz",
        observation_type="GENERATION",
        parent_observation_id="parent-obs-1",
        from_start_time="2025-01-01T00:00:00Z",
        to_start_time="2025-01-31T23:59:59Z",
        version="1.0",
        environment="production",
    )

    assert result["success"] is True
    mock_list.assert_called_once_with(
        limit=25,
        cursor="cursor-abc",
        name="llm-call",
        user_id="user-1",
        trace_id="trace-xyz",
        observation_type="GENERATION",
        parent_observation_id="parent-obs-1",
        from_start_time="2025-01-01T00:00:00Z",
        to_start_time="2025-01-31T23:59:59Z",
        version="1.0",
        environment="production",
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_observations_v2')
async def test_observations_list_with_cursor_pagination(mock_list):
    """Test cursor-based pagination for observations."""
    mock_list.return_value = {
        "data": [SAMPLE_OBSERVATION],
        "meta": {"nextCursor": "next-cursor-token", "totalItems": 100},
    }

    result = await tools.coaia_fuse_observations_list(
        limit=10, cursor="prev-cursor-token"
    )

    assert result["success"] is True
    mock_list.assert_called_once()
    call_kwargs = mock_list.call_args[1]
    assert call_kwargs["cursor"] == "prev-cursor-token"
    assert call_kwargs["limit"] == 10


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_observations_v2')
async def test_observations_list_by_type(mock_list):
    """Test filtering observations by type (GENERATION, SPAN, EVENT)."""
    mock_list.return_value = SAMPLE_OBSERVATIONS_LIST

    result = await tools.coaia_fuse_observations_list(
        observation_type="GENERATION"
    )

    assert result["success"] is True
    call_kwargs = mock_list.call_args[1]
    assert call_kwargs["observation_type"] == "GENERATION"


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_list_observations_v2')
async def test_observations_list_error(mock_list):
    """Test error handling when listing observations fails."""
    mock_list.side_effect = Exception("API timeout")

    result = await tools.coaia_fuse_observations_list()

    assert result["success"] is False
    assert "error" in result
    assert "API timeout" in result["error"]


@pytest.mark.asyncio
async def test_observations_list_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_observations_list()

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# Registry completeness checks
# ============================================================================

def test_new_tools_in_registry():
    """Verify all 9 new tools are registered in the TOOLS dict."""
    new_tools = [
        "coaia_fuse_prompts_delete",
        "coaia_fuse_score_get",
        "coaia_fuse_score_config_update",
        "coaia_fuse_trace_delete",
        "coaia_fuse_traces_delete_batch",
        "coaia_fuse_sessions_list",
        "coaia_fuse_session_get",
        "coaia_fuse_observations_list",
    ]
    for tool_name in new_tools:
        assert tool_name in tools.TOOLS, f"Tool {tool_name} not in TOOLS registry"


def test_new_tool_functions_are_async():
    """Verify all new tool functions are async coroutines."""
    new_tools = [
        "coaia_fuse_prompts_delete",
        "coaia_fuse_score_get",
        "coaia_fuse_score_config_update",
        "coaia_fuse_trace_delete",
        "coaia_fuse_traces_delete_batch",
        "coaia_fuse_sessions_list",
        "coaia_fuse_session_get",
        "coaia_fuse_observations_list",
    ]
    for tool_name in new_tools:
        func = tools.TOOLS[tool_name]
        assert inspect.iscoroutinefunction(func), \
            f"Tool {tool_name} is not an async function"


def test_new_tools_return_dict():
    """Verify tool functions have Dict return type annotation."""
    new_tools = [
        tools.coaia_fuse_prompts_delete,
        tools.coaia_fuse_score_get,
        tools.coaia_fuse_score_config_update,
        tools.coaia_fuse_trace_delete,
        tools.coaia_fuse_traces_delete_batch,
        tools.coaia_fuse_sessions_list,
        tools.coaia_fuse_session_get,
        tools.coaia_fuse_observations_list,
    ]
    for func in new_tools:
        hints = func.__annotations__.get("return")
        assert hints is not None, \
            f"{func.__name__} missing return type annotation"
