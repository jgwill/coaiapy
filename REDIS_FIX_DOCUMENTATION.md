# Redis Configuration Fix - Environment Variables Support

## Issue Summary
The `coaia tash` and `coaia fetch` commands were failing with "invalid username-password pair or user is disabled" error because the code didn't properly support the user's environment variable naming convention.

## What Was Fixed

### 1. **Support for Multiple Environment Variable Naming Conventions**
The code now supports BOTH naming conventions for Redis/Upstash credentials:

- `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` (original)
- `UPSTASH_REST_API_URL` and `UPSTASH_REST_API_TOKEN` (user's convention)

**Priority order**: The code checks for `UPSTASH_REDIS_REST_*` first, then falls back to `UPSTASH_REST_API_*`.

### 2. **Improved .env File Loading**
- The `.env` file in the current working directory is now properly loaded
- Variables from `.env` are set in `os.environ` for access throughout the application
- **Priority**: OS environment variables > .env file > config files
- `.env` file will NOT override existing OS environment variables

### 3. **Verbose Mode for Debugging**
Added `--verbose` (or `-v`) flag to both `coaia tash` and `coaia fetch` commands:

```bash
# Show detailed Redis connection information
coaia tash MY_KEY "my value" --verbose
coaia fetch MY_KEY --verbose
```

**Verbose output includes:**
- Redis server host
- Port number
- SSL status
- Password (last 4 characters only)
- Connection status

### 4. **Better Error Messages**
Error messages now mention both environment variable naming conventions and suggest using the `--verbose` flag for debugging.

## How to Use

### Option 1: Using .env File (Recommended for Development)

Create a `.env` file in your project directory:

```bash
# .env file
UPSTASH_REST_API_URL=https://your-redis-instance.upstash.io
UPSTASH_REST_API_TOKEN=your_secret_token_here
```

Or use the alternative naming:

```bash
# .env file
UPSTASH_REDIS_REST_URL=https://your-redis-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_secret_token_here
```

Then run commands normally:

```bash
coaia tash MY_KEY "test value"
coaia fetch MY_KEY
```

### Option 2: Using Environment Variables

Set environment variables in your shell:

```bash
export UPSTASH_REST_API_URL="https://your-redis-instance.upstash.io"
export UPSTASH_REST_API_TOKEN="your_secret_token_here"

coaia tash MY_KEY "test value"
coaia fetch MY_KEY
```

### Option 3: Using coaia.json Configuration File

Add Redis configuration to `~/coaia.json` or `./coaia.json`:

```json
{
  "jtaleconf": {
    "host": "your-redis-instance.upstash.io",
    "port": 6379,
    "password": "your_secret_token_here",
    "ssl": true
  }
}
```

## Configuration Priority

The configuration is loaded in this priority order (highest to lowest):

1. **OS Environment Variables** (set before running the command)
2. **.env File** (in current working directory)
3. **Local coaia.json** (`./coaia.json`)
4. **Home coaia.json** (`~/coaia.json`)
5. **Other config file locations**
6. **Default values**

## Debugging Connection Issues

If you're experiencing connection issues, use the `--verbose` flag:

```bash
coaia tash TEST_KEY "test" --verbose
```

This will show you:
- Which Redis server is being connected to
- The connection parameters being used
- Whether the connection succeeded or failed

Example verbose output:
```
Connecting to Redis server:
  Host: my-redis.upstash.io
  Port: 6379
  SSL: True
  Password: ***oken
  Status: Connection established successfully
```

## Supported Environment Variables

### Redis/Upstash Configuration
- `UPSTASH_REDIS_REST_URL` or `UPSTASH_REST_API_URL` - Full Redis REST URL
- `UPSTASH_REDIS_REST_TOKEN` or `UPSTASH_REST_API_TOKEN` - Authentication token
- `REDIS_HOST` or `UPSTASH_HOST` - Redis server hostname
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` or `UPSTASH_PASSWORD` - Redis password
- `REDIS_SSL` - Enable SSL (true/false)

### Other Services
- `OPENAI_API_KEY` - OpenAI API key
- `AWS_KEY_ID`, `AWS_SECRET_KEY`, `AWS_REGION` - AWS credentials for Polly
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST` - Langfuse integration

## Testing Your Configuration

1. Create a test `.env` file:
```bash
echo 'UPSTASH_REST_API_URL=https://your-redis.upstash.io' > .env
echo 'UPSTASH_REST_API_TOKEN=your_token' >> .env
```

2. Test with verbose mode:
```bash
coaia tash TEST_KEY "hello" --verbose
```

3. Verify the connection shows your Redis instance
4. Fetch the value back:
```bash
coaia fetch TEST_KEY --verbose
```

## Troubleshooting

### "invalid username-password pair" Error
- **Check**: Are your environment variables set correctly?
- **Try**: Run with `--verbose` to see which server is being used
- **Verify**: The URL format should be `https://your-instance.upstash.io`
- **Verify**: The token should match your Upstash dashboard credentials

### .env File Not Being Loaded
- **Check**: The `.env` file is in the current working directory
- **Check**: Variable names are correct (see supported variables above)
- **Check**: No syntax errors in `.env` file (one `KEY=value` per line)
- **Note**: OS environment variables override .env file values

### Using the Wrong Redis Server
- **Check**: Use `--verbose` to see which server is being connected to
- **Check**: Environment variables might be set at the OS level
- **Check**: There might be a `coaia.json` file in the current or home directory

## Changes Made to Code

1. **coaiapy/coaiamodule.py**:
   - Updated `load_env_file()` to set variables in `os.environ`
   - Added support for both `UPSTASH_REDIS_REST_*` and `UPSTASH_REST_API_*` naming
   - Added `verbose` parameter to `_newjtaler()`, `tash()`, and `fetch_key_val()`
   - Improved error messages

2. **coaiapy/coaiacli.py**:
   - Added `--verbose` flag to `tash` and `fetch` subcommands
   - Updated command handlers to pass `verbose` parameter

## Examples

### Basic Usage
```bash
# Set environment variables
export UPSTASH_REST_API_URL="https://my-redis.upstash.io"
export UPSTASH_REST_API_TOKEN="my_token_123"

# Store a value
coaia tash MY_KEY "Hello, World!"

# Retrieve the value
coaia fetch MY_KEY
```

### With .env File
```bash
# Create .env file
cat > .env << EOF
UPSTASH_REST_API_URL=https://my-redis.upstash.io
UPSTASH_REST_API_TOKEN=my_token_123
EOF

# Commands work automatically
coaia tash MY_KEY "Hello from .env!"
coaia fetch MY_KEY
```

### With Verbose Output
```bash
coaia tash DEBUG_KEY "test value" --verbose
# Shows:
# Connecting to Redis server:
#   Host: my-redis.upstash.io
#   Port: 6379
#   SSL: True
#   Password: ***_123
#   Status: Connection established successfully
# Key: DEBUG_KEY  was just saved to memory.
```

## Migration Guide

If you were using the old environment variable names, no changes are needed! Both naming conventions work:

**Old (still works)**:
```bash
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
```

**New (also works)**:
```bash
UPSTASH_REST_API_URL=...
UPSTASH_REST_API_TOKEN=...
```

You can use either set, or even mix them (though we recommend being consistent).
