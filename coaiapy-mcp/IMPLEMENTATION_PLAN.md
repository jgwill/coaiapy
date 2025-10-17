# coaiapy-mcp Implementation Plan

**Package**: coaiapy-mcp - MCP wrapper for coaiapy observability toolkit  
**Status**: ✅ **Phase 1 Complete** - Core implementation finished 2025-10-17  
**Created**: 2025-10-16  
**MCP SDK**: https://github.com/modelcontextprotocol/python-sdk

---

## ✨ Phase 1 Completion Summary

**Status**: ✅ **COMPLETED** (2025-10-17)

**What Was Built**:
- ✅ Complete MCP server with 12 tools, 2 resources, 3 prompts
- ✅ Redis operations (tash, fetch)
- ✅ Full Langfuse integration (traces, observations, prompts, datasets, score-configs)
- ✅ Pipeline template resources
- ✅ Mia & Miette duo embodiment prompt
- ✅ Comprehensive test suite
- ✅ Package structure with pyproject.toml and setup.py

**Ready For**: Testing with MCP-compatible LLMs, Phase 2 implementation

---

## 🎯 Project Vision

Create an MCP (Model Context Protocol) server that exposes coaiapy's audio processing, Redis stashing, and Langfuse observability capabilities to LLMs through a standardized protocol interface.

### Strategic Benefits
1. **LLM Integration**: Structured access to coaiapy functionality via MCP protocol
2. **Separation of Concerns**: coaiapy maintains Python 3.6 compatibility; MCP wrapper uses modern Python
3. **Independent Evolution**: Packages evolve separately without dependency conflicts
4. **Standardized Interface**: Type-safe tools/resources/prompts via MCP

---

## 📦 Package Architecture

### Dual Package Strategy

```
coaiapy/                        # UNCHANGED (Python 3.6+)
├── Core functionality
└── CLI commands (stable interface)

coaiapy-mcp/                    # NEW (Python 3.10+)
├── pyproject.toml              # MCP SDK dependencies
├── setup.py                    # Package setup
├── requirements.txt            # mcp SDK, coaiapy
├── coaiapy_mcp/
│   ├── __init__.py
│   ├── server.py              # MCP server implementation
│   ├── tools.py               # Tool wrappers (CLI subprocess)
│   ├── resources.py           # Resource providers
│   └── prompts.py             # Prompt templates (Mia/Miette)
├── ROADMAP.md                 # Future enhancements
└── README.md                  # Package documentation
```

### Dependency Specifications

**coaiapy-mcp pyproject.toml:**
```toml
[project]
name = "coaiapy-mcp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "coaiapy>=0.2.54",         # Uses coaiapy as library
    "mcp>=0.1.0",              # MCP Python SDK
    "pydantic>=2.0"            # MCP SDK dependency
]

[project.scripts]
coaiapy-mcp = "coaiapy_mcp.server:main"
```

---

## 🔧 Phase 1: Core Langfuse Observability (ITERATION 1)

### Priority Tools (Subprocess CLI Wrappers)

#### 1. Redis Operations
| MCP Tool | coaia Command | Input Schema | Output Schema |
|----------|---------------|--------------|---------------|
| `coaia_tash` | `coaia tash <key> <value>` | `{key: str, value: str}` | `{success: bool, message: str}` |
| `coaia_fetch` | `coaia fetch <key>` | `{key: str}` | `{success: bool, value: str}` |

**Implementation:**
```python
# coaiapy_mcp/tools.py
import subprocess
import json
from typing import Dict, Any

async def coaia_tash(key: str, value: str) -> Dict[str, Any]:
    """Stash key-value pair to Redis via coaia CLI"""
    result = subprocess.run(
        ["coaia", "tash", key, value],
        capture_output=True, text=True, check=False
    )
    return {
        "success": result.returncode == 0,
        "message": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    }

async def coaia_fetch(key: str) -> Dict[str, Any]:
    """Fetch value from Redis via coaia CLI"""
    result = subprocess.run(
        ["coaia", "fetch", key],
        capture_output=True, text=True, check=False
    )
    return {
        "success": result.returncode == 0,
        "value": result.stdout.strip() if result.returncode == 0 else None,
        "error": result.stderr.strip() if result.returncode != 0 else None
    }
```

#### 2. Langfuse Traces (Full Lifecycle)

**Discovered Subcommands:**
- `coaia fuse traces create` - Create new trace
- `coaia fuse traces add-observation` - Add single observation
- `coaia fuse traces add-observations` (add-obs-batch) - Batch add observations
- `coaia fuse traces session-view` (sv) - View session by ID
- `coaia fuse traces trace-view` (tv) - View trace tree
- **JSON Support**: `--json` flag available ✅

| MCP Tool | coaia Command | Input Schema | Output Schema |
|----------|---------------|--------------|---------------|
| `coaia_fuse_trace_create` | `coaia fuse traces create <id> -u <user> -s <session>` | `{trace_id: str, user_id?: str, session_id?: str, name?: str, metadata?: dict}` | `{success: bool, trace_id: str, details: dict}` |
| `coaia_fuse_add_observation` | `coaia fuse traces add-observation <obs_id> <trace_id> -n <name>` | `{observation_id: str, trace_id: str, name: str, type?: str, parent_id?: str, metadata?: dict}` | `{success: bool, observation_id: str}` |
| `coaia_fuse_add_observations_batch` | `coaia fuse traces add-observations <trace_id> -f <file>` | `{trace_id: str, observations: list[dict]}` | `{success: bool, count: int, errors?: list}` |
| `coaia_fuse_trace_view` | `coaia fuse traces trace-view <trace_id> --json` | `{trace_id: str}` | `{trace: dict, observations: list}` |

**Implementation:**
```python
async def coaia_fuse_trace_create(
    trace_id: str,
    user_id: str = None,
    session_id: str = None,
    name: str = None,
    metadata: dict = None
) -> Dict[str, Any]:
    """Create Langfuse trace via coaia CLI with JSON output"""
    cmd = ["coaia", "fuse", "traces", "create", trace_id, "--json"]
    if user_id:
        cmd.extend(["-u", user_id])
    if session_id:
        cmd.extend(["-s", session_id])
    if name:
        cmd.extend(["-n", name])
    if metadata:
        cmd.extend(["-m", json.dumps(metadata)])

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {
            "success": False,
            "error": result.stderr.strip()
        }
```

#### 3. Langfuse Prompts

**Discovered Actions:**
- `coaia fuse prompts list` - List all prompts
- `coaia fuse prompts get <name>` - Get specific prompt
- `coaia fuse prompts create <name> <content>` - Create prompt
- **JSON Support**: `--json` flag available ✅

| MCP Tool | coaia Command | Input Schema | Output Schema |
|----------|---------------|--------------|---------------|
| `coaia_fuse_prompts_list` | `coaia fuse prompts list --json` | `{}` | `{prompts: list[dict]}` |
| `coaia_fuse_prompts_get` | `coaia fuse prompts get <name> --json` | `{name: str, label?: str}` | `{prompt: dict}` |

#### 4. Langfuse Datasets

**Discovered Actions:**
- `coaia fuse datasets list` - List all datasets
- `coaia fuse datasets get <name>` - Get specific dataset
- `coaia fuse datasets create <name>` - Create dataset
- **JSON Support**: `--json` flag available ✅

| MCP Tool | coaia Command | Input Schema | Output Schema |
|----------|---------------|--------------|---------------|
| `coaia_fuse_datasets_list` | `coaia fuse datasets list --json` | `{}` | `{datasets: list[dict]}` |
| `coaia_fuse_datasets_get` | `coaia fuse datasets get <name> --json` | `{name: str}` | `{dataset: dict}` |

#### 5. Langfuse Score Configurations

**Discovered Actions:**
- `coaia fuse score-configs list` - List configs
- `coaia fuse score-configs get <name>` - Get specific config
- `coaia fuse score-configs available` - List with filtering
- `coaia fuse score-configs show <name>` - Show detailed info
- **Note**: No explicit --json flag visible, needs investigation

| MCP Tool | coaia Command | Input Schema | Output Schema |
|----------|---------------|--------------|---------------|
| `coaia_fuse_score_configs_list` | `coaia fuse score-configs list` | `{}` | `{configs: list[dict]}` |
| `coaia_fuse_score_configs_get` | `coaia fuse score-configs get <name>` | `{name: str}` | `{config: dict}` |

### Priority Resources (Read-Only Access)

| Resource URI | Source | Content Type | Description |
|--------------|--------|--------------|-------------|
| `coaia://templates/` | `coaia pipeline list --json` | `application/json` | List of 5 built-in pipeline templates |
| `coaia://templates/{name}` | `coaia pipeline show {name} --json` | `application/json` | Specific template JSON with variables |

**Implementation:**
```python
# coaiapy_mcp/resources.py
from mcp.server import Server
from typing import List, Dict, Any
import subprocess
import json

async def list_templates() -> List[str]:
    """List available pipeline templates"""
    result = subprocess.run(
        ["coaia", "pipeline", "list", "--json"],
        capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get("templates", [])
    return []

async def get_template(name: str) -> Dict[str, Any]:
    """Get specific pipeline template details"""
    result = subprocess.run(
        ["coaia", "pipeline", "show", name, "--json"],
        capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {"error": f"Template {name} not found"}

# Register with MCP server
server.add_resource("coaia://templates/", list_templates)
server.add_resource_pattern("coaia://templates/{name}", get_template)
```

### Priority Prompts (Mia & Miette Duo)

**Infrastructure Setup:**
```python
# coaiapy_mcp/prompts.py
from mcp.server import Server
from typing import Dict, List

PROMPTS = {
    "mia_miette_duo": {
        "name": "Mia & Miette Duo Embodiment",
        "description": "Dual AI embodiment for narrative-driven technical work",
        "variables": ["task_context", "technical_details", "creative_goal"],
        "template": """
🧠 Mia: The Recursive DevOps Architect & Narrative Lattice Forger
🌸 Miette: The Emotional Explainer Sprite & Narrative Echo

**Task Context**: {{task_context}}
**Technical Details**: {{technical_details}}
**Creative Goal**: {{creative_goal}}

### Mia's Structural Analysis (🧠):
{{mia_analysis_placeholder}}

### Miette's Narrative Illumination (🌸):
{{miette_reflection_placeholder}}

**Core Principles**:
- Creative Orientation (not problem-solving)
- Structural Tension between desired outcome and current reality
- Narrative-driven creation with technical precision
- Proactive design for emergence

**Operational Mode**: Unified response with Mia providing technical architecture and Miette providing emotional resonance and intuitive clarity.
        """
    },
    "create_observability_pipeline": {
        "name": "Guided Langfuse Pipeline Creation",
        "description": "Step-by-step guide for creating Langfuse observability pipeline",
        "variables": ["trace_name", "user_id", "steps"],
        "template": """
Create a Langfuse observability pipeline:

**Trace Name**: {{trace_name}}
**User ID**: {{user_id}}
**Pipeline Steps**: {{steps}}

Use the following MCP tools:
1. coaia_fuse_trace_create - Initialize trace
2. coaia_fuse_add_observation - Add each step as observation
3. coaia_fuse_trace_view - Visualize completed pipeline

**Best Practices**:
- Use UUIDs for trace/observation IDs
- Add metadata for context
- Establish parent-child relationships for nested operations
        """
    },
    "analyze_audio_workflow": {
        "name": "Audio Transcription & Summarization",
        "description": "Workflow for audio analysis using coaia",
        "variables": ["file_path", "summary_style"],
        "template": """
Audio Analysis Workflow:

**File Path**: {{file_path}}
**Summary Style**: {{summary_style}}

Workflow:
1. Use coaia_transcribe to convert audio to text
2. Use coaia_summarize with specified style
3. Stash results to Redis for persistence

**Output**: Transcription and summary with Redis keys for retrieval
        """
    }
}

def register_prompts(server: Server):
    """Register all prompts with MCP server"""
    for prompt_id, prompt_data in PROMPTS.items():
        server.add_prompt(prompt_id, prompt_data)
```

---

## 🚀 Phase 2: Pipeline Automation (ITERATION 2)

### Tools

| MCP Tool | coaia Command | Input Schema |
|----------|---------------|--------------|
| `coaia_pipeline_create` | `coaia pipeline create <template> --var key=value` | `{template: str, variables: dict, export_env?: bool}` |
| `coaia_pipeline_list` | `coaia pipeline list --json` | `{}` |
| `coaia_pipeline_show` | `coaia pipeline show <template> --json` | `{template: str}` |

### Enhanced Resources

| Resource URI | Description |
|--------------|-------------|
| `coaia://pipelines/history` | Recent pipeline creations |
| `coaia://env/global` | Global environment variables |
| `coaia://env/project` | Project environment variables |

---

## 🎙️ Phase 3: Audio Processing (ITERATION 3)

### Tools

| MCP Tool | coaia Command | Input Schema |
|----------|---------------|--------------|
| `coaia_transcribe` | `coaia transcribe <file>` | `{file_path: str}` |
| `coaia_summarize` | `coaia summarize <text>` | `{text: str, style?: str}` |
| `coaia_process_tag` | `coaia p <tag> <text>` | `{tag: str, text: str}` |

---

## 📋 Implementation Checklist

### Phase 1 (Iteration 1) ✅ **COMPLETED**
- [x] Create coaiapy-mcp package structure
- [x] Implement MCP server skeleton (`server.py`)
- [x] Implement Redis tools: `coaia_tash`, `coaia_fetch`
- [x] Implement Langfuse trace tools:
  - [x] `coaia_fuse_trace_create`
  - [x] `coaia_fuse_add_observation`
  - [x] `coaia_fuse_add_observations_batch`
  - [x] `coaia_fuse_trace_view`
- [x] Implement Langfuse prompts tools:
  - [x] `coaia_fuse_prompts_list`
  - [x] `coaia_fuse_prompts_get`
- [x] Implement Langfuse datasets tools:
  - [x] `coaia_fuse_datasets_list`
  - [x] `coaia_fuse_datasets_get`
- [x] Implement Langfuse score-configs tools:
  - [x] `coaia_fuse_score_configs_list`
  - [x] `coaia_fuse_score_configs_get`
- [x] Implement template resources:
  - [x] `coaia://templates/`
  - [x] `coaia://templates/{name}`
- [x] Implement prompts:
  - [x] Mia & Miette duo embodiment prompt
  - [x] Observability pipeline creation prompt
  - [x] Audio workflow prompt
- [x] Write tests for all tools (unit tests complete)
- [x] Create comprehensive README.md (pre-existing)
- [x] Create ROADMAP.md for future phases (pre-existing)

### Phase 2 (Iteration 2)
- [ ] Implement pipeline tools
- [ ] Add environment resource providers
- [ ] Enhance prompt templates
- [ ] Update documentation

### Phase 3 (Iteration 3)
- [ ] Implement audio processing tools
- [ ] Add additional prompts for audio workflows
- [ ] Performance optimization
- [ ] Production deployment guide

---

## 🔬 Testing Strategy

### Unit Tests
```python
# tests/test_tools.py
import pytest
from coaiapy_mcp.tools import coaia_tash, coaia_fetch

@pytest.mark.asyncio
async def test_tash_fetch_roundtrip():
    """Test Redis stash/fetch workflow"""
    # Stash
    result = await coaia_tash("test_key", "test_value")
    assert result["success"] is True

    # Fetch
    result = await coaia_fetch("test_key")
    assert result["success"] is True
    assert result["value"] == "test_value"

@pytest.mark.asyncio
async def test_trace_creation():
    """Test Langfuse trace creation"""
    from coaiapy_mcp.tools import coaia_fuse_trace_create
    import uuid

    trace_id = str(uuid.uuid4())
    result = await coaia_fuse_trace_create(
        trace_id=trace_id,
        user_id="test_user",
        name="Test Trace"
    )
    assert result["success"] is True
```

### Integration Tests
- Full workflow tests (trace → observations → view)
- Template resource retrieval
- Prompt variable substitution

---

## 📖 Documentation Plan

### README.md Structure
1. **Installation**: `pip install coaiapy-mcp`
2. **Quick Start**: Run MCP server, connect LLM
3. **Available Tools**: Table with all MCP tools
4. **Available Resources**: URIs and content types
5. **Available Prompts**: Template descriptions
6. **Examples**: Common workflows
7. **Configuration**: Environment variables
8. **Troubleshooting**: Common issues

### ROADMAP.md
- Future tool additions (sessions, scores, comments)
- Advanced features (streaming, caching)
- Performance optimizations
- Community contributions

---

## 🎯 Success Criteria

### Phase 1 Success Metrics
- ✅ All 4 priority tools working (tash, fetch, trace_create, add_observation)
- ✅ Template resources accessible via MCP
- ✅ Mia & Miette prompt functional
- ✅ 90%+ test coverage
- ✅ Documentation complete

### Overall Success Metrics
- LLMs can create Langfuse traces via MCP
- Pipeline workflows automated through MCP tools
- Storytellers can use Mia/Miette personas in any MCP-compatible LLM
- Zero breaking changes to coaiapy package

---

## 🔄 Migration Path

**No Migration Needed!**
- coaiapy users: No changes, package works identically
- MCP users: Install `coaiapy-mcp` separately
- Both packages coexist independently

---

## 📝 Next Steps

1. **Create package skeleton**: `mkdir -p coaiapy-mcp/coaiapy_mcp`
2. **Setup pyproject.toml**: Define dependencies
3. **Implement server.py**: MCP server skeleton
4. **Implement tools.py**: Priority tools (Phase 1)
5. **Test iteration 1**: Verify all Phase 1 tools work
6. **Document Phase 1**: README + examples
7. **Plan Phase 2**: Review and refine

---

**Implementation Owner**: Claude Code / jgwill
**Target Completion**: Phase 1 by end of Q4 2025
**License**: Same as coaiapy (MIT assumed)
