# Issue 74: MCP Context Token Usage Analysis

**Date:** 2025-11-28T17:27:45.946Z

## Issue Summary
When the MCP toolset is loaded into the LLM context, it consumes ~13,000 tokens—far exceeding the desired 2,000-token budget. This is problematic for efficient LLM operation, as it limits available context for user queries and responses.

## Root Causes
- **Excessive Docstrings/Descriptions:** Tool functions (especially in coaiapy_mcp/tools.py) have verbose docstrings, parameter explanations, and example blocks. These are all included in the context sent to the LLM.
- **Redundant Metadata:** Type annotations, repeated comments, and duplicated documentation across multiple files (tools.py, server.py, resources.py, prompts.py) inflate the token count.
- **Unfiltered Context Loading:** The loader may be including entire files or large blocks of documentation (README, implementation plans, test plans) rather than just the minimal tool interface required for LLM operation.

## Optimal Desired Results
- **Minimal Tool Context:** Only include the function name, a concise one-line description, and parameter names/types for each tool.  
  Example:  
  * coaia_tash 45
  * coaia_fetch 38
- **Aggressive Docstring Pruning:** Remove or drastically shorten all non-essential docstrings, comments, and example blocks in tool-exposed functions.
- **Loader Filtering:** Ensure the loader only pulls minimal metadata (no README, test, or plan files unless strictly required).
- **Token Auditing:** Use tiktoken or similar to audit and verify per-tool token usage, aiming for a total ≤ 2,000 tokens.

## Action Plan
1. Audit all tool-exposed functions for docstring and comment length.
2. Refactor code to minimize docstrings and remove redundant documentation.
3. Update loader logic to filter out non-essential context.
4. Validate with tiktoken to ensure total context is within the 2,000-token target.

## Result
This will maximize available context for user queries, improve LLM efficiency, and ensure the MCP toolset is loaded optimally for advanced AI workflows.
