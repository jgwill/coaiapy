# Langfuse Media Upload Guide

## Overview

CoaiaPy now supports uploading media files (images, videos, audio, documents) to Langfuse traces and observations with automatic token attachment for inline rendering in the Langfuse UI.

## Quick Start

### CLI Usage

```bash
# Upload image to trace input
coaia fuse media upload photo.jpg trace_abc123

# Upload video to observation output
coaia fuse media upload video.mp4 trace_abc123 \
  --observation-id obs_456 \
  --field output

# Upload audio with explicit content type
coaia fuse media upload recording.wav trace_abc123 \
  --content-type audio/wav \
  --field metadata

# Get media details
coaia fuse media get media_xyz789
```

### Python API Usage

```python
from coaiapy.cofuse import upload_and_attach_media, get_media, format_media_display

# Upload image to trace
result = upload_and_attach_media(
    file_path="screenshot.png",
    trace_id="trace_abc123",
    field="input"
)

if result["success"]:
    print(f"✅ Media ID: {result['media_id']}")
    print(f"📎 Token: {result['media_token']}")
    print(format_media_display(result['media_data']))
else:
    print(f"❌ Error: {result['error']}")

# Upload video to observation
result = upload_and_attach_media(
    file_path="demo.mp4",
    trace_id="trace_abc123",
    observation_id="obs_456",
    field="output"
)
```

### MCP Tool Usage

```python
# In MCP client/server
result = await coaia_fuse_media_upload(
    file_path="diagram.pdf",
    trace_id="trace_abc123",
    field="input"
)

# Get media details
media = await coaia_fuse_media_get(
    media_id=result["media_id"]
)
```

## Complete Workflow

The media upload process follows these steps:

### 1. File Validation
- Validates file exists
- Auto-detects MIME type from extension
- Validates against 52 supported content types
- Calculates SHA-256 hash for deduplication

### 2. Upload Initialization
- POST to `/api/public/media`
- Receives `mediaId` and presigned S3 `uploadUrl`

### 3. File Upload
- PUT file to presigned S3 URL
- **Security**: Validates URL domain is from trusted cloud storage providers:
  - AWS S3 (`amazonaws.com`, `s3.amazonaws.com`)
  - Google Cloud Storage (`storage.googleapis.com`)
  - Azure Blob Storage (`blob.core.windows.net`)
  - Cloudflare R2 (`r2.cloudflarestorage.com`)

### 4. Status Update
- PATCH to `/api/public/media/{mediaId}`
- Reports upload success/failure

### 5. Token Attachment (NEW!)
- Generates Langfuse Media Token:
  ```
  @@@langfuseMedia:type={MIME_TYPE}|id={MEDIA_ID}|source=file@@@
  ```
- Attaches token to trace or observation field
- Enables inline rendering in Langfuse UI

## Langfuse Media Token Format

The media token is a standardized string that Langfuse UI automatically detects and renders:

```
@@@langfuseMedia:type={MIME_TYPE}|id={MEDIA_ID}|source={SOURCE_TYPE}@@@
```

### Components
- **MIME_TYPE**: Content type (e.g., `image/jpeg`, `video/mp4`, `audio/mp3`)
- **MEDIA_ID**: Langfuse media ID from upload (e.g., `media_xyz789`)
- **SOURCE_TYPE**: Source of media - `file`, `base64_data_uri`, or `bytes`

### Examples
```
@@@langfuseMedia:type=image/png|id=media_abc123|source=file@@@
@@@langfuseMedia:type=video/mp4|id=media_xyz789|source=file@@@
@@@langfuseMedia:type=application/pdf|id=media_def456|source=file@@@
```

## Supported Content Types (52 total)

### Images (16)
- image/jpeg, image/jpg, image/png, image/gif, image/webp
- image/bmp, image/tiff, image/svg+xml, image/heic, image/heif
- image/avif, image/x-icon, image/vnd.microsoft.icon
- image/apng, image/jxl, image/x-png

### Videos (13)
- video/mp4, video/mpeg, video/quicktime, video/x-msvideo
- video/x-ms-wmv, video/x-flv, video/webm, video/3gpp, video/3gpp2
- video/x-matroska, video/ogg, video/mp2t, video/x-m4v

### Audio (13)
- audio/mpeg, audio/mp3, audio/wav, audio/x-wav, audio/wave
- audio/ogg, audio/webm, audio/aac, audio/x-aac, audio/flac
- audio/x-flac, audio/mp4, audio/m4a

### Documents (7)
- application/pdf, application/msword
- application/vnd.openxmlformats-officedocument.wordprocessingml.document
- application/vnd.ms-excel
- application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- application/vnd.ms-powerpoint
- application/vnd.openxmlformats-officedocument.presentationml.presentation

### Archives (3)
- application/zip, application/x-rar-compressed, application/x-7z-compressed

## Field Options

Media can be attached to three semantic fields:

- **input**: Media as input to the trace/observation
- **output**: Media as output from the trace/observation  
- **metadata**: Media as metadata/context

## Response Format

Successful upload returns:

```python
{
    "success": True,
    "media_id": "media_xyz789",
    "media_token": "@@@langfuseMedia:type=image/jpeg|id=media_xyz789|source=file@@@",
    "media_data": {
        "id": "media_xyz789",
        "traceId": "trace_abc123",
        "observationId": None,
        "field": "input",
        "contentType": "image/jpeg",
        "contentLength": 193424,
        "sha256Hash": "a1b2c3...",
        "uploadedAt": "2025-11-22T12:34:56Z"
    },
    "message": "Successfully uploaded photo.jpg (193424 bytes)",
    "upload_time_ms": 1234.56
}
```

Error returns:

```python
{
    "success": False,
    "error": "File not found: missing.jpg"
}
```

## Troubleshooting

### Upload fails with "Security error: Upload URL domain..."

The presigned URL is not from a trusted cloud storage provider. This is a security measure to prevent data exfiltration. Contact your Langfuse administrator to verify the storage configuration.

**Trusted domains:**
- AWS S3: `amazonaws.com`, `s3.amazonaws.com`
- Google Cloud: `storage.googleapis.com`
- Azure: `blob.core.windows.net`
- Cloudflare R2: `r2.cloudflarestorage.com`

### Upload succeeds but media not visible in Langfuse UI

1. Verify the media token was attached to the correct field
2. Check the trace/observation in Langfuse UI
3. Ensure your Langfuse version supports media rendering
4. Use `get_media()` to verify the upload completed:
   ```bash
   coaia fuse media get media_xyz789
   ```

### File validation fails

Check:
- File exists at the specified path
- File extension matches a supported content type
- Content type is in the list of 52 supported types

### SHA-256 hash calculation fails

The file may be locked by another process or you may not have read permissions. Verify:
```bash
ls -la /path/to/file
```

## Advanced Usage

### Manual Token Generation

```python
from coaiapy.cofuse import create_langfuse_media_token

# Generate token manually
token = create_langfuse_media_token(
    media_id="media_xyz789",
    content_type="image/jpeg",
    source="file"
)
print(token)
# @@@langfuseMedia:type=image/jpeg|id=media_xyz789|source=file@@@
```

### Manual Token Attachment

```python
from coaiapy.cofuse import (
    create_langfuse_media_token,
    attach_media_token_to_trace,
    attach_media_token_to_observation
)

# Create token
token = create_langfuse_media_token("media_xyz789", "image/png")

# Attach to trace
attach_media_token_to_trace(
    trace_id="trace_abc123",
    media_token=token,
    field="output"
)

# Attach to observation
attach_media_token_to_observation(
    observation_id="obs_456",
    trace_id="trace_abc123",
    media_token=token,
    field="input"
)
```

## Best Practices

1. **Use appropriate fields**: 
   - `input` for media provided TO the system
   - `output` for media generated BY the system
   - `metadata` for contextual media

2. **Let auto-detection work**: Don't specify `content_type` unless necessary

3. **Check return values**: Always verify `success` before using `media_id`

4. **Handle errors gracefully**: Upload failures should not crash your application

5. **Use SHA-256 deduplication**: Langfuse automatically deduplicates identical files

## Examples

### Upload Screenshot from Test Run

```python
import os
from coaiapy.cofuse import add_trace, upload_and_attach_media

# Create trace
trace_id = "test-run-" + os.environ.get("CI_BUILD_ID", "local")
add_trace(
    trace_id=trace_id,
    name="E2E Test Run",
    input={"test_suite": "checkout_flow"}
)

# Attach failure screenshot
result = upload_and_attach_media(
    file_path="/tmp/failure_screenshot.png",
    trace_id=trace_id,
    field="output"
)

if result["success"]:
    print(f"Screenshot attached: {result['media_id']}")
```

### Upload Audio Recording

```python
from coaiapy.cofuse import add_observation, upload_and_attach_media

# Create observation
obs_id = "voice-input-001"
add_observation(
    observation_id=obs_id,
    trace_id="conversation-123",
    observation_type="SPAN",
    name="Voice Input Processing"
)

# Attach audio
result = upload_and_attach_media(
    file_path="user_recording.mp3",
    trace_id="conversation-123",
    observation_id=obs_id,
    field="input"
)
```

### Upload Multiple Images

```python
from coaiapy.cofuse import upload_and_attach_media
import glob

trace_id = "image-processing-001"
media_ids = []

for img_path in glob.glob("screenshots/*.png"):
    result = upload_and_attach_media(
        file_path=img_path,
        trace_id=trace_id,
        field="input"
    )
    
    if result["success"]:
        media_ids.append(result["media_id"])
        print(f"✅ {img_path}: {result['media_id']}")
    else:
        print(f"❌ {img_path}: {result['error']}")

print(f"\nUploaded {len(media_ids)} images")
```

## See Also

- [Langfuse Multi-Modality Documentation](https://langfuse.com/docs/observability/features/multi-modality)
- [Langfuse Public API Reference](https://langfuse.com/docs/api)
- CoaiaPy Media API: `coaiapy/cofuse.py` lines 3640-4350
- CLI Reference: `coaia fuse media --help`
