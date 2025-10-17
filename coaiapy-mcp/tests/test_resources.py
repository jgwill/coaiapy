"""
Tests for coaiapy-mcp resources module
"""

import pytest
from coaiapy_mcp.resources import list_templates, get_template


@pytest.mark.asyncio
async def test_list_templates_structure():
    """Test that list_templates returns correct structure"""
    result = await list_templates()
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "templates" in result
    assert isinstance(result["templates"], list)


@pytest.mark.asyncio
async def test_get_template_structure():
    """Test that get_template returns correct structure"""
    # Try to get a template (may not exist in test environment)
    result = await get_template("simple-trace")
    
    assert isinstance(result, dict)
    # Either success with template data or error
    assert "success" in result or "error" in result
