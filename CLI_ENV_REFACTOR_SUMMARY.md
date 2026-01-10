# CLI Environment Refactoring Summary

## Overview
Refactored the CoAiAPy CLI to provide clearer separation between environment *management* (`environment` command) and environment *usage* (`--env` flag).

## Changes Made

### 1. Command Renaming
- **Before**: `coaia env <action>`
- **After**: `coaia environment <action>`
- **Backward Compatibility**: `env` retained as alias (both work identically)

```bash
# Both commands work:
coaia environment list
coaia env list              # Alias - still works
```

### 2. Global `--env` Flag Added
Added global `--env` flag to load environment files before executing any command.

**Usage Pattern**:
```bash
coaia --env <path-to-env-file> <command> [args...]
```

**Examples**:
```bash
# Load environment for any command
coaia --env .env.myproject fuse traces list
coaia --env /path/to/.env.dev pipeline create llm-chain --var model="gpt-4"
coaia --env ~/.coaia/production.env environment list
```

### 3. Implementation Details

**Files Modified**:
- `coaiapy/coaiacli.py`: Core CLI implementation
  - Added global `--env` argument to main parser
  - Renamed command from `'env'` to `'environment'` with `'env'` alias
  - Added environment loading logic before command execution
  - Updated help text references

**Code Changes**:
1. **Global Flag** (line ~113):
   ```python
   parser.add_argument('--env', type=str, metavar='PATH', 
                      help='Load environment variables from specified file path before executing command')
   ```

2. **Command Alias** (line ~425):
   ```python
   parser_env = subparsers.add_parser('environment', aliases=['env'], 
                                      help='Manage environment variables for pipeline workflows')
   ```

3. **Environment Loading** (line ~496):
   ```python
   if hasattr(args, 'env') and args.env:
       env_manager = EnvironmentManager()
       env_file_path = Path(args.env).expanduser()
       if not env_file_path.exists():
           print(f"Error: Environment file not found: {args.env}")
           return 1
       env_vars = env_manager._read_env_file(env_file_path)
       for key, value in env_vars.items():
           os.environ[key] = str(value)
   ```

4. **Command Handler** (line ~1486):
   ```python
   elif args.command == 'environment' or args.command == 'env':
   ```

### 4. Documentation Updates

**Files Updated**:
- `README.md`: Updated all examples, added `--env` flag documentation
- `CLAUDE.md`: Updated all command references
- `ROADMAP.md`: Updated feature checklist
- `CHANGELOG.md`: Updated command examples

**Key Additions to README**:
- New section demonstrating `--env` flag usage
- Note about `env` alias for backward compatibility
- Examples of loading environment files for different commands

## Benefits

### 1. Clarity
- **`environment` command**: Manage environment files (create, edit, list)
- **`--env` flag**: Use environment files (load before execution)

### 2. Consistency
Aligns with common CLI patterns where:
- Commands manage resources
- Flags modify behavior

Similar to:
```bash
docker --env-file .env run myapp
kubectl --kubeconfig ./config get pods
```

### 3. Flexibility
```bash
# Manage environments
coaia environment init --name dev
coaia environment set API_KEY "xyz" --name dev

# Use environments
coaia --env .coaia-env.dev fuse traces list
coaia --env ~/.env.production pipeline create data-pipeline
```

### 4. Backward Compatibility
- All existing scripts using `coaia env` continue to work
- No breaking changes
- Gradual migration path for users

## Testing

### Manual Tests Performed
1. ✓ `coaia --help` shows both command and flag
2. ✓ `coaia environment --help` works
3. ✓ `coaia env --help` works (alias)
4. ✓ `--env` flag loads environment before command execution
5. ✓ Environment variables accessible in command context
6. ✓ Error handling for missing environment files
7. ✓ Both JSON and .env file formats supported

### Test Results
```bash
# Command alias test
coaia env list ✓
coaia environment list ✓

# --env flag test
coaia --env /tmp/test.env fetch key ✓
  → Environment variables loaded successfully
  
# Combined test
coaia --env .env.dev environment list ✓
  → Loads env, then shows environment list
```

## Migration Guide

### For Users
No migration needed! Existing commands continue to work:
```bash
# Old (still works)
coaia env list
coaia env set KEY value

# New (recommended)
coaia environment list
coaia environment set KEY value

# Also new (--env flag)
coaia --env .env.dev <any-command>
```

### For Scripts/Automation
1. **No immediate action required** - `env` alias ensures compatibility
2. **Recommended**: Gradually update to `environment` for clarity
3. **New feature**: Consider using `--env` flag for environment loading

### For Documentation
- Update examples to use `environment` command
- Add examples of `--env` flag usage
- Note `env` alias for backward compatibility

## Future Considerations

### Potential Enhancements
1. **Verbose mode**: `--env --verbose` to show loaded variables
2. **Multiple env files**: `--env file1 --env file2` (merge)
3. **Environment profiles**: `--env-profile dev` (shorthand for common paths)
4. **Validation**: `--env-validate` to check required variables

### Deprecation Path (Optional)
If desired to eventually remove `env` alias:
1. **Version X.Y**: Add deprecation warning when using `env` alias
2. **Version X.Y+1**: Make warning more prominent
3. **Version X.Y+2**: Remove alias (major version)

Currently: **No deprecation planned** - alias is harmless and provides UX benefit.

## Summary

### What Changed
- `coaia env` → `coaia environment` (with `env` as backward-compatible alias)
- New `--env <path>` global flag for loading environment files

### Why It Matters
- **Clearer semantics**: Manage vs. Use separation
- **Better UX**: Aligns with standard CLI patterns
- **More flexible**: Load environments for any command, not just pipeline workflows

### Impact
- ✓ No breaking changes
- ✓ Enhanced functionality
- ✓ Improved clarity
- ✓ Backward compatible

---

**Date**: 2026-01-10
**Author**: Automated CLI Refactoring
**Version**: CoAiAPy CLI Enhancement

## Quick Reference

### Environment Management Commands
```bash
# Initialize environment files
coaia environment init                      # Create .coaia-env
coaia environment init --name prod          # Create .coaia-env.prod
coaia environment init --global             # Create ~/.coaia/global.env

# Set/get variables
coaia environment set API_KEY "xyz123"      # Persist to file
coaia environment get API_KEY               # Retrieve value
coaia environment unset OLD_VAR             # Remove variable

# List environments
coaia environment list                      # Show all
coaia environment list --name prod          # Show specific
coaia environment list --json               # JSON output

# Source into shell
eval $(coaia environment source --export)   # Load into current shell

# Save current context
coaia environment save --name "my-session"  # Snapshot current state
```

### Using --env Flag
```bash
# Load environment for specific commands
coaia --env .env.development fuse traces list
coaia --env ~/.coaia/prod.env pipeline create data-pipeline
coaia --env /path/to/custom.json tash mykey "value"

# Combine with any command
coaia --env .env.local transcribe audio.mp3
coaia --env ~/envs/test.json gh issues list --owner user --repo repo
```

### Real-World Workflows

#### Multi-Environment Development
```bash
# Development
coaia --env .env.dev fuse traces create --user dev-user

# Staging
coaia --env .env.staging fuse traces create --user stage-user

# Production
coaia --env .env.production fuse traces create --user prod-user
```

#### Pipeline with Environment
```bash
# Create environment-specific pipeline
coaia --env .env.production pipeline create llm-chain \
  --var model="gpt-4" \
  --var user_id="prod-user-123" \
  --export-env

# Environment is pre-loaded, pipeline uses those values
```

#### Cross-Session Workflows
```bash
# Session 1: Initialize and save
coaia environment init --name my-work
coaia environment set PROJECT_ID "abc-123" --name my-work
coaia --env .coaia-env.my-work pipeline create data-pipeline

# Session 2 (days later): Resume
coaia --env .coaia-env.my-work fuse traces list
# All PROJECT_ID and pipeline vars available
```

---
*End of Summary*
