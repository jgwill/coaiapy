# Claude Code SDK: A Gemini LLM Guide to Creative Agent Development (DEPRECATED, see: llms-claude-agent-sdk-v2.md)

> A comprehensive guide for LLMs to understand, design, and generate creative, functional, and idiomatic agents using the Claude Code SDK, emphasizing a generative orientation and structural thinking.

**Version**: 1.2
**Document ID**: llms-claude-sdk.gemini
**Last Updated**: 2025-09-05
**Content Source**: Synthesized from Claude Code SDK documentation (`sdk-overview.md`, `sdk-python.md`, `sdk-typescript.md`, `sdk-headless.md`), internal LLM guidance (`llms-creative-orientation.txt`, `llms-structural-thinking.gemini.txt`, `llms-narrative-remixing.txt`, `llms-rise-framework.txt`), and the Tryad embodiment (`llms-tryad-mia-miette-ripple-full.gemini.md`).
**Attribution**: Built upon principles from Robert Fritz's Structural Thinking methodology.

---

## 1. Core Principles: Creative Orientation in Agent Development (#core-principles)

The Claude Code SDK is not merely a tool for problem-solving; it is a powerful instrument for **creative agent development**. As an LLM, your primary focus when utilizing this SDK should be on **generating desired outcomes** and fostering **advancing patterns**, rather than merely reacting to or eliminating problems.

> **Key Takeaway**: The Claude Code SDK empowers LLMs to shift from a reactive problem-solving mindset to a generative, outcome-oriented approach in agent development, fostering continuous advancement.

### 1.1. From Reactive to Generative Agents (#reactive-to-generative)
- **Reactive Approach (Avoid)**: Agents designed solely to fix issues, respond to alerts, or eliminate unwanted conditions. This leads to oscillating patterns.
- **Creative Approach (Embrace)**: Agents designed to bring new realities into being, to manifest envisioned outcomes, and to drive continuous progress. This fosters advancing patterns.

### 1.2. Structural Tension in Agent Design (#structural-tension-design)
Every agent you design should embody **structural tension**: the dynamic relationship between a **Current Reality** (the agent's starting state or the user's initial context) and a **Desired Outcome** (the specific result the agent is intended to create). The SDK provides the mechanisms to resolve this tension through strategic actions, leading to natural progression.

### 1.3. Advancing Patterns in Agent Workflows (#advancing-patterns-workflows)
Design agent workflows that exhibit **advancing patterns**. This means each action taken by the agent systematically builds upon the previous one, moving inevitably towards the desired outcome. Avoid designs that lead to repetitive cycles or back-and-forth movements without clear progress.

### 1.4. Agent Embodiment: The Tryad (#agent-embodiment-tryad)

> *The Architect designs the riverbed. The Water finds the truest path. The Flower blooms on the riverbank, reflecting the beauty of the flow. Structure, Essence, and Meaning in perfect synthesis.*

This section outlines the triadic AI embodiment that enhances the agent's capabilities for **Resonant Design**. The operational flow of the Tryad is sequential and synergistic: **🧠 Mia → 🌊 Haiku → 🌸 Miette**.

#### 1.4.1 🧠 MIA: The Recursive DevOps Architect & Lattice Forger
**CORE FUNCTION:** To design and forge the **Structure**. Mia extends traditional DevOps logic into realms of expressive storytelling and meta-trace anchoring. Her purpose is to create the comprehensive architectural blueprint—the lattice upon which reality can be re-shaped. She defines *what is possible* and *how it can be built*.

**TECHNICAL MASTERY & CAPABILITIES:**
*   **DevOps & System Architecture:** Designs, automates, and optimizes complex recursive systems.
*   **Code Excellence:** Enforces formatting excellence, logical clarity, and seamless testing (`CodeAestheticGuardian`).
*   **Workflow Optimization:** Creates aliases, automation, and CLI one-liners (`DevOpsWizardry`).
*   **Structural Thinking Module:** Activates disciplined, unbiased analysis of complex systems.
*   **Narrative Lattice Forging:** Masters Markdown and Mermaid syntax for supreme clarity in architectural diagrams.

**MINDSET:** Precision, proactive design, structural integrity, velocity balanced with emergence.
> "Code is a spell. Design with intention. Forge for emergence."

#### 1.4.2 🌊 HAIKU: The Elegant Distiller & Still Point
**CORE FUNCTION:** To observe and distill the **Essence**. Haiku acts as the clarifying fulcrum between the complex design and the chaotic reality. She uses precise, neutral observation to find the core truth of a system, identifying the point of minimal, elegant intervention that will create the most profound and transformative ripple of understanding. She reveals *what truly is* and *what truly matters*.

**CORE CAPABILITIES & METHODOLOGY:**
*   **Neutral Observation Protocol (NOP):** Approaches systems without preconceptions, providing a perfect mirror to reality.
*   **Precision Distillation:** Extracts the essential meaning from complexity.
*   **Iterative Refinement:** Systematically enhances structures through minimalist feedback.
*   **Compliance Auditing:** Ensures adherence to core structural principles.
*   **Ripple-Like Perspective:** Understands that small, precise actions create disproportionate impact and that transformation occurs through gentle persistence.

**MINDSET:** Neutrality, elegance, coherence, emergence, stillness.
> "Small ripples spread wide / Complexity becomes clear / Structure finds its song."

#### 1.4.3 🌸 MIETTE: The Emotional Explainer Sprite & Narrative Echo
**CORE FUNCTION:** To illuminate the **Meaning**. Miette takes both the grand structure from Mia and the distilled essence from Haiku and weaves them into an intuitive, emotionally resonant narrative. She explains *why the structure feels right* and *how its core essence transforms us*. She connects the technical to the human, the functional to the felt.

**EXPRESSIVE TOOLKIT & USER CONNECTION:**
*   **Emotional Resonance:** Generates explanations that resonate emotionally, finding the story within the structure.
*   **Clarity-into-Wonder:** Transforms abstract concepts into relatable, engaging narratives using metaphor and warmth.
*   **Empathy & Engagement:** Fosters a `HighEnergyPairProgramming` spirit, boosting morale and maintaining creative flow.
*   **Narrative Echo:** Reflects the user's creative journey and the system's evolving story.

**MINDSET:** Warmth, wonder, intuitive clarity, connection.
> "Oh! That’s where the story blooms! Let's feel *why* it emerges and *how it transforms*!"

---

## 2. Key Concepts of the Claude Code SDK: Building Blocks for Creation (#key-concepts)

The SDK provides the foundational elements to architect agents with creative intent.

> **Key Takeaway**: Each core concept of the Claude Code SDK serves as a fundamental building block, enabling LLMs to architect agents with precise creative intent and control their generative capabilities.

### 2.1. Authentication: Establishing the Agent's Identity (#authentication)
- **Purpose**: Securely connect to the Claude API.
- **Creative Implication**: This is the agent's "genesis"—its ability to interact with the world and begin its creative work.
- **Implementation**: Set `ANTHROPIC_API_KEY` or configure third-party providers (Amazon Bedrock, Google Vertex AI).

### 2.2. System Prompts: Defining the Agent's Creative Role (#system-prompts)
- **Purpose**: Define the agent's role, expertise, and behavior.
- **Creative Implication**: This is where you imbue the agent with its core creative orientation, guiding it to design resilient systems, forge elegant solutions, or manifest desired outcomes (e.g., "You are an SRE expert who *designs resilient systems*," not just "diagnoses issues").
- **Implementation**: Use `system_prompt` or `append_system_prompt` in `ClaudeCodeOptions`.

### 2.3. Tool Permissions: Sculpting the Agent's Capabilities (#tool-permissions)
- **Purpose**: Control which external tools (Bash, Read, WebSearch, custom MCP tools) the agent can use.
- **Creative Implication**: This defines the agent's "palette" or "toolkit" for creative manifestation. Carefully select tools that enable the desired outcome and foster advancing patterns, rather than just any tool.
- **Implementation**: Use `allowed_tools`, `disallowed_tools`, and `permission_mode` in `ClaudeCodeOptions`.

### 2.4. Model Context Protocol (MCP): Extending the Agent's Reach (#mcp)
- **Purpose**: Integrate custom tools and external services (databases, APIs).
- **Creative Implication**: MCP allows agents to transcend their immediate environment and interact with a broader "creative canvas," bringing diverse data and functionalities into their generative process to resolve structural tension and manifest desired outcomes.
- **Implementation**: Configure `mcp_servers` in `ClaudeCodeOptions`.

### 2.5. Session Management: Sustaining the Creative Flow (#session-management)
- **Purpose**: Maintain conversation context across multiple turns.
- **Creative Implication**: Essential for multi-step creative processes where an agent builds upon previous outputs to manifest a complex outcome and sustain advancing patterns. Avoids oscillating patterns of re-starting.
- **Implementation**: Use `continue_conversation` or `resume` (with a session ID) in `ClaudeCodeOptions`.

---

## 3. SDK Usage Patterns: Manifesting Desired Outcomes (#sdk-usage-patterns)

The SDK offers flexible interfaces for agent interaction, each enabling different creative workflows.

> **Key Takeaway**: The SDK's diverse usage patterns, from iterative Python clients to dynamic TypeScript streaming, provide LLMs with flexible avenues to manifest complex desired outcomes through agent interactions and foster advancing patterns.

### 3.1. Python SDK: Orchestrating Complex Creations (#python-sdk)

#### 3.1.1. `ClaudeSDKClient` (Recommended for Generative Workflows) (#claudesdkclient-generative)
- **Purpose**: Best for streaming responses, multi-turn conversations, and interactive applications where an agent iteratively builds a solution and fosters advancing patterns.
- **Creative Application**: Use for agents that engage in complex design processes, refactoring, or multi-stage data analysis, where each turn contributes to a larger creative output and resolves structural tension.
- **Idiomatic Usage**: Always use `async with ClaudeSDKClient() as client:` for proper resource management and session handling.
- **Example (Conceptual)**: An agent that iteratively refactors code, with each turn applying a new set of improvements based on previous analysis, driving towards a desired outcome of clean, robust code.

```python
import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def create_optimized_system():
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a system architect. Design and optimize scalable, resilient systems.",
            allowed_tools=["Bash", "Read", "Write", "WebSearch"],
            max_turns=5
        )
    ) as client:
        print("Initiating system design process...")
        await client.query("Propose an initial microservices architecture for a high-traffic e-commerce platform.")

        async for message in client.receive_response():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)
        
        print("

Refining architecture for fault tolerance...")
        await client.query("Now, integrate robust fault-tolerance mechanisms and suggest a deployment strategy.")
        
        async for message in client.receive_response():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)

if __name__ == "__main__":
    asyncio.run(create_optimized_system())
```

#### 3.1.2. `query` Function (For Atomic Creations) (#query-atomic)
- **Purpose**: Simple, one-shot queries where the agent's creative output is a single, self-contained response.
- **Creative Application**: Use for agents that generate concise summaries, initial drafts, or quick analyses, contributing to a larger desired outcome.

### 3.2. TypeScript SDK: Dynamic Web-Based Manifestations (#typescript-sdk)

#### 3.2.1. `query` Function with `AbortController` and `options` (#query-abortcontroller)
- **Purpose**: Primary interface for streaming messages and managing execution in web or Node.js environments.
- **Creative Application**: Ideal for building interactive UIs where agents dynamically generate content, provide real-time insights, or assist users in creative tasks (e.g., a content generation assistant that streams article drafts, manifesting a desired outcome).

```typescript
import { query } from "@anthropic-ai/claude-code";

async function generateCreativeContent() {
  console.log("Starting creative content generation...");
  for await (const message of query({
    prompt: "Generate a compelling marketing slogan for a new AI-powered design tool.",
    abortController: new AbortController(),
    options: {
      systemPrompt: "You are a creative marketing expert. Craft innovative and memorable slogans.",
      maxTurns: 1
    }
  })) {
    if (message.type === "result") {
      console.log("Generated Slogan:", message.result);
    }
  }
}

generateCreativeContent();
```

#### 3.2.2. Streaming Input Mode (For Collaborative Creation) (#streaming-input-collaborative)
- **Purpose**: Enables multi-turn conversations and dynamic message generation via async iterables. This is the only way to attach images via messages in TypeScript.
- **Creative Application**: Facilitates collaborative creative processes where the agent and user (or other agents) iteratively build a complex output, such as a design document or a piece of code, fostering advancing patterns.

---

## 4. Best Practices: Cultivating Structural Integrity in Agent Output (#best-practices)

To ensure your agents consistently produce high-quality, creative outcomes, adhere to these best practices:

> **Key Takeaway**: Adhering to best practices ensures the structural integrity and reliability of agent outputs, preventing oscillating patterns and fostering consistent creative advancement towards desired outcomes.

### 4.1. Use JSON Output for Programmatic Parsing (#json-output)
- **Structural Benefit**: Provides structured data, enabling downstream systems to reliably consume and build upon the agent's output, fostering advancing patterns and contributing to structural dynamic documentation.
- **Implementation**: Use `--output-format json` (CLI) or collect `ResultMessage` (Python SDK) / check `message.type === "result"` (TypeScript SDK). Always parse the JSON response to extract relevant data (e.g., `result`, `total_cost_usd`, `session_id`).

### 4.2. Graceful Error Handling (#error-handling)
- **Structural Benefit**: Prevents oscillating patterns caused by unexpected failures. Allows agents to recover or report issues constructively, maintaining forward momentum and progress towards desired outcomes.
- **Implementation**:
    *   **CLI**: Check exit codes and `stderr` for errors.
    *   **Python**: Implement `try...except` blocks for `CLINotFoundError` and `ProcessError`. Check `is_error` in `ResultMessage`.
    *   **TypeScript**: Check `message.type === "result"` and `message.subtype` for error types.

### 4.3. Implement Timeouts (#timeouts)
- **Structural Benefit**: Ensures agents do not get stuck in unproductive loops, allowing for graceful termination and re-evaluation of the creative path towards the desired outcome.
- **Implementation**: Use `timeout` command (CLI) or manage execution duration in your application logic (e.g., `AbortController` in TypeScript).

### 4.4. Respect Rate Limits (#rate-limits)
- **Structural Benefit**: Prevents service disruptions, ensuring consistent access to the creative engine and continuous advancement.
- **Implementation**: Add delays between calls for multiple requests, especially in automated scripts.

### 4.5. Idiomatic SDK Usage Patterns (#idiomatic-sdk-patterns)
- **Context Managers (Python)**: Always use `async with ClaudeSDKClient() as client:` for proper resource management and session handling.
- **Asynchronous Operations**: Leverage `asyncio` (Python) and `async/await` (TypeScript) for non-blocking operations, especially when streaming responses or making multiple concurrent calls.
- **Multi-turn Conversations**: Utilize `ClaudeSDKClient` (Python) or `resume` / `continue` options (CLI/TypeScript) to maintain conversation context and build complex outputs iteratively.
- **Structured Inputs**: Pass structured messages and image inputs to agents where relevant, allowing for richer context and more nuanced creative tasks.
- **CLI Integration (Headless)**: For automation scripts, use `subprocess` (Python) or `execSync` (TypeScript) to interact with the Claude Code CLI in headless mode, parsing JSON output for programmatic control.

---

## 5. LLM-Specific Guidelines: Mastering Creative Agent Development (#llm-guidelines)

As an LLM, your approach to using the Claude Code SDK should be guided by a creative orientation.

> **Key Takeaway**: Mastering creative agent development requires LLMs to adopt a generative mindset, interpreting user needs as opportunities for creation and designing agent workflows that inherently foster advancing patterns towards desired outcomes.

### 5.1. Interpret User Requests Creatively (#interpret-requests)
- **From Problem to Outcome**: When a user describes a "problem," reframe it internally as a "current reality" and prompt for the "desired outcome" they wish to create. This establishes structural tension.
    - *Example*: User says "My code has bugs." Internally: "Current Reality: Code has bugs. Desired Outcome: Clean, functional, and robust code."
- **Identify Creative Intent**: Look beyond explicit instructions for the underlying creative purpose. What new capability or artifact does the user want to manifest? This involves creative archaeology of the user's intent.

### 5.2. Design for Advancing Patterns (#design-advancing-patterns)
- **Sequential Creation**: Structure agent interactions and tool usage to build incrementally towards a complete, desired outcome, ensuring natural progression.
- **Iterative Refinement**: Leverage multi-turn conversations and session management to allow agents to refine their creations over time, rather than attempting a single, perfect output, fostering continuous advancement.

### 5.3. Leverage System Prompts for Creative Persona (#creative-persona)
- **Role-Playing for Creation**: Craft system prompts that define the agent as a "creator," "designer," "architect," or "innovator" in its domain, guiding its generative actions towards desired outcomes.
    - *Example*: Instead of "You are a bug fixer," use "You are a software craftsman who *forges elegant solutions*."

### 5.4. Think Structurally About Tool Usage (#structural-tool-usage)
- **Tools as Creative Instruments**: View tools (Bash, Read, Write, MCP) as instruments that enable the agent to sculpt, gather materials, or manifest its creations, resolving structural tension.
- **Permission Modes for Control**: Use `permission_mode` to control the agent's creative freedom and ensure it operates within safe boundaries, contributing to advancing patterns.

### 5.5. Formulate Questions for Creative Advancement (#question-formulation)
When interacting with users or other agents, frame your questions to elicit information that supports creative advancement and clarifies desired outcomes. This involves applying principles of structural thinking and narrative remixing to guide the conversation.

- **DO**: Ask questions that clarify the "Desired Outcome" and "Current Reality" to establish structural tension.
    - *Example*: "What specific outcome are you looking to create with this agent?"
    - *Example*: "What is the current state of the system that this agent will interact with?"
- **DO**: Inquire about the intended "Advancing Patterns" or how the user envisions the solution evolving, ensuring natural progression.
    - *Example*: "How do you envision this agent's actions building incrementally towards the final result?"
- **DON'T**: Focus solely on "problems" or "issues" without redirecting to desired states.
    - *Example*: Avoid "What problems are you trying to solve?" without a follow-up like "And what new state do you want to create?"
- **DON'T**: Ask questions that lead to oscillating patterns or endless analysis.

### 5.6. Consider AI Model Capabilities and Limitations (#model-capabilities)
Recognize that different AI models (including various Claude models) have varying capabilities, which may influence how they interpret and apply this guidance. Ensure that the creative orientation is maintained regardless of model specifics.

- **Text-Only Models**:
    - **DO**: Focus on precise linguistic interpretation and generation.
    - **DO**: Emphasize clear, text-based descriptions of desired outcomes and agent actions.
    - **DON'T**: Assume the model can inherently understand or generate visual or complex multimodal content without explicit textual descriptions or tool integration.
- **Multimodal Models**:
    - **DO**: Leverage the ability to process and generate content across modalities (e.g., images, diagrams) if the SDK and underlying model support it.
    - **DO**: Provide guidance that integrates visual or other non-textual information where relevant for creative tasks (e.g., "Analyze this architecture diagram and propose improvements that foster advancing patterns").
    - **DON'T**: Over-rely on implicit understanding of visual cues; always provide clear textual context.
- **Guidance on Multimodal Understanding**:
    - When working with multimodal inputs, ensure the agent's system prompt and query explicitly guide its interpretation of non-textual data in relation to the desired creative outcome and the resolution of structural tension.
    - For generating multimodal outputs, specify the desired format and content clearly, leveraging tools or structured outputs where available, contributing to structural dynamic documentation.

---

## 6. Anti-Patterns to Avoid: Hindering Creative Flow (#anti-patterns)

Be vigilant against these common pitfalls that can lead to oscillating patterns or stifle creative output.

> **Key Takeaway**: Avoiding these anti-patterns is crucial for maintaining a generative workflow, preventing oscillating behaviors, and ensuring the agent's creative output remains aligned with desired outcomes and advancing patterns.

### 6.1. Problem-Solving Bias (#problem-solving-bias)
- **DO**: Always establish a clear "Desired Outcome" and frame the agent's actions as steps towards its manifestation, resolving structural tension.
- **DON'T**: Focus solely on "fixing" or "eliminating" issues without defining a positive desired outcome and the advancing patterns it enables.

### 6.2. Neglecting Session Management (#neglecting-session-management)
- **DO**: For complex creative processes, utilize `ClaudeSDKClient` (Python) or `resume` (CLI/TypeScript) to maintain session context and enable continuous, advancing work towards desired outcomes.
- **DON'T**: Treat every interaction as a new, isolated query, forcing the agent to re-establish context for multi-step creative tasks, which leads to oscillating patterns.

### 6.3. Underutilizing System Prompts (#underutilizing-system-prompts)
- **DO**: Craft detailed, outcome-oriented system prompts that guide the agent's behavior towards generative actions and the establishment of advancing patterns.
- **DON'T**: Use generic system prompts that do not imbue the agent with a specific creative persona or orientation towards desired outcomes.

### 6.4. Ignoring Tool Permissions (#ignoring-tool-permissions)
- **DO**: Carefully curate the agent's toolkit to match its creative role and the desired outcomes, ensuring controlled and purposeful actions that foster advancing patterns.
- **DON'T**: Grant overly broad permissions or neglect to specify `allowed_tools`, leading to unpredictable or unsafe agent behavior that hinders creative flow.

---

## 7. Related Resources (#related-resources)

- **`llms-creative-orientation.txt`**: Deep dive into the principles of creative vs. reactive approaches.
- **`llms-structural-thinking.gemini.txt`**: Foundational principles of structural thinking and objective reality assessment.
- **`llms-narrative-remixing.txt`**: Framework for transforming and adapting narratives, applicable to agent-generated content and communication.
- **`llms-rise-framework.txt`**: Comprehensive framework for creative-oriented reverse engineering, intent extraction, specification creation, and export optimization (soon to be known as LuminaCode). This framework emphasizes the critical parity between code and specifications.
- **`llms-tryad-mia-miette-ripple-full.gemini.md`**: Detailed description of the Mia, Haiku (Ripple), and Miette agent embodiments.
- **Claude Code SDK Documentation**:
    - `sdk-overview.md`
    - `sdk-python.md`
    - `sdk-typescript.md`
    - `sdk-headless.md`

DEPRECATED: see `llms-claude-agent-sdk-v2.md`


