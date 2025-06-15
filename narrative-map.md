# Narrative Map

- Implemented pagination for Langfuse prompt listing.
- Fixed configuration loading and tests.
- Added TestPyPI upload target and updated docs.
- Added `dist` Makefile target and documented distribution steps.
- Introduced `test-release` Makefile target for full build and TestPyPI upload.
- Retried test-release build; upload failed 400 Bad Request (missing TestPyPI credentials).
- Updated Makefile with explicit repository URL and retried upload; still fails with 400 Bad Request.
- Bumped version to 0.2.18 and successfully uploaded to TestPyPI.
