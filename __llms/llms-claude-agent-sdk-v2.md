# Claude Agent SDK v2: Complete Guide for Building AI Agents

> **Replacement for**: `llms-claude-sdk.gemini.md`  
> **Version**: 2.0 (Aligned with claude-agent-sdk package)  
> **Status**: Production Ready  
> **Last Updated**: 2025-10-31

## 🎯 Overview

The **Claude Agent SDK** (formerly Claude Code SDK) is a production-grade framework for building autonomous AI agents with advanced capabilities including:

- **Tool Integration**: File operations, code execution, web search, MCP extensibility
- **Multi-turn Conversations**: Context-aware, session-managed interactions
- **Streaming & Observability**: Real-time response streaming with comprehensive metrics
- **Creative Orientation**: Built on structural thinking and advancing patterns
- **Enterprise Features**: Error handling, context compression, prompt caching

## 📦 Installation & Package Names

### Python
```bash
# OLD (Deprecated)
pip install claude-code-sdk

# NEW (Current)
pip install claude-agent-sdk
```

### TypeScript/JavaScript
```bash
# OLD (Deprecated)
npm install @anthropic-ai/claude-code

# NEW (Current)
npm install @anthropic-ai/claude-agent-sdk
```

## 🔄 Breaking Changes Summary

### Package & Type Renaming
| Component | Old | New | Impact |
|-----------|-----|-----|--------|
| Python package | `claude-code-sdk` | `claude-agent-sdk` | **BREAKING** |
| Python import | `from claude_code_sdk` | `from claude_agent_sdk` | **BREAKING** |
| TypeScript package | `@anthropic-ai/claude-code` | `@anthropic-ai/claude-agent-sdk` | **BREAKING** |
| TypeScript import | `from @anthropic-ai/claude-code` | `from @anthropic-ai/claude-agent-sdk` | **BREAKING** |
| Python options class | `ClaudeCodeOptions` | `ClaudeAgentOptions` | **BREAKING** |
| Python client class | `ClaudeSDKClient` | `ClaudeSDKClient` | No change |

### Behavioral Changes

#### 1. System Prompt (BREAKING)
**Old Behavior**: Defaulted to Claude Code's system prompt automatically  
**New Behavior**: Must explicitly specify system prompt or use preset

```python
# OLD - Used Claude Code preset by default
async with ClaudeSDKClient() as client:
    await client.query("Do something")

# NEW - Must be explicit
async with ClaudeSDKClient(options=ClaudeAgentOptions(
    system_prompt="You are a helpful assistant"
)) as client:
    await client.query("Do something")

# Or use preset
async with ClaudeSDKClient(options=ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"}
)) as client:
    await client.query("Do something")
```

**Why**: Better isolation and explicit control for deployed applications, CI/CD pipelines, and multi-tenant systems.

#### 2. Settings Sources (BREAKING)
**Old Behavior**: Auto-loaded from filesystem (CLAUDE.md, settings.json, custom commands)  
**New Behavior**: Requires explicit opt-in to load filesystem settings

```python
# OLD - Auto-loaded all settings
async with ClaudeSDKClient() as client:
    await client.query("Analyze this")
    # Would read: ~/.claude/settings.json, CLAUDE.md, custom commands, etc.

# NEW - Must specify which sources to load
async with ClaudeSDKClient(options=ClaudeAgentOptions(
    setting_sources=["user", "project", "local"]
)) as client:
    await client.query("Analyze this")

# Or load only specific sources
async with ClaudeSDKClient(options=ClaudeAgentOptions(
    setting_sources=["project"]  # Only project-level settings
)) as client:
    await client.query("Analyze this")
```

**Why**: 
- **CI/CD**: Consistent behavior independent of local filesystem
- **Deployed Apps**: No dependency on local settings files
- **Testing**: Isolated test environments
- **Multi-tenant**: Prevent settings leakage between users

---

## 🏗️ Core Concepts

### System Prompts
Define your agent's role, expertise, and behavior. Always explicit in v2:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

system_prompt = """You are a creative storytelling assistant specializing in narrative structure.
Your expertise:
• Plot development and story arcs
• Character motivation and backstory
• Dialogue authenticity
• Thematic resonance

Always focus on what the user wants to CREATE, not problems to eliminate."""

async with ClaudeSDKClient(options=ClaudeAgentOptions(
    system_prompt=system_prompt,
    max_turns=5
)) as client:
    await client.query("Help me develop a character arc...")
```

### Tool Permissions
Fine-grained control over agent capabilities:

```python
options = ClaudeAgentOptions(
    # Explicit tool allowlist
    allowed_tools=["Read", "Write", "Grep"],
    
    # Or use allowlist + blocklist
    disallowed_tools=["ExecuteRemoteCode"],
    
    # Permission strategy: "acceptEdits" or "plan"
    permission_mode="acceptEdits"
)
```

### Multi-turn Conversations
Maintain context across multiple agent turns:

```python
async with ClaudeSDKClient(options=ClaudeAgentOptions(
    system_prompt="You remember previous interactions",
    max_turns=10
)) as client:
    # First turn
    await client.query("I want to write a fantasy novel")
    async for message in client.receive_response():
        print(message)
    
    # Second turn - context is maintained
    await client.query("Make the protagonist a reluctant hero")
    async for message in client.receive_response():
        print(message)
```

### Streaming Input (Recommended)
Persistent session with dynamic message queuing:

```python
async def message_generator():
    # First message
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": "Start a story"
        }
    }
    
    # Wait for conditions
    await asyncio.sleep(2)
    
    # Follow-up with image (streaming input only)
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {"type": "text", "text": "Review this visual"},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data
                }}
            ]
        }
    }

async for message in query({
    "prompt": message_generator(),
    "options": ClaudeAgentOptions(max_turns=10)
}):
    if message.type == "result":
        print(message.result)
```

---

## 🎨 Creative Orientation Framework

The Claude Agent SDK is designed with creative-first principles:

### Core Principles
1. **Focus on Creation**: What does the user want to CREATE?
2. **Structural Tension**: Establish clear gap between current reality and desired outcome
3. **Advancing Patterns**: Each action naturally progresses toward the goal
4. **No Problem Elimination**: Reframe "fixing problems" as "creating desired states"

### Example: Storytelling Use Case
```python
# NOT: "Help me fix my plot holes"
# YES: "Help me create a cohesive plot structure"

prompt = """I want to create a compelling narrative where:
- A reluctant hero discovers hidden power
- They must choose between personal desire and community need
- The resolution honors both the external quest and internal transformation

What structural elements will strengthen this vision?"""

async with ClaudeSDKClient(options=ClaudeAgentOptions(
    system_prompt=storytelling_system_prompt,
    setting_sources=["project"]  # Load project context
)) as client:
    await client.query(prompt)
```

---

## 🔌 Model Context Protocol (MCP) Integration

Extend agents with custom tools and external integrations:

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "my_database": {
            "type": "stdio",
            "command": "python",
            "args": ["/path/to/database_mcp.py"]
        }
    },
    allowed_tools=["custom_db_query", "custom_db_write"]
)
```

---

## 🎭 Agent Types for Storytelling

### Story Architect Agent
```python
storytelling_agent = ClaudeAgentOptions(
    system_prompt="""You are a Story Architect specializing in narrative structure.
    
Capabilities:
- Plot outlines with rising/falling action
- Character motivation mapping
- Three-act structure guidance
- Theme integration across scenes
    
Always ask: 'What story are you creating?'""",
    allowed_tools=["Read", "Write"],
    max_turns=10
)
```

### Character Development Agent
```python
character_agent = ClaudeAgentOptions(
    system_prompt="""You are a Character Specialist focused on creating authentic, compelling characters.
    
Approach:
- Explore core motivations
- Define character arc across story
- Create authentic dialogue voice
- Build relatable backstory
    
Guide users to create characters they love.""",
    allowed_tools=["Write"],
    max_turns=8
)
```

### Scene Visualization Agent
```python
scene_agent = ClaudeAgentOptions(
    system_prompt="""You are a Scene Visualizer creating vivid, sensory-rich narrative descriptions.
    
Focus:
- Sensory details (sight, sound, smell, touch, taste)
- Emotional resonance of settings
- Dynamic action sequences
- Atmospheric tension
    
Create scenes readers will visualize.""",
    allowed_tools=["Write"],
    max_turns=6
)
```

---

## 🔄 Multi-Agent Orchestration Pattern

For complex narrative work, orchestrate multiple specialized agents:

```python
class StoryOrchestrator:
    def __init__(self):
        self.architect = StoryArchitectAgent()
        self.character_dev = CharacterDevelopmentAgent()
        self.scene_viz = SceneVisualizationAgent()
    
    async def create_story(self, user_vision: str):
        # Step 1: Structural foundation
        structure = await self.architect.create_outline(user_vision)
        
        # Step 2: Character development
        characters = await self.character_dev.develop_characters(
            structure,
            user_vision
        )
        
        # Step 3: Scene creation
        scenes = await self.scene_viz.create_scenes(
            structure,
            characters
        )
        
        return {
            "structure": structure,
            "characters": characters,
            "scenes": scenes
        }
```

---

## 🧠 Structural Thinking Integration

Apply structural tension methodology to agent interactions:

### Desired Outcome → Current Reality → Action
```python
class StructuralAgent:
    async def create_with_structure(self, user_request: str):
        # Establish structural foundation
        prompt = f"""
        User's Creative Vision: {user_request}
        
        Before we proceed, let's establish structural tension:
        1. DESIRED OUTCOME: What specific result do they want to CREATE?
        2. CURRENT REALITY: What exists now?
        3. STRUCTURAL TENSION: What's the gap between them?
        4. ADVANCING ACTIONS: What steps naturally progress toward outcome?
        
        Guide them through this structure."""
        
        async with ClaudeSDKClient(options=ClaudeAgentOptions(
            system_prompt=prompt
        )) as client:
            await client.query(user_request)
```

---

## 🎮 Plugin Architecture (For Miadi#87)

### Integrating Specialized Agent Plugins

The mia-agents framework can be exposed as Claude Code plugins:

```python
# Plugin manifest structure
{
    "name": "storytelling-agents",
    "version": "1.0.0",
    "agents": [
        {
            "id": "story-architect",
            "name": "Story Architect",
            "description": "Create and refine story structure",
            "system_prompt": "...",
            "tools": ["Read", "Write", "Grep"]
        },
        {
            "id": "character-dev",
            "name": "Character Developer",
            "description": "Develop compelling characters",
            "system_prompt": "...",
            "tools": ["Write"]
        }
    ]
}
```

### Using Plugins in Agent Options
```python
options = ClaudeAgentOptions(
    plugins=["jgwill/storytelling-agents"],
    agents={
        "story-architect": {
            "description": "Create story structure",
            "tools": ["Read", "Write"]
        }
    }
)
```

---

## 🔒 Security & Best Practices

### 1. Never Use Default Settings in Production
```python
# DON'T - Inherits local filesystem settings
options = ClaudeAgentOptions(system_prompt="...")

# DO - Explicit, isolated configuration
options = ClaudeAgentOptions(
    system_prompt="...",
    setting_sources=[]  # No filesystem settings
)
```

### 2. Restrict Tools Appropriately
```python
# Different permission levels for different agents
read_only_agent = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep"],
    permission_mode="plan"  # Only propose, don't execute
)

creation_agent = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Execute"],
    permission_mode="acceptEdits"  # Execute immediately
)
```

### 3. Handle Errors Gracefully
```python
async def safe_agent_execution():
    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                # Process message
                pass
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        # Implement fallback strategy
```

---

## 📊 Common Patterns

### Pattern 1: Question-Answer with Context
```python
async def qa_agent(question: str, context: str):
    async with ClaudeSDKClient(options=ClaudeAgentOptions(
        system_prompt="Answer questions based on provided context",
        max_turns=1
    )) as client:
        prompt = f"Context: {context}\n\nQuestion: {question}"
        await client.query(prompt)
```

### Pattern 2: Iterative Refinement
```python
async def iterative_refinement(initial_idea: str):
    async with ClaudeSDKClient(options=ClaudeAgentOptions(
        system_prompt="Help refine and improve ideas",
        max_turns=5
    )) as client:
        version = initial_idea
        for i in range(3):
            await client.query(f"Refine this: {version}")
            # Collect response and update version
```

### Pattern 3: Multi-Perspective Analysis
```python
async def multi_perspective_analysis(topic: str):
    perspectives = ["technical", "creative", "business", "user"]
    results = {}
    
    for perspective in perspectives:
        options = ClaudeAgentOptions(
            system_prompt=f"Analyze from {perspective} perspective",
            max_turns=2
        )
        async with ClaudeSDKClient(options=options) as client:
            await client.query(topic)
            results[perspective] = collect_response()
    
    return results
```

---

## 🚀 Migration Checklist

When upgrading from claude-code-sdk:

- [ ] Update all imports: `claude_code_sdk` → `claude_agent_sdk`
- [ ] Rename all classes: `ClaudeCodeOptions` → `ClaudeAgentOptions`
- [ ] Add explicit `system_prompt` to all agent instantiations
- [ ] Add explicit `setting_sources` if filesystem settings needed
- [ ] Update all requirements.txt files
- [ ] Test streaming and multi-turn conversations
- [ ] Verify tool permissions still appropriate
- [ ] Test observability/logging integration
- [ ] Update documentation and examples

---

## 📚 References

- [Claude Agent SDK Overview](/en/api/agent-sdk/overview)
- [Python SDK Reference](/en/api/agent-sdk/python)
- [TypeScript SDK Reference](/en/api/agent-sdk/typescript)
- [Streaming vs Single Mode](/en/api/agent-sdk/streaming-vs-single-mode)
- [MCP Integration](/en/docs/claude-code/mcp)
- [Custom Tools](/en/api/agent-sdk/custom-tools)
- [Subagents](/en/docs/claude-code/sdk/subagents)

---

## 🎯 Next: Plugin Architecture for Storytelling

See `PLUGIN_ARCHITECTURE.md` for designing specialized agent plugins that integrate with the storytelling platform (jgwill/Miadi#87).
