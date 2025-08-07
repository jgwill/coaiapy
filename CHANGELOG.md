# Changelog

All notable changes to this project will be documented in this file.

## [0.2.51] - 2025-08-03

### Added
- **Fine-Tuning Export**: `datasets get` command can now export datasets in formats compatible with OpenAI (`--openai-ft`, `-oft`) and Gemini (`--gemini-ft`, `-gft`) for fine-tuning.
- **Custom System Instruction**: Added `--system-instruction` flag to customize the system message in fine-tuning exports.
- **Dataset Item Display**: `datasets get` command now fetches and displays the items within a dataset in a formatted table.
- **Content-Only Prompt Output**: Added `-c` / `--content-only` flag to `prompts get` to output only the raw prompt content.
- **Escaped Prompt Output**: Added `-e` / `--escaped` flag to `prompts get` to output prompt content as a single, JSON-escaped line for scripting.
- **ROADMAP.md**: Created a roadmap to track future development.
- **CHANGELOG.md**: Created a changelog to track project history.

### Changed
- **Default Prompt Label**: `prompts get` now defaults to fetching the `latest` label when no specific label is provided.
- **Documentation**: Updated `README.md` to include all new features for prompts and datasets.

### Fixed
- **Prompt Fetching Logic**: Corrected an issue where the `production` label was being unintentionally used as a fallback.
- **Error Display**: Improved error handling to show clear messages from the Langfuse API when a prompt or dataset is not found.
- **Prompt Content Parsing**: Enhanced display functions to correctly handle both string and chat-based (list of objects) prompt formats.

## [0.2.47] - 2025-06-15

### Added
- **Langfuse Integration**: Initial integration with the Langfuse API under the `coaia fuse` command.
- **Prompt Management**: Added `prompts list`, `prompts get`, and `prompts create` commands.
- **Dataset Management**: Added `datasets list`, `datasets get`, and `datasets create` commands.
- **Formatted Output**: Implemented pretty-printed tables for `prompts list` and `datasets list`.
- **JSON Output**: Added `--json` flag for raw API output.

### Fixed
- **API Pagination**: Implemented correct pagination handling for listing prompts.

## [0.2.40] - 2025-06-15

### Added
- **Redis `fetch` command**: Added `coaia fetch` to retrieve values from Redis.
- **CI/CD**: Set up GitHub Actions for continuous integration and testing.

### Changed
- **Configuration**: Migrated from `config.json` to `coaia.json` and improved config loading logic.

## [Initial Version]

### Added
- **Core Functionality**: Initial release with `transcribe`, `summarize`, `tash`, and custom process `p` commands.
- **AWS & Redis Integration**: Core integration with AWS for transcription and Redis for caching.
- **Build System**: `Makefile` for building and publishing the package.
