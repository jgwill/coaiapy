# AI Studio Gemini Workflow - Creating NEW Projects from Scratch

**Extension to**: [AI_STUDIO_WORKFLOW.md](./AI_STUDIO_WORKFLOW.md)
**Purpose**: Step-by-step instructions for creating brand new AI Studio projects from scratch
**Last Updated**: 2025-11-03

## Purpose
This document extends the existing AI Studio workflow to cover creating **new projects from scratch** (not just editing existing ones). It provides a complete end-to-end process from initial prompt drafting through GitHub repository creation, issue tracking, local cloning, and deployment.

## Prerequisites
- Google AI Studio account
- GitHub account with authentication
- Local development environment with git
- Understanding of RISE framework specifications (optional but helpful)

---

## Complete Workflow: New Project from Scratch

### Phase 1: Pre-Project Planning

#### Step 1: Draft Your Initial Prompt
**Goal**: Create a clear specification for what you want Gemini to build

**Best Practices**:
- Use RISE specifications if available (Desired Outcome → Current Reality → Natural Progression)
- Be explicit about:
  - Technology stack (e.g., "React + TypeScript + Tailwind CSS")
  - Key features and user flows
  - Visual design principles
  - Data structures needed
- Attach supporting documents/specifications
- Include examples if helpful

**Example Prompt Structure**:
```
Create a [APPLICATION TYPE] using [TECH STACK].

Core Intent:
This application enables users to [DESIRED OUTCOME].

Key Features:
1. [Feature 1 with details]
2. [Feature 2 with details]
3. [Feature 3 with details]

Visual Design:
- [Design principle 1]
- [Design principle 2]

Technical Requirements:
- [Requirement 1]
- [Requirement 2]

[Attach any RISE specs or reference documents]
```

#### Step 2: Prepare Supporting Files
**Goal**: Gather all documents Gemini should reference

**File Types to Consider**:
- RISE specifications (*.spec.md)
- Design mockups or wireframes
- Example applications for reference
- Data schemas or API contracts
- Style guides

**Location**: Have files ready on Google Drive or local for upload

---

### Phase 2: AI Studio Project Creation

#### Step 3: Navigate to AI Studio New Project
**URL**: https://aistudio.google.com/apps?source=start

**What You'll See**:
- "Create new app" button or similar
- Template options (may vary)

#### Step 4: Create New Project
**Actions**:
1. Click "Create new app" or equivalent
2. Select template if offered (or "Blank/Custom")
3. Give project a meaningful name

**Naming Convention**:
```
[PROJECT-PURPOSE]-[DATE-OR-VERSION]
Example: ceremonial-participant-guide-2511
```

#### Step 5: Attach Supporting Files
**CRITICAL**: Do this BEFORE sending initial prompt

**Process**:
1. Look for attachment/file icon in AI Studio interface
2. Upload or link your prepared files:
   - RISE specifications
   - Reference documents
   - Design files
3. Verify files are attached (should see file names/icons)

**Common Issues**:
- Files must be accessible to Gemini (check Google Drive permissions)
- Large files may take time to process
- Some file types may need conversion to text/markdown

#### Step 6: Send Initial Prompt to Gemini
**Process**:
1. Paste your drafted prompt into main textarea
2. Reference attached files explicitly: "Using the attached [filename], create..."
3. Click Send button
4. **Wait 2 seconds** for processing to start
5. **Verify Gemini started** (see thinking indicator or stop button)

**Verification Check**:
```javascript
// Check if Gemini is processing
const isProcessing = {
  hasStopButton: !!document.querySelector('[aria-label*="Stop"]'),
  showsThinking: document.body.innerText.includes('Thinking')
};
```

#### Step 7: Wait for Initial Implementation
**CRITICAL**: Be patient - initial implementations take time. Complex ceremonial or multi-feature apps may take longer than simple projects.

**Timeline Expectations**:
- **Minimum**: 90 seconds (simple prompt)
- **Typical**: 2-5 minutes (normal app with 2-4 features)
- **Complex**: 5-15 minutes (ceremonial apps, AI features, multiple complex components)
- **Very Complex**: May exceed 15 minutes for extensive feature suites

**Completion Verification (Critical Method)**:

To verify implementation is COMPLETE, check for:
1. **Stop button GONE**: Look for button with `aria-label` containing "Stop" - if it exists, still processing
2. **Page text check**: Search for "Running for", "Thinking", or "Thought" text - if found, still processing
3. **Success state**: When BOTH conditions are true:
   - No Stop button present
   - No processing indicators in page text
   - Then: Implementation is COMPLETE ✓

**Process**:
1. After confirming Gemini started, **sleep minimum 90 seconds**
2. Check completion using verification method above
3. If still processing (Stop button visible OR "Running"/"Thinking" in text), wait another 30-60 seconds
4. Re-check completion status
5. Repeat until both conditions show complete

**JavaScript Check to Verify Completion**:
```javascript
(function() {
  const btns = Array.from(document.querySelectorAll('button'));
  const hasStop = btns.some(btn => btn.getAttribute('aria-label')?.includes('Stop'));
  const txt = document.body.innerText;
  const processing = txt.includes('Running for') || txt.includes('Thinking');
  return {hasStop, processing, complete: !hasStop && !processing}
})()
// Result: {hasStop: false, processing: false, complete: true} = DONE
```

**DO NOT**:
- Interrupt or refresh during processing
- Send follow-up prompts while processing
- Assume it's done based on stopping after 90 seconds - VERIFY completion
- Proceed to GitHub operations until complete=true verified

#### Step 8: Edit App Name with UUID Prefix
**CRITICAL**: Must be done IMMEDIATELY after implementation completes, BEFORE any save/GitHub operations

**Why This Matters**:
- Enables traceability through Langfuse observability
- Creates consistent naming across app, repository, and deployed service
- Allows "creative archaeology" to track the complete creation process
- UUID from Claude Code session provides unique identifier

**Process**:
1. **Get UUID**: Use your Claude Code session UUID (e.g., `b40e2a3d-9330-46d4-a52d-50a056d5b46a`)
2. Click "Edit name of app" button (pencil/edit icon near app name)
3. Find the name input field (typically `id="name-input"`)
4. **Prepend UUID to existing name**: `{UUID}-{original-name}`
   - Example: `b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide`
5. Save the name change
6. **Verify**: Check that H1 element shows the UUID-prefixed name

**Common Mistake**:
❌ **DO NOT** click "Make new copy" or "Save" before editing the name
✅ **DO** edit the name first, then proceed with GitHub operations

**Automation via Chrome DevTools**:
```javascript
// Find edit button
const editButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Edit name of app'
);
editButton.click();

// Wait 2 seconds, then update name
const nameInput = document.getElementById('name-input');
const uuid = 'b40e2a3d-9330-46d4-a52d-50a056d5b46a'; // Your session UUID
nameInput.value = `${uuid}-${nameInput.value}`;
nameInput.dispatchEvent(new Event('input', { bubbles: true }));
// Click save button
```

---

### Phase 3: GitHub Integration

#### Step 9: Save Initial Implementation (After UUID Naming)
**Actions**:
1. Click the Save icon/button in AI Studio
2. Wait for save confirmation
3. Verify "Unsaved changes" indicator is gone

#### Step 10: Create GitHub Repository
**IMPORTANT**: Must create NEW repo for new project

**Process**:
1. In AI Studio, click "Save to GitHub" button
2. **Dialog will open** (wait 8-10 seconds for full load)
3. Look for "Create new repository" option (or "Create Git repo" button)
4. Fill in repository details:
   - **Repository name**: Use UUID-prefixed name (e.g., `b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide`)
   - **Description**: Brief explanation of the application
   - **Visibility**: **Private** (default unless specified otherwise)
5. Click "Create Git repo" or equivalent button
6. Wait 5-10 seconds for repository creation

**Repository Naming Convention**:
```
{UUID}-{SHORT-DESCRIPTIVE-NAME}
Example: b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide
```

**Note**: The UUID prefix must match the app name from Step 8.

#### Step 11: Create GitHub Issue for First Commit
**WHY**: Meaningful commit messages with issue references

**RECOMMENDED METHOD**: Use GitHub URL directly via Chrome DevTools
- **More Reliable**: Works independently of GitHub MCP availability
- **Better Control**: Direct interaction with GitHub interface
- **Always Available**: Not dependent on MCP server status

**Process via Chrome DevTools**:
1. Navigate to issues page: `https://github.com/{owner}/{repo}/issues/new`
2. Wait 3 seconds for page to load
3. Fill title input field (e.g., `id=":r1:"`)
4. Fill body textarea (e.g., `id=":r8:"`)
5. Click "Create" button (text includes "control" keyboard shortcut)
6. Verify issue created (URL changes to `/issues/1`)

**Alternative Process (Manual)**:
1. Open GitHub repository in browser
2. Click "Issues" tab
3. Click "New Issue" button
4. Create issue:
   - **Title**: "Initial implementation of [feature/app]"
   - **Body**:
     ```
     Initial implementation created via AI Studio.

     Features implemented:
     - [Feature 1]
     - [Feature 2]
     - [Feature 3]

     Technology stack:
     - [Tech 1]
     - [Tech 2]

     Reference: [Link to RISE spec or design doc if applicable]
     ```
6. Create issue and **note the issue number** (e.g., #1)

#### Step 12: Commit Initial Implementation
**Back in AI Studio**:

1. Navigate back to AI Studio edit URL
2. Click "Save to GitHub" button (if not already open)
3. **Wait 8-10 seconds** for GitHub panel to fully load
4. Verify you see "Stage and commit all changes" button
5. Fill commit message textarea:
   ```
   Initial implementation #[ISSUE-NUMBER]

   Created [application name] with:
   - [Key feature 1]
   - [Key feature 2]
   - [Key feature 3]

   🤖 Generated with Claude Code (https://claude.com/claude-code)

   Co-Authored-By: Gemini AI <noreply@google.com>
   ```
5. Click "Stage and commit all changes"
6. **Wait 5 seconds** for commit dialog
7. Click final "Save" or "Commit" button (if present)
8. Wait for confirmation

**Common Issues**:
- Dialog not ready: Wait longer (8-10 seconds)
- Commit fails: Check GitHub permissions
- No "Stage" button: Refresh and try again

---

### Phase 4: Deployment

#### Step 13: Deploy Application
**Process**:
1. Close GitHub dialog (if still open)
2. Click "Deploy app" button in AI Studio (rocket icon)
3. **Wait 8-10 seconds** for deploy dialog to load
4. Select Google Cloud Project:
   - Click project dropdown
   - Select target project (e.g., "spry-dispatcher")
   - **Default to Private** unless specified otherwise
5. Click "Deploy app" button in dialog
6. **Wait for deployment** (typically 30 seconds to 2 minutes)
7. Note the deployed URL when shown

**Deployment URL Format**:
```
https://{UUID-prefix}-{truncated-name}-{project-id}.{region}.run.app/
Example: https://b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-p-947142232746.us-west1.run.app
```

**Save this URL** to session tracking file

#### Step 14: Verify Deployment
**Process**:
1. Click deployed URL or copy to browser
2. Verify application loads correctly
3. Test key features
4. Check console for errors (F12 developer tools)

**If Issues**:
- Check console errors
- Review deploy logs in AI Studio
- May need to redeploy after fixes

---

### Phase 5: Local Repository Setup

#### Step 15: Clone Repository Locally
**WHY**: Observe code, make local changes, understand implementation

**RECOMMENDED**: Clone to `_protoapp/` directory alongside other proto apps

**Process**:
```bash
# Navigate to _protoapp directory
cd /a/src/twoeyesseen-thinking-mcp/_protoapp

# Clone using git protocol (not https)
git clone git@github.com:[USERNAME]/[UUID-REPOSITORY-NAME].git

# Navigate into repository
cd [UUID-REPOSITORY-NAME]

# Verify files
ls -la

# Check git status
git status

# View initial commit
git log

# View files
cat README.md
cat package.json
```

**Example**:
```bash
cd /a/src/twoeyesseen-thinking-mcp/_protoapp
git clone git@github.com:miadisabelle/b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide.git
cd b40e2a3d-9330-46d4-a52d-50a056d5b46a-ceremonial-participant-guide
ls -la
```

**What to Verify**:
- All files present (check App.tsx, package.json, etc.)
- Git history shows initial commit with your issue reference (#1)
- Components directory structure matches specification

#### Step 16: Review Generated Code
**Goal**: Understand what Gemini created

**Key Files to Review**:
- `App.tsx` - Main application component
- `package.json` - Dependencies and scripts
- `components/` - Individual UI components
- `data.ts` or `constants.ts` - Data structures
- `types.ts` - TypeScript type definitions
- `README.md` - Documentation

**Review Checklist**:
- ✅ Does code match your specification?
- ✅ Are all requested features present?
- ✅ Is code structure logical and maintainable?
- ✅ Are there any obvious issues or bugs?
- ✅ Does visual design match requirements?

#### Step 17: Document Project Details
**CRITICAL**: Create comprehensive documentation for future sessions

**In Repository, Create `CLAUDE.md`**:
```markdown
# [Project Name]

**Created**: [Date]
**AI Studio Edit URL**: [URL from AI Studio]
**Deployed URL**: [Deployment URL]
**GitHub Issues**: [Link to issues tab]

## Purpose
[Brief description of what this application does]

## Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Technology Stack
- [Tech 1]
- [Tech 2]
- [Tech 3]

## Development Process
Created via AI Studio using:
- Initial prompt: [Link to spec or paste summary]
- Supporting files: [List attached files]
- GitHub Issue #[NUMBER]: [Issue title]

## Local Development
\`\`\`bash
npm install
npm run dev
\`\`\`

## Deployment
Deployed via AI Studio to Google Cloud Run.
Redeploy via AI Studio interface.

## Related Projects
- [Link to related proto apps or specs]

## Notes
[Any important notes about implementation, future enhancements, or known issues]
```

**Commit Documentation**:
```bash
# In your local repository
git add CLAUDE.md
git commit -m "Add project documentation

Document AI Studio creation process, deployment details, and local development instructions.

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

---

### Phase 6: Iteration and Enhancement

#### Step 17: Making Changes via AI Studio
**Process** (refer to main AI_STUDIO_WORKFLOW.md):
1. Navigate back to AI Studio edit URL
2. Request changes: "Add [feature]" or "Fix [issue]"
3. Wait for implementation (90+ seconds)
4. Save changes
5. Create new GitHub issue for the change (#2, #3, etc.)
6. Commit with issue reference
7. Redeploy
8. Pull changes locally: `git pull`

#### Step 18: Making Local Changes
**When to Edit Locally**:
- Small tweaks or fixes
- Detailed code review and refactoring
- Testing and debugging
- Configuration changes

**Process**:
```bash
# Make your changes locally
# Test them: npm run dev

# Commit and push
git add .
git commit -m "Your change description #[ISSUE]"
git push

# Changes are now in GitHub
# Deploy via AI Studio if needed
```

---

## Complete Workflow Summary

**Full sequence for new project**:

1. ✅ Draft initial prompt with clear specification
2. ✅ Prepare and organize supporting files
3. ✅ Navigate to AI Studio new project page
4. ✅ Create new AI Studio app
5. ✅ Attach supporting files BEFORE sending prompt
6. ✅ Send initial prompt to Gemini
7. ✅ Verify Gemini started processing
8. ✅ **Sleep 90+ seconds** - wait for implementation
9. ✅ Verify implementation complete
10. ✅ Save implementation in AI Studio
11. ✅ Create new GitHub repository via AI Studio
12. ✅ Create GitHub issue for initial implementation
13. ✅ Commit to GitHub with issue reference
14. ✅ Deploy application via AI Studio
15. ✅ Verify deployed application works
16. ✅ Clone repository locally
17. ✅ Review generated code
18. ✅ Create CLAUDE.md documentation
19. ✅ Commit documentation
20. ✅ Iterate with changes as needed

---

## Key Differences from Editing Existing Projects

| Aspect | Existing Project | New Project |
|--------|------------------|-------------|
| **Starting Point** | AI Studio edit URL | AI Studio new project page |
| **GitHub Setup** | Repository exists | Must create new repository |
| **Issues** | Ongoing issue tracking | Create first issue for initial commit |
| **Local Clone** | Already cloned | Must clone after creation |
| **Documentation** | May exist | Must create CLAUDE.md |
| **Deployment** | Redeploy existing | Initial deploy |

---

## Common Mistakes and Solutions

### Mistake 1: Sending Prompt Before Attaching Files
**Problem**: Gemini doesn't have context from specs
**Solution**: Always attach files FIRST, then send prompt referencing them

### Mistake 2: Not Creating GitHub Issue First
**Problem**: Meaningless commit messages, hard to track
**Solution**: Create issue before committing, reference in commit message

### Mistake 3: Not Waiting Long Enough for Implementation
**Problem**: Think it failed when it's still processing
**Solution**: Wait minimum 90 seconds, check for stop button

### Mistake 4: Skipping Local Clone
**Problem**: Can't review code, understand implementation
**Solution**: Always clone locally and review generated code

### Mistake 5: Not Documenting AI Studio URLs
**Problem**: Can't find edit URL later to make changes
**Solution**: Create CLAUDE.md with all URLs immediately

---

## Testing This Workflow: Ceremonial Participant Guide

**Proposed Test**:
Use the newly created proto-app-3 specification to test this workflow.

**Materials Ready**:
- `/a/src/twoeyesseen-thinking-mcp/_protoapp/rispecs/proto-app-3-ceremonial-participant-guide.spec.md` (main prompt)
- `/src/IAIP/rispecs/ceremonial-technology.spec.md` (attach)
- `/src/IAIP/rispecs/four-directions.spec.md` (attach)
- `/src/IAIP/rispecs/relational-science.spec.md` (attach)

**Expected Result**:
- New AI Studio project created
- React TypeScript app implementing the specification
- GitHub repository: `ceremonial-participant-guide`
- Deployed application accessible via URL
- Local clone in `/a/src/ceremonial-participant-guide`
- Documentation in CLAUDE.md

---

## Success Criteria

A new project creation is successful when:

1. ✅ Specification correctly interpreted by Gemini
2. ✅ Application implements all requested features
3. ✅ GitHub repository created with meaningful name
4. ✅ Initial commit references GitHub issue
5. ✅ Application successfully deployed
6. ✅ Deployed URL works and displays correctly
7. ✅ Repository cloned locally
8. ✅ Code reviewed and understood
9. ✅ CLAUDE.md documentation complete
10. ✅ Can iterate with further changes

---

## Related Documentation

- [AI_STUDIO_WORKFLOW.md](./AI_STUDIO_WORKFLOW.md) - Editing existing projects
- [llms-rise-framework.txt](./llms-rise-framework.txt) - Creating specifications
- `/a/src/twoeyesseen-thinking-mcp/_protoapp/CLAUDE.md` - Example of two existing projects

---

**Document Status**: Active - Workflow Extension
**Created**: November 3, 2025
**Purpose**: Enable autonomous creation of new AI Studio projects from scratch
**Next Steps**: Test workflow with Proto App 3 creation
