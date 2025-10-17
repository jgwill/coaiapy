"""
Tests for coaiapy-mcp prompts module
"""

import pytest
from coaiapy_mcp.prompts import (
    get_prompt,
    list_prompts,
    render_prompt,
    PROMPTS
)


def test_list_prompts():
    """Test that list_prompts returns all prompt IDs"""
    prompt_ids = list_prompts()
    
    assert isinstance(prompt_ids, list)
    assert len(prompt_ids) > 0
    assert "mia_miette_duo" in prompt_ids
    assert "create_observability_pipeline" in prompt_ids
    assert "analyze_audio_workflow" in prompt_ids


def test_get_prompt_valid():
    """Test getting a valid prompt"""
    prompt = get_prompt("mia_miette_duo")
    
    assert prompt is not None
    assert "name" in prompt
    assert "description" in prompt
    assert "template" in prompt
    assert "arguments" in prompt


def test_get_prompt_invalid():
    """Test getting an invalid prompt"""
    prompt = get_prompt("nonexistent_prompt")
    
    assert prompt is None


def test_render_prompt_with_args():
    """Test rendering a prompt with arguments"""
    rendered = render_prompt(
        "mia_miette_duo",
        task_context="Test task",
        technical_details="Test details",
        creative_goal="Test goal",
        mia_analysis_placeholder="Test analysis",
        miette_reflection_placeholder="Test reflection"
    )
    
    assert isinstance(rendered, str)
    assert "Test task" in rendered
    assert "Test details" in rendered
    assert "Test goal" in rendered
    assert "Mia" in rendered
    assert "Miette" in rendered


def test_render_prompt_missing_args():
    """Test rendering a prompt with missing arguments"""
    rendered = render_prompt(
        "mia_miette_duo",
        task_context="Test task"
        # Missing required arguments
    )
    
    assert isinstance(rendered, str)
    assert "Error" in rendered or "Missing" in rendered


def test_prompt_structure():
    """Test that all prompts have required structure"""
    for prompt_id, prompt_data in PROMPTS.items():
        assert "name" in prompt_data
        assert "description" in prompt_data
        assert "template" in prompt_data
        assert "arguments" in prompt_data
        
        # Verify arguments structure
        for arg in prompt_data["arguments"]:
            assert "name" in arg
            assert "description" in arg
            assert "required" in arg


def test_observability_pipeline_prompt():
    """Test the observability pipeline prompt"""
    prompt = get_prompt("create_observability_pipeline")
    
    assert prompt is not None
    assert "Langfuse" in prompt["description"]
    
    rendered = render_prompt(
        "create_observability_pipeline",
        trace_name="Test Pipeline",
        user_id="test_user",
        steps="step1, step2, step3"
    )
    
    assert "Test Pipeline" in rendered
    assert "test_user" in rendered
    assert "step1" in rendered


def test_audio_workflow_prompt():
    """Test the audio workflow prompt"""
    prompt = get_prompt("analyze_audio_workflow")
    
    assert prompt is not None
    assert "audio" in prompt["description"].lower()
    
    rendered = render_prompt(
        "analyze_audio_workflow",
        file_path="/path/to/audio.mp3",
        summary_style="concise"
    )
    
    assert "/path/to/audio.mp3" in rendered
    assert "concise" in rendered
