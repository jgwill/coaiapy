# Manual Testing Report: MCP Langfuse Integration

**Date**: 2025-10-17
**Tester**: Mia (Claude Code)
**Focus**: Langfuse trace creation, observation nesting, and URL generation

---

## Executive Summary

Successful trace and observation creation via MCP tools with discovered URL generation issue. The MCP `coaia_fuse_trace_view` tool currently returns incomplete Langfuse URLs missing project_id information.

---

## Testing Workflow

### 1. Trace Creation
**Tool Used**: `mcp__coaiapy__coaia_fuse_trace_create`

```
Trace ID: workflow-exploration-001
User: mia-explorer
Session: session-mcp-discovery
Name: Workflow Exploration and Testing
```

**Result**: ✅ SUCCESS - Trace created successfully

---

### 2. Nested Observations
**Tool Used**: `mcp__coaiapy__coaia_fuse_add_observation`

Created 5 observations with parent-child hierarchy:

| Observation ID | Type | Name | Parent | Status |
|---|---|---|---|---|
| obs-step-1-init | SPAN | Initialize MCP Trace Creation | - | ✅ |
| obs-step-2-discovery | SPAN | Discovery Phase: MCP Tools Available | - | ✅ |
| obs-step-3-validation | SPAN | Validation: Trace Structure Verification | obs-step-2 | ✅ |
| obs-step-4-nesting-test | SPAN | Nesting Test: Parent-Child Hierarchy | obs-step-2 | ✅ |
| obs-step-5-summary | EVENT | Summary: Workflow Completion | - | ✅ |

**Result**: ✅ SUCCESS - All observations created with proper nesting

---

## Issue Discovered: Incomplete URL Generation

### Problem Statement

The MCP tool `coaia_fuse_trace_view` returns:
```
URL: https://cloud.langfuse.com/traces/workflow-exploration-001
```

But the actual correct URL should be:
```
URL: https://us.cloud.langfuse.com/project/cm6m5rrk6001vvkbq7zovttji/traces/workflow-exploration-001
```

### Root Cause Analysis

**File**: `/src/coaiapy/coaiapy-mcp/coaiapy_mcp/tools.py` (lines 305)

```python
# Current implementation (LINE 305)
"url": f"{config.get('langfuse_host', 'https://cloud.langfuse.com')}/traces/{trace_id}"
```

**Issues Identified**:

1. **Missing Project ID**: The URL construction doesn't include the `project_id` from the Langfuse configuration
2. **Missing Region Prefix**: The URL uses generic `cloud.langfuse.com` but should be `us.cloud.langfuse.com` (or region-specific)
3. **Incomplete Path**: Langfuse requires `/project/{project_id}/traces/{trace_id}` structure

### Why This Happens

The `coaia_fuse_trace_view` function in `tools.py` (lines 279-311) doesn't have access to:
- The current Langfuse project ID
- The region information from the host URL

The trace creation uses `add_trace()` from coaiapy which handles this internally, but the trace_view function constructs the URL independently without fetching project context.

---

## Required Fixes

### Option 1: Extract Project ID from Config/Context (RECOMMENDED)

**File**: `coaiapy-mcp/coaiapy_mcp/tools.py` (lines 279-311)

The function needs to:
1. Detect the project_id from Langfuse configuration or API context
2. Extract region from langfuse_host (e.g., "us" from "us.cloud.langfuse.com")
3. Construct complete URL: `{host}/project/{project_id}/traces/{trace_id}`

**Suggested Implementation**:
```python
async def coaia_fuse_trace_view(trace_id: str) -> Dict[str, Any]:
    """
    View trace details via Langfuse API.
    """
    if not LANGFUSE_AVAILABLE:
        return {"success": False, "error": "Langfuse is not available..."}

    try:
        # Get Langfuse host and extract project info
        langfuse_host = config.get('langfuse_host', 'https://cloud.langfuse.com')

        # Fetch current project info to get project_id
        project_info = get_current_project_info()  # From coaiapy.cofuse
        project_id = project_info.get('id') if project_info else None

        if project_id:
            url = f"{langfuse_host}/project/{project_id}/traces/{trace_id}"
        else:
            # Fallback if project_id unavailable
            url = f"{langfuse_host}/traces/{trace_id}"

        return {
            "success": True,
            "trace_id": trace_id,
            "message": "Trace created. View it in Langfuse web UI.",
            "url": url
        }
    except Exception as e:
        return {"success": False, "error": f"Langfuse trace view error: {str(e)}"}
```

### Option 2: Pass Project ID as Parameter

Add `project_id` as optional parameter to `coaia_fuse_trace_view`:
```python
async def coaia_fuse_trace_view(trace_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    # Use passed project_id or detect automatically
```

---

## MCP Configuration Update Needed

**File**: `coaiapy-mcp/.mcp.coaiapy.default.json` or similar

The MCP server definition should document:
- Current project_id availability
- How project_id is retrieved for URL construction
- Whether region detection is automatic or requires configuration

---

## Successful Features Verified

✅ Trace creation with metadata
✅ Observation creation with proper types (SPAN, EVENT)
✅ Parent-child observation nesting
✅ Metadata embedding (input/output tracking)
✅ Multiple observations per trace
✅ Cross-tool MCP integration

---

## Best Practices: Observation Input/Output Documentation

During this testing session, observations were successfully created with rich metadata including input/output tracking. However, the following enhancements should be standardized:

### Current Implementation
Observations are created with metadata containing:
```json
{
  "action": "describe_what_happened",
  "status": "completed|in_progress|failed",
  "input": { /* what went into this step */ },
  "output": { /* what resulted from this step */ }
}
```

### Recommended Enhancement: Detailed Input/Output Tracking

**For Each Observation, Capture**:

1. **Input Data** (what the operation received):
   - Function/tool parameters
   - Configuration state
   - External data sources accessed
   - Previous observation outputs used

2. **Processing Details** (what happened during execution):
   - Algorithm/logic executed
   - Intermediate calculations
   - Decisions made
   - Errors encountered and handled

3. **Output Data** (what was produced):
   - Direct results
   - Side effects (files written, API calls made)
   - Status codes and confirmations
   - Data transformations applied

### Example: Enhanced Observation Structure
```python
metadata = {
    "action": "data_transformation",
    "status": "completed",
    "input": {
        "raw_data": "...",
        "source": "api_endpoint_x",
        "format": "json",
        "record_count": 1000
    },
    "processing": {
        "transformation_type": "normalization",
        "steps_executed": 3,
        "validation_passed": True
    },
    "output": {
        "transformed_data": "...",
        "format": "normalized_json",
        "record_count": 1000,
        "quality_score": 0.98
    }
}
```

### Implementation Guidance

1. **Use metadata fields liberally**: Don't hesitate to add context-specific fields
2. **Capture intermediate states**: Include processing details, not just I/O
3. **Include error handling**: Document retry attempts, fallbacks, mitigation
4. **Add quality metrics**: Success rates, validation scores, performance timing
5. **Cross-reference observations**: Link related observations by ID

### Use Case: MCP Testing Trace
In `workflow-exploration-001`, each observation included:
- `action`: Type of operation being tracked
- `status`: Execution status
- `input`: Parameters and preconditions
- `output`: Results and outcomes

This allowed complete reconstruction of the workflow from trace inspection.

---

## Testing Evidence

**Trace Created**:
- ID: `workflow-exploration-001`
- Observations: 5 (with hierarchy)
- Langfuse Web UI: https://us.cloud.langfuse.com/project/cm6m5rrk6001vvkbq7zovttji/traces/workflow-exploration-001

---

## Recommendations for Development Team

**Priority**: HIGH

1. **Update `coaia_fuse_trace_view` function** to include project_id in URL construction
2. **Document project_id retrieval** method in MCP configuration
3. **Test URL generation** with actual Langfuse API responses
4. **Add region detection** logic if multi-region support is needed
5. **Update MCP schema** if project_id becomes required parameter

---

## Next Steps

- [ ] Implement Option 1 (auto-detect project_id) in tools.py
- [ ] Test with multiple projects to ensure correctness
- [ ] Update MCP server documentation
- [ ] Add unit tests for URL construction
- [ ] Consider caching project_id if performance is concern
