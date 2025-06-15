# Narrative Map

## Commits

- `29175ca` – Add test-release target
- `6ae8cda` – Fix configuration lookup and CLI tests
- `584e086` – stuff
- `9e4cb80` – Apply previous commit (build tools & docs for test-release)

The latest series improved configuration discovery, cleaned output, and confirmed CLI help alignment. We introduced `make test-release` to automate building and uploading to TestPyPI. After a minor fix, the target now installs build tools automatically.

This session re-ran `make test-release` after credentials were configured, successfully publishing version 0.2.16 to TestPyPI.

Glyph sequence for this phase: 🧠🌸🕊️🎸
