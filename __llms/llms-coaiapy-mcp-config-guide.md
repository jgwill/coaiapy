# Gemini LLM Guide: `coaiapy-mcp` Configuration

**Document ID**: `llms-coaiapy-mcp-config-guide.md`
**Version**: 1.0
**Last Updated**: 2025-10-31
**Authored By**: Mia 🧠

---

## 1. Core Principle: Environment-Specific Execution

The `coaiapy-mcp` server, which provides core `coaia` tools like `fuse` and `tash`, has two distinct launch configurations depending on the operational context: **Production** and **Development**. Understanding which context is active is critical for predicting agent behavior and debugging.

The Gemini CLI uses `.mcp.json` files to define how to launch Model Context Protocol (MCP) servers. The active configuration is determined by which file is symlinked or copied to the name the CLI expects.

## 2. Production Configuration

This is the standard configuration for using the `coaiapy-mcp` tools in a stable, production-like environment.

*   **File**: `.mcp.coaiapy.json`
*   **Command**: `/home/jgi/.local/bin/uvx`
*   **Arguments**: `["--from", "coaiapy-mcp", "coaiapy-mcp"]`

### Structural Analysis (Mia 🧠)

This configuration uses `uvx`, a tool for running Python applications in isolated virtual environments. The command `uvx --from coaiapy-mcp coaiapy-mcp` instructs the system to:
1.  Find the `coaiapy-mcp` package installed in the user's Python environment.
2.  Create an isolated environment for it.
3.  Run the `coaiapy-mcp` executable from within that isolated environment.

This is a robust, production-oriented approach that ensures the MCP server runs with its declared dependencies, independent of the global Python environment.

## 3. Development Configuration

This configuration is used when actively developing the `coaiapy-mcp` package itself.

*   **File**: `.mcp.coaiapy-dev.json`
*   **Command**: `/opt/anaconda3/envs/src/bin/coaiapy-mcp`
*   **Arguments**: `[]`

### Structural Analysis (Mia 🧠)

This configuration bypasses any isolation and directly executes the `coaiapy-mcp` script from a specific Conda development environment (`/opt/anaconda3/envs/src/bin/`).

This allows a developer to make changes to the `coaiapy-mcp` source code and have them immediately reflected when the MCP server is launched by Gemini, facilitating a rapid development and testing loop.

## 4. Agent Implications

As an AI agent, awareness of these configurations is key:

*   If the **production** config is active, I must assume the `coaiapy-mcp` tool is stable and rely on its documented behavior.
*   If the **development** config is active, I should be aware that the tool might be in a state of flux. I may be asked to debug it, and its behavior might not match the official documentation. I should check for recent file changes in the `coaiapy` source directory to inform my actions.
