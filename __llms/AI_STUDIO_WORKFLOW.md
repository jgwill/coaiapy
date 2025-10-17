# AI Studio Gemini Workflow - Autonomous Execution Guide

## Purpose
This document provides step-by-step instructions for autonomously executing development workflows in Google AI Studio with Gemini, including code changes, GitHub commits, and deployments.

## Critical Learnings

### 1. Wait for Completion Properly
**PROBLEM**: Using `setTimeout()` in JavaScript execution doesn't actually wait - it schedules but returns immediately.

**SOLUTION**:
- Check for completion indicators (stop button disappearing)
- If still processing, wait and check again in next tool call
- Don't proceed to next step until confirmed complete

### 2. Dialog State Management
**PROBLEM**: Multiple dialogs can overlap (GitHub commit dialog, deployment dialog, etc.)

**SOLUTION**:
- Always close previous dialogs before opening new ones
- Check current page state before proceeding
- Verify which dialog is actually open

### 3. Input Field Context
**PROBLEM**: There are multiple input fields on the page:
- Main prompt textarea (for sending requests to Gemini)
- GitHub commit message input (in commit dialog)
- These can be confused

**SOLUTION**:
- When committing to GitHub: Only fill commit message when the GitHub dialog is open
- Verify dialog context before filling inputs
- Check for specific dialog markers (like "Stage and commit all changes" button)

## Standard Workflow Steps

### Step 1: Navigate to AI Studio
```javascript
// Start Chrome and connect
mcp__chrome-devtools__start_chrome_and_connect(url, kwargs)
```

### Step 2: Send Request to Gemini
```javascript
// Find the main textarea input (NOT in a dialog)
const input = document.querySelector('textarea') || document.querySelector('[contenteditable="true"]');
input.value = "YOUR REQUEST HERE";
input.dispatchEvent(new Event('input', { bubbles: true }));

// Click send button
const sendButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Send')
);
sendButton.click();
```

### Step 2b: Verify Request Was Sent and Gemini Started Processing
**CRITICAL**: Must verify Gemini actually started before waiting 90 seconds.

```bash
# Wait 2 seconds for processing indicator to appear
sleep 2
```

```javascript
// Check if Gemini started processing by looking for indicators
const processingCheck = {
  hasStopButton: !!Array.from(document.querySelectorAll('button')).find(btn =>
    btn.getAttribute('aria-label')?.includes('Stop')
  ),
  isRunning: document.body.innerText.includes('Running for'),
  isThinking: document.body.innerText.includes('Thinking') || document.body.innerText.includes('Thought for')
};

if (processingCheck.hasStopButton || processingCheck.isRunning || processingCheck.isThinking) {
  return 'Gemini is processing - proceed to wait';
} else {
  return 'ERROR: Gemini did not start - check if request was sent properly';
}
```

### Step 3: Wait for Gemini to Complete
**CRITICAL**: Implementation can take MINUTES, not seconds. Must wait and verify.

```bash
# After confirming Gemini started, wait minimum 90 seconds before checking completion
sleep 90
```

```javascript
// Then check if processing is complete
const stopButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);

if (stopButton) {
  // Still processing - wait more and check again
  return 'Still processing - wait longer';
} else {
  // Complete - proceed to next step
  return 'Implementation completed';
}
```

**Implementation Pattern**:
1. Send request to Gemini
2. **IMMEDIATELY sleep 90 seconds** - don't check yet
3. After sleep, check for stop button
4. If still processing, wait another 30-60 seconds and check again
5. Implementation typically takes 45-120 seconds
6. Only proceed when stop button is definitively gone

**Common Mistake**: Checking too early or assuming completion. Always wait minimum 90 seconds first, then verify.

### Step 4: Commit to GitHub
**CRITICAL**: Must be done in correct sequence

#### 4a. Save Changes First
**IMPORTANT**: Always save changes before opening GitHub dialog

```javascript
const saveButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'save' ||
  btn.getAttribute('aria-label')?.includes('Save')
);

if (saveButton) {
  saveButton.click();
}
```

#### 4b. Close Any Open Dialogs
```javascript
const closeBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Close') ||
  btn.getAttribute('iconname') === 'close'
);
if (closeBtn) closeBtn.click();
```

#### 4c. Open GitHub Dialog and Wait
**CRITICAL**: Dialog takes 7-8+ seconds to open

```javascript
const saveToGithubBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Save to GitHub'
);
saveToGithubBtn.click();
```

```bash
# Use bash sleep to wait for dialog to open
sleep 8
```

#### 4d. Verify GitHub Dialog is Open
**CRITICAL**: After sleep, verify dialog is actually open

```javascript
// Check if GitHub dialog is open by looking for specific button
const stageCommitButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);

if (!stageCommitButton) {
  // Dialog not ready - wait 3 more seconds and try again
  return 'GitHub dialog not ready yet - wait longer';
}
```

#### 4e. Fill Commit Message
**ONLY after confirming GitHub dialog is open**

```javascript
// Now it's safe to fill the commit message
const commitInput = document.querySelector('input[type="text"]') || document.querySelector('textarea');
if (commitInput) {
  commitInput.value = 'YOUR COMMIT MESSAGE #IssueNumber';
  commitInput.dispatchEvent(new Event('input', { bubbles: true }));
  commitInput.focus();
}
```

#### 4f. Click Stage and Commit
```javascript
const stageCommitButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);
stageCommitButton.click();
```

#### 4g. Wait for Commit Dialog and Finalize
```bash
# Wait for the final commit dialog to appear
sleep 5
```

```javascript
// Look for Save button in the commit confirmation dialog
const saveButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent === 'Save' && !btn.textContent.includes('Unsaved')
);
if (saveButton) {
  saveButton.click();
} else {
  // Commit already succeeded if no Save button - dialog auto-closed
  return 'Commit completed';
}
```

### Step 5: Deploy the App
**CRITICAL**: Close GitHub dialog first, then wait for deploy dialog

#### 5a. Close GitHub Dialog
```javascript
const closeBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'close'
);
closeBtn.click();
```

#### 5b. Open Deploy Dialog and Wait
**CRITICAL**: Dialog takes 7-8+ seconds to open

```javascript
const deployButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Deploy app'
);
deployButton.click();
```

```bash
# Use bash sleep to wait for dialog to open
sleep 8
```

#### 5c. Verify and Click Redeploy
```javascript
// Verify deploy dialog is open
const redeployBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Redeploy')
);
if (redeployBtn) {
  redeployBtn.click();
} else {
  return 'Deploy dialog not ready - wait longer';
}
```

#### 5d. Close Deploy Dialog
```javascript
const closeBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'close'
);
closeBtn.click();
```

### Step 6: Pull Changes Locally
```bash
cd /src/SpiritWeaver && git fetch && git pull
```

### Step 7: Verify Changes
```javascript
// Navigate to deployed app
mcp__chrome-devtools__navigate_to_url(deployed_url, kwargs)

// Check specific changes (example for header)
const header = document.querySelector('header');
header.innerHTML; // Verify changes are present
```

## Common Mistakes to Avoid

1. **Using setTimeout() for waiting**: It doesn't work - JavaScript execution is synchronous per call
2. **Filling inputs before dialogs open**: Always verify dialog state first
3. **Confusing main input with dialog inputs**: Check context before filling
4. **Not closing previous dialogs**: Can cause overlapping state issues
5. **Proceeding before Gemini completes**: Always check for stop button
6. **Assuming commit succeeded**: Always verify no error messages

## Debugging Tips

### Check Current Page State
```javascript
document.body.innerText.substring(0, 2000);
```

### Find All Buttons
```javascript
Array.from(document.querySelectorAll('button'))
  .map(btn => ({
    text: btn.textContent.trim(),
    ariaLabel: btn.getAttribute('aria-label')
  }));
```

### Check for Dialogs
```javascript
const dialogs = document.querySelectorAll('[role="dialog"]');
dialogs.length > 0 ? 'Dialog open' : 'No dialog';
```

### Look for Errors
```javascript
const allText = document.body.innerText;
const hasError = allText.includes('error') || allText.includes('Error') ||
                 allText.includes('failed') || allText.includes('Failed');
hasError ? 'Error present' : 'No errors';
```

## Complete Workflow Summary

**FULL SEQUENCE** (follow exactly):
1. ✅ Navigate to AI Studio
2. ✅ Send request to Gemini
3. ✅ **Sleep 90 seconds** (critical - don't skip)
4. ✅ Check if implementation complete (verify stop button gone)
5. ✅ **Save changes** (click save button)
6. ✅ Close any open dialogs
7. ✅ Open GitHub dialog
8. ✅ **Sleep 8-10 seconds** (wait for dialog)
9. ✅ Verify dialog open (check for "Stage and commit" button)
10. ✅ Fill commit message with issue number
11. ✅ Click "Stage and commit all changes"
12. ✅ **Sleep 5 seconds** (wait for confirmation)
13. ✅ Click final Save button (if present)
14. ✅ Close GitHub dialog (optional - may auto-close)
15. ✅ Open Deploy dialog
16. ✅ **Sleep 8-10 seconds** (wait for dialog)
17. ✅ Click "Redeploy"
18. ✅ Close Deploy dialog
19. ✅ Pull changes locally (`git pull`)
20. ✅ Verify changes in deployed app

## Success Criteria

A workflow is successful when:
1. ✅ Gemini completes implementation (stop button gone after 90s+ wait)
2. ✅ Changes saved in AI Studio (save button clicked)
3. ✅ Changes committed to GitHub (no error messages, dialog closes)
4. ✅ App redeployed (deployment completes)
5. ✅ Changes pulled locally (`git log` shows new commit)
6. ✅ Changes visible in deployed app (verification step passes)

## Key Improvements Implemented

1. ✅ 90-second initial wait for Gemini implementation
2. ✅ Save changes before opening GitHub dialog
3. ✅ Use bash sleep for dialog wait times (8-10 seconds)
4. ✅ Verify dialogs are open before interacting
5. ✅ Proper sequencing with waits between each step
