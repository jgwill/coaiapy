# Redis Configuration Guide

## Overview

CoaiaPy supports multiple methods for configuring Redis connections, with automatic support for Upstash Redis REST API credentials.

## Environment Variable Priority

Configuration values are resolved in the following priority order (highest to lowest):

1.  **Upstash Direct (REST API)**: `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`
2.  **Vercel KV (REST API)**: `KV_REST_API_URL`, `KV_REST_API_TOKEN`
3.  **Vercel KV (Connection String)**: `KV_URL` or `REDIS_URL`
4.  **Traditional Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_SSL`
5.  **Config Files**: `./coaia.json` or `~/coaia.json`
6.  **Default values**

## Redis Connection Methods

### Upstash Redis REST API (Recommended)

The easiest way to configure Redis is using Upstash REST API credentials:

#### Environment Variables

```bash
export UPSTASH_REDIS_REST_URL="https://your-instance.upstash.io"
export UPSTASH_REDIS_REST_TOKEN="your_token_here"
```

#### .env File

Create a `.env` file in your project directory:

```env
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here
```

### Vercel KV Integration

For projects deployed on Vercel using Vercel KV, the following environment variables are supported:

#### Environment Variables (REST API)

```bash
export KV_REST_API_URL="https://your-instance.upstash.io"
export KV_REST_API_TOKEN="your_token_here"
```

#### .env File (REST API)

```env
KV_REST_API_URL=https://your-instance.upstash.io
KV_REST_API_TOKEN=your_token_here
```

#### Environment Variables (Connection String)

```bash
export KV_URL="rediss://default:your_password@your-host.upstash.io:6379"
# OR
export REDIS_URL="rediss://default:your_password@your-host.upstash.io:6379"
```

#### .env File (Connection String)

```env
KV_URL=rediss://default:your_password@your-host.upstash.io:6379
# OR
REDIS_URL=rediss://default:your_password@your-host.upstash.io:6379
```

### Automatic Configuration

When a URL-based environment variable (e.g., `UPSTASH_REDIS_REST_URL`, `KV_URL`, `REDIS_URL`) is set, CoaiaPy automatically:
- Extracts the hostname from the URL.
- Sets the port (default: 6379 if not specified in URL).
- Enables SSL for `https://` or `rediss://` URLs, disables for `http://` or `redis://`.
- Uses the corresponding token (e.g., `UPSTASH_REDIS_REST_TOKEN`, `KV_REST_API_TOKEN`) or password from the connection string as the Redis password.

**Example URL Parsing:**

| URL | Host | Port | SSL | Password Source |
|-----|------|------|-----|-----------------|
| `https://example.upstash.io` | `example.upstash.io` | 6379 | Yes | `UPSTASH_REDIS_REST_TOKEN` |
| `https://example.upstash.io:6380` | `example.upstash.io` | 6380 | Yes | `UPSTASH_REDIS_REST_TOKEN` |
| `http://localhost:6379` | `localhost` | 6379 | No | `UPSTASH_REDIS_REST_TOKEN` |
| `rediss://default:pass@host.upstash.io:6379` | `host.upstash.io` | 6379 | Yes | `pass` (from URL) |

## Traditional Redis Configuration

You can also use traditional Redis environment variables:

```bash
export REDIS_HOST="redis.example.com"
export REDIS_PORT="6379"
export REDIS_PASSWORD="your_password"
```

Or in `.env`:

```env
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=your_password
```

## Configuration File (~/.coaia.json)

For persistent configuration across all projects:

```json
{
  "jtaleconf": {
    "host": "your-redis-host.example.com",
    "port": 6379,
    "password": "your_password",
    "ssl": true
  }
}
```

## Testing Your Configuration

### Verify Configuration Loading

```bash
python -c "from coaiapy.coaiamodule import read_config; import json; print(json.dumps(read_config()['jtaleconf'], indent=2))"
```

### Test Redis Connection

```bash
# Store a test value with verbose output
coaia tash test_key "test_value" --verbose

# Retrieve the value with verbose output
coaia fetch test_key --verbose
```

**Verbose Output Example:**

```
Connecting to Redis server:
  Host: your-host.upstash.io
  Port: 6379
  SSL: True
  Password: ***word (last 4 characters shown for security)
  Status: Connection established successfully
Key: test_key was just saved to memory.
```

## Troubleshooting

### "Error: Redis connection failed" or "invalid username-password pair or user is disabled"

These errors typically indicate an issue with your Redis connection parameters or credentials.

1.  **Use `--verbose` flag**: Run your `coaia` command with `--verbose` to get detailed connection information. This will show you the host, port, SSL status, and masked password being used.

    ```bash
    coaia tash MY_KEY "my value" --verbose
    ```

2.  **Verify environment variables are set and correct:**
    ```bash
    echo $UPSTASH_REDIS_REST_URL
    echo $UPSTASH_REDIS_REST_TOKEN
    echo $KV_REST_API_URL
    echo $KV_REST_API_TOKEN
    echo $KV_URL
    echo $REDIS_URL
    echo $REDIS_HOST
    echo $REDIS_PORT
    echo $REDIS_PASSWORD
    ```
    Ensure the values match your Redis provider's dashboard.

3.  **Check .env file exists and is in the current directory:**
    ```bash
    cat .env
    ```
    Verify variable names and values. Remember that OS environment variables take precedence over `.env` file values.

4.  **Test network connectivity:**
    ```bash
    # Extract hostname from your Redis URL or REDIS_HOST
    ping your-redis-host.upstash.io
    ```

5.  **Verify credentials:**
    - Log into your Redis provider's dashboard (e.g., Upstash, Vercel).
    - Copy the URL and Token/Password exactly as shown.
    - Ensure no extra spaces or quotes.

6.  **Check configuration priority**: If you have multiple configuration methods (e.g., OS environment variables, `.env` file, `coaia.json`), ensure the one you intend to use is taking precedence. The priority order is listed at the beginning of this document.

### Configuration Not Loading from .env

1.  **Ensure .env file is in the current working directory:**
    ```bash
    pwd
    ls -la .env
    ```

2.  **Check file format:**
    - No spaces around `=`
    - No quotes needed for simple values
    - Each variable on its own line

3.  **Verify file encoding:**
    ```bash
    file .env  # Should show ASCII or UTF-8
    ```

4.  **OS environment variables override .env**: If an environment variable is set at the OS level, it will take precedence over the same variable in your `.env` file.

### Using the Wrong Redis Server

If `coaia tash --verbose` shows a different host than expected:

-   **Check OS environment variables**: You might have an old `export` command in your shell profile.
-   **Check `coaia.json` files**: Look for `./coaia.json` and `~/coaia.json` that might be overriding your intended configuration.
-   **Review priority order**: Understand how different configuration sources are prioritized.

## Examples

### Example 1: Using Upstash with .env File

```bash
# Create .env file
cat > .env << EOF
UPSTASH_REDIS_REST_URL=https://talented-aardvark-34524.upstash.io
UPSTASH_REDIS_REST_TOKEN=AYbcAAIncDE...
EOF

# Test connection with verbose output
coaia tash greeting "Hello, World!" --verbose
coaia fetch greeting --verbose
```

### Example 2: Using Vercel KV (REST API) with .env File

```bash
# Create .env file
cat > .env << EOF
KV_REST_API_URL=https://full-alpaca-12634.upstash.io
KV_REST_API_TOKEN=AaBbCcDdEeFf123456
EOF

# Test connection with verbose output
coaia tash vercel_key "Hello from Vercel KV!" --verbose
coaia fetch vercel_key --verbose
```

### Example 3: Using Vercel KV (Connection String) with Environment Variables

```bash
# Set environment variables
export KV_URL="rediss://default:AaBbCcDdEeFf123456@full-alpaca-12634.upstash.io:6379"

# Test connection with verbose output
coaia tash conn_string_key "Connection string test" --verbose
coaia fetch conn_string_key --verbose
```

### Example 4: Using Traditional Redis with Environment Variables

```bash
# Set environment variables
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_PASSWORD="mysecretpassword"

# Test connection with verbose output
coaia tash local_redis_key "Local Redis test" --verbose
coaia fetch local_redis_key --verbose
```

### Example 5: Multiple Environments

```bash
# Development environment (.env.development)
UPSTASH_REDIS_REST_URL=https://dev-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=dev_token

# Production environment (.env.production)
UPSTASH_REDIS_REST_URL=https://prod-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=prod_token

# Use development
cp .env.development .env
coaia fetch dev_key --verbose

# Switch to production
cp .env.production .env
coaia fetch prod_key --verbose
```

## Migration Guide

### From Old `REDIS_*` Variables

If you're currently using `REDIS_HOST` and `REDIS_PASSWORD`, you can:

**Option 1: Continue Using Existing Variables**
```bash
# These still work
export REDIS_HOST="redis.example.com"
export REDIS_PASSWORD="password"
```

**Option 2: Migrate to Upstash Format (Recommended for Upstash users)**
```bash
# Old
export REDIS_HOST="example.upstash.io"
export REDIS_PASSWORD="token123"

# New (recommended)
export UPSTASH_REDIS_REST_URL="https://example.upstash.io"
export UPSTASH_REDIS_REST_TOKEN="token123"
```

### From Removed `UPSTASH_REST_API_*` Variables

If you were using the non-standard `UPSTASH_REST_API_URL` and `UPSTASH_REST_API_TOKEN` (which were temporarily supported in a previous version), you **must** migrate to the correct standard variables for your platform:

**Old (no longer supported):**
```bash
UPSTASH_REST_API_URL=https://...
UPSTASH_REST_API_TOKEN=...
```

**New (choose based on your provider):**

**For Upstash Direct:**
```bash
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token
```

**For Vercel KV:**
```bash
KV_REST_API_URL=https://your-instance.upstash.io
KV_REST_API_TOKEN=your_token
# OR
KV_URL=rediss://default:password@host.upstash.io:6379
```

### From `config.json` Only

If you only have `~/.coaia.json`:

1.  Create a `.env` file in your project directory.
2.  Add the appropriate environment variables (e.g., `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, or Vercel KV variables).
3.  The `.env` file will take priority over the config file.

## Security Best Practices

1. **Never commit .env files to version control:**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment-specific files:**
   - `.env.development`
   - `.env.staging`
   - `.env.production`

3. **Rotate tokens regularly:**
   - Update tokens in Upstash dashboard
   - Update your `.env` files
   - Restart applications

4. **Use read-only tokens when possible:**
   - Upstash provides read-only tokens
   - Use for applications that only fetch data

## Advanced Configuration

### Using SSL Certificates

For custom Redis instances with SSL:

```json
{
  "jtaleconf": {
    "host": "redis.example.com",
    "port": 6380,
    "password": "your_password",
    "ssl": true,
    "ssl_cert_reqs": "required"
  }
}
```

### Connection Pooling

The Redis client automatically manages connection pooling. For custom settings, modify the `_newjtaler` function in `coaiamodule.py`.

## Support

For issues or questions:
- GitHub Issues: https://github.com/jgwill/coaiapy/issues
- Documentation: https://github.com/jgwill/coaiapy/wiki
