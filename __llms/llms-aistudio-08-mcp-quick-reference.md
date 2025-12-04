# AI Studio MCP - Quick Reference Card

> Fast lookup for configuration, common errors, and tools

**File**: [`llms-aistudio-07-mcp-server-setup.md`](./llms-aistudio-07-mcp-server-setup.md) for detailed documentation

---

## Installation (One-Time)

```bash
# Python dependencies
pip install mcp>=0.1.0 playwright>=1.40.0

# Playwright browser
playwright install chromium

# Playwright MCP (optional, can use npx instead)
npm install -g @playwright/mcp

# Verify
python -c "from mcp.server.fastmcp import FastMCP; print('✅')"
python -c "from playwright.async_api import async_playwright; print('✅')"
```

---

## Configuration

### Copy-Paste Template: `.mcp.json`

```json
{
  "mcpServers": {
    "aistudio": {
      "command": "python",
      "args": ["/a/src/llms/aistudio_mcp_tools.py"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Place in**: Workspace root directory for launcher instance, OR `~/.config/Claude/claude_desktop_config.json` for global

---

## Tools Available

| Tool | Purpose | Time |
|------|---------|------|
| `aistudio_login()` | Authenticate to Google AI Studio | 2 min |
| `aistudio_create_repo(...)` | Create GitHub repository | 30-40 sec |
| `aistudio_wait_for_implementation(...)` | Wait for Gemini to finish | 90+ sec |
| `aistudio_commit_and_deploy(...)` | Commit to GitHub + deploy | 35-70 sec |
| `aistudio_clone_repository(...)` | Clone repo locally | 10-30 sec |

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError: cannot import name 'FastMCP'` | Old MCP SDK | `pip install --upgrade mcp` |
| `ModuleNotFoundError: No module named 'aistudio_mcp_tools'` | Hyphenated filename | Rename `aistudio-mcp-tools.py` → `aistudio_mcp_tools.py` |
| `MCP server connection failed` | Invalid JSON config | Validate: `python -m json.tool < .mcp.json` |
| `No browser window opening` | Playwright not installed | `pip install playwright && playwright install chromium` |
| `Repository not found` | GitHub indexing delay | Wait 30-60 seconds, retry |

---

## File Naming Rules

✅ **Correct** (Python can import these):
- `aistudio_mcp_tools.py`
- `aistudio_playwright_helper.py`
- `import aistudio_playwright_helper`

❌ **Incorrect** (Python cannot import):
- `aistudio-mcp-tools.py`
- `aistudio-playwright-helper.py`
- `import aistudio-mcp-tools` ← ImportError!

---

## Pre-Flight Checklist

Before running workflows:

```bash
# 1. Files exist and named correctly
ls -l /a/src/llms/aistudio_mcp_tools.py
ls -l /a/src/llms/aistudio_playwright_helper.py

# 2. Configuration is valid JSON
python -m json.tool < .mcp.json > /dev/null && echo "✅ Valid"

# 3. MCP SDK is correct version
python -c "from mcp.server.fastmcp import FastMCP; print('✅ FastMCP ready')"

# 4. Server starts
python /a/src/llms/aistudio_mcp_tools.py 2>&1 | head -3
# Should show: "Starting AI Studio MCP Tools Server"

# 5. You're pre-logged in to Google
# (aistudio_login() will open browser if not)
```

---

## 10-Phase Workflow Summary

1. **Specification** - Create PROJECT_SPEC.md with requirements (RISE framework)
2. **Authentication** - `@aistudio aistudio_login()`
3. **Project Creation** - Manually create in AI Studio, get project URL
4. **Gemini Wait** - `@aistudio aistudio_wait_for_implementation(app_url, timeout_seconds=600)`
5. **GitHub Repo** - `@aistudio aistudio_create_repo(app_url, repo_name, description)`
6. **Initial Commit** - `@aistudio aistudio_commit_and_deploy(app_url, "Initial implementation #1", project_id, issue_number=1)`
7. **Cloud Run Deploy** - (Automatic with commit)
8. **Clone Locally** - `@aistudio aistudio_clone_repository(repo_url, local_path)`
9. **Documentation** - Create README, CLAUDE.md, update git
10. **Validation** - Test locally and in cloud, verify deployment URL

**Total Time**: ~30 minutes

---

## FastMCP Pattern

This is what works (current SDK):

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="aistudio")

@mcp.tool()
async def my_tool(param: str) -> dict:
    """Tool description"""
    return {"result": "value"}

if __name__ == "__main__":
    mcp.run()
```

This is outdated (old SDK):

```python
# ❌ OLD - doesn't work anymore
from mcp import Server, Tool
server = Server("aistudio")
server.add_tool(Tool(...))
```

---

## References

- **Detailed Guide**: [llms-aistudio-07-mcp-server-setup.md](./llms-aistudio-07-mcp-server-setup.md)
- **Test Results**: `/a/src/_sessiondata/178ca256-2a55-411a-90e7-d7f9954c5fb6/tst-aistudio-mcp-launcher/SESSION_MEMORY.md`
- **Launcher Example**: `/a/src/_sessiondata/178ca256-2a55-411a-90e7-d7f9954c5fb6/tst-aistudio-mcp-launcher/`
- **Helper Code**: [aistudio_playwright_helper.py](./aistudio_playwright_helper.py) (timing constants)

---

**Last Updated**: 2025-11-05
🧠 Keep this reference open while configuring new launchers
