#!/bin/bash
conda activate coaiapy
# coaiapy-mcp Release Script
# Prepares distribution and publishes to PyPI

set -e  # Exit on any error

echo "🚀 coaiapy-mcp Release Script Starting..."

# Navigate to the coaiapy-mcp directory
pushd "$(dirname "$0")"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
make clean

# Bump version
echo "📈 Bumping version..."
make bump

# Build distribution
echo "🔨 Building distribution..."
make build

# Upload to PyPI
echo "📦 Publishing to PyPI..."
make upload

# Get current version and create git tag
echo "🏷️ Creating git tag..."
VERSION=$(grep -E "^version\s*=\s*\"" pyproject.toml | sed -E "s/.*=\s*\"([^\"]+)\".*/\1/")
git add pyproject.toml setup.py coaiapy_mcp/__init__.py
git commit -m "coaiapy-mcp v${VERSION}" || echo "No changes to commit"
git tag "coaiapy-mcp-v${VERSION}"

# Navigate back to the original directory
popd

echo "✅ coaiapy-mcp Release complete!"
echo "📋 Version: v${VERSION}"
echo "📋 Next steps:"
echo "   - Push changes: git push origin main"
echo "   - Push tag: git push origin coaiapy-mcp-v${VERSION}"
echo "   - Verify package on PyPI: https://pypi.org/project/coaiapy-mcp/"
echo "   - Test installation: pip install coaiapy-mcp"
