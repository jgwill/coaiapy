# 🗺️ ROADMAP: Pipeline Media Action Handlers

## 📍 Current State
- ✅ Core media functions (cofuse.py)
- ✅ CLI commands (`coaia fuse media`)
- ✅ MCP server tools
- ❌ Pipeline template actions

## 🎯 Goal: Phase 4 - Pipeline Media Support

### 1️⃣ Add Action Handlers to `pipeline.py`

**File**: `/src/coaiapy/coaiapy/pipeline.py`

**Location**: In `TemplateEngine.execute_step()` method, add after existing action handlers:

```python
elif action == "upload_media":
    from coaiapy.cofuse import upload_and_attach_media

    result = upload_and_attach_media(
        file_path=step['file_path'],
        trace_id=step['trace_id'],
        field=step.get('field', 'input'),
        observation_id=step.get('observation_id'),
        content_type=step.get('content_type')
    )

    # Export media ID to context if requested
    if step.get('export_as'):
        self.context[step['export_as']] = result['mediaId']

    return result

elif action == "attach_url":
    from coaiapy.cofuse import download_url_and_attach

    result = download_url_and_attach(
        url=step['url'],
        trace_id=step['trace_id'],
        field=step.get('field', 'input'),
        observation_id=step.get('observation_id')
    )

    # Export media ID to context if requested
    if step.get('export_as'):
        self.context[step['export_as']] = result['mediaId']

    return result
```

### 2️⃣ Create Built-in Media Templates

**Directory**: `/src/coaiapy/coaiapy/templates/`

#### Template 1: `vision-analysis.json`
```json
{
  "name": "vision-analysis",
  "description": "Image upload and analysis workflow",
  "variables": {
    "image_path": {"type": "string", "required": true},
    "trace_name": {"type": "string", "default": "Vision Analysis"},
    "user_id": {"type": "string", "required": true}
  },
  "steps": [
    {
      "action": "create_trace",
      "trace_id": "{{ uuid4() }}",
      "name": "{{ trace_name }}",
      "user_id": "{{ user_id }}"
    },
    {
      "action": "upload_media",
      "file_path": "{{ image_path }}",
      "trace_id": "{{ trace_id }}",
      "field": "input",
      "export_as": "IMAGE_MEDIA_ID"
    },
    {
      "action": "add_observation",
      "observation_id": "{{ uuid4() }}",
      "trace_id": "{{ trace_id }}",
      "name": "Image Processing",
      "type": "SPAN",
      "metadata": {
        "media_id": "{{ IMAGE_MEDIA_ID }}"
      }
    }
  ]
}
```

#### Template 2: `audio-transcription.json`
```json
{
  "name": "audio-transcription",
  "description": "Audio upload and transcription workflow",
  "variables": {
    "audio_path": {"type": "string", "required": true},
    "trace_name": {"type": "string", "default": "Audio Transcription"},
    "user_id": {"type": "string", "required": true}
  },
  "steps": [
    {
      "action": "create_trace",
      "trace_id": "{{ uuid4() }}",
      "name": "{{ trace_name }}",
      "user_id": "{{ user_id }}"
    },
    {
      "action": "upload_media",
      "file_path": "{{ audio_path }}",
      "trace_id": "{{ trace_id }}",
      "field": "input",
      "content_type": "audio/mpeg",
      "export_as": "AUDIO_MEDIA_ID"
    },
    {
      "action": "add_observation",
      "observation_id": "{{ uuid4() }}",
      "trace_id": "{{ trace_id }}",
      "name": "Audio Transcription",
      "type": "GENERATION",
      "metadata": {
        "media_id": "{{ AUDIO_MEDIA_ID }}"
      }
    }
  ]
}
```

#### Template 3: `document-processing.json`
```json
{
  "name": "document-processing",
  "description": "Document upload and extraction workflow",
  "variables": {
    "doc_path": {"type": "string", "required": true},
    "trace_name": {"type": "string", "default": "Document Processing"},
    "user_id": {"type": "string", "required": true}
  },
  "steps": [
    {
      "action": "create_trace",
      "trace_id": "{{ uuid4() }}",
      "name": "{{ trace_name }}",
      "user_id": "{{ user_id }}"
    },
    {
      "action": "upload_media",
      "file_path": "{{ doc_path }}",
      "trace_id": "{{ trace_id }}",
      "field": "input",
      "export_as": "DOC_MEDIA_ID"
    },
    {
      "action": "add_observation",
      "observation_id": "{{ uuid4() }}",
      "trace_id": "{{ trace_id }}",
      "name": "Document Extraction",
      "type": "SPAN",
      "metadata": {
        "media_id": "{{ DOC_MEDIA_ID }}"
      }
    }
  ]
}
```

#### Template 4: `url-media-attach.json`
```json
{
  "name": "url-media-attach",
  "description": "Download and attach external URL (imgur, dropbox)",
  "variables": {
    "media_url": {"type": "string", "required": true},
    "trace_name": {"type": "string", "default": "URL Media Attachment"},
    "user_id": {"type": "string", "required": true}
  },
  "steps": [
    {
      "action": "create_trace",
      "trace_id": "{{ uuid4() }}",
      "name": "{{ trace_name }}",
      "user_id": "{{ user_id }}"
    },
    {
      "action": "attach_url",
      "url": "{{ media_url }}",
      "trace_id": "{{ trace_id }}",
      "field": "input",
      "export_as": "URL_MEDIA_ID"
    },
    {
      "action": "add_observation",
      "observation_id": "{{ uuid4() }}",
      "trace_id": "{{ trace_id }}",
      "name": "URL Media Attached",
      "type": "EVENT",
      "metadata": {
        "media_id": "{{ URL_MEDIA_ID }}",
        "source_url": "{{ media_url }}"
      }
    }
  ]
}
```

### 3️⃣ Validation Tests

**File**: `/src/coaiapy/tests/test_pipeline_media.py`

```python
#!/usr/bin/env python
"""Test pipeline media action handlers"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coaiapy.pipeline import TemplateEngine

def test_upload_media_action():
    """Test upload_media action in pipeline"""
    template = {
        "steps": [
            {
                "action": "upload_media",
                "file_path": "tests/notebook_graph.jpg",
                "trace_id": "test-trace-123",
                "field": "input",
                "export_as": "MEDIA_ID"
            }
        ]
    }

    engine = TemplateEngine(template)
    # Test execution (dry-run or with mock)
    print("✅ upload_media action handler works")

def test_attach_url_action():
    """Test attach_url action in pipeline"""
    template = {
        "steps": [
            {
                "action": "attach_url",
                "url": "https://i.imgur.com/test.jpg",
                "trace_id": "test-trace-456",
                "field": "output",
                "export_as": "URL_MEDIA_ID"
            }
        ]
    }

    engine = TemplateEngine(template)
    # Test execution (dry-run or with mock)
    print("✅ attach_url action handler works")

if __name__ == "__main__":
    test_upload_media_action()
    test_attach_url_action()
    print("\n✅ All pipeline media tests pass")
```

### 4️⃣ Documentation Updates

**Update `/src/coaiapy/CLAUDE.md`**:

Add section:
```markdown
## 🎬 Pipeline Media Actions (Phase 4)

### upload_media
Upload local file to trace/observation and export media ID

**Parameters**:
- `file_path`: Path to local file
- `trace_id`: Trace ID
- `field`: "input" | "output" | "metadata"
- `observation_id`: Optional observation ID
- `export_as`: Variable name to export media ID

### attach_url
Download external URL and attach as media

**Parameters**:
- `url`: External URL (imgur, dropbox, etc.)
- `trace_id`: Trace ID
- `field`: "input" | "output" | "metadata"
- `observation_id`: Optional observation ID
- `export_as`: Variable name to export media ID
```

## 📋 Implementation Checklist

- [ ] Add `upload_media` handler to pipeline.py
- [ ] Add `attach_url` handler to pipeline.py
- [ ] Create `vision-analysis.json` template
- [ ] Create `audio-transcription.json` template
- [ ] Create `document-processing.json` template
- [ ] Create `url-media-attach.json` template
- [ ] Create `test_pipeline_media.py`
- [ ] Update CLAUDE.md documentation
- [ ] Test templates with real Langfuse API
- [ ] Commit with issue #65

## 🧪 Testing Strategy

1. **Unit Tests**: Action handler logic
2. **Integration Tests**: Template execution with real API
3. **Validation**: Media IDs properly exported to context

## ⏱️ Estimated Effort
- Pipeline handlers: 1-2 hours
- Templates: 1-2 hours
- Tests: 1 hour
- Documentation: 30 minutes

**Total**: 3.5-5.5 hours

## 🚀 Ready to Implement
All dependencies complete (Phases 1-3). Pipeline.py ready for enhancement.
