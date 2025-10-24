"""
MCP Resources implementation for coaiapy templates and environment.

Resources provide read-only access to:
- Pipeline templates (built-in and custom)
- Environment variables (global and project-specific)
"""

from typing import Dict, Any, List, Optional
import json

try:
    from coaiapy.pipeline import TemplateLoader
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    TemplateLoader = None


# ============================================================================
# Template Resources
# ============================================================================

async def list_templates(include_path: bool = False) -> Dict[str, Any]:
    """
    List all available pipeline templates.
    
    Args:
        include_path: Whether to include template file paths
        
    Returns:
        Dict with success status and list of templates/error
    """
    if not PIPELINE_AVAILABLE:
        return {
            "success": False,
            "error": "Pipeline engine is not available. Check coaiapy installation."
        }
    
    try:
        loader = TemplateLoader()
        templates = loader.list_templates(include_path=include_path)
        
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Template list error: {str(e)}"
        }


async def get_template(name: str) -> Dict[str, Any]:
    """
    Get specific pipeline template details.
    
    Args:
        name: Template name
        
    Returns:
        Dict with success status and template data/error
    """
    if not PIPELINE_AVAILABLE:
        return {
            "success": False,
            "error": "Pipeline engine is not available. Check coaiapy installation."
        }
    
    try:
        loader = TemplateLoader()
        template = loader.load_template(name)
        
        if template is None:
            return {
                "success": False,
                "error": f"Template '{name}' not found"
            }
        
        # Convert template to dict
        template_dict = {
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "author": template.author,
            "variables": [
                {
                    "name": var.name,
                    "type": var.type,
                    "description": var.description,
                    "required": var.required,
                    "default": var.default,
                }
                for var in template.variables
            ],
            "steps": template.steps,
        }
        
        return {
            "success": True,
            "template": template_dict
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Template get error: {str(e)}"
        }


async def get_template_variables(name: str) -> Dict[str, Any]:
    """
    Get list of variables for a specific template.
    
    Args:
        name: Template name
        
    Returns:
        Dict with success status and variables list/error
    """
    if not PIPELINE_AVAILABLE:
        return {
            "success": False,
            "error": "Pipeline engine is not available. Check coaiapy installation."
        }
    
    try:
        loader = TemplateLoader()
        template = loader.load_template(name)
        
        if template is None:
            return {
                "success": False,
                "error": f"Template '{name}' not found"
            }
        
        variables = [
            {
                "name": var.name,
                "type": var.type,
                "description": var.description,
                "required": var.required,
                "default": var.default,
            }
            for var in template.variables
        ]
        
        return {
            "success": True,
            "variables": variables
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Template variables error: {str(e)}"
        }


# ============================================================================
# Resource Registry
# ============================================================================

# Define resource URIs and their handlers
RESOURCES = {
    "coaia://templates/": list_templates,
    "coaia://templates/{name}": get_template,
    "coaia://templates/{name}/variables": get_template_variables,
}

__all__ = [
    "RESOURCES",
    "list_templates",
    "get_template",
    "get_template_variables",
]
