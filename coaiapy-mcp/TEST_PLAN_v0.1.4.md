# coaiapy-mcp v0.1.4 Testing Plan

## Pre-Testing Setup

### 1. Install/Reinstall Package
```bash
cd /src/coaiapy/coaiapy-mcp
pip install -e .
```

### 2. Verify Version
```bash
python -c "from coaiapy_mcp import __version__; print(__version__)"
# Expected: 0.1.4
```

### 3. Start MCP Server (if needed manually)
```bash
python -m coaiapy_mcp.server
```

---

## Test Cases for Comment Support

### Test 1: List All Comments
**Tool:** `mcp__coaiapy__coaia_fuse_comments_list`

```python
# No filters - list all comments
await mcp__coaiapy__coaia_fuse_comments_list({})

# Expected: JSON with list of comments or empty list
```

### Test 2: Create Comment on Trace
**Tool:** `mcp__coaiapy__coaia_fuse_comments_create`

**Prerequisites:** Need a valid trace_id (create one first if needed)

```python
# First create a trace
trace_id = "test-trace-" + str(uuid.uuid4())
await mcp__coaiapy__coaia_fuse_trace_create({
    "trace_id": trace_id,
    "name": "Test Trace for Comments"
})

# Then add comment
await mcp__coaiapy__coaia_fuse_comments_create({
    "text": "This is a test comment on a trace",
    "object_type": "trace",
    "object_id": trace_id
})

# Expected: Success response with comment data including ID
```

### Test 3: List Comments for Specific Trace
**Tool:** `mcp__coaiapy__coaia_fuse_comments_list`

```python
# Using trace_id from Test 2
await mcp__coaiapy__coaia_fuse_comments_list({
    "object_type": "trace",
    "object_id": trace_id
})

# Expected: List containing the comment we just created
```

### Test 4: Get Comment by ID
**Tool:** `mcp__coaiapy__coaia_fuse_comments_get`

**Prerequisites:** Get comment_id from Test 2 or Test 3 response

```python
await mcp__coaiapy__coaia_fuse_comments_get({
    "comment_id": "<comment_id_from_previous_test>"
})

# Expected: Single comment object with all details
```

### Test 5: Create Comment on Observation
**Tool:** `mcp__coaiapy__coaia_fuse_comments_create`

```python
# First create observation
obs_id = "test-obs-" + str(uuid.uuid4())
await mcp__coaiapy__coaia_fuse_add_observation({
    "observation_id": obs_id,
    "trace_id": trace_id,
    "name": "Test Observation for Comments"
})

# Add comment to observation
await mcp__coaiapy__coaia_fuse_comments_create({
    "text": "Great observation! Performance looks good.",
    "object_type": "observation",
    "object_id": obs_id
})

# Expected: Success with comment data
```

### Test 6: Filter Comments by Author
**Tool:** `mcp__coaiapy__coaia_fuse_comments_list`

```python
await mcp__coaiapy__coaia_fuse_comments_list({
    "author_user_id": "your-user-id"
})

# Expected: Comments filtered by author
```

### Test 7: Pagination Test
**Tool:** `mcp__coaiapy__coaia_fuse_comments_list`

```python
# First page, limit 2
await mcp__coaiapy__coaia_fuse_comments_list({
    "page": 1,
    "limit": 2
})

# Second page, limit 2
await mcp__coaiapy__coaia_fuse_comments_list({
    "page": 2,
    "limit": 2
})

# Expected: Paginated results
```

### Test 8: Create Comment without Object Attachment
**Tool:** `mcp__coaiapy__coaia_fuse_comments_create`

```python
# Generic comment (not attached to any object)
await mcp__coaiapy__coaia_fuse_comments_create({
    "text": "This is a standalone comment"
})

# Expected: Success - comment created without object linkage
```

---

## Regression Tests (Verify Existing Features Still Work)

### Test 9: Verify Trace Creation
```python
await mcp__coaiapy__coaia_fuse_trace_create({
    "trace_id": "regression-test-trace",
    "name": "Regression Test"
})
```

### Test 10: Verify Prompts List
```python
await mcp__coaiapy__coaia_fuse_prompts_list({})
```

### Test 11: Verify Redis Tash/Fetch
```python
await mcp__coaiapy__coaia_tash({
    "key": "test-key",
    "value": "test-value"
})

await mcp__coaiapy__coaia_fetch({
    "key": "test-key"
})
```

---

## Version Verification Test

### Test 12: Check Server Version
**Expected:** Server should report version 0.1.4 when starting

Look for log output:
```
MCP Server created: coaiapy-mcp v0.1.4
```

---

## Error Handling Tests

### Test 13: Get Non-Existent Comment
```python
await mcp__coaiapy__coaia_fuse_comments_get({
    "comment_id": "non-existent-id-12345"
})

# Expected: Error response with appropriate message
```

### Test 14: Invalid Object Type
```python
await mcp__coaiapy__coaia_fuse_comments_list({
    "object_type": "invalid_type"
})

# Expected: Error or empty list
```

---

## Success Criteria

✅ All 14 tests pass without errors
✅ Server reports version 0.1.4
✅ Comment CRUD operations work correctly
✅ Filtering and pagination work as expected
✅ Existing features remain functional
✅ Error handling is graceful

---

## Quick Test Script

```python
import uuid

# Quick end-to-end test
trace_id = f"test-{uuid.uuid4()}"

# 1. Create trace
await mcp__coaiapy__coaia_fuse_trace_create({
    "trace_id": trace_id,
    "name": "Quick Test"
})

# 2. Add comment
result = await mcp__coaiapy__coaia_fuse_comments_create({
    "text": "Quick test comment",
    "object_type": "trace",
    "object_id": trace_id
})

# 3. List comments for this trace
comments = await mcp__coaiapy__coaia_fuse_comments_list({
    "object_type": "trace",
    "object_id": trace_id
})

print("✅ Quick test passed!" if comments else "❌ Test failed")
```

---

## Notes for Testing Session

1. **Langfuse Credentials:** Ensure `.coaia` config has valid credentials
2. **Redis:** Ensure Redis is running if testing tash/fetch
3. **Clean State:** May want to test with a fresh Langfuse project
4. **Observation:** Watch for any deprecation warnings or errors in logs

---

**Test Plan Version:** 1.0
**Package Version:** 0.1.4
**Date:** 2025-10-30
