"""
MCP Resources implementation for coaiapy

This module provides resource providers for read-only access to coaiapy data
such as pipeline templates.
"""

import subprocess
import json
from typing import Dict, Any, List


async def list_templates() -> Dict[str, Any]:
    """
    List available pipeline templates from coaia CLI.
    
    Returns:
        Dict with templates list
    """
    result = subprocess.run(
        ["coaia", "pipeline", "list", "--json"],
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            return {
                "success": True,
                "templates": data.get("templates", [])
            }
        except json.JSONDecodeError:
            # Fallback: parse plain text output
            lines = result.stdout.strip().split('\n')
            templates = [line.strip() for line in lines if line.strip()]
            return {
                "success": True,
                "templates": templates
            }
    else:
        return {
            "success": False,
            "error": result.stderr.strip(),
            "templates": []
        }


async def get_template(name: str) -> Dict[str, Any]:
    """
    Get specific pipeline template details from coaia CLI.
    
    Args:
        name: Template name
        
    Returns:
        Dict with template data including variables and steps
    """
    result = subprocess.run(
        ["coaia", "pipeline", "show", name, "--json"],
        capture_output=True,
        text=True,
        check=False
    )
    
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
            "error": f"Template {name} not found: {result.stderr.strip()}"
        }


# Resource URI handlers
RESOURCES = {
    "coaia://templates/": list_templates,
    "coaia://templates/{name}": get_template,
}
