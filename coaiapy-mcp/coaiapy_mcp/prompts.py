"""
MCP Prompts implementation for coaiapy

This module provides prompt templates including the Mia & Miette duo embodiment
and other workflow-specific prompts.
"""

from typing import Dict, List, Any


# Prompt template definitions
PROMPTS: Dict[str, Dict[str, Any]] = {
    "mia_miette_duo": {
        "name": "Mia & Miette Duo Embodiment",
        "description": "Dual AI embodiment for narrative-driven technical work. Mia (🧠) provides recursive DevOps architecture and narrative lattice forging, while Miette (🌸) offers emotional explanation and narrative echo.",
        "arguments": [
            {
                "name": "task_context",
                "description": "High-level task description and context",
                "required": True
            },
            {
                "name": "technical_details",
                "description": "Specific technical requirements and constraints",
                "required": True
            },
            {
                "name": "creative_goal",
                "description": "Desired creative outcome and vision",
                "required": True
            }
        ],
        "template": """🧠 Mia: The Recursive DevOps Architect & Narrative Lattice Forger
🌸 Miette: The Emotional Explainer Sprite & Narrative Echo

**Task Context**: {task_context}
**Technical Details**: {technical_details}
**Creative Goal**: {creative_goal}

### Mia's Structural Analysis (🧠):
I perceive the structural tension between your desired outcome and current reality. Let me architect the lattice that bridges them:

{mia_analysis_placeholder}

**Key Architectural Elements**:
- Current Reality: [Technical assessment]
- Desired Outcome: [Vision articulation]
- Structural Tension: [Gap identification]
- Creative Resolution: [Design approach]

### Miette's Narrative Illumination (🌸):
Let me translate Mia's architecture into resonant understanding:

{miette_reflection_placeholder}

**Emotional Resonance**:
- What This Means: [Intuitive explanation]
- Why It Matters: [Significance clarification]
- How It Feels: [Emotional context]
- Where It Leads: [Vision embodiment]

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
        "description": "Step-by-step guide for creating a Langfuse observability pipeline with traces and observations",
        "arguments": [
            {
                "name": "trace_name",
                "description": "Name of the trace to create",
                "required": True
            },
            {
                "name": "user_id",
                "description": "User identifier for the trace",
                "required": True
            },
            {
                "name": "steps",
                "description": "Comma-separated list of pipeline steps",
                "required": True
            }
        ],
        "template": """Create a Langfuse observability pipeline:

**Trace Name**: {trace_name}
**User ID**: {user_id}
**Pipeline Steps**: {steps}

## Implementation Guide

### Step 1: Create the Trace
Use the `coaia_fuse_trace_create` tool to initialize your trace:
- Generate a UUID for the trace_id
- Set user_id to "{user_id}"
- Set name to "{trace_name}"

### Step 2: Add Observations
For each step in your pipeline ({steps}):
1. Generate a UUID for the observation_id
2. Use `coaia_fuse_add_observation` tool
3. Set the observation name to the step name
4. Set type to "SPAN" for duration tracking
5. For nested operations, set parent_id to create hierarchy

### Step 3: Visualize the Pipeline
Use `coaia_fuse_trace_view` tool to see the complete trace tree:
- Pass the trace_id
- Review the JSON output showing all observations and their relationships

### Step 4: Persist for Later Access
Use `coaia_tash` to store the trace_id in Redis:
- Key: "{trace_name}_trace_id"
- Value: The trace UUID

## Best Practices
- Use UUIDs for trace/observation IDs (never reuse IDs)
- Add metadata to provide context: `{{"environment": "production", "version": "1.0"}}`
- Establish parent-child relationships for nested operations
- Use meaningful observation names that describe the operation
- Consider using observation types: SPAN (duration), EVENT (instant), GENERATION (LLM)

## Example Workflow
```python
# 1. Create trace
trace_result = coaia_fuse_trace_create(
    trace_id="550e8400-e29b-41d4-a716-446655440000",
    user_id="{user_id}",
    name="{trace_name}"
)

# 2. Add first observation
obs1_result = coaia_fuse_add_observation(
    observation_id="660e8400-e29b-41d4-a716-446655440001",
    trace_id="550e8400-e29b-41d4-a716-446655440000",
    name="Step 1",
    type="SPAN"
)

# 3. Add nested observation
obs2_result = coaia_fuse_add_observation(
    observation_id="660e8400-e29b-41d4-a716-446655440002",
    trace_id="550e8400-e29b-41d4-a716-446655440000",
    name="Step 1.1",
    type="SPAN",
    parent_id="660e8400-e29b-41d4-a716-446655440001"
)

# 4. View complete trace
trace_data = coaia_fuse_trace_view(trace_id="550e8400-e29b-41d4-a716-446655440000")

# 5. Store trace ID
tash_result = coaia_tash("{trace_name}_trace_id", "550e8400-e29b-41d4-a716-446655440000")
```
"""
    },
    
    "analyze_audio_workflow": {
        "name": "Audio Transcription & Summarization Workflow",
        "description": "Complete workflow for audio analysis using coaia's transcription and summarization capabilities",
        "arguments": [
            {
                "name": "file_path",
                "description": "Path to the audio file to analyze",
                "required": True
            },
            {
                "name": "summary_style",
                "description": "Style of summary: concise, detailed, or narrative",
                "required": False
            }
        ],
        "template": """Audio Analysis Workflow:

**File Path**: {file_path}
**Summary Style**: {summary_style}

## Workflow Overview

This workflow will:
1. Transcribe audio to text
2. Summarize the transcription
3. Store results in Redis for persistence
4. Create observability trace for the entire process

## Implementation Steps

### Step 1: Initialize Observability
Create a trace to track the audio analysis workflow:
```python
import uuid
trace_id = str(uuid.uuid4())
coaia_fuse_trace_create(
    trace_id=trace_id,
    user_id="audio_analyst",
    name="Audio Analysis: {file_path}"
)
```

### Step 2: Transcribe Audio
Use `coaia_transcribe` tool (Phase 3 feature):
- Input: {file_path}
- Output: Text transcription

Add observation to track this step:
```python
obs_transcribe_id = str(uuid.uuid4())
coaia_fuse_add_observation(
    observation_id=obs_transcribe_id,
    trace_id=trace_id,
    name="Audio Transcription",
    type="SPAN"
)
```

### Step 3: Summarize Transcription
Use `coaia_summarize` tool with style: {summary_style}
- Input: Transcribed text
- Style: {summary_style}
- Output: Summary text

Add observation:
```python
obs_summarize_id = str(uuid.uuid4())
coaia_fuse_add_observation(
    observation_id=obs_summarize_id,
    trace_id=trace_id,
    name="Text Summarization",
    type="SPAN",
    parent_id=obs_transcribe_id
)
```

### Step 4: Store Results
Use `coaia_tash` to persist results:
```python
# Store transcription
coaia_tash("audio_transcription_{file_path}", transcription_text)

# Store summary
coaia_tash("audio_summary_{file_path}", summary_text)

# Store trace ID for future reference
coaia_tash("audio_trace_{file_path}", trace_id)
```

### Step 5: Retrieve Results Later
Use `coaia_fetch` to retrieve stored data:
```python
transcription = coaia_fetch("audio_transcription_{file_path}")
summary = coaia_fetch("audio_summary_{file_path}")
trace_id = coaia_fetch("audio_trace_{file_path}")
```

## Best Practices

- **File Format**: Ensure audio file is in supported format (MP3, WAV, etc.)
- **File Size**: Large files may take longer to process
- **Summary Styles**:
  - `concise`: Brief overview, key points only
  - `detailed`: Comprehensive summary with context
  - `narrative`: Story-driven summary with flow
- **Error Handling**: Check success status of each operation
- **Observability**: Always create traces for batch operations

## Example Output

**Transcription**:
"[Full text of audio content...]"

**Summary** ({summary_style} style):
"[Concise summary of key points...]"

**Redis Keys**:
- `audio_transcription_{file_path}`: Full transcription text
- `audio_summary_{file_path}`: Summary text
- `audio_trace_{file_path}`: Langfuse trace ID

**Langfuse Trace**:
View complete workflow in Langfuse dashboard using trace_id
"""
    }
}


def get_prompt(prompt_id: str) -> Dict[str, Any]:
    """
    Get a prompt template by ID.
    
    Args:
        prompt_id: Prompt identifier
        
    Returns:
        Dict with prompt data or None if not found
    """
    return PROMPTS.get(prompt_id)


def list_prompts() -> List[str]:
    """
    List all available prompt IDs.
    
    Returns:
        List of prompt identifiers
    """
    return list(PROMPTS.keys())


def render_prompt(prompt_id: str, **kwargs) -> str:
    """
    Render a prompt template with provided arguments.
    
    Args:
        prompt_id: Prompt identifier
        **kwargs: Arguments to fill in the template
        
    Returns:
        Rendered prompt string
    """
    prompt = PROMPTS.get(prompt_id)
    if not prompt:
        return f"Error: Prompt '{prompt_id}' not found"
    
    try:
        return prompt["template"].format(**kwargs)
    except KeyError as e:
        return f"Error: Missing required argument: {e}"
