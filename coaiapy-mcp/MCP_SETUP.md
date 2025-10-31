# MCP Setup Instructions

## Quick Start

### Option A: Use Existing coaiapy Configuration (Recommended)

If you already have `coaia` configured with credentials in `/home/jgi/coaia.json`:

```bash
# Just copy the default config (no credentials needed)
cp .mcp.coaiapy.default.json .mcp.coaiapy.json
```

The server will automatically load credentials from coaiapy's existing configuration.

### Option B: Explicit Environment Variables

If you want to use different credentials or override coaiapy's config:

```bash
cp .mcp.coaiapy.dummy.json .mcp.coaiapy.json
```

Then edit `.mcp.coaiapy.json` and replace the placeholder values:

- `LANGFUSE_SECRET_KEY` - Your Langfuse secret key (sk-lf-...)
- `LANGFUSE_PUBLIC_KEY` - Your Langfuse public key (pk-lf-...)
- `LANGFUSE_HOST` - Your Langfuse host (default: https://cloud.langfuse.com)
- `REDIS_HOST` - Your Redis host (default: localhost)
- `REDIS_PORT` - Your Redis port (default: 6379)
- `REDIS_PASSWORD` - Your Redis password (leave empty if no auth)
- `AWS_ACCESS_KEY_ID` - Your AWS access key (for audio processing)
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key (for audio processing)

### 2. Install the package in development mode

```bash
pip install -e .
```

### 3. Configure your MCP client

#### For Claude Desktop:

Add to `~/.config/Claude/claude_desktop_config.json`:

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

#### For Claude Code:

Use the `/mcp` command or add to your MCP configuration file.

### 4. Restart your MCP client

Restart Claude Desktop or run `/mcp` in Claude Code to reload the server.

## Alternative: Using coaiapy's existing config

The MCP server will automatically load credentials from:

1. Environment variables (highest priority)
2. `~/.coaia/config.json` or `/home/jgi/coaia.json` (coaiapy's default config)
3. `.env` file in coaiapy-mcp directory

If you already have `coaia` configured, you may not need to set environment variables in the MCP config.

## Testing the Setup

Once configured, test with these MCP tools:

```python
# Test Redis
coaia_tash(key="test", value="hello")
coaia_fetch(key="test")

# Test Langfuse
coaia_fuse_trace_create(
    trace_id="test-trace-001",
    user_id="test-user",
    name="Test Trace"
)

# List Langfuse prompts
coaia_fuse_prompts_list()
```

## Troubleshooting

### "Redis is not available"
- Check Redis is running: `redis-cli ping`
- Verify Redis connection details in config
- Check firewall/network settings

### "Langfuse is not available"
- Verify credentials are correct
- Check Langfuse host URL
- Test credentials with: `coaia fuse prompts list`

### "MCP SDK not installed"
- Install MCP: `pip install mcp>=1.0.0`
- Reinstall package: `pip install -e .`

### Server not starting
- Check logs for error messages
- Verify Python version (>=3.10 required)
- Ensure all dependencies installed: `pip install -e ".[dev]"`

## Configuration File Locations

The MCP server looks for configuration in this order:

1. **Environment variables** (from MCP config)
2. **coaiapy config** (`~/.coaia/config.json` or `/home/jgi/coaia.json`)
3. **.env file** (in coaiapy-mcp directory)

### Example .env file

```bash
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_HOST=https://cloud.langfuse.com

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## Security Notes

⚠️ **IMPORTANT**: Never commit `.mcp.coaiapy.json` or `.env` files with real credentials to version control!

Add to `.gitignore`:
```
.mcp.coaiapy.json
.env
```

The `.mcp.coaiapy.dummy.json` file is safe to commit as it contains only placeholders.
