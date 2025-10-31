#!/usr/bin/env python3
"""
Example script demonstrating coaiapy-mcp tools usage.

This shows how to use the tools directly (without MCP server).
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coaiapy_mcp import tools, resources, prompts


async def demo_redis():
    """Demonstrate Redis tools."""
    print("\n=== Redis Tools Demo ===\n")
    
    # Stash a value
    print("Stashing value to Redis...")
    result = await tools.coaia_tash("demo_key", "demo_value")
    print(f"Result: {result}")
    
    # Fetch the value
    print("\nFetching value from Redis...")
    result = await tools.coaia_fetch("demo_key")
    print(f"Result: {result}")


async def demo_langfuse():
    """Demonstrate Langfuse tools."""
    print("\n=== Langfuse Tools Demo ===\n")
    
    # Create a trace
    print("Creating Langfuse trace...")
    result = await tools.coaia_fuse_trace_create(
        trace_id="demo-trace-001",
        user_id="demo_user",
        name="Demo Trace",
        metadata={"source": "demo_script"}
    )
    print(f"Result: {result}")
    
    # Add an observation
    print("\nAdding observation to trace...")
    result = await tools.coaia_fuse_add_observation(
        observation_id="demo-obs-001",
        trace_id="demo-trace-001",
        name="Demo Observation",
        observation_type="SPAN"
    )
    print(f"Result: {result}")
    
    # List prompts
    print("\nListing Langfuse prompts...")
    result = await tools.coaia_fuse_prompts_list()
    print(f"Result: {result}")


async def demo_templates():
    """Demonstrate template resources."""
    print("\n=== Template Resources Demo ===\n")
    
    # List templates
    print("Listing pipeline templates...")
    result = await resources.list_templates()
    print(f"Result: {result}")


def demo_prompts():
    """Demonstrate prompt rendering."""
    print("\n=== Prompts Demo ===\n")
    
    # List prompts
    print("Available prompts:")
    prompt_list = prompts.list_prompts()
    for prompt in prompt_list:
        print(f"  - {prompt['id']}: {prompt['name']}")
    
    # Render Mia & Miette prompt
    print("\nRendering Mia & Miette prompt...")
    rendered = prompts.render_prompt(
        "mia_miette_duo",
        {
            "task_context": "Build an observability system",
            "technical_details": "Using Langfuse for traces and observations",
            "creative_goal": "Create narrative-driven system monitoring"
        }
    )
    print("Rendered prompt (first 500 chars):")
    print(rendered[:500] + "..." if len(rendered) > 500 else rendered)


async def main():
    """Run all demos."""
    print("=" * 70)
    print("coaiapy-mcp Tools Demonstration")
    print("=" * 70)
    
    try:
        # Synchronous demos
        demo_prompts()
        
        # Async demos
        await demo_templates()
        await demo_redis()
        await demo_langfuse()
        
        print("\n" + "=" * 70)
        print("Demo completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
