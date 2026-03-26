# Configuration Guide

## Feature Configuration System

The coaiapy-mcp server supports selective feature exposure to optimize token usage in Claude Code and other MCP-compatible LLM contexts.

### Environment Variable

```bash
export COAIAPY_MCP_FEATURES="STANDARD"
```

Valid values: `MINIMAL`, `STANDARD`, `OBSERVABILITY`, `FULL`

Default: `STANDARD`

---

## Feature Levels

### MINIMAL

**Purpose**: Absolute minimum for core trace creation and observability

**Included:**
- ✅ **18 Tools**
  - Redis: `coaia_tash`, `coaia_fetch`
  - Traces: `coaia_fuse_trace_create`, `coaia_fuse_add_observation`, `coaia_fuse_trace_patch_output`, `coaia_fuse_trace_get`, `coaia_fuse_trace_view`, `coaia_fuse_observation_get`, `coaia_fuse_traces_session_view`
  - Comments: `coaia_fuse_comments_list`, `coaia_fuse_comments_get`, `coaia_fuse_comments_create`
  - Prompts (Langfuse): `coaia_fuse_prompts_list`, `coaia_fuse_prompts_get`
  - Datasets: `coaia_fuse_datasets_list`, `coaia_fuse_datasets_get`
  - Score Configs: `coaia_fuse_score_configs_list`, `coaia_fuse_score_configs_get`
- ❌ **0 Prompts**
- ❌ **0 Resources**

**Use Cases:**
- Basic trace and observation creation
- Langfuse management without workflow guides
- Minimal context window usage for long sessions

**Token Savings:** ~3000 tokens vs FULL

---

### STANDARD (Default)

**Purpose**: Balanced feature set for everyday workflows

**Included:**
- ✅ **18 Tools** (same as MINIMAL)
- ✅ **2 Prompts**
  - `create_observability_pipeline` - Guided Langfuse pipeline creation
  - `analyze_audio_workflow` - Audio transcription & summarization workflow
- ✅ **1 Resource**
  - `coaia://templates/` - Pipeline templates

**Use Cases:**
- Guided observability pipeline creation
- Audio analysis workflows
- Standard development sessions

**Token Savings:** ~1300 tokens vs FULL

---

### OBSERVABILITY

**Purpose**: Observability-focused workflows (currently identical to STANDARD, reserved for future expansion)

**Included:**
- ✅ **18 Tools** (same as MINIMAL)
- ✅ **2 Prompts** (same as STANDARD)
- ✅ **1 Resource** (same as STANDARD)

**Use Cases:**
- Same as STANDARD
- Future: Enhanced observability features

**Token Savings:** ~1300 tokens vs FULL

---

### FULL

**Purpose**: Complete feature access including Mia & Miette persona and media tools

**Included:**
- ✅ **20 Tools** (MINIMAL + media)
  - All MINIMAL tools
  - Media: `coaia_fuse_media_upload`, `coaia_fuse_media_get`
- ✅ **3 Prompts**
  - `mia_miette_duo` - Dual AI embodiment (Mia & Miette) for narrative-driven technical work
  - `create_observability_pipeline`
  - `analyze_audio_workflow`
- ✅ **1 Resource**
  - `coaia://templates/`

**Use Cases:**
- Mia & Miette dual AI embodiment workflows
- Media file attachment to traces
- Maximum flexibility

**Token Savings:** 0 (baseline)

---

## Configuration Examples

### Claude Code MCP Configuration

Add to your Claude Code MCP configuration file:

```json
{
  "mcpServers": {
    "coaiapy": {
      "command": "coaiapy-mcp",
      "args": ["start"],
      "env": {
        "COAIAPY_MCP_FEATURES": "STANDARD",
        "LANGFUSE_SECRET_KEY": "sk-lf-...",
        "LANGFUSE_PUBLIC_KEY": "pk-lf-...",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

### Shell Environment

```bash
# Set feature level
export COAIAPY_MCP_FEATURES="MINIMAL"

# Start server
coaiapy-mcp start
```

### Docker Environment

```dockerfile
ENV COAIAPY_MCP_FEATURES=STANDARD
```

---

## Feature Behavior

### Tool Filtering

Tools not in the current feature set:
- ❌ Are not listed in `server.list_tools()`
- ❌ Return error if called directly
- ✅ Reduce token usage in LLM context

### Prompt Filtering

Prompts not in the current feature set:
- ❌ Are not listed in `server.list_prompts()`
- ❌ Return error message if requested:
  ```
  Prompt 'mia_miette_duo' is not available in STANDARD feature set
  ```

### Resource Filtering

Resources not in the current feature set:
- ❌ Are not listed in `server.list_resources()`
- ❌ Return error JSON if accessed:
  ```json
  {"error": "Resource 'coaia://templates/' is not available in MINIMAL feature set"}
  ```

---

## Server Startup Logging

The server logs the active feature level on startup:

```
INFO - Starting coaiapy-mcp server with feature level: STANDARD
INFO - Enabled features: 18 tools, 2 prompts, 1 resources
```

This confirms the configuration is loaded correctly.

---

## Token Usage Analysis

### Estimated Token Counts (Approximate)

| Component | MINIMAL | STANDARD | OBSERVABILITY | FULL |
|-----------|---------|----------|---------------|------|
| **Tools** | ~3100 | ~3100 | ~3100 | ~3700 |
| **Prompts** | 0 | ~3000 | ~3000 | ~4200 |
| **Resources** | 0 | ~300 | ~300 | ~300 |
| **TOTAL** | **~3100** | **~6400** | **~6400** | **~8200** |
| **Savings vs FULL** | **~5100** | **~1800** | **~1800** | **0** |

### Prompt Breakdown

- `mia_miette_duo`: ~1200 tokens (FULL only)
- `create_observability_pipeline`: ~1800 tokens (STANDARD+)
- `analyze_audio_workflow`: ~1200 tokens (STANDARD+)

---

## Recommendations

### For Long Sessions
Use `MINIMAL` to preserve context window for actual work:
```bash
export COAIAPY_MCP_FEATURES="MINIMAL"
```

### For Workflow Development
Use `STANDARD` to access pipeline creation guides:
```bash
export COAIAPY_MCP_FEATURES="STANDARD"
```

### For Narrative-Driven Work
Use `FULL` to access Mia & Miette dual embodiment:
```bash
export COAIAPY_MCP_FEATURES="FULL"
```

---

## Troubleshooting

### Invalid Feature Level

If an invalid value is provided:
```
⚠️  Invalid COAIAPY_MCP_FEATURES='INVALID', using STANDARD
```

The server falls back to `STANDARD` and logs a warning.

### Accessing Disabled Features

If a tool/prompt/resource is accessed but not enabled:
- Tools: Error returned from `call_tool()`
- Prompts: Error message in `GetPromptResult`
- Resources: Error JSON from `read_resource()`

### Verification

Check server logs to confirm feature level:
```bash
grep "feature level" /var/log/coaiapy-mcp.log
```

---

## Implementation Details

### Source Files

- `coaiapy_mcp/config.py` - Feature configuration system
- `coaiapy_mcp/server.py` - Feature filtering logic

### Feature Set Definitions

All feature sets are defined in `config.py`:

```python
FEATURE_SETS = {
    "MINIMAL": {...},
    "STANDARD": {...},
    "OBSERVABILITY": {...},
    "FULL": {...},
}
```

### Runtime Behavior

1. **Server Startup**: `get_config()` reads `COAIAPY_MCP_FEATURES`
2. **Tool Registration**: `list_tools()` filters based on `is_tool_enabled()`
3. **Prompt Registration**: `list_prompts()` filters based on `is_prompt_enabled()`
4. **Resource Registration**: `list_resources()` filters based on `is_resource_enabled()`

---

## Future Enhancements

- Per-tool feature flags (e.g., `COAIAPY_MCP_TOOLS="tash,fetch,trace_create"`)
- User-defined feature sets via config file
- Dynamic feature toggling without server restart
- Feature usage analytics and recommendations

---

**Last Updated**: 2025-12-02
**Related Issues**: #75
