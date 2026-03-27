"""
Unit tests for prompt version management MCP tools.

Tests coaia_fuse_prompts_get (version/label), coaia_fuse_prompts_create,
and coaia_fuse_prompt_version_labels_update using mocked Langfuse API calls.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coaiapy_mcp import tools


# ============================================================================
# Fixtures
# ============================================================================

SAMPLE_PROMPT_DATA = {
    "name": "test-prompt",
    "version": 3,
    "prompt": "You are a helpful assistant for {{task}}.",
    "type": "text",
    "labels": ["production"],
    "tags": ["v1", "assistant"],
    "config": {"temperature": 0.7, "model": "gpt-4"},
}

SAMPLE_CREATED_PROMPT = {
    "name": "new-prompt",
    "version": 1,
    "prompt": "Summarize the following: {{input}}",
    "type": "text",
    "labels": ["staging"],
    "tags": ["summarizer"],
    "config": {},
}


# ============================================================================
# coaia_fuse_prompts_get — version/label parameter tests
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_with_version(mock_get_prompt):
    """Test getting a prompt by specific version number."""
    mock_get_prompt.return_value = SAMPLE_PROMPT_DATA

    result = await tools.coaia_fuse_prompts_get(name="test-prompt", version=3)

    assert result["success"] is True
    assert result["prompt"] == SAMPLE_PROMPT_DATA
    mock_get_prompt.assert_called_once_with(
        prompt_name="test-prompt", label=None, version=3
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_with_label(mock_get_prompt):
    """Test getting a prompt by deployment label (e.g. 'production')."""
    mock_get_prompt.return_value = SAMPLE_PROMPT_DATA

    result = await tools.coaia_fuse_prompts_get(name="test-prompt", label="production")

    assert result["success"] is True
    assert result["prompt"] == SAMPLE_PROMPT_DATA
    mock_get_prompt.assert_called_once_with(
        prompt_name="test-prompt", label="production", version=None
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_with_staging_label(mock_get_prompt):
    """Test getting a prompt with 'staging' label."""
    staging_data = {**SAMPLE_PROMPT_DATA, "labels": ["staging"], "version": 2}
    mock_get_prompt.return_value = staging_data

    result = await tools.coaia_fuse_prompts_get(name="test-prompt", label="staging")

    assert result["success"] is True
    assert result["prompt"]["labels"] == ["staging"]
    mock_get_prompt.assert_called_once_with(
        prompt_name="test-prompt", label="staging", version=None
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_default_no_version_no_label(mock_get_prompt):
    """Test default behavior when neither version nor label is provided."""
    mock_get_prompt.return_value = SAMPLE_PROMPT_DATA

    result = await tools.coaia_fuse_prompts_get(name="test-prompt")

    assert result["success"] is True
    mock_get_prompt.assert_called_once_with(
        prompt_name="test-prompt", label=None, version=None
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_version_and_label_both_passed(mock_get_prompt):
    """Test that both version and label can be passed (version takes precedence in cofuse)."""
    mock_get_prompt.return_value = SAMPLE_PROMPT_DATA

    result = await tools.coaia_fuse_prompts_get(
        name="test-prompt", label="production", version=3
    )

    assert result["success"] is True
    mock_get_prompt.assert_called_once_with(
        prompt_name="test-prompt", label="production", version=3
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_api_error(mock_get_prompt):
    """Test error handling when cofuse raises an exception."""
    mock_get_prompt.side_effect = Exception("Prompt 'nonexistent' not found")

    result = await tools.coaia_fuse_prompts_get(name="nonexistent")

    assert result["success"] is False
    assert "error" in result
    assert "nonexistent" in result["error"]


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_get_prompt')
async def test_prompts_get_invalid_version_error(mock_get_prompt):
    """Test error when invalid version number is requested."""
    mock_get_prompt.side_effect = Exception("Version 999 not found for prompt 'test-prompt'")

    result = await tools.coaia_fuse_prompts_get(name="test-prompt", version=999)

    assert result["success"] is False
    assert "error" in result
    assert "999" in result["error"]


@pytest.mark.asyncio
async def test_prompts_get_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_prompts_get(name="test-prompt")

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_prompts_create — new prompt version tests
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_create_prompt')
async def test_prompts_create_basic(mock_create):
    """Test basic prompt creation with name and content only."""
    mock_create.return_value = SAMPLE_CREATED_PROMPT

    result = await tools.coaia_fuse_prompts_create(
        name="new-prompt",
        content="Summarize the following: {{input}}"
    )

    assert result["success"] is True
    assert result["prompt"] == SAMPLE_CREATED_PROMPT
    mock_create.assert_called_once_with(
        prompt_name="new-prompt",
        content="Summarize the following: {{input}}",
        prompt_type="text",
        labels=None,
        tags=None,
        commit_message=None,
        config=None,
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_create_prompt')
async def test_prompts_create_with_all_params(mock_create):
    """Test prompt creation with all optional parameters."""
    full_prompt = {
        **SAMPLE_CREATED_PROMPT,
        "labels": ["production", "staging"],
        "tags": ["v2", "summarizer"],
        "config": {"temperature": 0.5, "model": "gpt-4o"},
    }
    mock_create.return_value = full_prompt

    result = await tools.coaia_fuse_prompts_create(
        name="new-prompt",
        content="Summarize: {{input}}",
        prompt_type="text",
        labels=["production", "staging"],
        tags=["v2", "summarizer"],
        commit_message="Initial version with dual labels",
        config={"temperature": 0.5, "model": "gpt-4o"},
    )

    assert result["success"] is True
    assert result["prompt"]["labels"] == ["production", "staging"]
    mock_create.assert_called_once_with(
        prompt_name="new-prompt",
        content="Summarize: {{input}}",
        prompt_type="text",
        labels=["production", "staging"],
        tags=["v2", "summarizer"],
        commit_message="Initial version with dual labels",
        config={"temperature": 0.5, "model": "gpt-4o"},
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_create_prompt')
async def test_prompts_create_chat_type(mock_create):
    """Test creating a chat-type prompt."""
    chat_prompt = {
        "name": "chat-prompt",
        "version": 1,
        "type": "chat",
        "prompt": '[{"role": "system", "content": "You are helpful."}]',
    }
    mock_create.return_value = chat_prompt

    result = await tools.coaia_fuse_prompts_create(
        name="chat-prompt",
        content='[{"role": "system", "content": "You are helpful."}]',
        prompt_type="chat",
    )

    assert result["success"] is True
    mock_create.assert_called_once()
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["prompt_type"] == "chat"


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_create_prompt')
async def test_prompts_create_with_labels(mock_create):
    """Test that labels are correctly forwarded to cofuse."""
    mock_create.return_value = {**SAMPLE_CREATED_PROMPT, "labels": ["canary"]}

    result = await tools.coaia_fuse_prompts_create(
        name="new-prompt",
        content="Hello {{name}}",
        labels=["canary"],
    )

    assert result["success"] is True
    call_kwargs = mock_create.call_args[1]
    assert call_kwargs["labels"] == ["canary"]


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_create_prompt')
async def test_prompts_create_api_error(mock_create):
    """Test error handling during prompt creation."""
    mock_create.side_effect = Exception("Langfuse API rate limit exceeded")

    result = await tools.coaia_fuse_prompts_create(
        name="new-prompt",
        content="content"
    )

    assert result["success"] is False
    assert "error" in result
    assert "rate limit" in result["error"].lower()


@pytest.mark.asyncio
async def test_prompts_create_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_prompts_create(
            name="new-prompt", content="content"
        )

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# coaia_fuse_prompt_version_labels_update tests
# ============================================================================

@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_prompt_version_labels')
async def test_labels_update_basic(mock_update):
    """Test basic label update on a prompt version."""
    mock_update.return_value = {**SAMPLE_PROMPT_DATA, "labels": ["production"]}

    result = await tools.coaia_fuse_prompt_version_labels_update(
        name="test-prompt",
        version=3,
        labels=["production"]
    )

    assert result["success"] is True
    assert result["prompt"]["labels"] == ["production"]
    mock_update.assert_called_once_with(
        prompt_name="test-prompt",
        version=3,
        new_labels=["production"],
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_prompt_version_labels')
async def test_labels_update_multiple_labels(mock_update):
    """Test updating with multiple labels."""
    mock_update.return_value = {
        **SAMPLE_PROMPT_DATA,
        "labels": ["production", "reviewed"],
    }

    result = await tools.coaia_fuse_prompt_version_labels_update(
        name="test-prompt",
        version=3,
        labels=["production", "reviewed"]
    )

    assert result["success"] is True
    mock_update.assert_called_once_with(
        prompt_name="test-prompt",
        version=3,
        new_labels=["production", "reviewed"],
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_prompt_version_labels')
async def test_labels_update_clear_labels(mock_update):
    """Test clearing all labels by passing empty list."""
    mock_update.return_value = {**SAMPLE_PROMPT_DATA, "labels": []}

    result = await tools.coaia_fuse_prompt_version_labels_update(
        name="test-prompt",
        version=3,
        labels=[]
    )

    assert result["success"] is True
    mock_update.assert_called_once_with(
        prompt_name="test-prompt",
        version=3,
        new_labels=[],
    )


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_prompt_version_labels')
async def test_labels_update_reserved_latest_error(mock_update):
    """Test error when trying to set reserved 'latest' label."""
    mock_update.side_effect = Exception(
        "Label 'latest' is reserved by Langfuse"
    )

    result = await tools.coaia_fuse_prompt_version_labels_update(
        name="test-prompt",
        version=3,
        labels=["latest"]
    )

    assert result["success"] is False
    assert "error" in result
    assert "latest" in result["error"].lower()


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_prompt_version_labels')
async def test_labels_update_invalid_version_error(mock_update):
    """Test error when version doesn't exist."""
    mock_update.side_effect = Exception(
        "Version 999 not found for prompt 'test-prompt'"
    )

    result = await tools.coaia_fuse_prompt_version_labels_update(
        name="test-prompt",
        version=999,
        labels=["production"]
    )

    assert result["success"] is False
    assert "999" in result["error"]


@pytest.mark.asyncio
@patch.object(tools, 'LANGFUSE_AVAILABLE', True)
@patch('coaiapy_mcp.tools.cofuse_update_prompt_version_labels')
async def test_labels_update_api_error(mock_update):
    """Test generic API error during label update."""
    mock_update.side_effect = Exception("Network timeout")

    result = await tools.coaia_fuse_prompt_version_labels_update(
        name="test-prompt",
        version=1,
        labels=["staging"]
    )

    assert result["success"] is False
    assert "error" in result
    assert "Network timeout" in result["error"]


@pytest.mark.asyncio
async def test_labels_update_langfuse_unavailable():
    """Test graceful degradation when Langfuse is not available."""
    original = tools.LANGFUSE_AVAILABLE
    try:
        tools.LANGFUSE_AVAILABLE = False
        result = await tools.coaia_fuse_prompt_version_labels_update(
            name="test-prompt",
            version=1,
            labels=["production"]
        )

        assert result["success"] is False
        assert "not available" in result["error"].lower()
    finally:
        tools.LANGFUSE_AVAILABLE = original


# ============================================================================
# Registry completeness check
# ============================================================================

def test_prompt_tools_in_registry():
    """Verify all prompt tools are registered in the TOOLS dict."""
    prompt_tools = [
        "coaia_fuse_prompts_list",
        "coaia_fuse_prompts_get",
        "coaia_fuse_prompts_create",
        "coaia_fuse_prompt_version_labels_update",
    ]
    for tool_name in prompt_tools:
        assert tool_name in tools.TOOLS, f"Tool {tool_name} not in TOOLS registry"


def test_prompt_tool_functions_are_async():
    """Verify all prompt tool functions are async."""
    import inspect

    prompt_tools = [
        "coaia_fuse_prompts_list",
        "coaia_fuse_prompts_get",
        "coaia_fuse_prompts_create",
        "coaia_fuse_prompt_version_labels_update",
    ]
    for tool_name in prompt_tools:
        func = tools.TOOLS[tool_name]
        assert inspect.iscoroutinefunction(func), \
            f"Tool {tool_name} is not an async function"
