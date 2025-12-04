# AI Studio Existing Project Workflow: Enhancement Cycle

> Streamlined step-by-step instructions for enhancing projects already created in AI Studio, including code changes, GitHub commits, and redeployment.

**Module**: 02-workflow-existing-project.md
**Related to**: 00-START-HERE.md, 04-browser-automation-reference.md, 06-best-practices-antipatterns.md
**Version**: 1.0
**Last Updated**: 2025-11-05

---

## #Quick-Overview

**Time per enhancement**: 10-15 minutes
**Prerequisites**: Project already created via `01-workflow-new-project.md`

| Step | Purpose | Time |
|------|---------|------|
| 1 | Navigate to project | 2 min |
| 2 | Describe enhancement | 3 min |
| 3 | Wait for implementation | 90+ sec |
| 4 | Verify completion | 2 min |
| 5 | Commit to GitHub | 5 min |
| 6 | Redeploy | 2-3 min |
| 7 | Pull locally + verify | 2 min |

---

## #Step-1: Navigate-to-Project

### Find Your Project
You'll need the AI Studio edit URL from your original project creation (Step 2.1 in `01-workflow-new-project.md`).

**Where to find it**:
- Check your `CLAUDE.md` file in the local repository
- Look in your session notes
- In AI Studio, go to "Recent" or search by project name

### Open the Edit URL
```
https://aistudio.google.com/apps/drive/[PROJECT-ID]?source=start&showAssistant=true...
```

---

## #Step-2: Describe-Your-Enhancement

### Send Request to Gemini
1. Locate main textarea input (NOT in a dialog)
2. Type your enhancement request:

**Examples**:
```
Add a [feature] to the existing [component/section].

Purpose:
This feature enables users to [desired outcome].

Implementation:
- [Technical detail 1]
- [Technical detail 2]

Integration:
- Add button/interface to [location]
- Update [data structure] to support [new data]
```

Or for bug fixes:
```
Fix the [issue description] in [component name].

Current behavior:
[What's wrong]

Expected behavior:
[What should happen]

Location:
[File path or component]
```

### Send the Request
1. Click Send button
2. **Wait 2 seconds** for processing to start
3. Proceed to "Verify Processing Started"

---

## #Step-3: Verify-Processing-Started

**CRITICAL**: Confirm Gemini is working before waiting.

```javascript
// Check if processing started
const processingCheck = {
  hasStopButton: !!Array.from(document.querySelectorAll('button')).find(btn =>
    btn.getAttribute('aria-label')?.includes('Stop')
  ),
  isRunning: document.body.innerText.includes('Running for'),
  isThinking: document.body.innerText.includes('Thinking')
};

if (processingCheck.hasStopButton || processingCheck.isRunning || processingCheck.isThinking) {
  return 'Processing started - proceed to wait';
} else {
  return 'ERROR: Processing did not start';
}
```

**If not processing**:
- Verify request was sent
- Check for error messages
- Retry Step 2

**If processing**:
- Proceed to "Wait for Implementation"

---

## #Step-4: Wait-for-Implementation (90+ SECONDS)

**CRITICAL TIMING**: Same as new project creation.

1. **Sleep 90 seconds** immediately (don't check early)
2. After 90s, check for Stop button:

```javascript
const stopButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('aria-label')?.includes('Stop')
);

if (stopButton) {
  return 'Still processing - wait another 30-60 seconds';
} else {
  return 'Implementation completed';
}
```

3. If Stop button still present: **Wait 30-60 more seconds**, then check again
4. If Stop button gone: Implementation is complete

**DO NOT**:
- Check too early
- Assume done before Stop button disappears
- Proceed with other steps while processing

---

## #Step-5: Verify-and-Save-Changes

### Check Implementation Quality
1. Scroll through the updated code
2. Verify changes match your request
3. Check for any obvious errors

### Save Changes
```javascript
const saveButton = Array.from(document.querySelectorAll('button')).find(btn =>
  btn.getAttribute('iconname') === 'save' ||
  btn.getAttribute('aria-label')?.includes('Save')
);

if (saveButton) {
  saveButton.click();
}
```

Wait for save confirmation (no "Unsaved changes" indicator).

---

## #Step-6: Commit-to-GitHub

### Create GitHub Issue for This Enhancement
1. Navigate to: `https://github.com/{owner}/{repo}/issues/new`
2. Fill in issue:
   - **Title**: "Add [feature]" or "Fix [issue]"
   - **Body**:
     ```
     Added [feature] to [component].

     Changes:
     - [Change 1]
     - [Change 2]

     Testing:
     - Tested [feature] works with [scenario]
     - Verified [existing feature] still works
     ```
3. Click "Create"
4. **Note the issue number** (e.g., #2, #3, etc.)

### Commit via GitHub Dialog

1. Click "Save to GitHub" button in AI Studio
2. **Wait 8-10 seconds** for GitHub dialog to load
3. Verify "Stage and commit all changes" button visible
4. Fill commit message:
   ```
   Add [feature name] #[ISSUE-NUMBER]

   - [Change 1]
   - [Change 2]

   🤖 Generated with Claude Code (https://claude.com/claude-code)

   Co-Authored-By: Gemini AI <noreply@google.com>
   ```
5. Click "Stage and commit all changes"
6. **Wait 5 seconds** for commit dialog
7. Click final "Save" button (if present)
8. Verify no error messages

---

## #Step-7: Redeploy-Application

### Open Deploy Dialog
1. Close GitHub dialog (click X)
2. Click "Deploy app" button in AI Studio
3. **Wait 8-10 seconds** for deploy dialog to load

### Execute Redeploy
1. Verify Google Cloud Project is selected
2. Click "Redeploy" button in dialog
3. **Wait for deployment** (30 seconds to 2 minutes)
4. Note the deployed URL (should be same as before)

### Close Dialog
Click close button (X icon) to dismiss deploy dialog.

---

## #Step-8: Pull-Changes-Locally

```bash
# Navigate to your local repository
cd /path/to/your/project

# Fetch and pull latest changes
git fetch
git pull

# View the new commit
git log -1 --oneline

# Verify changes are present
git diff HEAD~1 HEAD
```

---

## #Step-9: Verify-Deployed-Changes

### Test in Browser
1. Open your deployed URL
2. Test the new feature or fixed issue
3. Verify existing features still work
4. Check console for errors (F12)

### Success Indicators
- ✅ New feature appears and works
- ✅ No console errors
- ✅ Related features still function
- ✅ Deployment URL shows changes

---

## #Iterative-Enhancement-Pattern

For multiple enhancements in sequence:

1. Complete **Step 1-9** for first enhancement
2. For second enhancement: Start at **Step 2** (project already open)
3. Create new issue (#3, #4, etc.) for each enhancement
4. Continue the cycle

**Example sequence**:
```
Enhancement 1: Add voice feature
├─ Create issue #2
├─ Implement (Step 2-4)
├─ Commit #2 (Step 6)
└─ Redeploy + verify (Step 7-9)

Enhancement 2: Fix styling
├─ Create issue #3
├─ Implement (Step 2-4)
├─ Commit #3 (Step 6)
└─ Redeploy + verify (Step 7-9)

Enhancement 3: Add chatbot
├─ Create issue #4
├─ Implement (Step 2-4)
├─ Commit #4 (Step 6)
└─ Redeploy + verify (Step 7-9)
```

---

## #Enhancement-Workflow-Checklist

For each enhancement:

- [ ] Navigate to project (Step 1)
- [ ] Describe enhancement clearly (Step 2)
- [ ] Verify Gemini started processing (Step 3)
- [ ] Wait 90+ seconds for implementation (Step 4)
- [ ] Verify implementation quality (Step 5)
- [ ] Save changes in AI Studio (Step 5)
- [ ] Create GitHub issue (Step 6)
- [ ] Commit with issue reference (Step 6)
- [ ] Redeploy application (Step 7)
- [ ] Pull changes locally (Step 8)
- [ ] Test deployed changes (Step 9)
- [ ] Verify no regressions

---

## #Common-Enhancement-Requests

### Adding a Feature
```
Add [feature name] to [component].

Requirements:
- [Requirement 1]
- [Requirement 2]

UI/Integration:
- Place button at [location]
- Display result in [area]

User flow:
1. User [action 1]
2. System [response 1]
3. User [action 2]
4. System [response 2]
```

### Fixing a Bug
```
Fix [bug description] in [component].

Current behavior:
[What happens now]

Expected behavior:
[What should happen]

Steps to reproduce:
1. [Step 1]
2. [Step 2]
3. [Bug occurs]

Location:
[File path]
```

### Styling/Design Updates
```
Update the styling of [component/section].

Current design:
[Current appearance]

Desired design:
[New appearance]

Specific changes:
- [Color/size/spacing change 1]
- [Color/size/spacing change 2]

Reference:
[Link to design mockup if available]
```

### Performance Improvements
```
Optimize [component/feature] for better performance.

Current issue:
[Performance problem description]

Goals:
- [Goal 1]
- [Goal 2]

Suggestions:
- [Optimization 1]
- [Optimization 2]
```

---

## #Common-Issues

**Q: Gemini implementation looks incomplete**
- A: Check the Stop button disappeared (might still be processing), wait more if needed

**Q: GitHub dialog won't open**
- A: Click "Save to GitHub" again, wait full 8-10 seconds, verify via "Stage and commit" button

**Q: Deployment failed**
- A: Check browser console errors, review AI Studio deploy logs, try redeploying

**Q: Can't pull changes locally**
- A: Ensure you're in correct directory, run `git status` to see state, try `git fetch` first

**Q: Feature not showing in deployed app**
- A: Verify deployment completed, refresh browser (Ctrl+Shift+R for hard refresh), check console errors

---

## #Related-Modules

- `00-START-HERE.md` - Navigation and module overview
- `01-workflow-new-project.md` - For creating new projects
- `03-ai-features-catalog.md` - For adding AI capabilities
- `04-browser-automation-reference.md` - Exact command syntax
- `06-best-practices-antipatterns.md` - Troubleshooting

---

**Module Status**: Complete Enhancement Workflow
**Last Reviewed**: 2025-11-05
