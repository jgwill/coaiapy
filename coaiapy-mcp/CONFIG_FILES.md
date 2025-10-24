# MCP Configuration Files

This directory contains three MCP configuration files:

## 📁 Configuration Files

### `.mcp.coaiapy.default.json` ✅ **RECOMMENDED**
**Purpose**: Minimal config that uses coaiapy's existing configuration
**Credentials**: Loaded from `/home/jgi/coaia.json` automatically
**Safe to commit**: Yes (no secrets)
**Use when**: You already have `coaia` configured

```bash
cp .mcp.coaiapy.default.json .mcp.coaiapy.json
```

### `.mcp.coaiapy.dummy.json` 📋 Template
**Purpose**: Template with placeholder credentials
**Credentials**: Must be filled in manually
**Safe to commit**: Yes (only placeholders)
**Use when**: You want explicit environment variables or different credentials

```bash
cp .mcp.coaiapy.dummy.json .mcp.coaiapy.json
# Then edit .mcp.coaiapy.json with real credentials
```

### `.mcp.coaiapy.json` 🔒 **YOUR CONFIG** (gitignored)
**Purpose**: Your actual MCP configuration
**Credentials**: Contains real secrets
**Safe to commit**: NO! (gitignored automatically)
**Created by**: Copying one of the above templates

## 🔄 How Configuration Loading Works

The MCP server loads credentials in this priority order:

1. **Environment variables** (from `.mcp.coaiapy.json` `env` section)
2. **coaiapy config** (`/home/jgi/coaia.json` or `~/.coaia/config.json`)
3. **System environment** (`$LANGFUSE_SECRET_KEY`, etc.)

### Example: Using Default Config

```json
{
  "mcpServers": {
    "coaiapy": {
      "command": "python",
      "args": ["-m", "coaiapy_mcp.server"],
      "cwd": "/src/coaiapy/coaiapy-mcp"
    }
  }
}
```

No `env` section needed! Credentials loaded from `/home/jgi/coaia.json`.

### Example: Using Explicit Credentials

```json
{
  "mcpServers": {
    "coaiapy": {
      "command": "python",
      "args": ["-m", "coaiapy_mcp.server"],
      "cwd": "/src/coaiapy/coaiapy-mcp",
      "env": {
        "LANGFUSE_SECRET_KEY": "sk-lf-...",
        "LANGFUSE_PUBLIC_KEY": "pk-lf-...",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

Credentials in `env` section override coaiapy config.

## 🔒 Security

- ✅ `.mcp.coaiapy.default.json` - Safe to commit (no secrets)
- ✅ `.mcp.coaiapy.dummy.json` - Safe to commit (only placeholders)
- ❌ `.mcp.coaiapy.json` - **NEVER commit** (real credentials)

The `.gitignore` automatically excludes `*.mcp.json` patterns to protect your credentials.

## 📖 See Also

- **MCP_SETUP.md** - Complete setup instructions
- **README.md** - Package documentation
- **IMPLEMENTATION_PLAN.md** - Technical architecture
