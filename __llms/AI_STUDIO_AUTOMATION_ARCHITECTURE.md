# AI Studio Automation Architecture

> End-to-end programmatic automation of Google AI Studio workflows using Playwright and MCP (Model Context Protocol) tools.

**Version**: 1.0
**Status**: Foundation complete, ready for integration
**Created**: 2025-11-05

---

## Overview

The AI Studio automation system consists of three layers:

```
┌─────────────────────────────────────────┐
│  LLM Agents (Claude, other LLMs)        │  Access via MCP tools
├─────────────────────────────────────────┤
│  aistudio-mcp-tools.py                  │  Tool definitions & RPC
├─────────────────────────────────────────┤
│  aistudio-playwright-helper.py          │  Async functions + timing
├─────────────────────────────────────────┤
│  Playwright Browser Automation          │  Low-level browser control
├─────────────────────────────────────────┤
│  Google AI Studio                       │  Target application
└─────────────────────────────────────────┘
```

### Layer 1: Helper Functions (aistudio-playwright-helper.py)

**Purpose**: Core Playwright automation functions

**Key Functions**:
- `AIStudioAutomation.login_aistudio()` - Google authentication
- `AIStudioAutomation.open_github_panel()` - Navigate to project, open GitHub
- `AIStudioAutomation.create_github_repo()` - Create repository
- `AIStudioAutomation.commit_to_github()` - Commit changes
- `AIStudioAutomation.deploy_to_cloud_run()` - Deploy application
- `AIStudioAutomation.clone_repository_locally()` - Git clone
- `AIStudioAutomation.wait_for_gemini_implementation()` - Wait for processing

**Usage**:
```python
from aistudio_playwright_helper import AIStudioAutomation

automation = AIStudioAutomation()
context, page = await automation.login_aistudio()
result = await automation.create_github_repo(page, "repo-name", "description")
```

**Characteristics**:
- Async/await based (Playwright)
- Context-persistent (reuses authenticated session)
- Critical timing built-in (90s Gemini wait, 8s dialog load, etc.)
- Returns structured JSON results
- Comprehensive logging
- Error handling and recovery

---

### Layer 2: MCP Tool Wrapper (aistudio-mcp-tools.py)

**Purpose**: Expose helper functions as MCP tools for LLM access

**Tools Exposed**:
- `aistudio_login()` - Authenticate and save session
- `aistudio_create_repo()` - Create GitHub repository
- `aistudio_commit_and_deploy()` - Commit to GitHub and deploy
- `aistudio_clone_repository()` - Clone locally
- `aistudio_wait_for_implementation()` - Wait for Gemini

**Configuration** (Claude Desktop):
```json
{
  "mcpServers": {
    "aistudio": {
      "command": "python",
      "args": ["/a/src/llms/aistudio-mcp-tools.py"]
    }
  }
}
```

**Usage by LLM**:
```
LLM: "Please create a GitHub repository for the AI Studio project"

System: Calls aistudio_create_repo(
  app_url="https://...",
  repo_name="uuid-project-name",
  description="..."
)

LLM: "Repository created successfully at github.com/..."
```

**Characteristics**:
- Tool definitions with JSON schemas
- Error handling and logging
- Result formatting for LLM consumption
- Reuses authenticated state across calls

---

### Layer 3: LLM Agents

**Purpose**: Intelligent orchestration of workflows

**Examples**:
- "Create a new AI Studio project and deploy it"
- "Add a feature to this AI Studio project and redeploy"
- "Clone the project locally and create documentation"

**How it Works**:
1. User asks LLM to perform workflow
2. LLM reads guidance (llms-aistudio-*.md files)
3. LLM decides which tools to call and in what order
4. LLM calls tools via MCP
5. LLM combines results with additional steps (local file creation, etc.)
6. LLM reports completion to user

---

## Critical Timing Patterns

These are embedded in the helper functions and automatically applied:

### Pattern 1: Gemini Implementation Wait (90+ seconds)

**When**: After sending prompt to Gemini in AI Studio
**How**:
1. Sleep exactly 90 seconds (minimum)
2. Check for Stop button (indicates still processing)
3. If Stop button visible, wait 30-60 more seconds
4. Repeat until Stop button gone

**Code Location**: `AIStudioAutomation.wait_for_gemini_implementation()`

### Pattern 2: Dialog Load Wait (8-10 seconds)

**When**: Opening GitHub or Deploy dialogs
**How**:
1. Click button to open dialog
2. Sleep 8 seconds (fixed)
3. Verify dialog is ready (look for expected button)
4. Proceed with interaction

**Code Location**: `AIStudioAutomation.open_github_panel()`, `deploy_to_cloud_run()`

### Pattern 3: Navigation Wait (3 seconds)

**When**: Navigating between pages
**How**: Sleep 3 seconds after page load to allow JavaScript to settle

**Code Location**: All navigation functions

---

## File Structure

```
/a/src/llms/
├── aistudio-playwright-helper.py          # Core helper module
├── aistudio-mcp-tools.py                  # MCP tool wrapper
├── aistudio_config.json                   # Configuration (to create)
├── AI_STUDIO_AUTOMATION_ARCHITECTURE.md   # This file
├── llms-aistudio-00-START-HERE.md         # Navigation hub
├── llms-aistudio-01-workflow-new-project.md       # New project workflow
├── llms-aistudio-02-workflow-existing-project.md  # Enhancement workflow
├── llms-aistudio-03-ai-features-catalog.md        # AI Features reference
├── llms-aistudio-04-browser-automation-reference.md  # Technical reference
├── llms-aistudio-05-llm-decision-guide.md         # Decision patterns
└── llms-aistudio-06-best-practices-antipatterns.md  # Troubleshooting
```

---

## Example Workflows

### Workflow 1: Complete New Project Creation

**Steps**:
1. `aistudio_login()` - Authenticate (one-time setup)
2. User manually creates project in AI Studio + sends prompt
3. `aistudio_wait_for_implementation(app_url)` - Wait 90+ seconds
4. `aistudio_create_repo(app_url, repo_name, description)` - Create GitHub repo
5. `aistudio_commit_and_deploy(app_url, message, project)` - Commit + deploy
6. `aistudio_clone_repository(repo_url, local_path)` - Clone locally
7. User creates CLAUDE.md and commits

**Total Time**: 45-60 minutes (including waits)

### Workflow 2: Enhancement Iteration

**Steps**:
1. User describes enhancement in AI Studio
2. `aistudio_wait_for_implementation(app_url)` - Wait for Gemini
3. `aistudio_commit_and_deploy(app_url, message, project)` - Commit + deploy
4. Verify in deployed app
5. If issues, repeat with fixes

**Total Time**: 15-20 minutes per iteration

### Workflow 3: Quick Deployment

**Steps**:
1. Project already in AI Studio and committed
2. `aistudio_commit_and_deploy(app_url, message, project)` - Just deploy
3. Verify in deployed app

**Total Time**: 5-10 minutes

---

## Extending the System

### Adding New Helper Functions

**Pattern**:
```python
# In aistudio-playwright-helper.py

async def your_new_function(self, page: Page, param1: str, param2: str) -> Dict[str, Any]:
    """
    Your function description.

    Args:
        page: Playwright page
        param1: Parameter description
        param2: Parameter description

    Returns:
        Dict: Status and results
    """
    logger.info(f"Doing something: {param1}")

    try:
        # Your automation logic
        result = await some_action()

        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
```

### Wrapping as MCP Tool

**Pattern**:
```python
# In aistudio-mcp-tools.py

Tool(
    name="your_tool_name",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            },
            "param2": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1", "param2"]
    }
)

async def _tool_your_tool_name(param1: str, param2: str) -> list[TextContent]:
    """Tool implementation"""
    try:
        automation = AIStudioAutomation()
        result = await automation.your_new_function(page, param1, param2)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"status": "error", "error": str(e)}))]
```

---

## Configuration

### Create aistudio_config.json

```json
{
  "aistudio": {
    "browser_type": "chromium",
    "headless": false,
    "timeout_ms": 30000,
    "storage_state_path": "/home/user/.playwright/aistudio_auth_state.json"
  },
  "timing": {
    "gemini_implementation_wait": 90,
    "dialog_load_wait": 8,
    "verification_retry_wait": 3,
    "navigation_wait": 3
  },
  "deployment": {
    "default_cloud_project": "spry-dispatcher",
    "cloud_run_region": "us-central1",
    "timeout_minutes": 2
  }
}
```

### Load in Helper

```python
import json

with open("aistudio_config.json") as f:
    config = json.load(f)

GEMINI_IMPLEMENTATION_WAIT = config["timing"]["gemini_implementation_wait"]
```

---

## Testing the Automation

### Unit Test: Authentication

```bash
python -c "
import asyncio
from aistudio_playwright_helper import AIStudioAutomation

async def test_login():
    automation = AIStudioAutomation()
    context, page = await automation.login_aistudio()
    await context.close()
    await page.context.browser.close()
    print('Authentication test passed')

asyncio.run(test_login())
"
```

### Integration Test: Full Workflow

```bash
python aistudio-playwright-helper.py login

python -c "
import asyncio
from aistudio_playwright_helper import aistudio_create_github_repo

result = asyncio.run(aistudio_create_github_repo(
    app_url='https://aistudio.google.com/apps/drive/...',
    repo_name='test-repo-name',
    description='Test repository',
    use_existing_auth=True
))

print(result)
"
```

### MCP Tool Test

Once configured in Claude Desktop, test tools directly in Claude:

```
User: "@aistudio Call aistudio_create_repo with app_url=... repo_name=... description=..."

System: Executes tool via MCP and returns result
```

---

## Session Traceability

Each workflow maintains traceability through:

1. **UUID Prefixing**: All projects named `{UUID}-{descriptive-name}`
2. **GitHub Issue Tracking**: Each change referenced to issue number
3. **Commit Messages**: Include Claude Code attribution and co-author info
4. **Session Memory**: Saved to `/a/src/_sessiondata/{session-id}/SESSION_MEMORY.md`

**Example Commit Message**:
```
Initial implementation #1

Created AI Studio project with:
- Four Directions framework
- Participant circle management
- Sacred container creation

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Gemini AI <noreply@google.com>
```

---

## Related Documentation

- **llms-aistudio-00-START-HERE.md** - Navigation and module index
- **llms-aistudio-01-workflow-new-project.md** - Complete new project lifecycle (6 phases)
- **llms-aistudio-04-browser-automation-reference.md** - Command syntax and timing
- **llms-aistudio-06-best-practices-antipatterns.md** - Troubleshooting and anti-patterns
- **SESSION_MEMORY.md** - Session-specific context (in _sessiondata)

---

## Known Limitations

### Current Limitations
1. MCP tool wrapper requires proper MCP SDK setup
2. Authentication requires browser interaction first time
3. File uploads to AI Studio not yet automated
4. Custom model selection not yet automated

### Future Enhancements
1. Support for AI Features (voice, chatbot, TTS) integration
2. File upload automation
3. Batch project creation
4. Project cloning (copy existing project)
5. RISE specification → prompt conversion automation
6. Automated code review and testing

---

## Troubleshooting

### "Authentication failed"
- Ensure browser window appears and you can manually sign in
- Check storage state file exists: `~/.playwright/aistudio_auth_state.json`
- Try re-authenticating: `python aistudio-playwright-helper.py login`

### "Dialog not loading"
- Increase wait time from 8s to 10-15s (see DIALOG_LOAD_WAIT)
- Check if page has JavaScript errors (F12 console)
- Verify button selector is correct

### "Gemini implementation stuck"
- Check Stop button is actually visible
- Try waiting longer (90s is minimum, complex apps take 5+ minutes)
- Check for JavaScript errors on page

### "GitHub operations failing"
- Verify authentication is still valid (tokens may expire)
- Check GitHub repo doesn't already exist
- Verify git credentials configured locally for clone

---

## Next Steps

1. **Integration Testing**: Test each function independently
2. **MCP Configuration**: Set up aistudio MCP server in Claude Desktop
3. **User Testing**: Have LLMs execute workflows end-to-end
4. **Documentation**: Create RISE specs for automation workflows
5. **Iteration**: Add feedback and enhancements based on usage

---

**Document Status**: Foundation Architecture Complete
**Maintenance**: Review monthly for new patterns and improvements
**Last Updated**: 2025-11-05
