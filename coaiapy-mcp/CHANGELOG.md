# Changelog

All notable changes to coaiapy-mcp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2025-10-30

### Added
- **Complete Comment Support** for Langfuse objects (traces, observations, sessions, prompts)
  - `coaia_fuse_comments_list` - List/filter comments by object type, ID, or author
  - `coaia_fuse_comments_get` - Retrieve specific comment by ID
  - `coaia_fuse_comments_create` - Create comments attached to objects
- Enhanced `coaiapy.cofuse.get_comments()` with filtering parameters (object_type, object_id, author_user_id, pagination)
- New `coaiapy.cofuse.get_comment_by_id()` function for ID-based retrieval
- Enhanced `coaiapy.cofuse.post_comment()` to attach comments to specific objects

### Fixed
- Version sync issue where server reported 0.1.0 instead of actual version
- Enhanced `bump.py` to update all 3 version files automatically (pyproject.toml, setup.py, __init__.py)
- Made `server.py` import version dynamically from `__init__.py` for single source of truth

### Changed
- Updated `release.sh` to commit all version files (pyproject.toml, setup.py, __init__.py)

## [0.1.3] - 2025-10-30

### Added
- Initial MCP server implementation
- Redis tools (tash, fetch)
- Langfuse trace tools (create, add_observation, view)
- Langfuse prompts tools (list, get)
- Langfuse datasets tools (list, get)
- Langfuse score configs tools (list, get)
- Pipeline template resources
- Project-aware score-config caching system

### Documentation
- Complete MCP setup guide
- Implementation plan
- API documentation

## [0.1.0] - 2025-10-29

### Added
- Initial release of coaiapy-mcp
- Basic MCP server structure
- Core tool definitions

[0.1.4]: https://github.com/jgwill/coaiapy/compare/coaiapy-mcp-v0.1.3...coaiapy-mcp-v0.1.4
[0.1.3]: https://github.com/jgwill/coaiapy/compare/coaiapy-mcp-v0.1.0...coaiapy-mcp-v0.1.3
[0.1.0]: https://github.com/jgwill/coaiapy/releases/tag/coaiapy-mcp-v0.1.0
