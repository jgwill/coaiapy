# Narrative Map

## Commits

- `29175ca` – Add test-release target
- `6ae8cda` – Fix configuration lookup and CLI tests
- `584e086` – stuff

The last update repaired configuration discovery, removed stray debug prints, and confirmed that CLI help output matches documentation. A validation report notes the existence of an additional `fetch` command.

This round introduces a `make test-release` command that runs tests, builds the
package and uploads it to TestPyPI. Documentation was updated to describe the
workflow.

Glyph sequence for this phase: 🧠🌸🕊️🎸
