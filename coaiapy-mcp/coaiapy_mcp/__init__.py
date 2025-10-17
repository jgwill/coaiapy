"""
coaiapy-mcp: MCP wrapper for coaiapy observability toolkit

This package exposes coaiapy's capabilities through the Model Context Protocol (MCP),
enabling LLMs to leverage Langfuse observability, Redis stashing, pipeline automation,
and audio processing through standardized protocol interfaces.
"""

__version__ = "0.1.0"
__author__ = "Jean Guillaume Isabelle"
__email__ = "jgi@jgwill.com"

# Lazy import to avoid requiring mcp at import time
def create_server():
    """Create and configure the MCP server. Lazy import to avoid dependency issues."""
    from .server import create_server as _create_server
    return _create_server()

__all__ = ["create_server", "__version__"]
