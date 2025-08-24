#!/bin/bash

# CoaiaPy Release Script
# Prepares distribution and publishes to PyPI

set -e  # Exit on any error

echo "🚀 CoaiaPy Release Script Starting..."

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
VERSION=$(grep -E "^\s*version\s*=\s*[\"']" setup.py | sed -E "s/.*[\"']([^\"']+)[\"'].*/\1/")
git add setup.py pyproject.toml
git commit -m "v${VERSION}" || echo "No changes to commit"
git tag "v${VERSION}"

echo "✅ Release complete!"
echo "📋 Version: v${VERSION}"
echo "📋 Next steps:"
echo "   - Push changes: git push origin main"
echo "   - Push tag: git push origin v${VERSION}"
echo "   - Verify package on PyPI: https://pypi.org/project/coaiapy/"
echo "   - Test installation: pip install coaiapy"