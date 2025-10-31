#!/bin/bash

# release-all.sh
# Releases both coaiapy and coaiapy-mcp packages

set -e  # Exit on any error

echo "🚀 Starting full release process for coaiapy and coaiapy-mcp..."

# Release coaiapy
echo "\n--- Releasing coaiapy ---"
/src/coaiapy/release.sh

# Release coaiapy-mcp
echo "\n--- Releasing coaiapy-mcp ---"
/src/coaiapy/coaiapy-mcp/release.sh

echo "\n✅ Full release process complete!"
echo "Please remember to push all changes and tags to the remote repository."
