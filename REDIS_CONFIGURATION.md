# Redis Configuration Guide

## Overview

CoaiaPy supports multiple methods for configuring Redis connections, with automatic support for Upstash Redis REST API credentials.

## Environment Variable Priority

Configuration values are resolved in the following priority order (highest to lowest):

1. **System environment variables** (e.g., `export UPSTASH_REDIS_REST_URL=...`)
2. **.env file** in current working directory
3. **~/.coaia.json** configuration file
4. **Default values**

## Upstash Redis REST API (Recommended)

The easiest way to configure Redis is using Upstash REST API credentials:

### Environment Variables

```bash
export UPSTASH_REDIS_REST_URL="https://your-instance.upstash.io"
export UPSTASH_REDIS_REST_TOKEN="your_token_here"
```

### .env File

Create a `.env` file in your project directory:

```env
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here
```

### Automatic Configuration

When `UPSTASH_REDIS_REST_URL` is set, CoaiaPy automatically:
- Extracts the hostname from the URL
- Sets the port (default: 6379 if not specified in URL)
- Enables SSL for `https://` URLs, disables for `http://`
- Uses `UPSTASH_REDIS_REST_TOKEN` as the password

**Example URL Parsing:**

| URL | Host | Port | SSL |
|-----|------|------|-----|
| `https://example.upstash.io` | `example.upstash.io` | 6379 | Yes |
| `https://example.upstash.io:6380` | `example.upstash.io` | 6380 | Yes |
| `http://localhost:6379` | `localhost` | 6379 | No |

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
# Store a test value
coaia tash test_key "test_value"

# Retrieve the value
coaia fetch test_key
```

## Troubleshooting

### "Error: Redis connection failed"

1. **Verify environment variables are set:**
   ```bash
   echo $UPSTASH_REDIS_REST_URL
   echo $UPSTASH_REDIS_REST_TOKEN
   ```

2. **Check .env file exists and is in the current directory:**
   ```bash
   cat .env
   ```

3. **Test network connectivity:**
   ```bash
   # Extract hostname from URL
   ping your-instance.upstash.io
   ```

4. **Verify credentials:**
   - Log into your Upstash dashboard
   - Copy the REST URL and Token exactly as shown
   - Ensure no extra spaces or quotes

### "invalid username-password pair or user is disabled"

This error typically means:
- The `UPSTASH_REDIS_REST_TOKEN` is incorrect or expired
- The Upstash instance requires different authentication

**Solution:**
1. Get fresh credentials from Upstash dashboard
2. Update your `.env` file or environment variables
3. Restart your application

### Configuration Not Loading from .env

1. **Ensure .env file is in the current working directory:**
   ```bash
   pwd
   ls -la .env
   ```

2. **Check file format:**
   - No spaces around `=`
   - No quotes needed for simple values
   - Each variable on its own line

3. **Verify file encoding:**
   ```bash
   file .env  # Should show ASCII or UTF-8
   ```

## Examples

### Example 1: Using Upstash with .env File

```bash
# Create .env file
cat > .env << EOF
UPSTASH_REDIS_REST_URL=https://talented-aardvark-34524.upstash.io
UPSTASH_REDIS_REST_TOKEN=AYbcAAIncDE...
EOF

# Test connection
coaia tash greeting "Hello, World!"
coaia fetch greeting
```

### Example 2: Using Environment Variables

```bash
# Set environment variables
export UPSTASH_REDIS_REST_URL="https://talented-aardvark-34524.upstash.io"
export UPSTASH_REDIS_REST_TOKEN="AYbcAAIncDE..."

# Test connection
coaia tash mykey "myvalue" -T 60
coaia fetch mykey
```

### Example 3: Multiple Environments

```bash
# Development environment (.env.development)
UPSTASH_REDIS_REST_URL=https://dev-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=dev_token

# Production environment (.env.production)
UPSTASH_REDIS_REST_URL=https://prod-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=prod_token

# Use development
cp .env.development .env
coaia fetch dev_key

# Switch to production
cp .env.production .env
coaia fetch prod_key
```

## Migration Guide

### From Old REDIS_* Variables

If you're currently using `REDIS_HOST` and `REDIS_PASSWORD`, you can:

**Option 1: Continue Using Existing Variables**
```bash
# These still work
export REDIS_HOST="redis.example.com"
export REDIS_PASSWORD="password"
```

**Option 2: Migrate to Upstash Format**
```bash
# Old
export REDIS_HOST="example.upstash.io"
export REDIS_PASSWORD="token123"

# New (recommended)
export UPSTASH_REDIS_REST_URL="https://example.upstash.io"
export UPSTASH_REDIS_REST_TOKEN="token123"
```

### From config.json Only

If you only have `~/.coaia.json`:

1. Create a `.env` file in your project directory
2. Add the Upstash variables
3. The .env file will take priority over the config file

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
