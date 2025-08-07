# Manual Testing Guide for .env Langfuse Integration

This guide shows how to manually test the new .env functionality with actual Langfuse commands.

## Prerequisites

1. **Langfuse Account**: Get credentials from [Langfuse Cloud](https://cloud.langfuse.com)
2. **Docker**: For isolated testing environment
3. **Test Data**: Some prompts in your Langfuse project

## Quick Test (Recommended)

### 1. Create Test Environment
```bash
cd /src/coaiapy/tests
cp sample.env.langfuse-real .env
```

### 2. Edit .env with Real Credentials
```bash
# Edit .env file with your actual Langfuse credentials
LANGFUSE_SECRET_KEY=sk-lf-your-actual-secret-key
LANGFUSE_PUBLIC_KEY=pk-lf-your-actual-public-key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Test with Docker
```bash
# Build test image
docker build -f Dockerfile.test -t coaiapy-test ..

# Test coaia fuse commands with .env
docker run --rm \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd):/app/tests:ro \
  coaiapy-test python -c "
import sys; sys.path.append('/app/tests')
from test_langfuse_env_integration import run_langfuse_integration_tests
run_langfuse_integration_tests()
"
```

## Step-by-Step Manual Testing

### Test 1: Configuration Loading
```bash
# In Docker container or local environment with .env file
python3 -c "
import sys; sys.path.append('/app')
from coaiapy.coaiamodule import read_config
config = read_config()
print('Langfuse Secret:', config['langfuse_secret_key'][:10] + '...')
print('Langfuse Public:', config['langfuse_public_key'][:10] + '...')
print('Langfuse Host:', config['langfuse_base_url'])
"
```

### Test 2: CLI Help Commands
```bash
# These should work without network access
python3 -m coaiapy.coaiacli fuse --help
python3 -m coaiapy.coaiacli fuse prompts --help
python3 -m coaiapy.coaiacli fuse prompts list --help
python3 -m coaiapy.coaiacli fuse prompts get --help
```

### Test 3: Actual Langfuse Commands
```bash
# List prompts (requires valid credentials)
python3 -m coaiapy.coaiacli fuse prompts list

# List in JSON format
python3 -m coaiapy.coaiacli fuse prompts list --json

# Get specific prompt (replace with actual prompt name)
python3 -m coaiapy.coaiacli fuse prompts get "your-prompt-name"

# Test with debug output
python3 -m coaiapy.coaiacli fuse prompts list --debug
```

## Expected Results

### ✅ Success Indicators
- Configuration loads without errors
- CLI help commands work
- `prompts list` returns table format by default
- `prompts list --json` returns JSON format
- Actual prompts are displayed from your Langfuse project

### ❌ Common Issues
- **"No prompts found"**: Your Langfuse project might be empty
- **"Authentication failed"**: Check your credentials in .env
- **"Connection error"**: Check LANGFUSE_HOST URL
- **Import errors**: Package installation issues

## Environment Variable Priority Testing

### Test Override Behavior
```bash
# 1. Set .env file with test values
echo "LANGFUSE_SECRET_KEY=from_dotenv_file" > .env

# 2. Override with system environment
export LANGFUSE_SECRET_KEY=from_system_env

# 3. Check which one is used (should be system env)
python3 -c "
from coaiapy.coaiamodule import read_config
config = read_config()
print('Used value:', config['langfuse_secret_key'])
# Should print: Used value: from_system_env
"

# 4. Cleanup
unset LANGFUSE_SECRET_KEY
```

## Testing Different .env Scenarios

### Scenario 1: Only Langfuse Keys
```bash
cat > .env << EOF
LANGFUSE_SECRET_KEY=sk-test-secret
LANGFUSE_PUBLIC_KEY=pk-test-public
EOF

python3 -m coaiapy.coaiacli fuse prompts list --help
```

### Scenario 2: Complete Configuration
```bash
cat > .env << EOF
LANGFUSE_SECRET_KEY=sk-test-secret
LANGFUSE_PUBLIC_KEY=pk-test-public
LANGFUSE_HOST=https://custom.langfuse.com
OPENAI_API_KEY=sk-openai-test
REDIS_HOST=localhost
EOF

# Test that all configs load
python3 -c "
from coaiapy.coaiamodule import read_config
config = read_config()
print('Langfuse:', bool(config['langfuse_secret_key']))
print('OpenAI:', bool(config['openai_api_key']))
print('Redis:', config['jtaleconf']['host'])
"
```

### Scenario 3: No .env File
```bash
# Remove .env file
rm -f .env

# Should still work with help
python3 -m coaiapy.coaiacli fuse --help

# Will use defaults or system environment
python3 -c "
from coaiapy.coaiamodule import read_config
config = read_config()
print('Default Langfuse host:', config['langfuse_base_url'])
"
```

## Debugging Tips

### Check .env File Parsing
```python
from coaiapy.coaiamodule import load_env_file
env_vars = load_env_file('.env')
print("Parsed .env variables:")
for key, value in env_vars.items():
    if 'KEY' in key:
        print(f"{key}: {value[:10]}...")  # Truncate sensitive data
    else:
        print(f"{key}: {value}")
```

### Verify Configuration Merge
```python
from coaiapy.coaiamodule import read_config
config = read_config()

# Check all Langfuse-related config
langfuse_config = {k: v for k, v in config.items() if 'langfuse' in k}
print("Langfuse configuration:")
for key, value in langfuse_config.items():
    if 'key' in key.lower():
        print(f"{key}: {value[:10] if value else 'empty'}...")
    else:
        print(f"{key}: {value}")
```

## Integration with CI/CD

Add to your automation:

```bash
# Automated testing with mock credentials
cat > .env << EOF
LANGFUSE_SECRET_KEY=sk-test-mock-key
LANGFUSE_PUBLIC_KEY=pk-test-mock-key
LANGFUSE_HOST=https://test.mock.com
EOF

# Run tests (will fail on actual API calls but test config loading)
python3 -m pytest tests/test_langfuse_env_integration.py -v

# Or use Docker for complete isolation
make test-docker
```

## Security Notes

⚠️ **Never commit .env files with real credentials!**

- Add `.env` to `.gitignore`
- Use template files like `sample.env.langfuse-real`
- Use different credentials for testing vs production
- Rotate keys if accidentally exposed