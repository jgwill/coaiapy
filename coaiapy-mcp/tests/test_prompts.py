"""
Unit tests for coaiapy-mcp prompts.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coaiapy_mcp import prompts


def test_list_prompts():
    """Test listing all prompts."""
    prompt_list = prompts.list_prompts()
    
    assert isinstance(prompt_list, list)
    assert len(prompt_list) > 0
    
    # Check structure
    for prompt in prompt_list:
        assert "id" in prompt
        assert "name" in prompt
        assert "description" in prompt
        assert "variables" in prompt


def test_get_prompt_mia_miette():
    """Test getting Mia & Miette prompt."""
    prompt = prompts.get_prompt("mia_miette_duo")
    
    assert prompt is not None
    assert isinstance(prompt, dict)
    assert "name" in prompt
    assert "description" in prompt
    assert "variables" in prompt
    assert "template" in prompt
    
    # Check variables
    variables = prompt["variables"]
    var_names = [v["name"] for v in variables]
    assert "task_context" in var_names
    assert "technical_details" in var_names
    assert "creative_goal" in var_names


def test_get_prompt_observability():
    """Test getting observability pipeline prompt."""
    prompt = prompts.get_prompt("create_observability_pipeline")
    
    assert prompt is not None
    assert isinstance(prompt, dict)
    
    variables = prompt["variables"]
    var_names = [v["name"] for v in variables]
    assert "trace_name" in var_names
    assert "user_id" in var_names
    assert "steps" in var_names


def test_get_prompt_audio():
    """Test getting audio workflow prompt."""
    prompt = prompts.get_prompt("analyze_audio_workflow")
    
    assert prompt is not None
    assert isinstance(prompt, dict)
    
    variables = prompt["variables"]
    var_names = [v["name"] for v in variables]
    assert "file_path" in var_names
    assert "summary_style" in var_names


def test_get_nonexistent_prompt():
    """Test getting a non-existent prompt."""
    prompt = prompts.get_prompt("nonexistent_prompt_xyz")
    
    assert prompt is None


def test_render_prompt_mia_miette():
    """Test rendering Mia & Miette prompt with variables."""
    variables = {
        "task_context": "Design a microservices architecture",
        "technical_details": "Event-driven system with message queues",
        "creative_goal": "Scalable narrative-driven platform",
    }
    
    rendered = prompts.render_prompt("mia_miette_duo", variables)
    
    assert rendered is not None
    assert isinstance(rendered, str)
    
    # Check that variables were substituted
    assert "Design a microservices architecture" in rendered
    assert "Event-driven system with message queues" in rendered
    assert "Scalable narrative-driven platform" in rendered
    
    # Check that Mia and Miette sections are present
    assert "Mia" in rendered or "🧠" in rendered
    assert "Miette" in rendered or "🌸" in rendered


def test_render_prompt_observability():
    """Test rendering observability prompt with variables."""
    variables = {
        "trace_name": "ETL Pipeline",
        "user_id": "data_engineer",
        "steps": "extract, transform, load",
    }
    
    rendered = prompts.render_prompt("create_observability_pipeline", variables)
    
    assert rendered is not None
    assert isinstance(rendered, str)
    
    # Check variable substitution
    assert "ETL Pipeline" in rendered
    assert "data_engineer" in rendered
    assert "extract, transform, load" in rendered


def test_render_prompt_audio():
    """Test rendering audio workflow prompt with variables."""
    variables = {
        "file_path": "/path/to/audio.mp3",
        "summary_style": "narrative",
    }
    
    rendered = prompts.render_prompt("analyze_audio_workflow", variables)
    
    assert rendered is not None
    assert isinstance(rendered, str)
    
    # Check variable substitution
    assert "/path/to/audio.mp3" in rendered
    assert "narrative" in rendered


def test_render_prompt_partial_variables():
    """Test rendering with partial variables (some missing)."""
    variables = {
        "task_context": "Build a system",
        # Missing: technical_details, creative_goal
    }
    
    rendered = prompts.render_prompt("mia_miette_duo", variables)
    
    assert rendered is not None
    
    # Should substitute available variables
    assert "Build a system" in rendered
    
    # Missing variables will still have placeholders
    assert "{{technical_details}}" in rendered
    assert "{{creative_goal}}" in rendered


def test_render_nonexistent_prompt():
    """Test rendering a non-existent prompt."""
    rendered = prompts.render_prompt("nonexistent_prompt", {})
    
    assert rendered is None


def test_prompt_registry_completeness():
    """Test that all expected prompts are in the registry."""
    expected_prompts = [
        "mia_miette_duo",
        "create_observability_pipeline",
        "analyze_audio_workflow",
    ]
    
    for prompt_id in expected_prompts:
        assert prompt_id in prompts.PROMPTS, f"Prompt {prompt_id} not in PROMPTS registry"


def test_all_prompts_have_required_fields():
    """Test that all prompts have required structure."""
    for prompt_id, prompt_data in prompts.PROMPTS.items():
        assert "name" in prompt_data, f"Prompt {prompt_id} missing 'name'"
        assert "description" in prompt_data, f"Prompt {prompt_id} missing 'description'"
        assert "variables" in prompt_data, f"Prompt {prompt_id} missing 'variables'"
        assert "template" in prompt_data, f"Prompt {prompt_id} missing 'template'"
        
        # Check variables structure
        for var in prompt_data["variables"]:
            assert "name" in var
            assert "type" in var
            assert "description" in var
            assert "required" in var
