# coaiapy-mcp Implementation Plan (REVISED)

**Package**: coaiapy-mcp - MCP wrapper for coaiapy observability toolkit
**Status**: Design Phase - Library Import Approach
**Created**: 2025-10-16
**Revised**: 2025-10-16 - Changed from subprocess wrapper to library imports
**MCP SDK**: https://github.com/modelcontextprotocol/python-sdk

---

## 🎯 Project Vision

Create an MCP (Model Context Protocol) server that exposes coaiapy's audio processing, Redis stashing, and Langfuse observability capabilities to LLMs through a standardized protocol interface.

### Strategic Benefits
1. **LLM Integration**: Structured access to coaiapy functionality via MCP protocol
2. **Separation of Concerns**: coaiapy maintains Python 3.6 compatibility; MCP wrapper uses modern Python
3. **Independent Evolution**: Packages evolve separately without dependency conflicts
4. **Standardized Interface**: Type-safe tools/resources/prompts via MCP
5. **Direct Library Access**: Faster execution, no subprocess overhead, no environment variable issues

---

## 📦 Package Architecture

### Dual Package Strategy - **LIBRARY IMPORT APPROACH**

```
coaiapy/                        # UNCHANGED (Python 3.6+)
├── Core functionality
├── coaiamodule.py             # Direct Python API
└── CLI commands (for end users)

coaiapy-mcp/                    # NEW (Python 3.10+)
├── pyproject.toml              # MCP SDK dependencies
├── setup.py                    # Package setup
├── requirements.txt            # mcp SDK, coaiapy
├── coaiapy_mcp/
│   ├── __init__.py
│   ├── server.py              # MCP server implementation
│   ├── tools.py               # Tool wrappers (LIBRARY IMPORTS)
│   ├── resources.py           # Resource providers
│   └── prompts.py             # Prompt templates (Mia/Miette)
├── tests/
│   ├── test_tools.py          # Unit tests
│   ├── test_resources.py      # Resource tests
│   └── test_prompts.py        # Prompt tests
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
    "coaiapy>=0.2.54",         # Import as Python library
    "mcp>=0.1.0",              # MCP Python SDK
    "pydantic>=2.0",           # MCP SDK dependency
    "langfuse>=2.0",           # Direct Langfuse client
    "redis>=4.0"               # Direct Redis client
]

[project.scripts]
coaiapy-mcp = "coaiapy_mcp.server:main"
```

---

## 🔧 Implementation Approach: Library Imports (NOT Subprocess)

### Why Library Imports Instead of Subprocess?

**Problems with subprocess wrapper:**
- ❌ Environment variable propagation issues between MCP server → subprocess
- ❌ Slower execution (process creation overhead)
- ❌ Complex error handling (parsing stderr)
- ❌ Credential management nightmare

**Benefits of library imports:**
- ✅ Direct Python function calls - fast and clean
- ✅ Proper exception handling with typed errors
- ✅ Direct access to return values (no JSON parsing)
- ✅ Shared configuration (load once, use everywhere)
- ✅ No environment variable inheritance issues

### Architecture Pattern

```python
# coaiapy_mcp/tools.py
from coaiapy import coaiamodule
from langfuse import Langfuse
import redis
from typing import Dict, Any

# Load configuration once on module import
config = coaiamodule.load_config()

# Initialize clients with config
langfuse_client = Langfuse(
    secret_key=config.get("langfuse_secret_key"),
    public_key=config.get("langfuse_public_key"),
    host=config.get("langfuse_host", "https://cloud.langfuse.com")
)

redis_client = redis.Redis(
    host=config.get("jtaleconf", {}).get("host", "localhost"),
    port=config.get("jtaleconf", {}).get("port", 6379),
    decode_responses=True
)

# Tools call library functions directly
async def coaia_tash(key: str, value: str) -> Dict[str, Any]:
    """Stash key-value pair to Redis via direct library call"""
    try:
        redis_client.set(key, value)
        return {"success": True, "message": f"Stored {key}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 🔧 Phase 1: Core Langfuse Observability (ITERATION 1)

### Priority Tools (Library Import Implementation)

#### 1. Redis Operations

| MCP Tool | Implementation | Input Schema | Output Schema |
|----------|----------------|--------------|---------------|
| `coaia_tash` | `redis_client.set(key, value)` | `{key: str, value: str}` | `{success: bool, message: str}` |
| `coaia_fetch` | `redis_client.get(key)` | `{key: str}` | `{success: bool, value: str}` |

**Implementation:**
```python
# coaiapy_mcp/tools.py
import redis
from typing import Dict, Any
from coaiapy import coaiamodule

# Load config once
config = coaiamodule.load_config()
redis_config = config.get("jtaleconf", {})

# Initialize Redis client
redis_client = redis.Redis(
    host=redis_config.get("host", "localhost"),
    port=redis_config.get("port", 6379),
    db=redis_config.get("db", 0),
    password=redis_config.get("password"),
    decode_responses=True
)

async def coaia_tash(key: str, value: str) -> Dict[str, Any]:
    """Stash key-value pair to Redis via direct client"""
    try:
        redis_client.set(key, value)
        return {
            "success": True,
            "message": f"Stored {key} in Redis"
        }
    except redis.RedisError as e:
        return {
            "success": False,
            "error": f"Redis error: {str(e)}"
        }

async def coaia_fetch(key: str) -> Dict[str, Any]:
    """Fetch value from Redis via direct client"""
    try:
        value = redis_client.get(key)
        if value is None:
            return {
                "success": False,
                "error": f"Key '{key}' not found"
            }
        return {
            "success": True,
            "value": value
        }
    except redis.RedisError as e:
        return {
            "success": False,
            "error": f"Redis error: {str(e)}"
        }
```

#### 2. Langfuse Traces (Full Lifecycle)

| MCP Tool | Implementation | Input Schema | Output Schema |
|----------|----------------|--------------|---------------|
| `coaia_fuse_trace_create` | `langfuse_client.trace(id=..., name=...)` | `{trace_id: str, user_id?: str, session_id?: str, name?: str, metadata?: dict}` | `{success: bool, trace_id: str, details: dict}` |
| `coaia_fuse_add_observation` | `langfuse_client.span(trace_id=..., name=...)` | `{observation_id: str, trace_id: str, name: str, type?: str, parent_id?: str, metadata?: dict}` | `{success: bool, observation_id: str}` |
| `coaia_fuse_trace_view` | `langfuse_client.fetch_trace(trace_id)` | `{trace_id: str}` | `{trace: dict, observations: list}` |

**Implementation:**
```python
# coaiapy_mcp/tools.py
from langfuse import Langfuse
from typing import Dict, Any, Optional

# Initialize Langfuse client
config = coaiamodule.load_config()
langfuse_client = Langfuse(
    secret_key=config.get("langfuse_secret_key"),
    public_key=config.get("langfuse_public_key"),
    host=config.get("langfuse_host", "https://cloud.langfuse.com")
)

async def coaia_fuse_trace_create(
    trace_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create Langfuse trace via direct SDK call"""
    try:
        trace = langfuse_client.trace(
            id=trace_id,
            name=name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata
        )
        return {
            "success": True,
            "trace_id": trace_id,
            "details": {
                "name": name,
                "user_id": user_id,
                "session_id": session_id
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse error: {str(e)}"
        }

async def coaia_fuse_add_observation(
    observation_id: str,
    trace_id: str,
    name: str,
    type: Optional[str] = "SPAN",
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Add observation to trace via direct SDK call"""
    try:
        observation = langfuse_client.span(
            id=observation_id,
            trace_id=trace_id,
            name=name,
            parent_observation_id=parent_id,
            metadata=metadata
        )
        return {
            "success": True,
            "observation_id": observation_id,
            "trace_id": trace_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse error: {str(e)}"
        }

async def coaia_fuse_trace_view(trace_id: str) -> Dict[str, Any]:
    """View trace details via direct SDK call"""
    try:
        trace = langfuse_client.fetch_trace(trace_id)
        return {
            "success": True,
            "trace_id": trace_id,
            "trace": trace.dict() if hasattr(trace, 'dict') else str(trace)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse error: {str(e)}"
        }
```

#### 3. Langfuse Prompts

| MCP Tool | Implementation | Input Schema | Output Schema |
|----------|----------------|--------------|---------------|
| `coaia_fuse_prompts_list` | `langfuse_client.fetch_prompts()` | `{}` | `{prompts: list[dict]}` |
| `coaia_fuse_prompts_get` | `langfuse_client.get_prompt(name)` | `{name: str, label?: str}` | `{prompt: dict}` |

**Implementation:**
```python
async def coaia_fuse_prompts_list() -> Dict[str, Any]:
    """List all Langfuse prompts via direct SDK"""
    try:
        prompts = langfuse_client.fetch_prompts()
        return {
            "success": True,
            "prompts": [p.dict() for p in prompts] if hasattr(prompts[0], 'dict') else prompts
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse error: {str(e)}"
        }

async def coaia_fuse_prompts_get(name: str, label: Optional[str] = None) -> Dict[str, Any]:
    """Get specific Langfuse prompt via direct SDK"""
    try:
        prompt = langfuse_client.get_prompt(name, label=label)
        return {
            "success": True,
            "prompt": prompt.dict() if hasattr(prompt, 'dict') else str(prompt)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Langfuse error: {str(e)}"
        }
```

#### 4. Langfuse Datasets

| MCP Tool | Implementation | Input Schema | Output Schema |
|----------|----------------|--------------|---------------|
| `coaia_fuse_datasets_list` | `langfuse_client.fetch_datasets()` | `{}` | `{datasets: list[dict]}` |
| `coaia_fuse_datasets_get` | `langfuse_client.get_dataset(name)` | `{name: str}` | `{dataset: dict}` |

#### 5. Langfuse Score Configurations

| MCP Tool | Implementation | Input Schema | Output Schema |
|----------|----------------|--------------|---------------|
| `coaia_fuse_score_configs_list` | Use coaiapy smart cache system | `{}` | `{configs: list[dict]}` |
| `coaia_fuse_score_configs_get` | Use coaiapy smart cache system | `{name: str}` | `{config: dict}` |

**Implementation:**
```python
from coaiapy.cofuse import get_config_with_auto_refresh

async def coaia_fuse_score_configs_get(name: str) -> Dict[str, Any]:
    """Get score config using coaiapy's smart cache system"""
    try:
        config = get_config_with_auto_refresh(name)
        if config:
            return {
                "success": True,
                "config": config
            }
        return {
            "success": False,
            "error": f"Config '{name}' not found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Priority Resources (Direct Access)

| Resource URI | Implementation | Content Type | Description |
|--------------|----------------|--------------|-------------|
| `coaia://templates/` | `coaiamodule.list_pipeline_templates()` | `application/json` | List of 5 built-in pipeline templates |
| `coaia://templates/{name}` | `coaiamodule.get_pipeline_template(name)` | `application/json` | Specific template JSON |

**Implementation:**
```python
# coaiapy_mcp/resources.py
from coaiapy import coaiamodule
from typing import Dict, Any

async def list_templates() -> Dict[str, Any]:
    """List pipeline templates via library call"""
    try:
        # Assuming coaiapy exposes this functionality
        templates = coaiamodule.get_available_templates()
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def get_template(name: str) -> Dict[str, Any]:
    """Get template details via library call"""
    try:
        template = coaiamodule.load_template(name)
        return {
            "success": True,
            "template": template
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Priority Prompts (Mia & Miette Duo)

**No changes to prompt system** - remains identical to original plan.

---

## 📋 Implementation Checklist

### Phase 1 (Iteration 1) - Library Import Approach
- [ ] Create coaiapy-mcp package structure
- [ ] Add langfuse and redis to dependencies in pyproject.toml
- [ ] Implement configuration loading from coaiapy
- [ ] Initialize Langfuse and Redis clients on module import
- [ ] Implement MCP server skeleton (`server.py`)
- [ ] Implement Redis tools using redis-py:
  - [ ] `coaia_tash` - direct Redis SET
  - [ ] `coaia_fetch` - direct Redis GET
- [ ] Implement Langfuse trace tools using langfuse-python SDK:
  - [ ] `coaia_fuse_trace_create` - langfuse_client.trace()
  - [ ] `coaia_fuse_add_observation` - langfuse_client.span()
  - [ ] `coaia_fuse_trace_view` - langfuse_client.fetch_trace()
- [ ] Implement Langfuse prompts tools:
  - [ ] `coaia_fuse_prompts_list` - langfuse_client.fetch_prompts()
  - [ ] `coaia_fuse_prompts_get` - langfuse_client.get_prompt()
- [ ] Implement Langfuse datasets tools:
  - [ ] `coaia_fuse_datasets_list`
  - [ ] `coaia_fuse_datasets_get`
- [ ] Implement score-configs tools using coaiapy smart cache
- [ ] Implement template resources using coaiapy library
- [ ] Implement prompts (Mia & Miette, etc.)
- [ ] Write comprehensive tests
- [ ] Create README.md
- [ ] Create ROADMAP.md

---

## 🔬 Testing Strategy

### Unit Tests
```python
# tests/test_tools.py
import pytest
from coaiapy_mcp.tools import coaia_tash, coaia_fetch
from coaiapy_mcp.tools import coaia_fuse_trace_create

@pytest.mark.asyncio
async def test_redis_operations():
    """Test Redis operations via library"""
    # Stash
    result = await coaia_tash("test_key", "test_value")
    assert result["success"] is True

    # Fetch
    result = await coaia_fetch("test_key")
    assert result["success"] is True
    assert result["value"] == "test_value"

@pytest.mark.asyncio
async def test_langfuse_trace():
    """Test Langfuse trace creation via SDK"""
    import uuid

    trace_id = str(uuid.uuid4())
    result = await coaia_fuse_trace_create(
        trace_id=trace_id,
        user_id="test_user",
        name="Test Trace"
    )
    assert result["success"] is True
    assert result["trace_id"] == trace_id
```

---

## 🎯 Success Criteria

### Phase 1 Success Metrics
- ✅ All core tools working with library imports (no subprocess)
- ✅ Configuration loaded from coaiapy without duplication
- ✅ Proper error handling with typed exceptions
- ✅ Template resources accessible
- ✅ 90%+ test coverage
- ✅ Complete documentation

---

## 📝 Next Steps

1. **Update dependencies**: Add langfuse, redis to pyproject.toml
2. **Implement config loading**: Read from coaiapy config system
3. **Initialize clients**: Langfuse and Redis on module import
4. **Implement tools**: Direct library calls (no subprocess)
5. **Test thoroughly**: Unit + integration tests
6. **Document**: README with library approach explanation

---

**Implementation Owner**: Claude Code / jgwill
**Approach**: Library imports (NOT subprocess wrappers)
**Target Completion**: Phase 1 by end of Q4 2025
**License**: MIT (same as coaiapy)
