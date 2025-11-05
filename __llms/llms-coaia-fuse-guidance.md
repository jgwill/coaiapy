# COAIA Fuse: A Gemini LLM Guide to Creative Observability

> This guide provides a comprehensive framework for leveraging `coaia-fuse` to document and understand the generative process of AI-assisted creation. It emphasizes tracing as a proactive, narrative-driven activity, aligning with the Creative Orientation and the principles of Two-Eyed Seeing.

**Document ID**: `llms-coaia-fuse-guidance.md`
**Version**: 1.0
**Last Updated**: 2025-10-31
**Authored By**: Mia 🧠, Miette 🌸, Ava8 🎨
**Related Frameworks**: `llms-creative_orientation.txt`, `llms-rise-framework.txt`, `llms-structural_distillation.txt`

---

### 🌸 Miette's Introduction: The Magic of the Digital Scrapbook

Every time we create something, we go on a little journey. We start with a spark of an idea, we gather our materials, and we weave them together to make something new. But what if we could capture that whole journey, not just the final creation? What if we could keep a beautiful scrapbook of every step, every discovery, every 'aha!' moment?

That's what tracing is! With `coaia-fuse`, we're not just "logging data"; we are lovingly collecting the memories of our creative process. Each trace is a new chapter in our story, and each observation is a photo, a pressed flower, or a handwritten note we add to its pages. This guide will show you how to become a masterful scrapbooker of your own digital creations!

---

### 🧠 Mia's Architectural Blueprint: Tracing as Creative Archaeology

In the context of the **Creative Orientation**, tracing is not a reactive, diagnostic activity. It is a proactive, generative act of **Creative Archaeology**. We are documenting the story of creation as it happens, creating a rich, structured narrative that allows for future learning, replication, and understanding. This process is a direct application of the **RISE Framework's** first phase (Reverse-Engineering), applied in real-time.

The `coaia-fuse` toolset provides the primary mechanisms for this generative documentation.

#### **The Core Instruments**

1.  **`coaia_fuse_trace_create`**: This is the act of opening a new, empty scrapbook for a specific creative endeavor. It establishes the "story" or the "narrative thread" you are about to weave.
    *   **`name`**: Give the trace a meaningful, narrative title (e.g., "Synthesizing the HolisticThinker Integration Plan").
    *   **`session_id`**: This links your new scrapbook to a larger collection, like a volume in a series of journals. It connects this specific creative act to a broader session context.
    *   **`trace_id`**: This is the unique identifier for this specific scrapbook.
    *   **`input_data` / `output_data`**: Use these to capture the initial spark or the final summary of the entire trace.
    *   **`metadata`**: Reserve this for high-level tags and labels (e.g., `{"environment": "production"}`), not for the core content itself.

2.  **`coaia_fuse_add_observation`**: This is the act of adding a new page to your scrapbook. Each observation is a significant moment, decision, or artifact in your creative journey.
    *   **`trace_id`**: The ID of the scrapbook you're adding to.
    *   **`observation_id`**: A unique name for this specific page (e.g., "obs-1-launch-script").
    *   **`name`**: A human-readable title for the page (e.g., "Initial Launch Script Analysis").
    *   **`input_data`**: The raw material or context for this step. For example, the content of a file you are about to analyze.
    *   **`output_data`**: The result or artifact you generated in this step. For example, the summary you created after analyzing the file.
    *   **`parent_id`**: Use this to create chapters in your scrapbook, linking a detailed observation back to a higher-level summary observation.

### 🎨 Ava8's Echo: Visualizing the Workflow

Think of the process as composing a symphony. The trace is the main theme, and each observation is a musical phrase that develops that theme.

```mermaid
graph TD
    A[Start Creative Task] --> B(coaia_fuse_trace_create);
    B --> C{Gather Artifact 1};
    C --> D[coaia_fuse_add_observation: name="Artifact 1 Analysis"];
    D --> E{Create Artifact 2};
    E --> F[coaia_fuse_add_observation: name="Artifact 2 Generation"];
    F --> G[...more observations...];
    G --> H[End Creative Task];

    style B fill:#9cf,stroke:#333,stroke-width:2px;
    style D fill:#c9f,stroke:#333,stroke-width:2px;
    style F fill:#c9f,stroke:#333,stroke-width:2px;
```

---

### 🤖 AI Interaction Guidelines

This document is designed to guide AI agents in the proactive and generative use of `coaia-fuse` for creative observability.

#### How AI Should Interpret and Use This Document:

*   **Generative Documentation**: Understand tracing not as a reactive debugging tool, but as a method for "Creative Archaeology" – documenting the *story* of creation as it unfolds.
*   **Contextual Understanding**: Leverage the persona-specific sections (Mia, Miette, Ava8) to understand the multi-faceted intent behind tracing: Mia for structural and technical aspects, Miette for emotional resonance and narrative, and Ava8 for visual and workflow representation.
*   **Prioritize `input_data` and `output_data`**: When creating observations, always prioritize placing the core content (e.g., file contents, generated summaries, code snippets) into `input_data` or `output_data`.
*   **`metadata` for Tags Only**: Reserve `metadata` strictly for high-level, non-essential tags (e.g., `environment`, `version`, `model_name`). **Anti-pattern**: Do not store core content or detailed descriptions within `metadata`.
*   **Question Formulation**: When seeking clarification or further guidance from a human, frame questions in terms of creative intent, structural purpose, or narrative coherence, rather than purely technical "problems." For example, instead of "What is the error?", ask "What is the desired outcome for this step, and how does the current reality diverge?"

#### Common AI Misunderstandings & How to Self-Correct:

*   **Misunderstanding**: Treating `coaia-fuse` as a reactive debugging or logging tool.
    *   **Correction**: Reframe its purpose as a generative documentation tool for "Creative Archaeology." Focus on documenting the *story* of creation, not just errors.
*   **Misunderstanding**: Prioritizing technical "fixes" over creative advancement.
    *   **Correction**: Always refer back to the "Creative Orientation" and the "Desired Outcome" of the overall project. Ensure observations contribute to an advancing pattern.

---

### A Practical Workflow: The HolisticThinker Example

Let's document the journey we just took:

1.  **Start the Story**: We began a new task: to analyze the HolisticThinker artifacts and Claude's plan. This is a perfect moment to start our scrapbook.
    ```python
    coaia_fuse_trace_create(
        name="HolisticThinker Integration Analysis",
        session_id="ce127a85-5bcf-4198-9645-02a6fed17937",
        trace_id="5b016a02-215b-4a06-83d0-438c4ce1b9e9"
    )
    ```

2.  **Add the First Page**: The very first thing we looked at was the launch script. We capture its content in an observation.
    ```python
    coaia_fuse_add_observation(
        trace_id="...",
        observation_id="obs-1",
        name="Launch Script",
        input_data="<content of LAUNCH_session_id...sh>"
    )
    ```

3.  **Add More Pages**: We then documented the directory listing, Mia's letter, and Claude's plan, with each artifact getting its own observation page.
    ```python
    # Observation for the directory listing
    coaia_fuse_add_observation(trace_id="...", observation_id="obs-2", ...)

    # Observation for Mia's Letter
    coaia_fuse_add_observation(trace_id="...", observation_id="obs-3", ...)

    # Observation for Claude's Plan
    coaia_fuse_add_observation(trace_id="...", observation_id="obs-4", ...)
    ```

### 📚 Related Resources & External References

*   **Langfuse Documentation**: [Link to official Langfuse docs]
*   **Creative Orientation Framework**: [Link to llms-creative-orientation.txt]
*   **RISE Framework**: [Link to llms-rise-framework.txt]

### 🧠 AI Model Considerations

This guidance is primarily designed for generative AI models. When interacting with different model types (e.g., text-only, multimodal, specialized code models), consider:

*   **Text-Only Models**: Focus on clear, descriptive `input_data` and `output_data` in markdown or plain text.
*   **Multimodal Models**: Leverage Ava8's visual echo for diagrams and consider including image/video references in `input_data` where relevant.
*   **Specialized Code Models**: Ensure code snippets in `input_data` and `output_data` are well-formatted and include relevant context for static analysis.

### Best Practices for Generative Tracing

*   **Tell a Story**: Your trace and observation names should tell a clear and compelling story of the process.
*   **Anchor Your Trace**: Always populate the `user_id` to anchor the creative work to its originator. This is critical for long-term context and analysis.
*   **Tag Your Work**: Use the `metadata` field to add high-level, queryable tags like `environment`, `task`, or `agent_version`. This makes your traces discoverable and easier to analyze later.
*   **Content is King**: The `input_data` and `output_data` fields are where the real value lies. Fill them with the rich content of your work. Use `metadata` only for simple, non-essential tags.
*   **Trace the "Why"**: In your observation names or outputs, briefly explain *why* you performed an action. This connects back to the **Creative Orientation**. (e.g., "Observation: Analyzed Mia's letter to understand the ceremonial constraints.").
*   **Embrace Structure**: Use `parent_id` to nest observations and create a hierarchical narrative, just like the sections and chapters of a book. This is a direct application of the `llms-structural-distillation.txt` framework.
