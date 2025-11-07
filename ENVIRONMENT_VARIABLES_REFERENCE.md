# Supported Environment Variables - Quick Reference

## Redis/Upstash Connection Variables

### Priority Order (Highest to Lowest)

1. **Upstash Direct (REST API)**
   ```bash
   UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
   UPSTASH_REDIS_REST_TOKEN=your_token_here
   ```

2. **Vercel KV (REST API)**
   ```bash
   KV_REST_API_URL=https://your-instance.upstash.io
   KV_REST_API_TOKEN=your_token_here
   ```

3. **Vercel KV (Connection String)**
   ```bash
   KV_URL=rediss://default:your_password@your-host.upstash.io:6379
   # OR
   REDIS_URL=rediss://default:your_password@your-host.upstash.io:6379
   ```

4. **Traditional Redis**
   ```bash
   REDIS_HOST=your-host.upstash.io
   REDIS_PORT=6379
   REDIS_PASSWORD=your_password
   REDIS_SSL=true
   ```

5. **Config Files** (lowest priority)
   - `./coaia.json` (current directory)
   - `~/coaia.json` (home directory)
   
   ```json
   {
     "jtaleconf": {
       "host": "your-host.upstash.io",
       "port": 6379,
       "password": "your_password",
       "ssl": true
     }
   }
   ```

## When to Use Each Format

### Use Upstash Direct Format When:
- You're using Upstash directly (not through Vercel)
- You have the Upstash dashboard credentials

### Use Vercel KV Format When:
- You're deploying on Vercel
- Vercel automatically sets these variables
- You're using Vercel's KV storage integration

### Use Config Files When:
- You want to commit configuration (without secrets)
- You need project-specific defaults
- Environment variables aren't available

## Example .env Files

### For Upstash Direct Users
```bash
# .env
UPSTASH_REDIS_REST_URL=https://talented-aardvark-12345.upstash.io
UPSTASH_REDIS_REST_TOKEN=AaBbCcDdEeFf123456
```

### For Vercel Users (REST API)
```bash
# .env (copied from Vercel dashboard)
KV_REST_API_URL=https://full-alpaca-12634.upstash.io
KV_REST_API_TOKEN=AaBbCcDdEeFf123456
KV_REST_API_READ_ONLY_TOKEN=XxYyZz789012
```

### For Vercel Users (Connection String)
```bash
# .env (copied from Vercel dashboard)
KV_URL=rediss://default:AaBbCcDdEeFf123456@full-alpaca-12634.upstash.io:6379
REDIS_URL=rediss://default:AaBbCcDdEeFf123456@full-alpaca-12634.upstash.io:6379
```

## Testing Your Configuration

```bash
# Test with verbose mode to see which configuration is being used
coaia tash TEST_KEY "test value" --verbose

# Expected output:
# Connecting to Redis server:
#   Host: your-host.upstash.io
#   Port: 6379
#   SSL: True
#   Password: ***3456
#   Status: Connection established successfully
# Key: TEST_KEY  was just saved to memory.
```

## Troubleshooting

### Wrong Redis Server Being Used?
Run with `--verbose` to see which host is being connected to:
```bash
coaia tash KEY "value" --verbose
```

Check the priority order - OS environment variables override .env file, which overrides config files.

### "Invalid username-password pair" Error?
1. Verify your credentials are correct
2. Check which variables you're setting match your provider:
   - Upstash direct → Use `UPSTASH_REDIS_REST_*`
   - Vercel → Use `KV_*` variables
3. Use `--verbose` to see the masked password and verify it's correct

### Variables Not Being Loaded from .env?
1. Ensure `.env` file is in your current working directory
2. Check for typos in variable names
3. OS environment variables take priority over .env file
4. Use `--verbose` to confirm which configuration is active

## Migration Guide

### Migrating from Old UPSTASH_REST_API_* Variables
If you were using the non-standard `UPSTASH_REST_API_*` variables, update to standard names:

**Old (no longer supported):**
```bash
UPSTASH_REST_API_URL=...
UPSTASH_REST_API_TOKEN=...
```

**New (choose based on your provider):**
```bash
# For Upstash direct:
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...

# For Vercel KV:
KV_REST_API_URL=...
KV_REST_API_TOKEN=...
```

## Summary Table

| Variable | Provider | Format | Priority |
|----------|----------|--------|----------|
| `UPSTASH_REDIS_REST_URL` | Upstash | HTTPS | 1 (Highest) |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash | Token | 1 |
| `KV_REST_API_URL` | Vercel | HTTPS | 2 |
| `KV_REST_API_TOKEN` | Vercel | Token | 2 |
| `KV_URL` | Vercel | Connection String | 3 |
| `REDIS_URL` | Vercel | Connection String | 3 |
| `REDIS_HOST` | Generic | Hostname | 4 |
| `REDIS_PASSWORD` | Generic | Password | 4 |
| Config files | Any | JSON | 5 (Lowest) |
