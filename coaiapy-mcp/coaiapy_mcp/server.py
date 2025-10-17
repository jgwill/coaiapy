"""
MCP Server implementation for coaiapy

This module implements the Model Context Protocol server that exposes coaiapy
functionality through standardized tools, resources, and prompts.
"""

import asyncio
import sys
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    PromptMessage,
    GetPromptResult,
)

from . import tools, resources, prompts


def create_server() -> Server:
    """
    Create and configure the MCP server with all tools, resources, and prompts.
    
    Returns:
        Configured MCP Server instance
    """
    server = Server("coaiapy-mcp")
    
    # ========================================================================
    # Register Tools
    # ========================================================================
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            # Redis Operations
            Tool(
                name="coaia_tash",
                description="Stash key-value pair to Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Redis key"},
                        "value": {"type": "string", "description": "Value to store"}
                    },
                    "required": ["key", "value"]
                }
            ),
            Tool(
                name="coaia_fetch",
                description="Fetch value from Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Redis key to fetch"}
                    },
                    "required": ["key"]
                }
            ),
            
            # Langfuse Traces
            Tool(
                name="coaia_fuse_trace_create",
                description="Create new Langfuse trace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trace_id": {"type": "string", "description": "Unique trace identifier"},
                        "user_id": {"type": "string", "description": "User identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"},
                        "name": {"type": "string", "description": "Trace name"},
                        "metadata": {"type": "object", "description": "Metadata dictionary"}
                    },
                    "required": ["trace_id"]
                }
            ),
            Tool(
                name="coaia_fuse_add_observation",
                description="Add observation to Langfuse trace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "observation_id": {"type": "string", "description": "Unique observation identifier"},
                        "trace_id": {"type": "string", "description": "Parent trace identifier"},
                        "name": {"type": "string", "description": "Observation name"},
                        "type": {"type": "string", "description": "Observation type (SPAN, EVENT, GENERATION)"},
                        "parent_id": {"type": "string", "description": "Parent observation ID"},
                        "metadata": {"type": "object", "description": "Metadata dictionary"}
                    },
                    "required": ["observation_id", "trace_id", "name"]
                }
            ),
            Tool(
                name="coaia_fuse_add_observations_batch",
                description="Batch add observations to Langfuse trace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trace_id": {"type": "string", "description": "Parent trace identifier"},
                        "observations": {
                            "type": "array",
                            "description": "List of observation dictionaries",
                            "items": {"type": "object"}
                        }
                    },
                    "required": ["trace_id", "observations"]
                }
            ),
            Tool(
                name="coaia_fuse_trace_view",
                description="View Langfuse trace tree with JSON output",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trace_id": {"type": "string", "description": "Trace identifier to view"}
                    },
                    "required": ["trace_id"]
                }
            ),
            
            # Langfuse Prompts
            Tool(
                name="coaia_fuse_prompts_list",
                description="List all Langfuse prompts",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="coaia_fuse_prompts_get",
                description="Get specific Langfuse prompt",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Prompt name"},
                        "label": {"type": "string", "description": "Prompt label/version"}
                    },
                    "required": ["name"]
                }
            ),
            
            # Langfuse Datasets
            Tool(
                name="coaia_fuse_datasets_list",
                description="List all Langfuse datasets",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="coaia_fuse_datasets_get",
                description="Get specific Langfuse dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Dataset name"}
                    },
                    "required": ["name"]
                }
            ),
            
            # Langfuse Score Configurations
            Tool(
                name="coaia_fuse_score_configs_list",
                description="List all Langfuse score configurations",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="coaia_fuse_score_configs_get",
                description="Get specific Langfuse score configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Score configuration name"}
                    },
                    "required": ["name"]
                }
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute a tool and return its result."""
        tool_func = tools.TOOLS.get(name)
        
        if not tool_func:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
        
        try:
            result = await tool_func(**arguments)
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing tool '{name}': {str(e)}"
            )]
    
    # ========================================================================
    # Register Resources
    # ========================================================================
    
    @server.list_resources()
    async def list_resources() -> list[Dict[str, Any]]:
        """List all available resources."""
        return [
            {
                "uri": "coaia://templates/",
                "name": "Pipeline Templates List",
                "mimeType": "application/json",
                "description": "List of all available pipeline templates"
            },
            {
                "uri": "coaia://templates/{name}",
                "name": "Pipeline Template Details",
                "mimeType": "application/json",
                "description": "Specific pipeline template with variables and steps"
            }
        ]
    
    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI."""
        import json
        
        if uri == "coaia://templates/":
            result = await resources.list_templates()
            return json.dumps(result, indent=2)
        
        elif uri.startswith("coaia://templates/"):
            template_name = uri.replace("coaia://templates/", "")
            result = await resources.get_template(template_name)
            return json.dumps(result, indent=2)
        
        else:
            return json.dumps({
                "error": f"Unknown resource URI: {uri}"
            })
    
    # ========================================================================
    # Register Prompts
    # ========================================================================
    
    @server.list_prompts()
    async def list_prompts() -> list[Dict[str, Any]]:
        """List all available prompts."""
        prompt_list = []
        for prompt_id in prompts.list_prompts():
            prompt_data = prompts.get_prompt(prompt_id)
            prompt_list.append({
                "name": prompt_id,
                "description": prompt_data["description"],
                "arguments": prompt_data.get("arguments", [])
            })
        return prompt_list
    
    @server.get_prompt()
    async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> GetPromptResult:
        """Get a specific prompt with optional arguments."""
        prompt_data = prompts.get_prompt(name)
        
        if not prompt_data:
            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Error: Prompt '{name}' not found"
                        )
                    )
                ]
            )
        
        # Render prompt with arguments if provided
        if arguments:
            rendered = prompts.render_prompt(name, **arguments)
        else:
            # Return template with placeholders
            rendered = prompt_data["template"]
        
        return GetPromptResult(
            description=prompt_data["description"],
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=rendered
                    )
                )
            ]
        )
    
    return server


async def main():
    """Main entry point for the MCP server."""
    server = create_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def cli_main():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
