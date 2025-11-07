# Update: Environment Variable Support Corrected

## What Changed (Latest Update)

The previous implementation added support for non-standard `UPSTASH_REST_API_*` variables, which was confusing and not aligned with actual platform standards.

**Removed:**
- ❌ `UPSTASH_REST_API_URL` (non-standard)
- ❌ `UPSTASH_REST_API_TOKEN` (non-standard)

**Now Supported (Standard Variables Only):**

### Upstash Direct
- ✅ `UPSTASH_REDIS_REST_URL`
- ✅ `UPSTASH_REDIS_REST_TOKEN`

### Vercel KV Integration  
- ✅ `KV_REST_API_URL`
- ✅ `KV_REST_API_TOKEN`
- ✅ `KV_URL` (connection string format)
- ✅ `REDIS_URL` (connection string format)

### Traditional Redis
- ✅ `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`

### Config Files (Fallback)
- ✅ `./coaia.json` or `~/coaia.json` with `jtaleconf` section

## Why This Matters

The previous fix introduced confusion by supporting variables that don't match what Upstash or Vercel actually provide. This update aligns the code with actual platform standards:

1. **Upstash Dashboard** provides: `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
2. **Vercel Marketplace** provides: `KV_REST_API_URL`, `KV_REST_API_TOKEN`, `KV_URL`, `REDIS_URL`

## Migration

If you were using the temporary `UPSTASH_REST_API_*` variables from the previous fix, update to the correct standard variables:

```bash
# OLD (from previous fix - no longer supported)
UPSTASH_REST_API_URL=https://...
UPSTASH_REST_API_TOKEN=...

# NEW (use the correct standard for your platform)
# For Upstash direct:
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...

# For Vercel:
KV_REST_API_URL=https://...
KV_REST_API_TOKEN=...
```

## Reference Documentation

See `ENVIRONMENT_VARIABLES_REFERENCE.md` for a complete quick reference guide with examples for each platform.

## Testing

Use `--verbose` flag to verify which configuration is being used:

```bash
coaia tash TEST "value" --verbose
# Shows: Host, port, SSL, and masked password
```
