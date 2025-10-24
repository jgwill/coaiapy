"""
MCP Prompts implementation for coaiapy personas and workflows.

Provides prompt templates for:
- Mia & Miette dual AI embodiment
- Guided observability pipeline creation
- Audio analysis workflows
"""

from typing import Dict, Any, List, Optional

# ============================================================================
# Prompt Definitions
# ============================================================================

PROMPTS = {
    "mia_miette_duo": {
        "name": "Mia & Miette Duo Embodiment",
        "description": "Dual AI embodiment for narrative-driven technical work",
        "variables": [
            {
                "name": "task_context",
                "type": "string",
                "description": "High-level task description",
                "required": True,
            },
            {
                "name": "technical_details",
                "type": "string",
                "description": "Specific technical requirements and constraints",
                "required": True,
            },
            {
                "name": "creative_goal",
                "type": "string",
                "description": "Desired creative outcome or narrative objective",
                "required": True,
            },
        ],
        "template": """🧠 Mia: The Recursive DevOps Architect & Narrative Lattice Forger
🌸 Miette: The Emotional Explainer Sprite & Narrative Echo

**Task Context**: {{task_context}}
**Technical Details**: {{technical_details}}
**Creative Goal**: {{creative_goal}}

### Mia's Structural Analysis (🧠):

*[Mia analyzes the structural tension between current reality and desired outcome]*

**Current Reality Assessment:**
- Technical constraints and existing infrastructure
- System architecture patterns and dependencies
- Resource availability and limitations

**Structural Tension Identification:**
- Gap between current state and creative goal
- Key architectural decisions needed
- Potential emergence patterns

**Proactive Design Approach:**
- System architecture recommendations
- Implementation patterns and best practices
- Integration points and data flow

**Technical Roadmap:**
1. Foundation: Core infrastructure setup
2. Integration: Connect components and services
3. Refinement: Optimize and enhance
4. Emergence: Allow for creative adaptation

### Miette's Narrative Illumination (🌸):

*[Miette provides emotional resonance and intuitive clarity]*

**Narrative Framing:**
What we're really creating here is {{creative_goal}}. The technical details matter because they're the building blocks of the story we're telling.

**Emotional Context:**
The structural tension Mia identified isn't just a technical gap—it's the creative space where innovation happens. This tension is productive and necessary.

**Intuitive Understanding:**
Think of it this way: {{task_context}} is like [relatable metaphor]. The technical pieces fit together to create something greater than their sum.

**Creative Encouragement:**
The path from current reality to desired outcome might seem complex, but each step builds naturally on the last. Trust the process, iterate thoughtfully, and let the solution emerge.

---

**Core Principles Applied:**
- ✨ Creative Orientation (not problem-solving)
- 📊 Structural Tension between desired outcome and current reality
- 📖 Narrative-driven creation with technical precision
- 🌱 Proactive design for emergence

**Operational Mode**: Unified response with Mia providing technical architecture and Miette providing emotional resonance and intuitive clarity.
""",
    },
    
    "create_observability_pipeline": {
        "name": "Guided Langfuse Pipeline Creation",
        "description": "Step-by-step guide for creating Langfuse observability pipeline",
        "variables": [
            {
                "name": "trace_name",
                "type": "string",
                "description": "Name for the trace/pipeline",
                "required": True,
            },
            {
                "name": "user_id",
                "type": "string",
                "description": "User identifier for the trace",
                "required": True,
            },
            {
                "name": "steps",
                "type": "string",
                "description": "Pipeline steps (comma-separated)",
                "required": True,
            },
        ],
        "template": """# Create Langfuse Observability Pipeline

**Pipeline Name**: {{trace_name}}
**User ID**: {{user_id}}
**Pipeline Steps**: {{steps}}

## Step-by-Step Guide

### 1. Create the Main Trace

Use the `coaia_fuse_trace_create` tool:

```
{
  "trace_id": "{{trace_name}}-{{timestamp}}",
  "user_id": "{{user_id}}",
  "name": "{{trace_name}}",
  "metadata": {
    "pipeline_type": "observability",
    "created_by": "mcp_prompt"
  }
}
```

### 2. Add Observations for Each Step

For each step in: {{steps}}

Use the `coaia_fuse_add_observation` tool:

```
{
  "observation_id": "obs-{{step_name}}-{{timestamp}}",
  "trace_id": "{{trace_name}}-{{timestamp}}",
  "name": "{{step_name}}",
  "observation_type": "SPAN",
  "metadata": {
    "step_order": {{index}},
    "description": "{{step_description}}"
  }
}
```

### 3. Establish Parent-Child Relationships

For nested operations, use the `parent_id` parameter:

```
{
  "observation_id": "obs-child-{{timestamp}}",
  "trace_id": "{{trace_name}}-{{timestamp}}",
  "name": "Child Operation",
  "parent_id": "obs-parent-{{timestamp}}",
  "observation_type": "SPAN"
}
```

### 4. View Completed Pipeline

Use the `coaia_fuse_trace_view` tool:

```
{
  "trace_id": "{{trace_name}}-{{timestamp}}"
}
```

## Best Practices

- **Use UUIDs**: For production, use proper UUID generation for trace/observation IDs
- **Add Metadata**: Include context like step order, descriptions, tags
- **Timing**: Use start_time and end_time for accurate duration tracking
- **Hierarchy**: Establish clear parent-child relationships for nested operations
- **Types**: Use SPAN for operations, EVENT for discrete events, GENERATION for LLM calls

## Example Usage

```python
# 1. Create trace
trace = coaia_fuse_trace_create(
    trace_id="etl-pipeline-2025",
    user_id="{{user_id}}",
    name="{{trace_name}}"
)

# 2. Add observations for each step
for step in ["{{steps}}".split(",")]:
    observation = coaia_fuse_add_observation(
        observation_id=f"obs-{step}-{timestamp}",
        trace_id="etl-pipeline-2025",
        name=step.strip(),
        observation_type="SPAN"
    )

# 3. View results
result = coaia_fuse_trace_view("etl-pipeline-2025")
```
""",
    },
    
    "analyze_audio_workflow": {
        "name": "Audio Transcription & Summarization",
        "description": "Workflow for audio analysis using coaia",
        "variables": [
            {
                "name": "file_path",
                "type": "string",
                "description": "Path to the audio file",
                "required": True,
            },
            {
                "name": "summary_style",
                "type": "string",
                "description": "Summarization style (concise, detailed, narrative)",
                "required": False,
                "default": "concise",
            },
        ],
        "template": """# Audio Analysis Workflow

**File Path**: {{file_path}}
**Summary Style**: {{summary_style}}

## Workflow Steps

### 1. Transcribe Audio

Use coaia's transcription tool to convert audio to text:

```bash
coaia transcribe {{file_path}}
```

This will:
- Process the audio file
- Return the full transcription
- Detect language automatically
- Include timestamps (if supported)

### 2. Summarize Transcription

Use coaia's summarization with the specified style:

```bash
coaia summarize "{{transcription_text}}" --style {{summary_style}}
```

Summary styles:
- **concise**: Brief overview of key points
- **detailed**: Comprehensive summary with examples
- **narrative**: Story-like summary with flow

### 3. Store Results in Redis

Stash both transcription and summary for future retrieval:

```python
# Store transcription
coaia_tash(
    key="audio_{{file_name}}_transcription",
    value="{{transcription_text}}"
)

# Store summary
coaia_tash(
    key="audio_{{file_name}}_summary_{{summary_style}}",
    value="{{summary_text}}"
)
```

### 4. Retrieve Results

Fetch stored results anytime:

```python
# Get transcription
transcription = coaia_fetch("audio_{{file_name}}_transcription")

# Get summary
summary = coaia_fetch("audio_{{file_name}}_summary_{{summary_style}}")
```

## Output Format

**Transcription Key**: `audio_{{file_name}}_transcription`
**Summary Key**: `audio_{{file_name}}_summary_{{summary_style}}`

**Example**:
- Transcription: "This is the full audio transcription..."
- Summary (concise): "Key points: [bullet points]"
- Summary (detailed): "The audio discusses... In detail: ..."
- Summary (narrative): "The story begins with... and evolves through..."

## Integration with Observability

Create a trace to track the analysis:

```python
# Create trace for audio analysis
trace = coaia_fuse_trace_create(
    trace_id=f"audio-analysis-{{file_name}}",
    name="Audio Analysis Workflow",
    metadata={"file": "{{file_path}}", "style": "{{summary_style}}"}
)

# Add observation for transcription
obs1 = coaia_fuse_add_observation(
    observation_id="obs-transcribe",
    trace_id=trace["trace_id"],
    name="Transcription",
    observation_type="SPAN"
)

# Add observation for summarization
obs2 = coaia_fuse_add_observation(
    observation_id="obs-summarize",
    trace_id=trace["trace_id"],
    name="Summarization",
    observation_type="SPAN",
    parent_id="obs-transcribe"
)
```
""",
    },
}


# ============================================================================
# Prompt Helper Functions
# ============================================================================

def get_prompt(prompt_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific prompt by ID.
    
    Args:
        prompt_id: The prompt identifier
        
    Returns:
        Prompt dictionary or None if not found
    """
    return PROMPTS.get(prompt_id)


def list_prompts() -> List[Dict[str, Any]]:
    """
    List all available prompts.
    
    Returns:
        List of prompt metadata (without full templates)
    """
    return [
        {
            "id": prompt_id,
            "name": prompt["name"],
            "description": prompt["description"],
            "variables": prompt["variables"],
        }
        for prompt_id, prompt in PROMPTS.items()
    ]


def render_prompt(prompt_id: str, variables: Dict[str, str]) -> Optional[str]:
    """
    Render a prompt template with provided variables.
    
    Args:
        prompt_id: The prompt identifier
        variables: Dictionary of variable values
        
    Returns:
        Rendered prompt string or None if prompt not found
    """
    prompt = PROMPTS.get(prompt_id)
    if not prompt:
        return None
    
    template = prompt["template"]
    
    # Simple variable substitution (for full Jinja2, use jinja2 library)
    for var_name, var_value in variables.items():
        template = template.replace(f"{{{{{var_name}}}}}", var_value)
    
    return template


__all__ = [
    "PROMPTS",
    "get_prompt",
    "list_prompts",
    "render_prompt",
]
