# AI Studio MCP Server Setup & Usage

> Guidance for configuring and using the AI Studio MCP (Model Context Protocol) server for LLM integration.

**Version**: 1.0
**Reference**: modelcontextprotocol/python-sdk v0.1+
**Status**: Production Ready

---

## Quick Start

### Prerequisites

1. **Python and MCP SDK**:
   ```bash
   # MCP SDK (FastMCP pattern, version 0.1+)
   pip install mcp>=0.1.0
   ```

2. **Playwright Installation** (required for browser automation):
   ```bash
   pip install playwright
   playwright install chromium
   ```

3. **Playwright MCP** (for standalone Playwright tool access):
   ```bash
   npm install -g @playwright/mcp
   # OR via npx (no installation needed, runs on demand)
   ```

4. **Verify Installations**:
   ```bash
   python3 -c "from mcp.server.fastmcp import FastMCP; print('✅ MCP SDK ready')"
   python3 -c "from playwright.async_api import async_playwright; print('✅ Playwright ready')"
   ```

### Configure MCP Servers

Edit `~/.config/Claude/claude_desktop_config.json` or in Claude Code workspace use `.mcp.json`:

**Option A: Claude Desktop (Global Configuration)**
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

**Option B: Claude Code Workspace (Local `.mcp.json`)**
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

Place this `.mcp.json` in your Claude Code workspace root directory for that session/project.

**Restart Claude Desktop** (or reload workspace in Claude Code) for changes to take effect.

---

## Available Tools

### 1. `aistudio_login()`

Authenticate to Google Account and AI Studio.

**Parameters**: None (interactive authentication)

**Returns**:
```json
{
  "status": "success",
  "message": "Authenticated to AI Studio. Session saved to...",
  "storage_state_path": "/home/user/.playwright/aistudio_auth_state.json"
}
```

**Usage**:
```
User: "Authenticate me to Google AI Studio"
System: Calls aistudio_login()
Result: Session saved for future operations
```

---

### 2. `aistudio_create_repo(app_url, repo_name, description, visibility="private")`

Create GitHub repository for AI Studio project.

**Parameters**:
- `app_url` (string, required): Full AI Studio project URL
  - Example: `https://aistudio.google.com/apps/drive/1HLs3IoJElo7p0fTjOANSFpp1qP3zP5nQ?source=start&showAssistant=true`
- `repo_name` (string, required): Repository name with UUID prefix
  - Example: `178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion`
- `description` (string, required): Repository description
- `visibility` (string, optional): `"private"` or `"public"` (default: `"private"`)

**Returns**:
```json
{
  "status": "success",
  "repository": "178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion",
  "repository_url": "https://github.com/miadisabelle/178ca256-...",
  "owner": "miadisabelle",
  "timestamp": "2025-11-05T21:30:00Z"
}
```

**Timing**: Approximately 30-40 seconds (includes dialog load and form submission)

**Usage**:
```
User: "Create a GitHub repository for my AI Studio project"
System: Calls aistudio_create_repo(
  app_url="https://aistudio.google.com/apps/drive/...",
  repo_name="uuid-project-name",
  description="Project description"
)
Result: Repository created and ready for commits
```

---

### 3. `aistudio_commit_and_deploy(app_url, commit_message, google_cloud_project, issue_number=None)`

Commit changes to GitHub and deploy to Cloud Run in sequence.

**Parameters**:
- `app_url` (string, required): AI Studio project URL
- `commit_message` (string, required): Git commit message
  - Should reference issue number: `"Feature description #1"`
- `google_cloud_project` (string, required): Google Cloud project ID
  - Example: `"spry-dispatcher"` or `"spry-dispatcher-471221-d4"`
- `issue_number` (integer, optional): GitHub issue number for tracking

**Returns**:
```json
{
  "status": "success",
  "commit": "c0a5a88",
  "commit_message": "Initial implementation #1",
  "deployment": {
    "service": "service-178ca256-2a55-411a-90e7-d7f9954c5fb6-visi",
    "url": "https://service-178ca256-...-visi-947142232746.us-west1.run.app",
    "status": "deployed"
  },
  "timestamp": "2025-11-05T21:36:00Z"
}
```

**Timing**:
- Commit phase: 5-10 seconds
- Deploy phase: 30-60 seconds
- Total: 35-70 seconds

**Critical Pattern**: Waits for "Stage and commit" dialog, then clicks button and waits for deployment

**Usage**:
```
User: "Commit the changes and deploy to Cloud Run"
System: Calls aistudio_commit_and_deploy(
  app_url="https://aistudio.google.com/apps/drive/...",
  commit_message="Feature description #2",
  google_cloud_project="spry-dispatcher-471221-d4",
  issue_number=2
)
Result: Application deployed and live
```

---

### 4. `aistudio_clone_repository(repo_url, local_path, branch="main")`

Clone GitHub repository to local development environment.

**Parameters**:
- `repo_url` (string, required): GitHub repository URL
  - HTTPS: `https://github.com/owner/repo.git`
  - SSH: `git@github.com:owner/repo.git`
- `local_path` (string, required): Local directory path
  - Example: `/a/src/178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion`
- `branch` (string, optional): Git branch to clone (default: `"main"`)

**Returns**:
```json
{
  "status": "success",
  "repository": "178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion",
  "local_path": "/a/src/178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion",
  "branch": "main",
  "commit_count": 2,
  "latest_commit": "c0a5a88",
  "timestamp": "2025-11-05T21:41:00Z"
}
```

**Timing**: 10-30 seconds (depends on repository size)

**Usage**:
```
User: "Clone the repository locally"
System: Calls aistudio_clone_repository(
  repo_url="https://github.com/miadisabelle/178ca256-...",
  local_path="/a/src/178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion"
)
Result: Repository ready for local development
```

---

### 5. `aistudio_wait_for_implementation(app_url, timeout_seconds=300)`

Wait for Gemini to complete AI Studio project implementation.

**Parameters**:
- `app_url` (string, required): AI Studio project URL
- `timeout_seconds` (integer, optional): Maximum wait time in seconds (default: 300 = 5 minutes)

**Returns**:
```json
{
  "status": "success",
  "implementation_time": 180,
  "stop_button_visible": false,
  "content_generated": true,
  "timestamp": "2025-11-05T21:25:00Z"
}
```

**Critical Timing Pattern**:
- Sleeps exactly 90 seconds (minimum for Gemini processing)
- Checks for Stop button every 30 seconds
- Continues waiting until Stop button disappears
- Total wait: 90+ seconds depending on complexity

**Usage**:
```
User: "Wait for the AI Studio project to finish generating code"
System: Calls aistudio_wait_for_implementation(
  app_url="https://aistudio.google.com/apps/drive/...",
  timeout_seconds=300
)
Result: Implementation complete, ready for commit
```

---

## Complete Workflow Example

### Scenario: Create and Deploy a New AI Studio Project

```
1. User: "Create a new AI Studio project for a Visioning Circle app"
   → User manually creates project in AI Studio
   → User sends prompt: "Create ceremonial web app with Four Directions framework"

2. User: "Wait for Gemini to finish implementing the project"
   System: aistudio_wait_for_implementation(
     app_url="https://aistudio.google.com/apps/drive/...",
     timeout_seconds=300
   )
   → Waits 90+ seconds for code generation
   → Returns when Stop button disappears

3. User: "Create a GitHub repository for the project"
   System: aistudio_create_repo(
     app_url="https://aistudio.google.com/apps/drive/...",
     repo_name="178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion",
     description="Ceremonial web application..."
   )
   → Repository created at GitHub

4. User: "Create Issue #1 for tracking"
   → User manually creates GitHub Issue #1 with feature specs
   (Future: Could automate with GitHub API)

5. User: "Commit the initial code and deploy"
   System: aistudio_commit_and_deploy(
     app_url="https://aistudio.google.com/apps/drive/...",
     commit_message="Initial implementation #1",
     google_cloud_project="spry-dispatcher-471221-d4",
     issue_number=1
   )
   → Code committed to GitHub
   → Deployed to Cloud Run
   → Application live

6. User: "Clone the repository locally"
   System: aistudio_clone_repository(
     repo_url="https://github.com/miadisabelle/178ca256-...",
     local_path="/a/src/178ca256-2a55-411a-90e7-d7f9954c5fb6-visioning-circle-companion"
   )
   → Repository ready for local development

7. User: "Create project documentation"
   → User creates CLAUDE.md and .aistudio-config.json

8. User: "Deploy the documentation"
   System: aistudio_commit_and_deploy(
     app_url="https://aistudio.google.com/apps/drive/...",
     commit_message="Add project documentation #2",
     google_cloud_project="spry-dispatcher-471221-d4",
     issue_number=2
   )
   → Documentation committed and deployed
```

**Total Time**: 45-60 minutes (including waits)

---

## Critical Timing Reference

These timing patterns are embedded in `aistudio-playwright-helper.py`:

| Operation | Wait Time | Pattern | Notes |
|-----------|-----------|---------|-------|
| Gemini Implementation | 90+ seconds | Wait minimum 90s, check Stop button every 30s | Minimum required for code generation |
| Dialog Load | 8-10 seconds | Fixed sleep after clicking button | GitHub/Deploy dialog rendering |
| Navigation | 3 seconds | Fixed sleep after page load | JavaScript settlement |
| Deployment | 30-60 seconds | Fixed wait after clicking deploy | Cloud Run build and deployment |

---

## Authentication

### First Run
1. Tool calls `aistudio_login()`
2. Browser window opens automatically
3. You sign in to Google
4. Authentication state saved to `~/.playwright/aistudio_auth_state.json`
5. Future calls reuse this authentication

### Subsequent Runs
- Authentication state automatically loaded
- No manual sign-in required
- Session remains valid for extended periods

### Token Expiration
- If authentication fails, manually re-run `aistudio_login()`
- Deletes old state and creates new authentication

---

## Error Handling

### Common Errors

**Error**: `Repository not found`
- **Cause**: GitHub hasn't indexed repository yet
- **Solution**: Wait 30-60 seconds and retry clone

**Error**: `Dialog not loading`
- **Cause**: Browser timing issues or page lag
- **Solution**: Increase `DIALOG_LOAD_WAIT` in helper to 10-15 seconds

**Error**: `Gemini implementation stuck`
- **Cause**: Stop button still visible (processing ongoing)
- **Solution**: Increase `timeout_seconds` parameter

**Error**: `MCP server connection failed`
- **Cause**: Port conflict or incorrect configuration
- **Solution**:
  1. Check Claude Desktop config.json syntax
  2. Verify path to aistudio-mcp-tools.py
  3. Restart Claude Desktop

---

---

## What Had To Be Configured (And Why)

### 1. **Python Module Naming** (Critical Issue)

**Problem**: Files named with hyphens (`aistudio-mcp-tools.py`) cannot be imported by Python.

**Solution**: Use underscores in module filenames:
- ✅ `aistudio_mcp_tools.py` - Can be imported
- ❌ `aistudio-mcp-tools.py` - ImportError

**Why**: Python's import system treats hyphens as minus operators, not valid identifiers.

### 2. **FastMCP Pattern** (vs Outdated Server Class)

**Problem**: Old MCP SDK used `Server()` class with manual tool registration. Current SDK (0.1+) uses `FastMCP`.

**Current Pattern** (Working):
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="aistudio")

@mcp.tool()
async def aistudio_login() -> dict:
    """Authenticate to Google AI Studio and save session state."""
    # implementation
    return {"status": "success"}

if __name__ == "__main__":
    mcp.run()
```

**Old Pattern** (Broken):
```python
# ❌ This pattern no longer works
from mcp import Server, Tool
server = Server("aistudio")
server.add_tool(Tool(...))
```

### 3. **MCP Configuration Location**

**Launcher Instance**: Use `.mcp.json` in workspace root
- Location: `/a/src/_sessiondata/{session_id}/tst-aistudio-mcp-launcher/.mcp.json`
- Applies only to that Claude Code instance
- Useful for testing before global deployment

**Global (Claude Desktop)**: Use `claude_desktop_config.json`
- Location: `~/.config/Claude/claude_desktop_config.json`
- Applies to all Claude Desktop instances
- Use when MCP tools are fully tested and production-ready

### 4. **File Naming Consistency**

All related files must use underscores (not hyphens):
- `aistudio_mcp_tools.py` ✅
- `aistudio_playwright_helper.py` ✅
- Imports: `from aistudio_playwright_helper import AIStudioAutomation` ✅

### 5. **Git Protocol Preference**

**Recommendation**: Use SSH for cloning
```bash
# Preferred - SSH
git@github.com:miadisabelle/project-name.git

# Works but less preferred - HTTPS
https://github.com/miadisabelle/project-name.git
```

**Why SSH**: No password prompts in automation, cleaner local development

---

## Configuration Reference

### Claude Desktop Config (Typical)

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

### Helper Constants (in aistudio_playwright_helper.py)

```python
GEMINI_IMPLEMENTATION_WAIT = 90  # Seconds
DIALOG_LOAD_WAIT = 8             # Seconds
VERIFICATION_RETRY_WAIT = 3      # Seconds
NAVIGATION_WAIT = 3              # Seconds
```

### Storage State

- **Location**: `~/.playwright/aistudio_auth_state.json`
- **Purpose**: Persistent authentication across sessions
- **Reset**: Delete this file to re-authenticate

---

## Best Practices

1. **Always reference GitHub issues** in commit messages:
   - ✅ Good: `"Feature description #1"`
   - ❌ Bad: `"Feature description"`

2. **Wait for Gemini before committing**:
   - Call `aistudio_wait_for_implementation()` after sending prompt
   - Don't commit code while Stop button is visible

3. **Create issues before commits**:
   - Create GitHub Issue #1 before first commit
   - Reference issue in commit message

4. **Test locally before deploying**:
   - Clone repository locally
   - Test with `npm run dev` or equivalent
   - Commit and deploy when verified

5. **Use configuration files**:
   - Create `.aistudio-config.json` in project root
   - Track metadata for automation

---

## Successful Launcher Test Results

**Reference**: `/a/src/_sessiondata/178ca256-2a55-411a-90e7-d7f9954c5fb6/tst-aistudio-mcp-launcher/SESSION_MEMORY.md`

**Test Execution**: Complete 10-phase autonomous workflow
- **Total Time**: ~30 minutes end-to-end
- **Status**: ✅ All phases successful
- **Deployment**: Live at https://dummy-prototype-947142232746.us-west1.run.app

**Phases Executed**:
1. ✅ Specification (RISE framework) - 5 min
2. ✅ Authentication (Google) - 2 min
3. ✅ Project Creation (AI Studio) - 5 min
4. ✅ Gemini Implementation Wait - 67 seconds
5. ✅ GitHub Repository Creation - 10 min
6. ✅ Initial Commit - 5 min
7. ✅ Cloud Run Deployment - 120 seconds
8. ✅ Local Clone - 1 min
9. ✅ Documentation - 5 min
10. ✅ Validation (/api/health → 200 OK) - 2 min

**Key Findings**:
- MCP tools execute reliably when properly configured
- FastMCP pattern is stable and production-ready
- Both aistudio and playwright MCP servers work together
- Autonomous execution works end-to-end without manual intervention

---

## Troubleshooting

### Server Won't Start

**Symptom**: Claude Desktop shows "Unable to connect"

**Diagnosis Steps**:
1. Check Python installed: `python3 --version`
2. Check MCP SDK: `pip list | grep mcp` (should show mcp 0.1.0+)
3. Test server directly: `python /a/src/llms/aistudio_mcp_tools.py`
   - Should print: "Starting AI Studio MCP Tools Server"
4. Check for error messages in terminal output

**Common Issues**:
- ❌ `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`
  - Solution: `pip install --upgrade mcp`
- ❌ `ImportError: cannot import name 'AIStudioAutomation'`
  - Solution: Check `aistudio_playwright_helper.py` is in `/a/src/llms/`
  - Solution: Ensure file is named with underscores, not hyphens

### Tools Not Appearing

**Symptom**: Tools not visible in Claude

**Diagnosis Steps**:
1. Restart Claude Desktop completely
2. Verify `.mcp.json` or `claude_desktop_config.json` syntax:
   - Use JSON validator: https://jsonlint.com/
   - Common error: Missing comma between properties
3. Verify file path is correct and file exists
4. Check file permissions: `ls -l aistudio_mcp_tools.py` (should be readable)

**Debug**: Manually test the server:
```bash
cd /a/src/llms
python aistudio_mcp_tools.py
# Should output: Starting AI Studio MCP Tools Server
# And list available tools
```

### Browser Not Opening

**Symptom**: No browser window appears during login

**Steps**:
1. Check Playwright installed: `pip list | grep playwright`
2. Verify chromium: `python -c "from playwright.async_api import async_playwright; print('OK')"`
3. Try manual login: Run `python aistudio-mcp-tools.py` directly

### Deployment Timeout

**Symptom**: Deploy takes longer than expected

**Steps**:
1. Check Cloud Run service exists
2. Verify project ID is correct
3. Check network connectivity
4. Increase timeout parameter

---

---

## Complete Configuration Examples

### Example 1: Local Launcher Workspace

**File**: `/a/src/_sessiondata/{session-id}/tst-aistudio-mcp-launcher/.mcp.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "aistudio": {
      "command": "python",
      "args": ["/a/src/llms/aistudio_mcp_tools.py"]
    }
  }
}
```

**Why this works**:
- Playwright MCP comes first (npx can run without installation)
- aistudio MCP uses full path to Python server
- Both configured in single workspace
- Applies only to that Claude Code instance

### Example 2: Global Claude Desktop Configuration

**File**: `~/.config/Claude/claude_desktop_config.json`

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

**Why use this**:
- Applies to all Claude Desktop instances
- Persistent across sessions
- Single point of configuration management
- Best for production use

### Example 3: With Environment Variables

**File**: `.mcp.json` with environment configuration

```json
{
  "mcpServers": {
    "aistudio": {
      "command": "python",
      "args": ["/a/src/llms/aistudio_mcp_tools.py"],
      "env": {
        "PYTHONPATH": "/a/src/llms",
        "PLAYWRIGHT_HEADLESS": "false"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Why**:
- Ensures correct module paths for imports
- Controls Playwright browser visibility (headless vs headful)
- Useful for debugging

---

## Verification Checklist

Before running autonomous workflows, verify:

- [ ] **Files exist and named correctly** (underscores not hyphens):
  ```bash
  ls -l /a/src/llms/aistudio_mcp_tools.py
  ls -l /a/src/llms/aistudio_playwright_helper.py
  ```

- [ ] **Configuration syntax valid** (JSON):
  ```bash
  cat .mcp.json | python -m json.tool >/dev/null && echo "✅ Valid JSON"
  ```

- [ ] **MCP SDK installed**:
  ```bash
  python -c "from mcp.server.fastmcp import FastMCP; print('✅ FastMCP ready')"
  ```

- [ ] **Playwright installed and chromium available**:
  ```bash
  python -c "from playwright.async_api import async_playwright; print('✅ Playwright ready')"
  ```

- [ ] **Server starts without errors**:
  ```bash
  python /a/src/llms/aistudio_mcp_tools.py 2>&1 | head -5
  # Should show: "Starting AI Studio MCP Tools Server"
  ```

- [ ] **Google authentication ready** (pre-login):
  - Browser must be able to reach accounts.google.com
  - User must have Google account with AI Studio access

---

## Next Steps

### For Next Session
1. Copy `.mcp.json` to new workspace directory
2. Verify all checklist items pass
3. Test with `@aistudio aistudio_login()` first
4. Then execute full 10-phase workflow

### For Future Enhancements
- Parameterize Google Cloud project ID
- Add GitHub issue creation automation
- Add deployment health checks with Playwright
- Add rollback capability for failed deployments
- Add multi-project management dashboard

---

**Status**: Production Ready ✅
**Last Updated**: 2025-11-05
**Maintenance**: Refer to [aistudio_playwright_helper.py](./aistudio_playwright_helper.py) for timing patterns

🧠 MCP Server production-tested and ready for integration with Claude Code

