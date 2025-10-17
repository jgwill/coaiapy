#!/bin/bash
# resume-mcp-test.sh - Launch MCP server for testing
# This script resumes testing with the coaiapy-mcp server

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🧠 Mia: Resuming coaiapy-mcp testing session"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.template .env
    echo "✅ Created .env - Please edit with your credentials before continuing"
    echo ""
    echo "Required variables:"
    echo "  - LANGFUSE_SECRET_KEY"
    echo "  - LANGFUSE_PUBLIC_KEY"
    echo "  - LANGFUSE_HOST"
    echo "  - REDIS_HOST (default: localhost)"
    echo ""
    exit 1
fi

# Load environment variables
echo "📋 Loading environment from .env..."
export $(grep -v '^#' .env | xargs)

# Verify required variables
if [ -z "$LANGFUSE_SECRET_KEY" ] || [ -z "$LANGFUSE_PUBLIC_KEY" ]; then
    echo "❌ Error: Missing required Langfuse credentials in .env"
    echo "   Please set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY"
    exit 1
fi

# Check if already installed
if ! python -c "import coaiapy_mcp" 2>/dev/null; then
    echo "📦 Installing coaiapy-mcp in editable mode..."
    pip install -e ".[dev]" > /dev/null 2>&1
    echo "✅ Installation complete"
fi

echo ""
echo "🧪 Running test suite..."
echo ""
pytest tests/ -v

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "🚀 Starting MCP server..."
    echo "   Use Ctrl+C to stop"
    echo ""
    echo "📖 To connect an MCP client:"
    echo "   Use the config in: mcp-config.json"
    echo ""

    # Start server
    python -m coaiapy_mcp.server
else
    echo ""
    echo "❌ Tests failed - fix errors before starting server"
    exit 1
fi
