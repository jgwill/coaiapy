"""
coaiapy-mcp: MCP (Model Context Protocol) wrapper for coaiapy observability toolkit

This package exposes coaiapy's capabilities through the Model Context Protocol,
enabling any MCP-compatible LLM to leverage:
- Langfuse Observability (traces, observations, prompts, datasets, score configurations)
- Redis Data Stashing (persistent key-value storage)
- Pipeline Automation (template-based workflow creation)
- Audio Processing (transcription and synthesis via AWS Polly)

The package uses direct library imports from coaiapy, langfuse, and redis
instead of subprocess wrappers for better performance and error handling.
"""

__version__ = "0.1.20"
__author__ = "Guillaume Isabelle"
__email__ = "jgi@jgwill.com"

from coaiapy_mcp.server import main

__all__ = ["main", "__version__"]
