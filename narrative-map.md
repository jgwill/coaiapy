# Narrative Map

## Commits

- `29175ca` – Add test-release target
- `6ae8cda` – Fix configuration lookup and CLI tests
- `584e086` – stuff
- `9e4cb80` – Apply previous commit (build tools & docs for test-release)

The latest series improved configuration discovery, cleaned output, and confirmed CLI help alignment. We introduced `make test-release` to automate building and uploading to TestPyPI. After a minor fix, the target now installs build tools automatically.

This session re-ran `make test-release` after credentials were configured, successfully publishing version 0.2.16 to TestPyPI.

Glyph sequence for this phase: 🧠🌸🕊️🎸

The new request introduces a helper script for installing the TestPyPI
package in a conda environment. It ensures an environment named
`testcoaiapy` exists, activates it and installs from TestPyPI for easier
testing.

This iteration bumped the version to 0.2.19 so `make test-release` could
upload successfully. Docs now mention using `bump.py` before releasing.
- `42e5c3a` – Document repository state and installation instructions
