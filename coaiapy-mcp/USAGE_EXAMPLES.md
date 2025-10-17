# coaiapy-mcp Usage Examples

This document provides practical examples for using coaiapy-mcp with MCP-compatible LLMs.

## Installation

```bash
# Install coaiapy-mcp (includes coaiapy as dependency)
pip install coaiapy-mcp

# Or install from source
git clone https://github.com/jgwill/coaiapy.git
cd coaiapy/coaiapy-mcp
pip install -e .
```

## Prerequisites

Before using coaiapy-mcp, ensure you have:

1. **Redis server** running (for tash/fetch operations)
2. **Langfuse credentials** configured (environment variables):
   ```bash
   export LANGFUSE_SECRET_KEY="sk-lf-..."
   export LANGFUSE_PUBLIC_KEY="pk-lf-..."
   export LANGFUSE_HOST="https://cloud.langfuse.com"
   ```
3. **AWS credentials** (for audio processing in Phase 3)

## Starting the MCP Server

```bash
# Start the MCP server
coaiapy-mcp

# Or run as Python module
python -m coaiapy_mcp.server
```

## MCP Client Configuration

Configure your MCP-compatible LLM client to connect to coaiapy-mcp:

### Claude Desktop Configuration

Add to `~/.config/Claude/config.json`:

```json
{
  "mcpServers": {
    "coaiapy": {
      "command": "coaiapy-mcp",
      "args": []
    }
  }
}
```

### Generic MCP Client Configuration

```json
{
  "servers": [
    {
      "name": "coaiapy",
      "command": ["coaiapy-mcp"],
      "env": {
        "LANGFUSE_SECRET_KEY": "sk-lf-...",
        "LANGFUSE_PUBLIC_KEY": "pk-lf-...",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  ]
}
```

## Example Workflows

### 1. Create a Langfuse Observability Pipeline

**Prompt to LLM**:
```
Use the create_observability_pipeline prompt to help me create a data pipeline trace with these details:
- Trace name: "ETL Data Pipeline"
- User ID: "data_engineer_001"
- Steps: "Extract, Transform, Validate, Load"
```

**Expected Workflow**:
1. LLM loads the `create_observability_pipeline` prompt
2. LLM uses `coaia_fuse_trace_create` to create the trace
3. LLM uses `coaia_fuse_add_observation` for each step
4. LLM uses `coaia_fuse_trace_view` to show the complete trace
5. LLM uses `coaia_tash` to store the trace ID in Redis

### 2. Use Mia & Miette for Technical Guidance

**Prompt to LLM**:
```
I need help designing a microservices architecture. Use the mia_miette_duo prompt with:
- Task context: "Design event-driven microservices for real-time data processing"
- Technical details: "Need to handle 10k events/second with observability"
- Creative goal: "Build a narrative-driven system that tells the story of data flow"
```

**Expected Response**:
- Mia (🧠) provides structural architecture with technical precision
- Miette (🌸) explains the emotional resonance and intuitive understanding
- Unified response combining technical depth with narrative clarity

### 3. List Available Pipeline Templates

**Prompt to LLM**:
```
Read the coaia://templates/ resource to show me available pipeline templates
```

**Expected Response**:
- List of 5 built-in templates
- Template descriptions
- Template variables

### 4. Get Specific Template Details

**Prompt to LLM**:
```
Read the coaia://templates/data-pipeline resource to show me the data pipeline template details
```

**Expected Response**:
- Complete template JSON
- Variable definitions
- Step descriptions

### 5. Stash and Retrieve Data

**Prompt to LLM**:
```
Use coaia_tash to store this configuration:
- Key: "production_config"
- Value: "{\"database\": \"postgres\", \"port\": 5432}"

Then use coaia_fetch to retrieve it and verify.
```

**Expected Workflow**:
1. LLM calls `coaia_tash` tool
2. LLM calls `coaia_fetch` tool
3. LLM shows both results

### 6. Complete Trace Creation Example

**Prompt to LLM**:
```
Create a complete Langfuse trace for my ML pipeline:
1. Generate a UUID for the trace
2. Create trace with name "ML Training Pipeline"
3. Add observations for: Data Loading, Preprocessing, Training, Evaluation
4. Create a parent-child hierarchy where Training has children: Forward Pass, Backward Pass, Optimizer Step
5. Show me the complete trace tree
6. Store the trace ID in Redis with key "ml_pipeline_trace"
```

**Expected Workflow**:
1. LLM generates UUIDs
2. LLM calls `coaia_fuse_trace_create`
3. LLM calls `coaia_fuse_add_observation` multiple times
4. LLM calls `coaia_fuse_trace_view`
5. LLM calls `coaia_tash`
6. LLM presents formatted results

### 7. Query Langfuse Prompts

**Prompt to LLM**:
```
Use coaia_fuse_prompts_list to show all available Langfuse prompts in my project
```

**Expected Response**:
- List of all prompts with metadata
- JSON-formatted output

### 8. Get Dataset Information

**Prompt to LLM**:
```
Use coaia_fuse_datasets_list to show all datasets, then get details for dataset "training_data"
```

**Expected Workflow**:
1. LLM calls `coaia_fuse_datasets_list`
2. LLM calls `coaia_fuse_datasets_get` with name "training_data"
3. LLM presents formatted results

## Advanced Usage

### Batch Observation Creation

**Prompt to LLM**:
```
Create a trace and use coaia_fuse_add_observations_batch to add these observations in one call:
[
  {"id": "obs1", "name": "Step 1", "type": "SPAN"},
  {"id": "obs2", "name": "Step 2", "type": "SPAN", "parent_id": "obs1"},
  {"id": "obs3", "name": "Step 3", "type": "EVENT"}
]
```

### Score Configuration Management

**Prompt to LLM**:
```
List all score configurations, then get details for the "Helpfulness" configuration
```

## Error Handling

All tools return JSON with status information:

```json
{
  "success": true,
  "data": "..."
}
```

Or in case of error:

```json
{
  "success": false,
  "error": "Error message"
}
```

LLMs should check the `success` field and handle errors appropriately.

## Best Practices

1. **Always use UUIDs** for trace and observation IDs
2. **Provide meaningful names** for traces and observations
3. **Use metadata** to add context to traces
4. **Create hierarchies** with parent-child relationships
5. **Store trace IDs** in Redis for later retrieval
6. **Check success status** before proceeding
7. **Use appropriate observation types**: SPAN (duration), EVENT (instant), GENERATION (LLM)

## Troubleshooting

### "coaia command not found"
- Ensure coaiapy is installed: `pip install coaiapy`
- Check PATH includes pip install location

### "Redis connection failed"
- Start Redis: `redis-server`
- Check Redis is running: `redis-cli ping`

### "Langfuse authentication failed"
- Verify environment variables are set
- Check credentials are valid
- Ensure LANGFUSE_HOST is correct

### "Template not found"
- Verify template name is correct
- Use `coaia pipeline list` to see available templates

## Next Steps

- Explore Phase 2 features (pipeline automation) when available
- Explore Phase 3 features (audio processing) when available
- Check ROADMAP.md for upcoming features
- Report issues on GitHub

## Resources

- **Documentation**: https://github.com/jgwill/coaiapy/tree/main/coaiapy-mcp
- **Main coaiapy Package**: https://pypi.org/project/coaiapy/
- **MCP Protocol**: https://github.com/modelcontextprotocol
- **Langfuse**: https://langfuse.com/
