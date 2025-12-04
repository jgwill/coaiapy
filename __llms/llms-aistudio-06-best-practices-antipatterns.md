# AI Studio Best Practices & Anti-Patterns: Troubleshooting Guide

> Consolidated best practices, common mistakes with solutions, debugging strategies, success criteria, and code snippets for AI Studio workflows.

**Module**: 06-best-practices-antipatterns.md
**Related to**: 01-workflow-new-project.md, 02-workflow-existing-project.md, 04-browser-automation-reference.md
**Version**: 1.0
**Last Updated**: 2025-11-05

---

## #Critical-Learnings-Library

These learnings prevent 80% of workflow failures.

### Learning 1: Timing is Everything
**Principle**: Always wait the full time. Never check early.

**Why**: Gemini implementation takes time, dialogs render slowly. Checking too early causes false "failures."

**Pattern**:
- Gemini implementation: **Sleep 90 seconds BEFORE checking**
- Dialog load: **Sleep 8-10 seconds BEFORE interacting**
- GitHub commit: **Sleep 5 seconds BEFORE verifying**

**Violation Example** (❌ Don't do this):
```javascript
// WRONG: Check after only 10 seconds
setTimeout(() => {
  const stopBtn = document.querySelector('[aria-label*="Stop"]');
  if (!stopBtn) console.log("Done!");
}, 10000);
```

**Correct Example** (✅ Do this):
```bash
# Sleep full time
sleep 90
```

Then check:
```javascript
const stopBtn = document.querySelector('[aria-label*="Stop"]');
return stopBtn ? 'Still processing' : 'Complete';
```

---

### Learning 2: Dialog State Management
**Principle**: Dialogs have three states; always verify before interaction.

**States**:
1. **Closed**: No dialog visible
2. **Opening**: Dialog exists but not interactive (7-10s rendering)
3. **Open**: Dialog ready for interaction

**Violation Example** (❌ Don't do this):
```javascript
// WRONG: Click button before dialog loads
const githubBtn = document.querySelector('[aria-label="Save to GitHub"]');
githubBtn.click();
// Immediately try to fill message - fails because dialog not ready yet
const commitInput = document.querySelector('textarea');
commitInput.value = "message";
```

**Correct Example** (✅ Do this):
```javascript
// Click to open
const githubBtn = document.querySelector('[aria-label="Save to GitHub"]');
githubBtn.click();
```

```bash
# Wait for dialog to render
sleep 8
```

Then verify and interact:
```javascript
// Verify dialog ready
const stageBtn = document.querySelector('button:has-text("Stage and commit")');
if (!stageBtn) return 'Dialog not ready - wait more';

// Now safe to fill
const commitInput = document.querySelector('textarea');
commitInput.value = "message";
```

---

### Learning 3: Input Field Context Awareness
**Principle**: Multiple input fields exist on different pages; know which one you're filling.

**Contexts**:
- Main prompt textarea (for sending to Gemini)
- GitHub commit message textarea (in dialog)
- App name input (in edit dialog)
- Search/navigation input

**Violation Example** (❌ Don't do this):
```javascript
// WRONG: Not context-aware
const input = document.querySelector('textarea');
input.value = "commit message"; // Might fill wrong textarea!
```

**Correct Example** (✅ Do this):
```javascript
// Verify which dialog is open FIRST
const stageCommitBtn = document.querySelector('button:has-text("Stage and commit")');
if (stageCommitBtn) {
  // We're in GitHub dialog - safe to fill
  const commitInput = document.querySelector('textarea');
  commitInput.value = "commit message";
} else {
  return 'ERROR: GitHub dialog not open';
}
```

---

### Learning 4: UUID Naming for Traceability
**Principle**: Always prepend session UUID to app name immediately after creation.

**Why**: Enables finding all artifacts from one session (app, repo, deploy URL, specs)

**Critical Timing**: Do this IMMEDIATELY after implementation completes, BEFORE GitHub operations.

**Violation Example** (❌ Don't do this):
```javascript
// WRONG: Forget UUID step, go straight to GitHub
// Later, you lose traceability between app, repo, and deployment
```

**Correct Example** (✅ Do this):
```javascript
// Step 1: Implementation complete
// Step 2: Edit app name with UUID (IMMEDIATELY)
const editBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Edit name of app'
);
editBtn.click();

// Wait then update
const nameInput = document.getElementById('name-input');
const uuid = 'b40e2a3d-9330-46d4-a52d-50a056d5b46a';
nameInput.value = `${uuid}-${nameInput.value}`;

// Step 3: Now proceed with GitHub (with traceability in place)
```

---

### Learning 5: GitHub Dialog Readiness Verification
**Principle**: GitHub dialogs take 8-10 seconds to fully load AND display the right button.

**What to verify**:
- Dialog is visible
- "Stage and commit all changes" button exists
- Textarea is ready for input

**Violation Example** (❌ Don't do this):
```javascript
// WRONG: Check too early
githubBtn.click();
sleep 2; // Too short!
const commitInput = document.querySelector('textarea');
commitInput.value = "message"; // Fills wrong element or doesn't work
```

**Correct Example** (✅ Do this):
```javascript
githubBtn.click();
sleep 8; // Full wait

// Verify specific button from GitHub dialog
const stageBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);

if (!stageBtn) {
  return 'GitHub dialog not ready - wait more';
}

// Now safe to fill
const commitInput = document.querySelector('textarea');
commitInput.value = "message";
```

---

### Learning 6: Closing Previous Dialogs
**Principle**: Always close previous dialog before opening new one.

**Why**: Overlapping dialogs cause state confusion and element selection issues.

**Violation Example** (❌ Don't do this):
```javascript
// GitHub dialog is still open
// Try to open Deploy dialog
const deployBtn = document.querySelector('[aria-label="Deploy app"]');
deployBtn.click(); // This might click the wrong button or nothing
```

**Correct Example** (✅ Do this):
```javascript
// Step 1: Close GitHub dialog
const closeBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'close'
);
closeBtn.click();

sleep 2; // Wait for dialog to close

// Step 2: Now open Deploy dialog
const deployBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Deploy app'
);
deployBtn.click();
```

---

### Learning 7: Save Changes Before Dialogs
**Principle**: Always click Save button before opening GitHub/Deploy dialogs.

**Why**: Changes need to be persisted before committing/deploying.

**Violation Example** (❌ Don't do this):
```javascript
// Changes not saved
const githubBtn = document.querySelector('[aria-label="Save to GitHub"]');
githubBtn.click(); // Nothing to commit - fails
```

**Correct Example** (✅ Do this):
```javascript
// Step 1: Save changes
const saveBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'save'
);
if (saveBtn) saveBtn.click();

sleep 2; // Wait for save

// Step 2: Now open GitHub dialog
const githubBtn = document.querySelector('[aria-label="Save to GitHub"]');
githubBtn.click();
```

---

### Learning 8: Gemini Stopping = Completion
**Principle**: When Stop button disappears, Gemini is done (not while button present).

**Check Pattern**:
```javascript
const stopButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);

if (stopButton) {
  return 'Still processing';
} else {
  return 'Complete';
}
```

**Remember**: Stop button may briefly reappear if Gemini refines output. Wait for final disappearance.

---

## #Anti-Patterns-With-Solutions

### Anti-Pattern 1: Using setTimeout for Waiting
**Problem**: JavaScript execution is synchronous per tool call. setTimeout schedules but returns immediately.

❌ **WRONG**:
```javascript
setTimeout(() => {
  check_something();
}, 90000);
// Execution continues - doesn't actually wait!
```

✅ **RIGHT**:
```bash
sleep 90
```

Then in separate tool call:
```javascript
check_something();
```

---

### Anti-Pattern 2: Filling Inputs Before Dialogs Open
**Problem**: Input not yet rendered, value fill fails.

❌ **WRONG**:
```javascript
githubBtn.click();
const input = document.querySelector('textarea');
input.value = "text"; // Input doesn't exist yet!
```

✅ **RIGHT**:
```javascript
githubBtn.click();
```

```bash
sleep 8
```

Then:
```javascript
const input = document.querySelector('textarea');
input.value = "text"; // Input now exists
```

---

### Anti-Pattern 3: Confusing Main Input with Dialog Input
**Problem**: Multiple textareas exist; filling wrong one.

❌ **WRONG**:
```javascript
// Could be any textarea
const input = document.querySelector('textarea');
input.value = "commit message";
// But might fill Gemini prompt input instead!
```

✅ **RIGHT**:
```javascript
// Verify dialog open first
const stageBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);
if (!stageBtn) return 'GitHub dialog not open';

// Now safe to fill
const input = document.querySelector('textarea');
input.value = "commit message";
```

---

### Anti-Pattern 4: Not Verifying Completion
**Problem**: Assuming Gemini is done without checking Stop button.

❌ **WRONG**:
```bash
sleep 90
# Assume done, proceed to save
save_button.click();
# But implementation still running - saves incomplete code!
```

✅ **RIGHT**:
```bash
sleep 90
```

```javascript
const stopBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);

if (stopBtn) {
  return 'Still processing - wait more';
}
// Only proceed if truly complete
```

---

### Anti-Pattern 5: Skipping UUID Naming
**Problem**: Lose traceability between app, repo, deploy URL.

❌ **WRONG**:
```javascript
// Implementation done, skip straight to GitHub
// Later: can't find which app created which repo/deployment
```

✅ **RIGHT**:
```javascript
// Implementation done → immediately edit name with UUID
// Then GitHub → with UUID in repo name
// Then Deploy → UUID is in deployment URL
// Traceability: app UUID → repo UUID → deployment URL UUID
```

---

### Anti-Pattern 6: Not Closing Previous Dialogs
**Problem**: Multiple dialogs open, selectors find wrong buttons.

❌ **WRONG**:
```javascript
// GitHub dialog open
const deployBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Deploy app'
);
deployBtn.click(); // Might click wrong button in overlapping dialogs
```

✅ **RIGHT**:
```javascript
// Close GitHub first
const closeBtn = document.querySelector('[aria-label*="close"]');
closeBtn.click();

sleep 2;

// Now open Deploy
const deployBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Deploy app'
);
deployBtn.click();
```

---

### Anti-Pattern 7: Not Handling API Errors
**Problem**: API call fails, assume success, proceed incorrectly.

❌ **WRONG**:
```javascript
// Send request, assume success
input.value = "prompt";
sendBtn.click();
// No error checking - might fail silently
```

✅ **RIGHT**:
```javascript
const input = document.querySelector('textarea');
const sendBtn = document.querySelector('button:has-text("Send")');

if (!input || !sendBtn) {
  return 'ERROR: Could not find input or send button';
}

input.value = "prompt";
sendBtn.click();

sleep 2;

// Verify it actually sent
const hasStopBtn = !!document.querySelector('[aria-label*="Stop"]');
if (!hasStopBtn) {
  return 'ERROR: Gemini did not start processing';
}
```

---

### Anti-Pattern 8: Poor Commit Messages
**Problem**: Meaningless commit messages make history useless.

❌ **WRONG**:
```
Commit message: "Update"
No issue reference
No description
```

✅ **RIGHT**:
```
Add voice interface and TTS for accessibility #5

- Implemented Gemini Live API for voice conversation
- Added text-to-speech to all major content sections
- Includes floating widget for feature access

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Gemini AI <noreply@google.com>
```

---

### Anti-Pattern 9: Skipping Local Code Review
**Problem**: Deploy untested, problematic code.

❌ **WRONG**:
```bash
# Create repo, commit, deploy - done!
# No verification of generated code
```

✅ **RIGHT**:
```bash
# Clone locally
git clone ...

# Review key files
cat App.tsx
cat package.json
ls components/

# Spot-check for issues:
# - Does code match specification?
# - Are all features present?
# - Any obvious bugs?

# Only then proceed with deployment confidence
```

---

### Anti-Pattern 10: Not Documenting Deployments
**Problem**: Later can't remember URLs, process, or decisions.

❌ **WRONG**:
```
No CLAUDE.md
No notes
URLs scattered
```

✅ **RIGHT**:
```markdown
# [Project Name]

**Created**: 2025-11-05
**AI Studio Edit URL**: https://aistudio.google.com/apps/drive/...
**Deployed URL**: https://[uuid]-[name]-[project].us-west1.run.app
**GitHub Issues**: [link]

## Key Commands
npm install
npm run dev

## Features Implemented
- [Feature 1]
- [Feature 2]
```

---

## #Success-Criteria-Checklists

### New Project Completion Checklist

**Project Created**:
- [ ] AI Studio project created with descriptive name
- [ ] Initial prompt sent to Gemini
- [ ] Waited 90+ seconds for implementation
- [ ] Verified Stop button disappeared (implementation complete)
- [ ] App name edited with UUID prefix
- [ ] Changes saved in AI Studio

**GitHub Integration**:
- [ ] New GitHub repository created (with UUID-prefixed name)
- [ ] GitHub issue #1 created for initial implementation
- [ ] Changes committed with issue reference
- [ ] No error messages during commit

**Deployment**:
- [ ] Application deployed to Google Cloud Run
- [ ] Deployed URL obtained and saved
- [ ] Application loads in browser without errors
- [ ] Key features visible and testable

**Local Setup**:
- [ ] Repository cloned locally to `_protoapp/` directory
- [ ] All files present and readable
- [ ] `git log` shows initial commit with issue reference
- [ ] Code reviewed (App.tsx, package.json, components)

**Documentation**:
- [ ] `CLAUDE.md` created with URLs and development instructions
- [ ] Documentation committed to repository
- [ ] `git push` successful

**Ready for Enhancement**:
- [ ] Can navigate back to AI Studio edit URL
- [ ] Can send enhancement requests to Gemini
- [ ] Can commit new changes to GitHub
- [ ] Can iterate on features

---

### Enhancement Completion Checklist

**Request Sent**:
- [ ] Navigated to AI Studio edit URL
- [ ] Described enhancement clearly
- [ ] Clicked Send button
- [ ] Verified Gemini started (Stop button appeared)

**Implementation**:
- [ ] Waited 90+ seconds for processing
- [ ] Verified Stop button disappeared (complete)
- [ ] Reviewed implementation quality
- [ ] Changes look correct and complete

**Committed**:
- [ ] Created GitHub issue (#2, #3, etc.)
- [ ] Saved changes in AI Studio
- [ ] Opened GitHub commit dialog
- [ ] Waited 8-10 seconds for dialog ready
- [ ] Verified "Stage and commit" button visible
- [ ] Filled commit message with issue reference
- [ ] Clicked "Stage and commit all changes"
- [ ] No error messages

**Deployed**:
- [ ] Closed GitHub dialog
- [ ] Opened Deploy dialog
- [ ] Waited 8-10 seconds for dialog ready
- [ ] Clicked "Redeploy"
- [ ] Deployment completed (URL shown)

**Verified**:
- [ ] Pulled changes locally (`git pull`)
- [ ] Visited deployed URL
- [ ] New feature/fix visible and working
- [ ] No console errors (F12)
- [ ] Related features still work

---

### AI Features Implementation Checklist

**Feature Selected**:
- [ ] Identified appropriate AI Feature from catalog
- [ ] User confirmed feature choice
- [ ] Understood integration requirements

**Prompt Crafted**:
- [ ] Detailed description of desired feature
- [ ] Clear integration points (where in app)
- [ ] User interaction flow specified
- [ ] Any domain-specific requirements included

**Implemented**:
- [ ] Sent feature request to Gemini
- [ ] Waited 90+ seconds for implementation
- [ ] Verified implementation complete
- [ ] Reviewed implementation quality

**Deployed**:
- [ ] Committed with issue reference
- [ ] Redeployed application
- [ ] Feature visible and functional
- [ ] No integration issues with existing features

---

## #Debugging-Procedures

### When Gemini Doesn't Start
**Symptom**: No Stop button appears, no "Running for" message

**Diagnosis**:
1. Check request was typed correctly
2. Verify Send button was clicked
3. Check for error messages on page

**Fix**:
```javascript
// Check what's displayed
document.body.innerText.substring(0, 1000)

// Look for error
document.body.innerText.includes('error')

// Try sending again
const input = document.querySelector('textarea');
input.value = "YOUR PROMPT";
input.dispatchEvent(new Event('input', { bubbles: true }));
const sendBtn = document.querySelector('button:has-text("Send")');
sendBtn.click();
```

---

### When Implementation Seems Stuck
**Symptom**: Stop button still present after 2+ minutes

**Diagnosis**:
1. Check browser console for errors (F12)
2. Check if page is responsive
3. Check AI Studio status page

**Fix**:
```javascript
// Verify page is responsive
document.body.innerText !== "" ? 'Page has content' : 'Page blank'

// Check for error indicators
document.querySelectorAll('[role="alert"]').length

// Wait longer - some complex implementations take 5-10 minutes
```

If truly stuck, manually refresh page and retry.

---

### When Dialog Won't Open
**Symptom**: Click button, dialog doesn't appear

**Diagnosis**:
1. Verify button was actually clicked
2. Check if wait time was long enough (8-10 seconds)
3. Look for overlay/dialog in DOM

**Fix**:
```javascript
// Verify button exists
const btn = document.querySelector('[aria-label="Save to GitHub"]');
btn ? 'Button found' : 'Button not found'

// Verify dialog exists after wait
document.querySelectorAll('[role="dialog"]').length

// Try clicking again with scroll
const btn = document.querySelector('[aria-label="Save to GitHub"]');
btn.scrollIntoView();
btn.click();
```

---

### When Input Value Won't Update
**Symptom**: Set input.value but text doesn't appear

**Diagnosis**:
1. Verify you're updating the right input
2. Check if input is contenteditable vs. regular input
3. Verify events are dispatched

**Fix**:
```javascript
// Try multiple event types
const input = document.querySelector('textarea');
input.value = "new text";
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
input.dispatchEvent(new KeyboardEvent('keyup', { key: 'a' }));
```

---

### When Commit Fails
**Symptom**: Error message in GitHub dialog, commit doesn't go through

**Diagnosis**:
1. Check GitHub credentials/permissions
2. Verify repository exists and is accessible
3. Check for unstageable changes

**Fix**:
```javascript
// Check for error message
document.body.innerText.includes('error') ||
document.body.innerText.includes('Error')

// Try clicking "Stage and commit" again
const stageBtn = document.querySelector('button:has-text("Stage and commit")');
stageBtn?.click();
```

If persistent: manually commit via terminal:
```bash
git add .
git commit -m "Your message #issue-number"
git push
```

---

### When Deployment Fails
**Symptom**: Deploy dialog shows error, deployment doesn't complete

**Diagnosis**:
1. Check Google Cloud project permissions
2. Verify project has deployment quota
3. Check browser console for API errors

**Fix**:
```javascript
// Check error message
document.body.innerText.includes('Error')

// Try redeploying
const redeployBtn = document.querySelector('button:has-text("Redeploy")');
redeployBtn?.click();
```

If persistent: Check AI Studio deploy logs, project permissions, or quota.

---

## #Code-Snippet-Library

Organized by function.

### Finding Elements
```javascript
// Button by text
Array.from(document.querySelectorAll('button')).find(b =>
  b.textContent.includes('TEXT')
)

// Button by aria label
Array.from(document.querySelectorAll('button')).find(b =>
  b.getAttribute('aria-label')?.includes('LABEL')
)

// Input by ID
document.getElementById('name-input')

// All textareas
document.querySelectorAll('textarea')

// Dialog
document.querySelector('[role="dialog"]')
```

### Verifying State
```javascript
// Processing check
!!document.querySelector('[aria-label*="Stop"]')

// Dialog open check
document.querySelectorAll('[role="dialog"]').length > 0

// Page text
document.body.innerText.substring(0, 2000)

// Error check
document.body.innerText.includes('error')
```

### Interaction Patterns
```javascript
// Click
element.click()

// Fill input
input.value = "text"
input.dispatchEvent(new Event('input', { bubbles: true }))

// Scroll into view
element.scrollIntoView({ block: 'center' })

// Get text
element.textContent
```

---

## #Related-Modules

- `01-workflow-new-project.md` - Use this when things fail
- `02-workflow-existing-project.md` - Use this when things fail
- `04-browser-automation-reference.md` - Exact command syntax

---

**Module Status**: Complete Best Practices & Troubleshooting
**Last Reviewed**: 2025-11-05
