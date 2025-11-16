# Trace Output Patching - CoaiaPy

Update the output field of existing Langfuse traces after creation. Perfect for scenarios where results become available after trace creation or when you need to modify trace outputs.

## Overview

The trace output patching feature allows you to:
- Update trace output after initial trace creation
- Correct or append to trace results
- Support complex data structures (objects, arrays, strings)
- Work seamlessly across CLI, Python SDK, and MCP

## API

### Core Function

```python
def patch_trace_output(trace_id: str, output_data: Any) -> str:
    """
    Update the output field of an existing trace in Langfuse.

    Args:
        trace_id: ID of the trace to update
        output_data: New output data (string, object, or any JSON-serializable data)

    Returns:
        JSON response with success/error status
    """
```

## Usage

### 1. CLI Usage

#### Update with inline JSON
```bash
coaia fuse traces patch-output trace-123 '{"result": "success", "value": 42}'
```

#### Update with string data
```bash
coaia fuse traces patch-output trace-123 "Operation completed successfully"
```

#### Update from file
```bash
coaia fuse traces patch-output trace-123 --file output.json
```

#### Update from stdin
```bash
cat result.json | coaia fuse traces patch-output trace-123
```

#### Auto-detect JSON
```bash
# Automatically parsed as JSON if starts with { or [
coaia fuse traces patch-output trace-123 '[{"id": 1}, {"id": 2}]'
```

### 2. Python SDK Usage

```python
from coaiapy.cofuse import patch_trace_output

# Simple string output
patch_trace_output("trace-id-123", "Processing complete")

# JSON object output
patch_trace_output("trace-id-123", {
    "status": "completed",
    "result": 42,
    "timestamp": "2025-01-01T12:00:00Z"
})

# Array output
patch_trace_output("trace-id-123", [
    {"item": 1, "value": "a"},
    {"item": 2, "value": "b"}
])
```

### 3. MCP Tool Usage

```python
# In Claude or other MCP client
await coaia_fuse_trace_patch_output(
    trace_id="trace-id-123",
    output_data={"result": "success", "data": {...}}
)
```

## Workflow Examples

### Example 1: Initial Trace, Deferred Output

```bash
# Create trace without output (fire and forget)
trace_id=$(uuidgen)
coaia fuse traces create $trace_id -u john -n "Data Processing"

# ... do processing ...

# Patch with final result when ready
coaia fuse traces patch-output $trace_id '{
  "status": "completed",
  "processed_items": 1000,
  "duration_ms": 5432
}'
```

### Example 2: Progressive Updates

```python
from coaiapy.cofuse import add_trace, patch_trace_output
import uuid

trace_id = str(uuid.uuid4())
add_trace(trace_id, name="Multi-step Process")

# Step 1: Initial status
patch_trace_output(trace_id, {"step": 1, "status": "started"})

# Step 2: Progress update
patch_trace_output(trace_id, {"step": 2, "status": "processing", "progress": 50})

# Step 3: Final result
patch_trace_output(trace_id, {
    "step": 3,
    "status": "completed",
    "result": "success",
    "duration": 1234
})
```

### Example 3: LLM Response Streaming

```python
from coaiapy.cofuse import add_trace, patch_trace_output
import uuid

# Create trace with query
trace_id = str(uuid.uuid4())
add_trace(
    trace_id,
    name="LLM Query",
    input_data={"query": "What is AI?"}
)

# Stream response and collect
response_chunks = []
for chunk in llm.stream_response(query):
    response_chunks.append(chunk)

# Patch with complete response
complete_response = "".join(response_chunks)
patch_trace_output(trace_id, {"response": complete_response})
```

### Example 4: Error Correction

```python
from coaiapy.cofuse import add_trace, patch_trace_output

# Initial (incorrect) output
trace_id = "trace-abc-123"
add_trace(
    trace_id,
    name="Calculation",
    output_data={"result": 43}  # Oops, wrong!
)

# Correct it later
patch_trace_output(trace_id, {"result": 42, "corrected": True})
```

### Example 5: Enrichment Pipeline

```python
from coaiapy.cofuse import add_trace, patch_trace_output
import json

# Create minimal trace
trace_id = "pipeline-trace-001"
add_trace(
    trace_id,
    name="Data Pipeline",
    input_data={"raw_data": [...]}
)

# Stage 1: Validation
validation_result = validate_data(raw_data)
patch_trace_output(trace_id, {
    "stage": "validation",
    "valid": validation_result["is_valid"]
})

# Stage 2: Processing
processed = process_data(raw_data)
patch_trace_output(trace_id, {
    "stage": "processing",
    "count": len(processed)
})

# Stage 3: Final with all results
patch_trace_output(trace_id, {
    "stage": "completed",
    "validation": validation_result,
    "processed_count": len(processed),
    "final_data": processed
})
```

## Technical Details

### How It Works

1. **Langfuse Event Model**: Uses Langfuse's ingestion API with event-based updates
2. **Merge Strategy**: When same trace ID is sent with different event ID, Langfuse merges the update
3. **Minimal Payload**: Only sends `output_data` field (plus required trace ID and timestamp)
4. **No Duplication**: Unique event IDs prevent accidental deduplication

### Implementation

```python
def patch_trace_output(trace_id, output_data):
    # Minimal trace body
    body = {
        "id": trace_id,
        "timestamp": now,
        "output": output_data  # Only send output field
    }

    # Unique event ID for this patch
    event_id = f"{trace_id}-patch-{uuid.uuid4().hex[:8]}"

    # Send to Langfuse ingestion API
    event = {
        "id": event_id,
        "timestamp": now,
        "type": "trace-create",  # Langfuse handles as upsert
        "body": body
    }
```

## Supported Data Types

All JSON-serializable types are supported:

- **Strings**: `"simple text"` or JSON strings
- **Numbers**: `42`, `3.14`
- **Booleans**: `true`, `false`
- **Objects**: `{"key": "value", "nested": {...}}`
- **Arrays**: `[1, 2, 3]` or `[{...}, {...}]`
- **Null**: `null`
- **Mixed**: Any combination of the above

## Error Handling

### Common Issues

| Issue | Solution |
|-------|----------|
| Invalid trace ID | Ensure trace exists before patching |
| Invalid JSON | Use `--json` flag or proper JSON syntax |
| Auth failures | Check `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` |
| Large payloads | Keep output under 3.5 MB (Langfuse limit) |

### CLI Error Examples

```bash
# Invalid JSON - will fail with --json flag
coaia fuse traces patch-output trace-123 '{invalid json}' --json
# Error: Failed to parse output as JSON

# Missing trace - creates new trace (Langfuse behavior)
coaia fuse traces patch-output nonexistent-id "output"
# Success: Creates trace if it doesn't exist

# File not found
coaia fuse traces patch-output trace-123 --file missing.json
# Error: File 'missing.json' does not exist
```

## Testing

Run the test suite:

```bash
python test_trace_patch_output.py
```

Tests cover:
- Basic patching with objects
- String output patching
- Complex nested structures
- Array output patching
- Multiple patches to same trace

## Performance

- **Speed**: ~100-200ms per patch (Langfuse API latency)
- **Throughput**: Multiple patches to different traces in parallel
- **Storage**: No additional storage - updates existing trace

## Compatibility

- **CLI**: All operating systems (Unix, Windows, macOS)
- **Python**: 3.6+ (Pythonista compatible)
- **Langfuse**: All projects and organizations
- **MCP**: Available through MCP servers using coaiapy_mcp

## Related Commands

```bash
# Create trace (with or without initial output)
coaia fuse traces create <trace_id> [-o <output>]

# View trace with output
coaia fuse traces trace-view <trace_id>

# Add observations (separate from patch)
coaia fuse traces add-observation <trace_id>

# View trace in JSON
coaia fuse traces trace-view <trace_id> --json
```

## Advanced Patterns

### Conditional Updates
```python
if final_status == "success":
    patch_trace_output(trace_id, {"status": "success", "result": data})
else:
    patch_trace_output(trace_id, {"status": "failed", "error": error_msg})
```

### Batch Updates
```python
import asyncio
from coaiapy.cofuse import patch_trace_output

async def patch_multiple(updates):
    tasks = [
        asyncio.to_thread(patch_trace_output, tid, output)
        for tid, output in updates.items()
    ]
    return await asyncio.gather(*tasks)
```

### Template Variables
```bash
# Using shell variables
RESULT=$(curl https://api.example.com/result)
coaia fuse traces patch-output "$TRACE_ID" "$RESULT"

# Using environment variables
export RESULT='{"status": "complete"}'
coaia fuse traces patch-output $TRACE_ID "$RESULT"
```

## Best Practices

1. **Use Unique Event IDs**: System auto-generates these, no need to worry
2. **Keep Payloads Reasonable**: Large outputs work but impact performance
3. **Complete Early**: Patch output soon after computation for accurate timing
4. **Idempotent Updates**: Multiple patches merge gracefully
5. **Document Intent**: Use clear field names in output data

## Troubleshooting

### Patch not appearing in Langfuse UI

1. Verify trace exists: `coaia fuse traces trace-view <trace_id>`
2. Check Langfuse connectivity: `coaia fuse traces list`
3. Verify credentials: `echo $LANGFUSE_PUBLIC_KEY`
4. Check network: Ensure API endpoint is accessible

### Commands fail silently

```bash
# Add verbose output
coaia fuse traces patch-output trace-id "data" 2>&1

# Check credentials
coaia --help | grep fuse
```

## See Also

- [Langfuse Documentation](https://langfuse.com/docs/tracing)
- [CoaiaPy Traces](./README.md#langfuse-traces)
- [CLI Reference](./README.md#cli-commands)
- [MCP Tools](./coaiapy-mcp/README.md)

---

**Last Updated**: 2025-11-11
**Version**: 0.2.54+
**Status**: Production Ready
