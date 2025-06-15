# CoAiAPy Update

This update summarizes the current capabilities of the project and how to install the latest TestPyPI release.

## Current Features
- Audio transcription using OpenAI's API.
- Summarization and process commands using configurable instructions.
- Redis integration for stashing and fetching data.
- Langfuse integration via the `fuse` command.
- Helper script `scripts/install_test_release.sh` to create or activate a conda environment named `testcoaiapy` and install the package from TestPyPI.
- `make test-release` cleans, builds, and uploads the package to TestPyPI after bumping the version.

## Validation
- Verified CLI help outputs match documentation (with an additional `fetch` command not listed in the helps snippet).
- Unit tests for fetch command pass.
- `make test-release` requires valid TestPyPI credentials and will install build tools automatically.

## Installation from TestPyPI
Run the helper script to create or activate the conda environment and install:

```bash
scripts/install_test_release.sh
```

Alternatively, you can install directly using pip:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple coaiapy
```

