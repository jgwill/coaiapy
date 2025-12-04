# AI Studio New Project Workflow: 6-Phase Lifecycle

> Complete step-by-step instructions for creating brand new AI Studio projects from scratch, from specification drafting through GitHub integration, deployment, and local setup.

**Module**: 01-workflow-new-project.md
**Related to**: 00-START-HERE.md, 04-browser-automation-reference.md, 06-best-practices-antipatterns.md
**Version**: 1.0
**Last Updated**: 2025-11-05

---

## #Overview: 6-Phase Lifecycle

| Phase | Purpose | Time | Key Action |
|-------|---------|------|-----------|
| 1 | Pre-Project Planning | 5-10 min | Draft prompt + gather specs |
| 2 | AI Studio Creation | 10-30 min | Create project + send to Gemini |
| 2b | AI Features Integration | 5-15 min | Suggest/add intelligent features |
| 3 | GitHub Integration | 10-15 min | Create repo + initial commit |
| 4 | Deployment | 10-15 min | Deploy to Google Cloud Run |
| 5 | Local Setup | 5-10 min | Clone + review + document |

**Total: 45-95 minutes** (depending on app complexity and feature additions)

---

## #Phase-1: Pre-Project-Planning

### Goal
Create a clear specification that Gemini can execute accurately.

### Step 1.1: Draft Initial Prompt
**Best practices**:
- Use RISE specifications if available (Current Reality → Desired Outcome → Natural Progression)
- Be explicit about technology stack (React, TypeScript, Tailwind CSS, etc.)
- List key features with user flows
- Include visual design principles
- Define data structures needed

**Template**:
```
Create a [APPLICATION TYPE] using [TECH STACK].

Core Intent:
This application enables users to [DESIRED OUTCOME].

Key Features:
1. [Feature 1 with implementation details]
2. [Feature 2 with implementation details]
3. [Feature 3 with implementation details]

Visual Design:
- [Design principle 1]
- [Design principle 2]

Technical Requirements:
- [Requirement 1]
- [Requirement 2]

[Attach any RISE specs or reference documents]
```

### Step 1.2: Prepare Supporting Files
Gather all documents Gemini should reference:
- RISE specifications (*.spec.md)
- Design mockups or wireframes
- Example applications for reference
- Data schemas or API contracts
- Style guides

**Location**: Have files ready on Google Drive or local for upload.

### Step 1.3: Plan UUID Naming
Prepare your session UUID for the app name:
- Obtain UUID from Claude Code session (e.g., `b40e2a3d-9330-46d4-a52d-50a056d5b46a`)
- This will prefix app name: `{UUID}-{descriptive-name}`
- Example: `b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide`

---

## #Phase-2: AI-Studio-Creation

### Step 2.1: Navigate to New Project
- URL: `https://aistudio.google.com/apps?source=start`
- Click "Create new app" or equivalent button
- Select template (or "Blank/Custom" if available)

### Step 2.2: Create Project with Meaningful Name
**Naming**: Use descriptive name (the UUID will be prepended in Step 2.5)
- Example: `ceremonial-participant-guide`
- Be specific about purpose, not generic

### Step 2.3: Attach Supporting Files (CRITICAL)
**Do this BEFORE sending your prompt**:

1. Look for attachment/file icon in AI Studio interface
2. Upload or link all prepared files:
   - RISE specifications
   - Reference documents
   - Design files
3. Verify files are attached (see file names/icons)

### Step 2.4: Send Initial Prompt to Gemini
1. Paste your drafted prompt into main textarea
2. Reference attached files explicitly: "Using the attached [filename], create..."
3. Click Send button
4. **Wait 2 seconds** for processing to start

### Step 2.5: Verify Gemini Started Processing
**CRITICAL**: Must confirm before proceeding.

```javascript
// Check if Gemini is processing
const isProcessing = {
  hasStopButton: !!document.querySelector('[aria-label*="Stop"]'),
  showsThinking: document.body.innerText.includes('Thinking'),
  hasRunning: document.body.innerText.includes('Running for')
};
```

**If processing**:
- Proceed to "Wait for Implementation"

**If NOT processing**:
- Check if request was sent properly
- Retry Step 2.4

### Step 2.6: Wait for Implementation (MINIMUM 90 SECONDS)
**CRITICAL TIMING**: Initial implementations take TIME.

**Timeline**:
- Minimum: 90 seconds
- Typical: 2-5 minutes for complex apps
- Complex: 5-10+ minutes

**Process**:
1. After confirming Gemini started, **sleep 90 seconds**
2. Check if stop button is gone
3. If still processing: wait another 30-60 seconds
4. Repeat until complete

**DO NOT**:
- Interrupt during processing
- Assume done too early
- Send follow-up prompts while processing

**See**: `06-best-practices-antipatterns.md` if timing goes wrong

### Step 2.7: Edit App Name with UUID (IMMEDIATELY after Step 2.6)
**Why**: Enables traceability through observability tools + creates consistent naming

**Process**:
1. Click "Edit name of app" button (pencil/edit icon)
2. Find the name input field
3. **Prepend your UUID**: `{UUID}-{current-name}`
   - Example: `b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide`
4. Save the name change
5. Verify H1 shows UUID-prefixed name

**Automation via Chrome DevTools**:
```javascript
// Find edit button
const editButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Edit name of app'
);
editButton.click();

// Wait 2 seconds then update
const nameInput = document.getElementById('name-input');
const uuid = 'YOUR-SESSION-UUID';
nameInput.value = `${uuid}-${nameInput.value}`;
nameInput.dispatchEvent(new Event('input', { bubbles: true }));
```

---

## #Phase-2b: AI-Features-Integration (Optional)

**When**: If you want to add AI capabilities (voice, chatbots, TTS, etc.)

**How**:
1. Look for "AI Features" button in chat window (sparkle ✨ icon)
2. Review: `03-ai-features-catalog.md` for available options
3. Consider: `05-llm-decision-guide.md` if collaborating with user
4. Send feature-specific prompt with integration requirements
5. Wait for implementation (same 90+ second rule)

**Continue**: To Phase 3 (GitHub Integration) after features are added

---

## #Phase-3: GitHub-Integration

### Step 3.1: Save Changes in AI Studio
1. Click Save button/icon
2. Wait for save confirmation
3. Verify "Unsaved changes" indicator is gone

### Step 3.2: Create New GitHub Repository
**Process**:
1. In AI Studio, click "Save to GitHub" button
2. **Wait 8-10 seconds** for GitHub dialog to fully load
3. Select "Create new repository" option
4. Fill in repository details:
   - **Repository name**: Use UUID-prefixed name (same as app name from Step 2.7)
   - **Description**: Brief explanation of the application
   - **Visibility**: Private (default unless specified otherwise)
5. Click "Create Git repo" button
6. Wait 5-10 seconds for repository creation

**Repository Naming**:
```
{UUID}-{SHORT-DESCRIPTIVE-NAME}
Example: b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide
```

### Step 3.3: Create GitHub Issue for Initial Commit
**Why**: Meaningful commit messages with issue tracking

**Process** (via Chrome DevTools - more reliable):
1. Navigate to: `https://github.com/{owner}/{repo}/issues/new`
2. Wait 3 seconds for page load
3. Fill title input (e.g., "Initial implementation of [feature/app]")
4. Fill body with:
   ```
   Initial implementation created via AI Studio.

   Features implemented:
   - [Feature 1]
   - [Feature 2]

   Technology stack:
   - React
   - TypeScript
   - [Other tech]

   Reference: [Link to RISE spec if applicable]
   ```
5. Click "Create" button
6. **Note the issue number** (e.g., #1)

### Step 3.4: Commit Initial Implementation
Back in AI Studio:

1. Click "Save to GitHub" button (if not already open)
2. **Wait 8-10 seconds** for GitHub panel to fully load
3. Verify you see "Stage and commit all changes" button
4. Fill commit message textarea:
   ```
   Initial implementation #1

   Created [application name] with:
   - [Key feature 1]
   - [Key feature 2]

   🤖 Generated with Claude Code (https://claude.com/claude-code)

   Co-Authored-By: Gemini AI <noreply@google.com>
   ```
5. Click "Stage and commit all changes"
6. **Wait 5 seconds** for commit dialog
7. Click final "Save" or "Commit" button (if present)

**See**: `06-best-practices-antipatterns.md` if dialog not ready

---

## #Phase-4: Deployment

### Step 4.1: Close GitHub Dialog
1. Click close button (X icon)
2. Verify dialog closed

### Step 4.2: Deploy Application
1. Click "Deploy app" button in AI Studio (rocket icon)
2. **Wait 8-10 seconds** for deploy dialog to load
3. Select Google Cloud Project:
   - Click project dropdown
   - Select target project (e.g., "spry-dispatcher")
   - Default to Private unless specified
4. Click "Deploy app" button in dialog
5. **Wait for deployment** (typically 30 seconds to 2 minutes)
6. **Note the deployed URL** when shown

**URL Format**:
```
https://{UUID-prefix}-{truncated-name}-{project-id}.{region}.run.app/
```

### Step 4.3: Verify Deployed Application
1. Click deployed URL or copy to browser
2. Verify application loads correctly
3. Test key features
4. Check console for errors (F12 developer tools)

**If issues**: Check console errors, review deploy logs in AI Studio

---

## #Phase-5: Local-Repository-Setup

### Step 5.1: Clone Repository Locally
**Directory**: Clone to `_protoapp/` alongside other proto apps

```bash
# Navigate to _protoapp directory
cd /a/src/twoeyesseen-thinking-mcp/_protoapp

# Clone repository
git clone git@github.com:[USERNAME]/[UUID-REPOSITORY-NAME].git

# Navigate into repository
cd [UUID-REPOSITORY-NAME]

# Verify files
ls -la

# View initial commit
git log
```

### Step 5.2: Review Generated Code
**Key files to check**:
- `App.tsx` - Main application component
- `package.json` - Dependencies and scripts
- `components/` - Individual UI components
- `types.ts` - TypeScript type definitions
- `README.md` - Documentation

**Review checklist**:
- ✅ Does code match your specification?
- ✅ Are all requested features present?
- ✅ Is code structure logical?
- ✅ Any obvious issues?

### Step 5.3: Create Project Documentation
In repository, create or update `CLAUDE.md`:

```markdown
# [Project Name]

**Created**: [Date]
**AI Studio Edit URL**: [URL from AI Studio]
**Deployed URL**: [Deployment URL]

## Purpose
[Brief description]

## Features
- [Feature 1]
- [Feature 2]

## Technology Stack
- React + TypeScript
- [Other tech]

## Development
\`\`\`bash
npm install
npm run dev
\`\`\`

## Deployment
Deployed via AI Studio to Google Cloud Run.
```

**Commit**:
```bash
git add CLAUDE.md
git commit -m "Add project documentation

Document AI Studio creation process and deployment details.

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

---

## #Phase-6: Iteration-and-Enhancement

### For AI Studio Changes
1. Navigate back to AI Studio edit URL
2. Request change: "Add [feature]" or "Fix [issue]"
3. **Wait 90+ seconds** for implementation
4. Create new GitHub issue (#2, #3, etc.)
5. Commit with issue reference
6. Redeploy
7. Pull changes locally: `git pull`

### For Local Changes
1. Make changes locally
2. Test: `npm run dev`
3. Commit and push:
   ```bash
   git add .
   git commit -m "Your change description #[ISSUE]"
   git push
   ```

---

## #Complete-Workflow-Checklist

- [ ] Phase 1: Specification drafted and files prepared
- [ ] Phase 2: AI Studio project created, prompt sent, 90+ seconds waited
- [ ] Phase 2: Implementation complete, verified via stop button check
- [ ] Phase 2b: AI Features added (if applicable)
- [ ] Phase 2.7: App name edited with UUID prefix
- [ ] Phase 3: GitHub repository created
- [ ] Phase 3: GitHub issue #1 created for initial commit
- [ ] Phase 3: Initial commit sent with issue reference
- [ ] Phase 4: Application deployed successfully
- [ ] Phase 4: Deployed URL noted
- [ ] Phase 5: Repository cloned locally
- [ ] Phase 5: Code reviewed and understood
- [ ] Phase 5: CLAUDE.md created and committed
- [ ] Phase 6: Ready for iterative enhancements

---

## #Common-Issues

**Q: Gemini didn't start processing**
- A: Check request was sent properly, look for Stop button, retry

**Q: Implementation seemed done but I'm not sure**
- A: Check for Stop button. If missing, it's done. If present, wait more.

**Q: GitHub dialog won't open**
- A: Wait 8-10 seconds (dialog load is slow), verify with "Stage and commit" button

**Q: Deployment failed**
- A: Check console errors in F12, review deploy logs, try redeploying

**Q: Can't clone repository**
- A: Verify SSH key configured, try HTTPS if SSH fails, check permissions

---

## #Related-Modules

- `00-START-HERE.md` - Navigation and module overview
- `04-browser-automation-reference.md` - Exact command syntax
- `06-best-practices-antipatterns.md` - Troubleshooting failed steps
- `03-ai-features-catalog.md` - For Phase 2b enhancements

---

**Module Status**: Complete Workflow
**Last Reviewed**: 2025-11-05
