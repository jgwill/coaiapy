# How to Create a Claude.ai Skill: A Guide for LLMs

> A comprehensive guide for LLMs on how to conceptualize, structure, and implement custom skills for Claude.ai, using the `aistudio-scaffolder` as a practical example. This document follows the Creative Orientation and Structural Thinking principles.

**Version**: 1.0
**UUID**: llms-claude-skill-creation-guide-2025-11-07
**Content Sources**:
-   Official Claude.ai Skill Creation Documentation
-   `aistudio-scaffolder` Skill Implementation
-   `llms-txt-compliance-checklist.md`

---

## #Core-Concept-What-Is-a-Skill

A Claude.ai skill is a packaged set of instructions and tools that extends Claude's native capabilities. It allows Claude to perform specialized, multi-step tasks by following a predefined workflow.

Think of a skill not as a single tool, but as a **recipe** that tells Claude how to use a series of tools and prompts to achieve a complex outcome.

### Key Principles:
1.  **Creative Orientation**: A skill should be designed to *create* a desired outcome, not just *solve* a problem.
2.  **Structured Workflow**: A skill provides a clear, step-by-step process for Claude to follow.
3.  **Tool Integration**: A skill can include and orchestrate executable scripts to perform actions beyond text generation.

---

## #Anatomy-of-a-Skill

A skill is contained within a directory. The two essential components are:

1.  **`SKILL.md`**: The heart of the skill. This Markdown file contains the metadata and the workflow instructions.
2.  **`scripts/` directory**: An optional directory containing any helper scripts the skill needs to execute.

### The `SKILL.md` File

This file has two parts:

#### 1. The YAML Frontmatter (The "What")
This is a metadata block at the very top of the file, enclosed in `---`.

```yaml
---
name: aistudio-scaffolder
description: This skill helps bootstrap a new Google AI Studio project by generating the initial prompt and specification artifacts from a high-level idea.
---
```

-   `name`: A unique, concise, lowercase identifier for the skill.
-   `description`: A clear and comprehensive explanation of what the skill does. This is **critical**, as Claude uses this description to determine when to use the skill.

#### 2. The Markdown Body (The "How")
This section provides a detailed, step-by-step workflow for the LLM (Claude) to follow. It should be written as a guide or a set of instructions.

**A good skill body includes:**
-   **Workflow Steps**: Clearly defined stages of the process.
-   **Interaction Guidance**: Instructions on how to interact with the user (e.g., what questions to ask).
-   **Script Execution**: Clear instructions on when and how to run any included scripts.
-   **Expected Output**: A description of the final artifact the skill should produce.

---

## #Practical-Example-The-aistudio-scaffolder-Skill

Let's analyze the `aistudio-scaffolder` skill to see these principles in action.

**Goal**: To generate the initial planning documents for a new Google AI Studio project.

### Directory Structure:
```
/aistudio-scaffolder/
├── SKILL.md
└── scripts/
    ├── generate_initial_prompt.py
    └── generate_rise_specs.py
```

### `SKILL.md` Analysis:

The `SKILL.md` for this skill defines a clear, five-step workflow:
1.  **Understand the Desired Outcome**: Ask the user for their high-level vision.
2.  **Gather Core Requirements**: Ask clarifying questions about the tech stack, features, and design.
3.  **Generate the Initial AI Studio Prompt**: Use the `generate_initial_prompt.py` script to create a structured prompt.
4.  **Generate Placeholder RISE Specifications**: Use the `generate_rise_specs.py` script to create `.spec.md` files.
5.  **Package the Artifacts**: Present the generated files to the user in a structured format.

This structure is effective because it guides the LLM through a logical sequence of information gathering, tool use, and final output generation.

### `scripts/` Analysis:

The scripts are simple, single-purpose Python files that take command-line arguments.

-   **`generate_initial_prompt.py`**: Takes user requirements (name, outcome, stack, etc.) and prints a formatted Markdown prompt to standard output.
-   **`generate_rise_specs.py`**: Takes a list of features and creates a `rispecs` directory with placeholder `.spec.md` files.

This approach is robust because it separates the logic for generating artifacts from the instructional workflow in `SKILL.md`.

---

## #How-to-Create-a-New-Skill-Step-by-Step

1.  **Define the Desired Outcome**:
    *   Start by asking: "What do I want to *create* with this skill?"
    *   *Example*: "I want to create a skill that drafts a weekly project status report."

2.  **Design the Workflow**:
    *   Break down the process into logical steps. What information is needed? What actions must be taken?
    *   *Example Workflow*:
        1.  Ask the user for the project name.
        2.  Ask for a list of completed tasks this week.
        3.  Ask for any blockers or challenges.
        4.  Use a script to format this information into a report template.
        5.  Present the final report to the user.

3.  **Create the Skill Directory**:
    *   `mkdir -p my-new-skill/scripts`

4.  **Write the `SKILL.md`**:
    *   Create the YAML frontmatter with a clear `name` and `description`.
    *   Write the step-by-step workflow in the body of the file. Be explicit about when to ask the user for input and when to run scripts.

5.  **Write the Helper Scripts (if any)**:
    *   Create the Python or shell scripts in the `scripts/` directory.
    *   Ensure they are executable and take clear command-line arguments.

6.  **Test the Skill**:
    *   Invoke the skill with Claude and follow the workflow.
    *   Verify that it asks the right questions, runs the scripts correctly, and produces the expected output.

---

## #Best-Practices-and-Anti-Patterns

### Best Practices (Do This):
-   **Keep Skills Focused**: Each skill should have one clear, well-defined purpose.
-   **Write Descriptive `description`s**: This is the most important part for skill discovery. Explain the *outcome*, not just the action.
-   **Separate Logic from Instructions**: Put complex formatting or data manipulation logic into scripts. Keep the `SKILL.md` as a high-level guide.
-   **Use the Creative Orientation**: Frame the skill's purpose around what it helps the user *create*.

### Anti-Patterns (Avoid This):
-   **Vague Descriptions**: A description like "Runs a script" is useless. Claude won't know when to use it.
-   **Monolithic Scripts**: Avoid writing a single, complex script that tries to do everything. Break it down into smaller, reusable tools.
-   **Problem-Solving Focus**: Don't frame the skill around "fixing" or "solving". Frame it around "generating," "drafting," "creating," or "scaffolding."
-   **Hardcoding Data**: Don't hardcode values in your scripts. Pass them in as arguments based on the user's input.

---
