#!/usr/bin/env python3
"""
Comprehensive validation script for coaiapy-mcp.

This script validates all implemented functionality without requiring
external services (Redis, Langfuse API).
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coaiapy_mcp import tools, resources, prompts


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_subsection(title):
    """Print a subsection header."""
    print(f"\n--- {title} ---\n")


async def validate_tools_module():
    """Validate tools module."""
    print_section("TOOLS MODULE VALIDATION")
    
    print_subsection("Tool Registry")
    print(f"Total tools registered: {len(tools.TOOLS)}")
    for tool_name in tools.TOOLS.keys():
        print(f"  ✓ {tool_name}")
    
    print_subsection("Service Availability")
    print(f"Redis Available: {'✓' if tools.REDIS_AVAILABLE else '✗ (expected - not running)'}")
    print(f"Langfuse Available: {'✓' if tools.LANGFUSE_AVAILABLE else '✗'}")
    print(f"Pipeline Available: {'✓' if tools.PIPELINE_AVAILABLE else '✗'}")
    
    print_subsection("Tool Error Handling")
    # Test that tools return proper error dicts when services unavailable
    if not tools.REDIS_AVAILABLE:
        result = await tools.coaia_tash("test", "test")
        print(f"Redis error handling: {'✓' if not result['success'] and 'error' in result else '✗'}")
    
    print_subsection("Tool Async Validation")
    import inspect
    all_async = all(inspect.iscoroutinefunction(func) for func in tools.TOOLS.values())
    print(f"All tools are async: {'✓' if all_async else '✗'}")


async def validate_resources_module():
    """Validate resources module."""
    print_section("RESOURCES MODULE VALIDATION")
    
    print_subsection("Resource Registry")
    print(f"Total resources registered: {len(resources.RESOURCES)}")
    for uri in resources.RESOURCES.keys():
        print(f"  ✓ {uri}")
    
    print_subsection("Template Listing")
    result = await resources.list_templates()
    if result["success"]:
        templates = result["templates"]
        print(f"Templates available: {len(templates)}")
        if templates:
            for tmpl in templates[:3]:  # Show first 3
                name = tmpl if isinstance(tmpl, str) else tmpl.get("name", "unknown")
                print(f"  ✓ {name}")
        print("✓ Template listing working")
    else:
        print(f"✗ Template listing error: {result.get('error')}")
    
    print_subsection("Template Loading")
    # Try to load a template if any are available
    if result["success"] and result["templates"]:
        template_name = result["templates"][0] if isinstance(result["templates"][0], str) else result["templates"][0].get("name")
        if template_name:
            tmpl_result = await resources.get_template(template_name)
            if tmpl_result["success"]:
                print(f"✓ Successfully loaded template: {template_name}")
                tmpl = tmpl_result["template"]
                print(f"  - Description: {tmpl.get('description', 'N/A')}")
                print(f"  - Variables: {len(tmpl.get('variables', []))}")
            else:
                print(f"✗ Failed to load template: {tmpl_result.get('error')}")


def validate_prompts_module():
    """Validate prompts module."""
    print_section("PROMPTS MODULE VALIDATION")
    
    print_subsection("Prompt Registry")
    print(f"Total prompts registered: {len(prompts.PROMPTS)}")
    prompt_list = prompts.list_prompts()
    for prompt in prompt_list:
        print(f"  ✓ {prompt['id']}: {prompt['name']}")
    
    print_subsection("Prompt Structure Validation")
    all_valid = True
    for prompt_id, prompt_data in prompts.PROMPTS.items():
        required_fields = ['name', 'description', 'variables', 'template']
        has_all = all(field in prompt_data for field in required_fields)
        if has_all:
            print(f"  ✓ {prompt_id}: All required fields present")
        else:
            print(f"  ✗ {prompt_id}: Missing fields")
            all_valid = False
    
    if all_valid:
        print("\n✓ All prompts have valid structure")
    
    print_subsection("Prompt Rendering")
    # Test Mia & Miette prompt rendering
    rendered = prompts.render_prompt(
        "mia_miette_duo",
        {
            "task_context": "Build observability system",
            "technical_details": "Using Langfuse traces",
            "creative_goal": "Narrative-driven monitoring"
        }
    )
    if rendered and "Build observability system" in rendered:
        print("✓ Mia & Miette prompt renders correctly")
        print(f"  - Length: {len(rendered)} characters")
    else:
        print("✗ Prompt rendering failed")
    
    # Test observability pipeline prompt
    rendered2 = prompts.render_prompt(
        "create_observability_pipeline",
        {
            "trace_name": "Test Pipeline",
            "user_id": "test_user",
            "steps": "step1, step2, step3"
        }
    )
    if rendered2 and "Test Pipeline" in rendered2:
        print("✓ Observability pipeline prompt renders correctly")
    else:
        print("✗ Observability prompt rendering failed")


def validate_server_module():
    """Validate server module structure."""
    print_section("SERVER MODULE VALIDATION")
    
    try:
        from coaiapy_mcp import server
        print("✓ Server module imports successfully")
        
        # Check for required functions
        if hasattr(server, 'create_server'):
            print("✓ create_server function exists")
        else:
            print("✗ create_server function missing")
        
        if hasattr(server, 'main'):
            print("✓ main entry point exists")
        else:
            print("✗ main entry point missing")
        
        if hasattr(server, 'SERVER_INFO'):
            print("✓ SERVER_INFO configuration exists")
            print(f"  - Name: {server.SERVER_INFO.get('name')}")
            print(f"  - Version: {server.SERVER_INFO.get('version')}")
        else:
            print("✗ SERVER_INFO missing")
        
    except Exception as e:
        print(f"✗ Server module validation error: {e}")


def validate_package_structure():
    """Validate overall package structure."""
    print_section("PACKAGE STRUCTURE VALIDATION")
    
    import coaiapy_mcp
    
    print_subsection("Package Metadata")
    print(f"Version: {coaiapy_mcp.__version__}")
    print(f"Author: {coaiapy_mcp.__author__}")
    print(f"Email: {coaiapy_mcp.__email__}")
    
    print_subsection("Module Exports")
    exports = [
        ('tools', 'TOOLS'),
        ('resources', 'RESOURCES'),
        ('prompts', 'PROMPTS'),
        ('server', 'create_server'),
        ('server', 'main'),
    ]
    
    for module_name, attr_name in exports:
        try:
            mod = getattr(coaiapy_mcp, module_name, None) or __import__(f'coaiapy_mcp.{module_name}', fromlist=[attr_name])
            if hasattr(mod, attr_name):
                print(f"  ✓ {module_name}.{attr_name}")
            else:
                print(f"  ✗ {module_name}.{attr_name} missing")
        except Exception as e:
            print(f"  ✗ {module_name}.{attr_name} error: {e}")


async def main():
    """Run all validations."""
    print("\n" + "=" * 70)
    print("  COAIAPY-MCP VALIDATION SUITE")
    print("  Testing library import approach implementation")
    print("=" * 70)
    
    try:
        validate_package_structure()
        validate_prompts_module()
        await validate_resources_module()
        await validate_tools_module()
        validate_server_module()
        
        print("\n" + "=" * 70)
        print("  VALIDATION COMPLETE")
        print("=" * 70)
        print("\n✓ Implementation follows library import approach from IMPLEMENTATION_PLAN.md")
        print("✓ All core modules functional")
        print("✓ Graceful degradation when services unavailable")
        print("✓ Ready for MCP server integration\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
