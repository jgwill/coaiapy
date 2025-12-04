# AI Studio Browser Automation Reference: Chrome DevTools & Playwright

> Complete technical reference for browser automation commands, critical timing patterns, dialog state management, and completion verification using Chrome DevTools or Playwright MCPs during AI Studio workflows.

**Module**: 04-browser-automation-reference.md
**Related to**: 01-workflow-new-project.md, 02-workflow-existing-project.md, 06-best-practices-antipatterns.md
**Version**: 1.0
**Last Updated**: 2025-11-05

---

## #Critical-Timing-Patterns

These timing patterns are used across all workflows. Understand them first.

### Pattern 1: Gemini Implementation Wait (90+ Seconds)

**Why**: Gemini takes time to implement complex features - rushing causes false failures.

**How**:
1. Send request to Gemini
2. Wait 2 seconds for processing to start
3. Verify processing started (check Stop button)
4. **Sleep exactly 90 seconds** (use bash sleep, not JavaScript)
5. After 90s sleep, check if Stop button gone
6. If still processing: wait another 30-60 seconds
7. If Stop button gone: implementation complete

**Command**:
```bash
sleep 90
```

**Why this timing**: Most implementations complete in 45-120 seconds. Checking too early causes false "failures."

---

### Pattern 2: Dialog Load Wait (8-10 Seconds)

**Why**: UI dialogs (GitHub, Deploy) take time to fully render and become interactive.

**How**:
1. Click button to open dialog (Save to GitHub, Deploy app, etc.)
2. **Sleep exactly 8-10 seconds** (use bash sleep)
3. After sleep, verify dialog is ready (look for expected button)
4. If not ready: wait another 3 seconds, verify again
5. Only interact with dialog after verification

**Command**:
```bash
sleep 8
```

**Why this timing**: Dialogs typically render in 7-10 seconds. Clicking too early hits not-yet-ready elements.

---

### Pattern 3: Dialog Readiness Verification

**After** dialog load wait, verify it's ready before interacting.

```javascript
// Example: Verify GitHub dialog is ready
const stageCommitButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);

if (!stageCommitButton) {
  return 'GitHub dialog not ready yet - wait longer';
} else {
  return 'Dialog ready - proceed with interaction';
}
```

---

### Pattern 4: Completion Verification Loop

```javascript
// Check for stop button (indicates processing)
const stopButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);

if (stopButton) {
  return 'Still processing - wait 30-60 more seconds';
} else {
  return 'Implementation complete - proceed';
}
```

---

## #Chrome-DevTools-MCP-Command-Library

### Navigation Commands

#### Navigate to URL
```javascript
mcp__chrome-devtools__navigate_to_url("https://aistudio.google.com/apps?source=start", {})
```

#### Go to Existing AI Studio Project
```javascript
const editUrl = "https://aistudio.google.com/apps/drive/[PROJECT-ID]?source=start&showAssistant=true";
mcp__chrome-devtools__navigate_to_url(editUrl, {})
```

---

### Element Finding & Interaction

#### Find Button by Text
```javascript
const button = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('BUTTON TEXT')
);
```

#### Find Button by Aria Label
```javascript
const button = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('ARIA LABEL TEXT')
);
```

#### Find Input Field
```javascript
// Textarea
const input = document.querySelector('textarea');

// Text input with ID
const input = document.getElementById('name-input');

// Any text input
const input = document.querySelector('input[type="text"]');

// Contenteditable (rich text)
const input = document.querySelector('[contenteditable="true"]');
```

#### Fill Input Value
```javascript
const input = document.querySelector('textarea');
input.value = "YOUR TEXT HERE";
input.dispatchEvent(new Event('input', { bubbles: true }));
input.focus();
```

#### Click Button
```javascript
const button = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('BUTTON TEXT')
);
button.click();
```

---

### Dialog Management

#### Check if Dialog is Open
```javascript
const dialogs = document.querySelectorAll('[role="dialog"]');
dialogs.length > 0 ? 'Dialog open' : 'No dialog';
```

#### Close Dialog
```javascript
const closeButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'close' ||
  btn.textContent.includes('Close')
);
if (closeButton) closeButton.click();
```

#### Verify Specific Dialog Content
```javascript
// Check for specific button that appears only in certain dialog
const stageButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);

if (stageButton) {
  return 'GitHub dialog confirmed open';
} else {
  return 'Dialog not ready';
}
```

---

### Page State Inspection

#### Get Full Page Text (first 2000 chars)
```javascript
document.body.innerText.substring(0, 2000)
```

#### Check for Processing Indicator
```javascript
const hasStopButton = !!Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);
const isRunning = document.body.innerText.includes('Running for');
const isThinking = document.body.innerText.includes('Thinking');

return { hasStopButton, isRunning, isThinking };
```

#### Check for Error Messages
```javascript
const allText = document.body.innerText;
const hasError = allText.includes('error') ||
                 allText.includes('Error') ||
                 allText.includes('failed') ||
                 allText.includes('Failed');
return hasError ? 'Error detected' : 'No errors';
```

#### Get All Buttons with Labels
```javascript
Array.from(document.querySelectorAll('button'))
  .map(btn => ({
    text: btn.textContent.trim().substring(0, 30),
    ariaLabel: btn.getAttribute('aria-label'),
    visible: btn.offsetParent !== null
  }));
```

---

## #Step-by-Step-Automation-Patterns

### Complete New Project Workflow Automation

#### Step 1: Navigate to New Project
```bash
# Use Chrome DevTools
mcp__chrome-devtools__navigate_to_url("https://aistudio.google.com/apps?source=start", {})
# Wait for page load
sleep 3
```

#### Step 2: Create and Name Project
```javascript
// Click "Create new app"
const createBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Create new app')
);
createBtn.click();

// Wait for dialog
sleep 3

// Fill project name
const nameInput = document.querySelector('input[type="text"]');
nameInput.value = "project-name";
nameInput.dispatchEvent(new Event('input', { bubbles: true }));

// Click create/submit
const submitBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Create')
);
submitBtn.click();
```

#### Step 3: Send Request to Gemini
```javascript
// Find main textarea (not in dialog)
const textarea = document.querySelector('textarea');
textarea.value = "Your prompt here...";
textarea.dispatchEvent(new Event('input', { bubbles: true }));

// Click send
const sendBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Send') ||
  btn.textContent.includes('Send')
);
sendBtn.click();
```

#### Step 4: Verify Gemini Started
```bash
sleep 2
```

```javascript
const isProcessing = {
  hasStopButton: !!Array.from(document.querySelectorAll('button')).find(btn =>
    btn.getAttribute('aria-label')?.includes('Stop')
  ),
  hasThinking: document.body.innerText.includes('Thinking')
};

return isProcessing.hasStopButton || isProcessing.hasThinking ? 'Processing' : 'ERROR: Not started';
```

#### Step 5: Wait for Implementation
```bash
sleep 90
```

```javascript
const stopButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);

return stopButton ? 'Still processing' : 'Complete';
```

#### Step 6: Edit App Name with UUID
```bash
sleep 3
```

```javascript
const editBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Edit name of app'
);
editBtn.click();
```

```bash
sleep 2
```

```javascript
const nameInput = document.getElementById('name-input');
const uuid = 'b40e2a3d-9330-46d4-a52d-50a056d5b46a';
const currentName = nameInput.value;
nameInput.value = `${uuid}-${currentName}`;
nameInput.dispatchEvent(new Event('input', { bubbles: true }));

const saveBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Save') || btn.textContent.includes('Done')
);
saveBtn.click();
```

#### Step 7: Save Changes
```javascript
const saveBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'save' ||
  btn.getAttribute('aria-label')?.includes('Save')
);
if (saveBtn) saveBtn.click();
```

```bash
sleep 3
```

#### Step 8: Commit to GitHub
```javascript
const githubBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Save to GitHub'
);
githubBtn.click();
```

```bash
sleep 8
```

```javascript
// Verify GitHub dialog ready
const stageBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);
return stageBtn ? 'GitHub ready' : 'GitHub not ready - wait more';
```

```javascript
// Fill commit message
const commitInput = document.querySelector('textarea') || document.querySelector('input[type="text"]');
commitInput.value = "Initial implementation #1\n\n🤖 Generated with Claude Code";
commitInput.dispatchEvent(new Event('input', { bubbles: true }));

// Click stage commit
const stageBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Stage and commit all changes')
);
stageBtn.click();
```

```bash
sleep 5
```

```javascript
// Click final save if present
const finalSave = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent === 'Save' && !btn.textContent.includes('Unsaved')
);
if (finalSave) finalSave.click();
```

#### Step 9: Deploy
```javascript
// Close GitHub dialog
const closeBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'close'
);
closeBtn.click();
```

```bash
sleep 3
```

```javascript
// Click deploy
const deployBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label') === 'Deploy app'
);
deployBtn.click();
```

```bash
sleep 8
```

```javascript
// Click redeploy
const redeployBtn = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.textContent.includes('Redeploy')
);
if (redeployBtn) {
  redeployBtn.click();
  return 'Deploy started';
} else {
  return 'Deploy dialog not ready';
}
```

```bash
sleep 3
```

---

## #Playwright-MCP-Equivalents

If using Playwright MCP instead of Chrome DevTools:

```javascript
// Navigate
await page.goto("https://aistudio.google.com/apps?source=start");

// Find and click
const button = await page.locator('button:has-text("Button Text")').first();
await button.click();

// Fill input
const input = await page.locator('textarea');
await input.fill("Your text here");

// Wait for selector
await page.waitForSelector('button:has-text("Expected Button")', { timeout: 10000 });

// Get text
const text = await page.textContent('body');

// Wait time
await page.waitForTimeout(90000); // 90 seconds
```

---

## #Selector-Fallback-Strategies

When primary selector doesn't work:

### Button Selection Strategies (in order of preference)

1. **Aria Label**: `btn.getAttribute('aria-label')?.includes('LABEL')`
2. **Text Content**: `btn.textContent.includes('TEXT')`
3. **Icon Name**: `btn.getAttribute('iconname') === 'save'`
4. **Role**: `document.querySelector('[role="button"][aria-label*="LABEL"]')`
5. **Nearby Element**: Find parent/sibling first, then navigate

### Input Selection Strategies

1. **ID**: `document.getElementById('id-name')`
2. **Type+class**: `document.querySelector('input.class-name[type="text"]')`
3. **Placeholder**: `document.querySelector('input[placeholder*="text"]')`
4. **Aria Label**: `document.querySelector('[aria-label*="label"]')`
5. **Parent container**: Find parent div, then find input inside

---

## #Debugging-Command-Library

### Check Current Page State
```javascript
// Show first 1500 chars of page
document.body.innerText.substring(0, 1500)
```

### Find Element in DOM
```javascript
// Find all elements containing text
Array.from(document.querySelectorAll('*')).find(el =>
  el.textContent.includes('SEARCH TEXT')
);

// Find by class
document.querySelector('.class-name');

// Find nearest button
element.closest('button') ||
element.querySelector('button');
```

### Check Element Visibility
```javascript
const element = document.querySelector('selector');
element.offsetParent !== null ? 'visible' : 'hidden';
```

### Get Element Attributes
```javascript
const btn = document.querySelector('button');
{
  text: btn.textContent.trim(),
  ariaLabel: btn.getAttribute('aria-label'),
  classes: btn.className,
  id: btn.id,
  visible: btn.offsetParent !== null
}
```

### Inspect All Form Inputs
```javascript
Array.from(document.querySelectorAll('input, textarea, [contenteditable]')).map(el => ({
  type: el.tagName,
  placeholder: el.placeholder,
  ariaLabel: el.getAttribute('aria-label'),
  value: el.value ? el.value.substring(0, 50) : '',
  visible: el.offsetParent !== null
}));
```

---

## #Common-Issues-And-Fixes

### Issue: Button Click Doesn't Work

**Check**:
1. Element is visible (offsetParent !== null)
2. Element is clickable (not disabled)
3. Element is in viewport (scroll if needed)

**Fix**:
```javascript
// Scroll into view
element.scrollIntoView({ behavior: 'smooth', block: 'center' });

// Wait and click
setTimeout(() => element.click(), 500);
```

---

### Issue: Input Value Not Updating

**Check**:
1. You found the right input
2. Input is not readonly
3. Event is being dispatched

**Fix**:
```javascript
// Use different event dispatch
const input = document.querySelector('input');
input.value = "new value";
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
```

---

### Issue: Dialog Not Appearing

**Check**:
1. Element that opens dialog was clicked
2. Wait time was sufficient (8-10 seconds)
3. Dialog selector is correct

**Fix**:
```javascript
// Check what dialogs exist
document.querySelectorAll('[role="dialog"], .dialog, .modal').length

// Look for overlay
document.querySelector('[role="presentation"]')

// Check for visibility changes
document.body.style.overflow // might be 'hidden' when dialog open
```

---

### Issue: Scrolling During Interaction

**Check**:
1. Element is in viewport
2. Page isn't scrolling automatically

**Fix**:
```javascript
// Scroll element into view
element.scrollIntoView({ behavior: 'instant', block: 'center' });

// Click after scroll
setTimeout(() => element.click(), 300);
```

---

## #Performance-Optimization

### Batch Operations
Combine multiple element selections:
```javascript
// Inefficient: multiple finds
btn.click();
input.value = "text";
input.dispatchEvent(...);

// Better: do related operations together
const btn = document.querySelector('.btn');
const input = document.querySelector('input');
btn.click();
input.value = "text";
input.dispatchEvent(new Event('input', { bubbles: true }));
```

### Reuse Element References
```javascript
// Cache elements if using multiple times
const buttons = Array.from(document.querySelectorAll('button'));
const saveBtn = buttons.find(b => b.textContent.includes('Save'));
const sendBtn = buttons.find(b => b.textContent.includes('Send'));
```

---

## #Related-Modules

- `01-workflow-new-project.md` - Uses these commands
- `02-workflow-existing-project.md` - Uses these commands
- `06-best-practices-antipatterns.md` - Troubleshooting guide

---

**Module Status**: Complete Technical Reference
**Last Reviewed**: 2025-11-05
