"""
MCP Server implementation for coaiapy.

This module implements the Model Context Protocol server that exposes
coaiapy's capabilities (tools, resources, prompts) to MCP-compatible LLMs.

The server uses direct library imports from coaiapy instead of subprocess
wrappers for better performance and error handling.

Configuration:
  COAIAPY_ENV_PATH: Custom path to .env file (default: .env in current directory)
                   Set via MCP server environment configuration.
                   Example: COAIAPY_ENV_PATH=/path/to/custom/.env
"""

import asyncio
import logging
from typing import Any, Dict, List
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("coaiapy-mcp")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    logger.error("MCP SDK not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False
    Server = None
    stdio_server = None
    types = None

from coaiapy_mcp import tools, resources, prompts
from coaiapy_mcp import __version__

# ============================================================================
# Server Configuration
# ============================================================================

SERVER_INFO = {
    "name": "coaiapy-mcp",
    "version": __version__,
    "description": "MCP wrapper for coaiapy observability toolkit",
    "capabilities": {
        "tools": True,
        "resources": True,
        "prompts": True,
    }
}


# ============================================================================
# MCP Server Setup
# ============================================================================

def create_server() -> Server:
    """
    Create and configure the MCP server.
    
    Returns:
        Configured MCP Server instance
    """
    if not MCP_AVAILABLE:
        raise RuntimeError("MCP SDK not available. Install with: pip install mcp")
    
    server = Server(SERVER_INFO["name"])
    
    # ========================================================================
    # Tool Registration
    # ========================================================================
    
    @server.list_tools()
    async def list_tools() -> List[types.Tool]:
        """List all available tools."""
        tool_definitions = []
        
        # Redis tools
        tool_definitions.append(types.Tool(
            name="coaia_tash",
            description="Stash key-value pair to Redis",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Redis key"},
                    "value": {"type": "string", "description": "Value to store"},
                },
                "required": ["key", "value"],
            }
        ))
        
        tool_definitions.append(types.Tool(
            name="coaia_fetch",
            description="Fetch value from Redis",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Redis key to fetch"},
                },
                "required": ["key"],
            }
        ))
        
        # Langfuse trace tools
        tool_definitions.append(types.Tool(
            name="coaia_fuse_trace_create",
            description="Create Langfuse trace for observability. IMPORTANT: Use 'input_data' for context/inputs and 'output_data' for results/outputs. Use 'metadata' only for additional tags/labels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string", "description": "Unique trace identifier"},
                    "user_id": {"type": "string", "description": "User identifier"},
                    "session_id": {"type": "string", "description": "Session identifier"},
                    "name": {"type": "string", "description": "Trace name"},
                    "input_data": {"type": ["object", "string", "array"], "description": "PREFERRED: The input/context data for this trace (e.g., user query, request parameters). Use this instead of metadata for actual data."},
                    "output_data": {"type": ["object", "string", "array"], "description": "PREFERRED: The output/result data for this trace (e.g., response, generated content). Use this instead of metadata for actual data."},
                    "metadata": {"type": "object", "description": "Additional metadata for tags/labels only (e.g., environment, version). Prefer using input_data and output_data for actual content."},
                },
                "required": ["trace_id"],
            }
        ))
        
        tool_definitions.append(types.Tool(
            name="coaia_fuse_add_observation",
            description="Add observation to Langfuse trace. IMPORTANT: Use 'input_data' for inputs/context and 'output_data' for results. Use 'metadata' only for tags/labels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "observation_id": {"type": "string", "description": "Unique observation identifier"},
                    "trace_id": {"type": "string", "description": "Parent trace identifier"},
                    "name": {"type": "string", "description": "Observation name"},
                    "observation_type": {"type": "string", "description": "Type: SPAN, EVENT, or GENERATION", "default": "SPAN"},
                    "parent_id": {"type": "string", "description": "Parent observation ID for nesting"},
                    "input_data": {"type": ["object", "string", "array"], "description": "PREFERRED: The input/context for this observation (e.g., function parameters, prompt). Use this instead of metadata for actual data."},
                    "output_data": {"type": ["object", "string", "array"], "description": "PREFERRED: The output/result of this observation (e.g., function return, LLM response). Use this instead of metadata for actual data."},
                    "metadata": {"type": "object", "description": "Additional metadata for tags/labels only (e.g., model name, temperature). Prefer using input_data and output_data for actual content."},
                    "start_time": {"type": "string", "description": "Optional start timestamp (ISO 8601)"},
                    "end_time": {"type": "string", "description": "Optional end timestamp (ISO 8601)"},
                },
                "required": ["observation_id", "trace_id", "name"],
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_trace_patch_output",
            description="Update the output field of an existing trace. Use this to patch/modify trace results after creation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string", "description": "Trace identifier to update"},
                    "output_data": {"type": ["object", "string", "array"], "description": "New output data (string, object, or array - any JSON-serializable data)"},
                },
                "required": ["trace_id", "output_data"],
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_trace_get",
            description="Get a specific trace by ID from Langfuse with all its observations. Returns trace data with optional formatted tree view.",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string", "description": "Trace identifier to retrieve"},
                    "json_output": {"type": "boolean", "description": "Return raw JSON data instead of formatted tree", "default": False},
                },
                "required": ["trace_id"],
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_trace_view",
            description="View Langfuse trace details with observations (alias for coaia_fuse_trace_get). Returns trace data with optional formatted tree view.",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string", "description": "Trace identifier to view"},
                    "json_output": {"type": "boolean", "description": "Return raw JSON data instead of formatted tree", "default": False},
                },
                "required": ["trace_id"],
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_observation_get",
            description="Get a specific observation by ID from Langfuse. Returns observation data with optional formatted display.",
            inputSchema={
                "type": "object",
                "properties": {
                    "observation_id": {"type": "string", "description": "Observation identifier to retrieve"},
                    "json_output": {"type": "boolean", "description": "Return raw JSON data instead of formatted display", "default": False},
                },
                "required": ["observation_id"],
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_traces_session_view",
            description="View all traces for a specific Langfuse session. Returns formatted table by default or raw JSON if json_output=true",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session identifier to filter traces"},
                    "json_output": {"type": "boolean", "description": "Return raw JSON data instead of formatted table", "default": False},
                },
                "required": ["session_id"],
            }
        ))

        # Langfuse prompts tools
        tool_definitions.append(types.Tool(
            name="coaia_fuse_prompts_list",
            description="List all Langfuse prompts",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ))
        
        tool_definitions.append(types.Tool(
            name="coaia_fuse_prompts_get",
            description="Get specific Langfuse prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Prompt name"},
                    "label": {"type": "string", "description": "Prompt label/version"},
                },
                "required": ["name"],
            }
        ))
        
        # Langfuse datasets tools
        tool_definitions.append(types.Tool(
            name="coaia_fuse_datasets_list",
            description="List all Langfuse datasets",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ))
        
        tool_definitions.append(types.Tool(
            name="coaia_fuse_datasets_get",
            description="Get specific Langfuse dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Dataset name"},
                },
                "required": ["name"],
            }
        ))
        
        # Langfuse score configs tools
        tool_definitions.append(types.Tool(
            name="coaia_fuse_score_configs_list",
            description="List all Langfuse score configurations",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ))
        
        tool_definitions.append(types.Tool(
            name="coaia_fuse_score_configs_get",
            description="Get specific Langfuse score configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_or_id": {"type": "string", "description": "Score config name or ID"},
                },
                "required": ["name_or_id"],
            }
        ))

        # Langfuse comments tools
        tool_definitions.append(types.Tool(
            name="coaia_fuse_comments_list",
            description="List comments with optional filtering by object type/ID or author",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_type": {"type": "string", "description": "Filter by object type (trace, observation, session, prompt)"},
                    "object_id": {"type": "string", "description": "Filter by specific object ID (requires object_type)"},
                    "author_user_id": {"type": "string", "description": "Filter by author user ID"},
                    "page": {"type": "integer", "description": "Page number (starts at 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Items per page", "default": 50},
                },
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_comments_get",
            description="Get a specific comment by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment_id": {"type": "string", "description": "The unique Langfuse identifier of a comment"},
                },
                "required": ["comment_id"],
            }
        ))

        tool_definitions.append(types.Tool(
            name="coaia_fuse_comments_create",
            description="Create a comment attached to an object (trace, observation, session, or prompt)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The comment text/content"},
                    "object_type": {"type": "string", "description": "Type of object to attach comment to (trace, observation, session, prompt) - REQUIRED"},
                    "object_id": {"type": "string", "description": "ID of the object to attach comment to - REQUIRED"},
                    "author_user_id": {"type": "string", "description": "Optional user ID of the comment author"},
                },
                "required": ["text", "object_type", "object_id"],
            }
        ))

        return tool_definitions
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute a tool with the given arguments."""
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        
        # Get the tool function
        tool_func = tools.TOOLS.get(name)
        if not tool_func:
            error_msg = f"Tool '{name}' not found"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        
        try:
            # Call the tool
            result = await tool_func(**arguments)
            
            # Convert result to JSON string
            import json
            result_str = json.dumps(result, indent=2)
            
            logger.info(f"Tool {name} completed successfully")
            return [types.TextContent(type="text", text=result_str)]
            
        except Exception as e:
            error_msg = f"Error executing tool {name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [types.TextContent(type="text", text=error_msg)]
    
    # ========================================================================
    # Resource Registration
    # ========================================================================
    
    @server.list_resources()
    async def list_resources() -> List[types.Resource]:
        """List all available resources."""
        resource_list = [
            types.Resource(
                uri="coaia://templates/",
                name="Pipeline Templates",
                description="List of all available pipeline templates",
                mimeType="application/json",
            ),
        ]
        
        return resource_list
    
    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI."""
        logger.info(f"Reading resource: {uri}")
        
        import json
        
        try:
            if uri == "coaia://templates/":
                result = await resources.list_templates()
                return json.dumps(result, indent=2)
            
            elif uri.startswith("coaia://templates/"):
                # Extract template name from URI
                template_name = uri.replace("coaia://templates/", "").rstrip("/")
                
                if "/variables" in template_name:
                    # Get variables for template
                    template_name = template_name.replace("/variables", "")
                    result = await resources.get_template_variables(template_name)
                else:
                    # Get template details
                    result = await resources.get_template(template_name)
                
                return json.dumps(result, indent=2)
            
            else:
                error_msg = f"Unknown resource URI: {uri}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
                
        except Exception as e:
            error_msg = f"Error reading resource {uri}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    # ========================================================================
    # Prompt Registration
    # ========================================================================
    
    @server.list_prompts()
    async def list_prompts_handler() -> List[types.Prompt]:
        """List all available prompts."""
        prompt_list = []
        
        for prompt_data in prompts.list_prompts():
            prompt_list.append(types.Prompt(
                name=prompt_data["id"],
                description=prompt_data["description"],
                arguments=[
                    types.PromptArgument(
                        name=var["name"],
                        description=var["description"],
                        required=var["required"],
                    )
                    for var in prompt_data["variables"]
                ],
            ))
        
        return prompt_list
    
    @server.get_prompt()
    async def get_prompt_handler(name: str, arguments: Dict[str, str]) -> types.GetPromptResult:
        """Get a specific prompt with variables filled in."""
        logger.info(f"Getting prompt: {name} with arguments: {arguments}")
        
        try:
            rendered = prompts.render_prompt(name, arguments)
            
            if rendered is None:
                error_msg = f"Prompt '{name}' not found"
                logger.error(error_msg)
                return types.GetPromptResult(
                    description=f"Error: {error_msg}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=error_msg)
                        )
                    ],
                )
            
            return types.GetPromptResult(
                description=f"Rendered prompt: {name}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=rendered)
                    )
                ],
            )
            
        except Exception as e:
            error_msg = f"Error rendering prompt {name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return types.GetPromptResult(
                description=f"Error: {error_msg}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=error_msg)
                    )
                ],
            )
    
    logger.info(f"MCP Server created: {SERVER_INFO['name']} v{SERVER_INFO['version']}")
    return server


# ============================================================================
# Main Entry Point
# ============================================================================

async def main_async():
    """Async main function to run the MCP server."""
    if not MCP_AVAILABLE:
        logger.error("MCP SDK not installed. Install with: pip install mcp")
        sys.exit(1)
    
    logger.info("Starting coaiapy-mcp server...")
    
    try:
        server = create_server()
        
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point for the coaiapy-mcp server."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
