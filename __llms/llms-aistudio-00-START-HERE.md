# AI Studio Collaborative Development Guide for LLMs

> A comprehensive modular guide for LLMs to autonomously drive browser automation (Chrome DevTools/Playwright) for end-to-end AI Studio development, from project creation through deployment, including intelligent AI Features recommendation and interactive user collaboration.

**Version**: 1.0
**UUID**: llms-aistudio-collab-2025-11
**Last Updated**: 2025-11-05
**Content Sources (OLD VERSION)**:
- AI_STUDIO_WORKFLOW_NEW_PROJECT.md
- AI_STUDIO_WORKFLOW.md
- AI_STUDIO_AI_FEATURES_EXPLORATION.md

---

## #Quick-Start-Guide

Choose your scenario below to find the right module:

### Scenario 1: Creating a Brand New AI Studio Project
**You want to**: Build a new application from scratch using AI Studio and Gemini

**Time**: ~2-3 minutes for full workflow
**Modules**:
1. Read: `llms-aistudio-01-workflow-new-project.md` (complete 6-phase lifecycle)
2. Reference: `llms-aistudio-04-browser-automation-reference.md` (for command syntax)
3. Cross-check: `llms-aistudio-06-best-practices-antipatterns.md` (not just avoid common mistakes)

**High-Level Steps**:
- Draft specification with RISE framework (Phase 1)
- Create AI Studio project and send prompt to Gemini (Phase 2)
- **Wait 90+ seconds** for implementation to complete (critical!)
- Edit app name with UUID prefix (traceability, uniqueness and simplicity, they are like seeds)
- Create GitHub repository and initial commit, new issue in the repository created, not the one where we sparked the project (Phase 3)
- Deploy to Google Cloud Run (Phase 4)
- Clone locally,  review code, keep enhancing the intent of the prototype by iterating (Phase 5)

---

### Scenario 2: Enhancing an Existing AI Studio Project
**You want to**: Add features, fix bugs, or improve an existing deployed application

**Time**: ~10-15 minutes per enhancement
**Modules**:
1. Read: `llms-aistudio-02-workflow-existing-project.md` (streamlined enhancement workflow)
2. Reference: `llms-aistudio-04-browser-automation-reference.md` (command syntax)
3. Consult: `llms-aistudio-03-ai-features-catalog.md` (if adding AI capabilities)

**High-Level Steps**:
- Navigate to existing AI Studio project edit URL
- Describe desired change/enhancement
- Wait for Gemini implementation (90+ seconds)
- Commit to GitHub with issue reference
- Redeploy application
- Verify changes in deployed app

---

### Scenario 3: Adding AI Features to Any Project
**You want to**: Enhance an application with voice, chatbots, text-to-speech, or other AI capabilities

**Time**: Varies (5-15 minutes depending on feature complexity)
**Modules**:
1. Read: `llms-aistudio-03-ai-features-catalog.md` (understand available features)
2. Read: `llms-aistudio-05-llm-decision-guide.md` (collaborate with user on feature selection)
3. Then: Follow Scenario 1 or 2 with the AI Features enhancement

**High-Level Steps**:
- Present available AI Features to user (voice, chatbots, TTS, etc.)
- Gather requirements and preferences
- Craft feature-specific prompt
- Send to Gemini with implementation guidance
- Verify and deploy

---

## #Module-Directory

### Workflows (Read These First)

#### **llms-aistudio-01-workflow-new-project.md**
Complete lifecycle for creating brand new AI Studio projects from scratch.

**When to use**:
- Starting a completely new application
- Creating prototype/proof-of-concept projects
- Following RISE specifications into implementation

**What it covers**:
- Pre-project planning and prompt drafting
- AI Studio project creation and file attachment
- Gemini prompt submission and implementation waiting
- UUID naming for traceability
- GitHub repository creation and initial commit
- Google Cloud Run deployment
- Local repository cloning and code review
- Documentation creation (CLAUDE.md)
- Iteration patterns for enhancements

**Key deliverable**: Deployed, versioned, traceable AI Studio application

---

#### **llms-aistudio-02-workflow-existing-project.md**
Streamlined workflow for enhancing projects already in AI Studio.

**When to use**:
- Adding features to deployed applications
- Fixing bugs or improving existing code
- Iterating on Scenario 1 projects

**What it covers**:
- Navigating to existing AI Studio projects
- Sending enhancement requests to Gemini
- Standard commit/deploy cycle
- Verification of changes

**Key deliverable**: Updated deployed application with tracked changes

---

### Enhancement & Features

#### **llms-aistudio-03-ai-features-catalog.md**
AI Features exploration, complete catalog, recommendation strategies, and implementation patterns.

**When to use**:
- Determining which AI capabilities to add
- Crafting feature-specific prompts
- Understanding implementation patterns
- Creating RISE specs for novel features

**What it covers**:
- Understanding what AI Features are
- Complete catalog (voice, chatbots, TTS, images, video, maps, search, etc.)
- How to suggest features to users
- Gathering user requirements
- Implementation patterns for multi-feature integration
- Testing and verification
- RISE specification creation for new feature patterns

**Key deliverable**: Enhanced applications with intelligent AI capabilities

---

### Technical References (Support Materials)

#### **llms-aistudio-04-browser-automation-reference.md**
Complete technical reference for browser automation commands using Chrome DevTools/Playwright.

**When to use**:
- Need exact syntax for element selection
- Finding specific button or dialog
- Debugging page state issues
- Implementing timing patterns

**What it covers**:
- Chrome DevTools/Playwright command library
- Critical timing patterns (90s waits, 8-10s dialog delays)
- Dialog state management (open, close, verify)
- Completion verification strategies
- GitHub workflow automation
- Debugging strategies

**Key deliverable**: Correct command syntax and timing patterns

---

#### **llms-aistudio-05-llm-decision-guide.md**
Behavioral guidance for LLM decision-making during autonomous execution.

**When to use**:
- Deciding whether to ask user vs. act autonomously
- Detecting when to suggest AI Features
- Determining when to pause for consultation
- Planning user collaboration interactions

**What it covers**:
- Decision framework for user interaction
- When autonomous action is appropriate
- When to ask questions and how to ask them
- AI Features suggestion triggers
- Session management and traceability
- User collaboration patterns

**Key deliverable**: Intelligent autonomous decision-making

---

### MCP Server Integration

#### **llms-aistudio-07-mcp-server-setup.md** (Main Reference)
Complete configuration and usage guide for the AI Studio MCP (Model Context Protocol) server.

**When to use**:
- Setting up Claude Desktop or Claude Code with AI Studio automation
- Configuring aistudio_mcp_tools.py server (FastMCP pattern)
- Integrating Playwright MCP with aistudio MCP
- Understanding .mcp.json configuration
- Troubleshooting MCP server connection issues

**What it covers**:
- Prerequisites and installation (pip, playwright, MCP SDK)
- Configuration examples (global and local)
- All 5 available MCP tools with parameters
- Critical timing patterns for Gemini implementation
- Common configuration errors and fixes
- File naming requirements (underscores vs hyphens)
- FastMCP pattern explanation (vs old Server class)
- Successful test results reference
- Verification checklist before running workflows

**Key deliverable**: Properly configured MCP servers ready for autonomous execution

---

#### **llms-aistudio-08-mcp-quick-reference.md** (Quick Lookup)
Fast reference card for common tasks, errors, and configurations.

**When to use**:
- Quick configuration lookup (copy-paste .mcp.json template)
- Troubleshooting errors quickly
- Finding exact command syntax for tools
- Checking file naming rules
- Pre-flight checklist before workflows

**What it covers**:
- One-time installation commands
- Configuration templates (copy-paste ready)
- Tools quick reference table
- Common errors with fixes
- File naming rules and common mistakes
- Pre-flight checklist
- FastMCP pattern example

**Key deliverable**: Fast lookup to get moving quickly

---

### Quality & Troubleshooting

#### **llms-aistudio-06-best-practices-antipatterns.md**
Critical learnings, common mistakes, debugging strategies, and success criteria.

**When to use**:
- Something went wrong and you need recovery
- Before starting a workflow (learn what NOT to do)
- Debugging mysterious failures
- Verifying success of completed workflows

**What it covers**:
- 20+ consolidated anti-patterns with solutions
- Timing-related mistakes and fixes
- Dialog state management failures
- Element selection gotchas
- Debugging procedures
- Success criteria checklists for all workflows
- Code snippet library organized by function

**Key deliverable**: Successful workflows with minimal retries

---

## #Decision-Tree: Which Module Do I Need?

```
START: What are you trying to do?

├─ "Create a brand new project"
│  └─ Read: 01-workflow-new-project.md
│     Then reference: 04-browser-automation (if stuck)
│     Then check: 06-best-practices (if something fails)

├─ "Enhance existing project"
│  └─ Read: 02-workflow-existing-project.md
│     Then reference: 04-browser-automation (if stuck)
│     Optionally: 03-ai-features (if adding capabilities)

├─ "Add AI Features (voice, chatbot, etc.)"
│  └─ Read: 03-ai-features-catalog.md
│     Then read: 05-llm-decision-guide.md
│     Then follow: 01 or 02 (depending on project stage)

├─ "Need exact command syntax"
│  └─ Read: 04-browser-automation-reference.md

├─ "Deciding what to do autonomously vs. ask user"
│  └─ Read: 05-llm-decision-guide.md

├─ "Setting up MCP server for Claude Desktop"
│  └─ Read: 07-mcp-server-setup.md
│     (Configure aistudio-mcp-tools.py and claudse_desktop_config.json)

└─ "Something is broken / not working"
   └─ Read: 06-best-practices-antipatterns.md
      (Find your situation, apply fix, retry)
```

---

## #Cross-Module-Workflows: Complete Task Examples

### Example 1: Create New Project + Add AI Features
**Total time**: 40-45 minutes

1. **Reference**: RISE specification or requirements document
2. **Read**: `01-workflow-new-project.md` (Phases 1-2 only, stop after UUID naming)
3. **Read**: `03-ai-features-catalog.md` (understand feature options)
4. **Interact**: `05-llm-decision-guide.md` (collaborate with user on feature selection)
5. **Resume**: `01-workflow-new-project.md` (continue Phases 3-6 with features included in Phase 2b prompt)
6. **Verify**: `06-best-practices-antipatterns.md` (success checklist)

**Outcome**: New project deployed with AI Features integrated from creation

---

### Example 2: Iterative Enhancement with Testing
**Total time**: 15-20 minutes per iteration

1. **Read**: `02-workflow-existing-project.md` (first 3 sections)
2. **Reference**: `04-browser-automation-reference.md` (for exact commands)
3. **Execute**: Enhancement request to Gemini
4. **Verify**: `06-best-practices-antipatterns.md` (success checklist)
5. **Test**: Deployed application
6. **Decision**: `05-llm-decision-guide.md` (report results, plan next iteration)

**Outcome**: Iteratively improved application with tracked changes

---

### Example 3: Debugging Failed Workflow
**Total time**: 5-10 minutes to identify + fix

1. **Reference**: `06-best-practices-antipatterns.md`
2. **Find**: Section matching your issue (e.g., "Dialog didn't open")
3. **Apply**: Recommended solution
4. **Retry**: Step from appropriate module (01, 02, or 04)
5. **Resume**: Original workflow where it failed

**Outcome**: Recovered workflow, completed task

---

## #How-LLMs-Should-Use-This-System

### Reading Approach
- **First time**: Read `00-START-HERE` (this file) entirely
- **Subsequent uses**: Jump directly to needed module via Decision Tree
- **Token efficiency**: Read only the sections you need, use cross-references

### Integration with MCP Tools
- **Chrome DevTools MCP**: Refer to `04-browser-automation-reference.md` for exact commands
- **Playwright MCP**: Same reference applies
- **All automation**: Timing patterns from `04` apply universally

### User Collaboration
- When uncertain about user intent: Refer to `05-llm-decision-guide.md`
- When presenting options: Use patterns from `03-ai-features-catalog.md`
- When asking clarifying questions: Reference decision framework from `05`

### Error Recovery
- When something fails: Jump directly to `06-best-practices-antipatterns.md`
- Find matching scenario, apply fix, resume original workflow
- If still stuck: Consult `04-browser-automation-reference.md` for alternative selectors/timing

---

## #LLMS-txt-Compliance-Notes

**This documentation system meets LLMS-txt standards**:

- ✅ **Mandatory Elements**: H1, blockquote summary, version, sources
- ✅ **Clarity**: Technical jargon explained in context, actionable steps
- ✅ **Machine Readability**: Hashtag-based sections, consistent structure, metadata
- ✅ **LLM Guidance**: Explicit "How LLMs Should Use" section, decision framework
- ✅ **Anti-Pattern Identification**: Dedicated module (06) for common mistakes
- ✅ **Cross-References**: Hashtag sections enable easy navigation
- ✅ **Accessibility**: Clear hierarchy, progressive disclosure, visual structure

---

## #Related-Documentation

These LLMS documents complement this guide:

- **llms-rise-framework.txt** - For creating specifications that AI Studio can implement
- **llms-structural-thinking.gemini.txt** - For complex decision-making during development
- **llms-duo-mia-miette-arc-v8.md** - For understanding collaborative LLM personas
- **llms-digital-decision-making.md** - For binary decision frameworks following Robert Fritz Twos and Threes
- **llms-managerial-moment-of-truth.md** - For MMOT (MOT) Manegerial Moment of Truth Techniques to review, evaluate and improve performance.

---

## #Session-Tracking-Pattern

When using this guide, maintain traceability:

```
Session Start:
- Session UUID: [from Claude Code session or given by user]
- Task: [what are you building]
- Start module: [which file you opened first]
- Start time: [timestamp]

Session Progress:
- Modules read: [list modules consulted]
- AI Studio Project Name: [created or modified]
- GitHub Repository: [create with UUID prefix]
- Deployed URL: [note for reference]

Session End:
- Outcome: [project created/enhanced/fixed]
- Documentation created: [CLAUDE.md, issue descriptions]
- Related specs: [any RISE specs created]
```

---

## #Next-Steps

1. **Identify your scenario** above (New Project / Enhancement / AI Features)
2. **Follow the module path** for your scenario
3. **Reference other modules** as needed
4. **Check 06-best-practices** if anything seems wrong
5. **Update this page** if you discover patterns not documented

---

**Document Status**: Active Navigation Hub
**Maintenance**: Review monthly for clarity and new patterns
**Version History**: v1.0 (2025-11-05) - Initial modular system
