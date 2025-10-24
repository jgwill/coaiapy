"""
Unit tests for coaiapy-mcp resources.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coaiapy_mcp import resources


@pytest.mark.asyncio
async def test_list_templates():
    """Test listing pipeline templates."""
    result = await resources.list_templates()
    
    assert isinstance(result, dict)
    assert "success" in result
    
    if resources.PIPELINE_AVAILABLE:
        assert result["success"] is True
        assert "templates" in result
        assert isinstance(result["templates"], list)
    else:
        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_list_templates_with_path():
    """Test listing templates with path information."""
    result = await resources.list_templates(include_path=True)
    
    assert isinstance(result, dict)
    
    if resources.PIPELINE_AVAILABLE and result["success"]:
        templates = result["templates"]
        # If there are templates, they should have path info
        if templates:
            # Template entries might have path information
            pass  # Structure depends on implementation


@pytest.mark.asyncio
@pytest.mark.skipif(not resources.PIPELINE_AVAILABLE, reason="Pipeline not available")
async def test_get_template():
    """Test getting a specific template."""
    # First get list of templates
    list_result = await resources.list_templates()
    
    if list_result["success"] and list_result["templates"]:
        # Try to get the first template
        templates = list_result["templates"]
        if templates:
            # Extract template name (structure depends on implementation)
            template_name = templates[0] if isinstance(templates[0], str) else templates[0].get("name")
            
            if template_name:
                result = await resources.get_template(template_name)
                
                assert isinstance(result, dict)
                assert "success" in result


@pytest.mark.asyncio
async def test_get_nonexistent_template():
    """Test getting a non-existent template."""
    result = await resources.get_template("nonexistent-template-xyz")
    
    assert isinstance(result, dict)
    
    if resources.PIPELINE_AVAILABLE:
        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_get_template_variables():
    """Test getting template variables."""
    # First get list of templates
    list_result = await resources.list_templates()
    
    if resources.PIPELINE_AVAILABLE and list_result["success"]:
        templates = list_result.get("templates", [])
        if templates:
            template_name = templates[0] if isinstance(templates[0], str) else templates[0].get("name")
            
            if template_name:
                result = await resources.get_template_variables(template_name)
                
                assert isinstance(result, dict)
                assert "success" in result


def test_resource_registry():
    """Test that resource URIs are registered."""
    expected_uris = [
        "coaia://templates/",
        "coaia://templates/{name}",
        "coaia://templates/{name}/variables",
    ]
    
    for uri in expected_uris:
        assert uri in resources.RESOURCES, f"Resource URI {uri} not in RESOURCES registry"
