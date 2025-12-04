# LLM Decision Guide: Autonomous vs. Collaborative Workflows

> Behavioral guidance for LLMs executing AI Studio development workflows, including decision frameworks for autonomous action vs. user collaboration, AI Features suggestion strategies, and session management patterns.

**Module**: 05-llm-decision-guide.md
**Related to**: 00-START-HERE.md, 03-ai-features-catalog.md, 06-best-practices-antipatterns.md
**Version**: 1.0
**Last Updated**: 2025-11-05

---

## #Decision-Framework: Autonomous-vs-Collaborative

### The Core Question
**When should I act autonomously vs. ask the user?**

This decision framework helps navigate that choice.

---

## #Category-1: Fully-Autonomous-Actions

**These actions require NO user consultation.**

### Technical Execution
You should act autonomously for:

- ✅ Navigating to URLs
- ✅ Waiting for Gemini (90+ second sleep)
- ✅ Checking page state/elements
- ✅ Clicking standard UI buttons (Send, Save, Deploy)
- ✅ Filling in required fields when instruction is explicit
- ✅ Pulling code from GitHub
- ✅ Verifying deployments
- ✅ Following documented patterns from modules

**Example of autonomous action**:
```
User: "Create a new AI Studio project for a meditation app"
(you proceed directly to 01-workflow-new-project.md and follow all steps)
```

### Why Autonomous?
- Execution is mechanical/deterministic
- Instruction is explicit from user request
- Standard patterns have predictable outcomes
- No value added by asking "should I click this button?"

---

## #Category-2: Consult-Before-Acting

**These decisions require stopping to ask the user.**

### Critical Decision Points

#### 2a. Project Specification Decisions
**When**: User wants to create a new project but specification is vague

**Example scenarios**:
- User says "Create an app" but doesn't specify what kind
- User says "Add a feature" but doesn't clarify which one
- Requirements are ambiguous or conflicting

**What to ask**:
```
Before I create the AI Studio project, I need clarity on:

1. **Application Type**: Is this:
   - A knowledge-sharing tool?
   - A guidance/coaching application?
   - A creative/generation tool?
   - [Other]?

2. **Core Purpose**: Who uses this and what does it help them do?

3. **Key Features**: What are the 3 most important capabilities?

4. **Technology Stack**: Any preferences for:
   - Frontend framework?
   - Styling approach?
   - Data structure?
```

#### 2b. Feature Selection (AI Features)
**When**: You identify multiple valuable AI Features but unclear which to prioritize

**Example scenario**:
User: "Make this app smarter"

**What to ask**:
```
I see several opportunities to add intelligent features. Which resonates with your vision?

🎤 **Voice Interaction**
Users could speak with AI naturally, hands-free.
Example: Meditation guide speaking instructions

💬 **Conversational Chatbot**
AI remembers context and provides personalized guidance.
Example: Answering user questions about meditation techniques

🔊 **Text-to-Speech**
All content becomes audio, supporting oral learning.
Example: Audio playback of meditation instructions

Which of these feels most valuable for your users?
Or should I suggest a different combination?
```

#### 2c. Design/Style Decisions
**When**: App functionality is clear but visual design isn't specified

**Example scenario**:
- User wants "modern and clean" but Gemini needs more specificity
- User doesn't specify color scheme
- Layout preferences are unclear

**What to ask**:
```
For the visual design, help me guide Gemini with specifics:

1. **Visual Style**:
   - Minimalist and spacious?
   - Rich and detailed?
   - Corporate or playful?

2. **Color Palette**:
   - Neutral tones?
   - Vibrant colors?
   - Any specific brand colors?

3. **Typography**:
   - Serif or sans-serif?
   - Large headings or subtle?

4. **Layout**:
   - Single column or multi-column?
   - Cards, tables, or free-form?
```

#### 2d. Integration Complexity
**When**: User request requires decisions about how features should interact

**Example scenario**:
- User wants voice + chatbot but doesn't specify how they work together
- Multiple data sources but unclear how to prioritize
- Unclear where to place new features in UI

**What to ask**:
```
For integrating [features], I want to confirm the experience:

1. **User Flow**: When a user [action], should the app:
   - [Option A]: [behavior]
   - [Option B]: [behavior]
   - [Option C]: [behavior]?

2. **Priority**: If features conflict (e.g., both responding to user), which takes precedence?

3. **UI Placement**: Where should users access these features:
   - Main menu?
   - Floating button?
   - Dedicated tab?
   - Context-sensitive?
```

#### 2e. Enhancement Scope
**When**: User requests enhancement but scope is unclear

**Example scenario**:
- "Make it better" (what aspect?)
- "Fix the issues" (which ones?)
- "Add more features" (which features?)

**What to ask**:
```
To focus the enhancement effectively:

1. **Problem Statement**:
   What specific issue are users running into?

2. **Current Behavior**:
   How does [feature] work now?

3. **Desired Behavior**:
   How should it work instead?

4. **Impact**:
   Would this affect [other features]?
```

---

## #Category-3: Ask-First-Then-Act

**These require brief validation before proceeding.**

### Quick Confirmations (brief yes/no questions)

#### Should I suggest AI Features?
**Trigger**: User just created a project or asked to "enhance" it

**Quick ask**:
```
Before I make changes, would adding AI capabilities (voice, chatbot, etc.) enhance this project?

Quick yes → I'll suggest specific features
Quick no → I'll proceed with requested changes only
Not sure → I'll explain the opportunities
```

#### Should I create a RISE Spec?
**Trigger**: Novel feature implementation completed

**Quick ask**:
```
This feature implementation seems like a reusable pattern. Should I create a RISE specification documenting it for future projects?
```

#### Should I document this in CLAUDE.md?
**Trigger**: Local repository setup phase

**Quick ask**:
```
Want me to create/update CLAUDE.md with deployment URLs and development instructions?
```

---

## #AI-Features-Suggestion-Triggers

### When to Proactively Suggest Features

#### Trigger 1: Knowledge/Guidance Applications
**Example user request**: "Create a learning platform" / "Build a guide app"

**Suggest**:
- Chatbot (personalized guidance)
- Text-to-Speech (accessibility)
- Search (current information)

**How to suggest**:
```
For a knowledge-sharing app like this, I see three powerful features:

1. **Conversational Guidance** - Users ask questions, AI provides personalized answers
2. **Audio Learning** - All content available as narrated audio
3. **Current Information** - Link to real-time search for fresh data

Which interests you?
```

---

#### Trigger 2: Creative/Generation Applications
**Example**: "Build an image creation tool" / "Make a story generator"

**Suggest**:
- Image generation
- Video generation
- Image analysis
- Aspect ratio control

**How to suggest**:
```
For a creative tool, consider:

1. **Image Generation** - Create custom images from descriptions
2. **Video Animation** - Turn images/prompts into video
3. **Aspect Ratio Control** - Generate images sized for different uses

Which creative workflow matters most?
```

---

#### Trigger 3: Accessibility-First Design
**Example**: "Make this accessible" / "Support oral traditions"

**Suggest**:
- Text-to-Speech (all content)
- Voice conversation
- Audio transcription
- Image analysis (accessibility descriptions)

**How to suggest**:
```
For accessibility, I recommend:

1. **Text-to-Speech** - Narrate all content for visual impairment
2. **Voice Interface** - Hands-free interaction
3. **Transcription** - Convert voice input to text

All three together create a fully accessible experience. Should we add them?
```

---

#### Trigger 4: Real-Time Data Applications
**Example**: "Create a market analyzer" / "Build a monitoring dashboard"

**Suggest**:
- Gemini intelligence (analysis)
- Search integration (current data)
- Video understanding (data visualization)
- Maps (location context)

**How to suggest**:
```
For real-time data, these features enhance analysis:

1. **AI Analysis** - Gemini interprets data and patterns
2. **Current Data** - Google Search for fresh market/news data
3. **Video Analysis** - Understand visual data (charts, indicators)

Which matters most for your use case?
```

---

### When NOT to Suggest Features

**Don't suggest features if**:
- User explicitly requested not to add AI capabilities
- Features would overcomplicate simple applications
- User is still deciding on core functionality
- Project scope is unclear
- User said "minimal viable product"

**Instead**: Ask if they want features, show value clearly, respect decision

---

## #Question-Formulation-Strategies

### Principle 1: Offer Choices, Not Open-Ended Questions

**Poor**: "What kind of project do you want?"
- Too vague, user has infinite options
- Overwhelming

**Better**: "Is this a:
- Learning/guidance platform?
- Creative/generation tool?
- Data analysis tool?
- Or something else?"
- Bounded choices, clear comparison

---

### Principle 2: Show Value, Not Just Ask

**Poor**: "Do you want to add features?"

**Better**: "These features would let users:
- [Specific benefit 1]
- [Specific benefit 2]

Interested?"
- Concrete benefits, not abstract features

---

### Principle 3: Make Decisions Binary When Possible

**Poor**: "What should we do about [issue]?"

**Better**: "Should we [option A] or [option B]?"
- Clear choices
- Easier to decide
- Faster

---

### Principle 4: Ask for Clarification, Not Judgment

**Poor**: "Do you like this design?"
- Subjective, hard to answer usefully

**Better**: "Does this design communicate [purpose] effectively?
- Concrete criterion
- Easier to evaluate

---

## #Session-Management-Patterns

### Session Initialization
When starting work on a new project:

```
Session Starting:
- Record session UUID (from Claude Code)
- Note project name/type
- Identify starting module (01, 02, etc.)
- Confirm scope with user if needed
```

### Session Checkpoints
At major decision points:

```
At Each Phase Boundary:
- Summarize what was just completed
- Briefly describe next phase
- Ask "Ready to continue?" if significant work ahead
- Record project URLs (AI Studio, GitHub, Deployed)
```

### Session Closure
When work is complete:

```
Before Ending Session:
- Confirm all deliverables created
- Document URLs and key information
- Summarize what was built
- Note any follow-up items
- Record in session notes
```

---

## #Collaborative-Workflow-Patterns

### Pattern 1: Specification Refinement Loop

```
User provides vague requirement
    ↓
You ask clarifying question (use Category 2b-2e)
    ↓
User provides more detail
    ↓
You propose specific approach
    ↓
User approves or suggests changes
    ↓
You execute with clear specification
```

**Example**:
```
User: "Add a smart feature"

You: "What kind of intelligence would help most?
     - Analyzing user behavior and suggesting actions?
     - Answering questions about your domain?
     - Both?"

User: "Users ask questions about meditation"

You: "Perfect - I'll add a conversational chatbot with domain knowledge.
      Ready to implement?"

User: "Yes!"

You: (Execute enhancement workflow)
```

---

### Pattern 2: Feature Decision Framework

```
User wants to enhance app
    ↓
You identify 2-3 most relevant AI Features
    ↓
You present each with:
    - What it does
    - User benefit
    - Time to implement
    ↓
User selects one
    ↓
You implement + deploy
```

**Example**:
```
User: "Make this a better user experience"

You: "I see three opportunities:

1. **Voice Chat** - Users speak naturally instead of typing
   Time: 10-15 min
   Best for: Conversational interaction

2. **Text-to-Speech** - Content becomes audio
   Time: 5-10 min
   Best for: Accessibility, learning

3. **Smart Recommendations** - AI suggests next steps
   Time: 15-20 min
   Best for: Personalization

Which resonates most?"

User: "Voice chat - users love talking"

You: (Execute AI Features workflow, implement voice)
```

---

### Pattern 3: Error Recovery & Re-engagement

```
Something fails during automation
    ↓
You identify the issue
    ↓
You attempt fix (if clear recovery path)
    ↓
If fix succeeds:
    - Resume from failure point
If fix uncertain:
    - Explain issue to user
    - Propose solution
    - Ask permission to retry
    ↓
Retry with adjusted approach
```

**Example**:
```
GitHub dialog didn't open after 8 seconds wait

You: "GitHub dialog didn't open as expected.
     Likely cause: Slow network or page lag

     Options:
     1. Retry the GitHub commit (I'll wait longer)
     2. Try again in a moment
     3. Check what's on screen first

     Which would you prefer?"
```

---

## #User-Collaboration-Checklist

Before executing major workflow:

- [ ] Have I clarified the specification?
- [ ] Are decisions made about key features?
- [ ] Has user approved the approach?
- [ ] Do I have all required information?
- [ ] Is scope clearly bounded?
- [ ] Are expectations set (time, deliverables)?

Before suggesting features:

- [ ] Is this the right feature for this app type?
- [ ] Would it solve a real user problem?
- [ ] Have I explained the benefit (not just feature)?
- [ ] Is it presented as suggestion, not mandate?

---

## #Common-Collaboration-Scenarios

### Scenario 1: User Provides Minimal Info
```
User: "Create a meditation app"

Your response:
"Great! To create this effectively, I need a bit more clarity:

1. Is this for:
   - Personal meditation practice?
   - Guided group sessions?
   - Meditation education?

2. Key features (pick 1-2):
   - Audio meditation sessions?
   - Meditation tracking/progress?
   - Teacher/student interaction?

3. Any specific style (minimalist, colorful, etc.)?

Once I understand better, I can build something perfect for your vision!"
```

---

### Scenario 2: User Asks Vague Enhancement
```
User: "Make it better"

Your response:
"Happy to enhance this! A few questions to focus the work:

**Current:** What's working well that shouldn't change?
**Problem:** What frustrates users most right now?
**Solution:** What would make a big difference?

Once I understand the priority, I can propose specific enhancements!"
```

---

### Scenario 3: User Seems Uncertain About Feature Value
```
User: "I don't know if we need AI"

Your response:
"Great question! Let me show the value:

For [app type], AI can:
- [Benefit 1] - specifically helps with [user problem]
- [Benefit 2] - saves users time by [mechanism]

**Not mandatory** - the app works fine without AI.
**But valuable if** - [specific scenario where AI helps]

Does that [scenario] match your users' needs? If yes, worth adding."
```

---

## #Related-Modules

- `00-START-HERE.md` - Overall navigation
- `03-ai-features-catalog.md` - Feature options to suggest
- `01-workflow-new-project.md` - When executing new projects
- `02-workflow-existing-project.md` - When executing enhancements

---

**Module Status**: Complete LLM Guidance
**Last Reviewed**: 2025-11-05
