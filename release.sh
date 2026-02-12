#!/bin/bash
set -e

# Release script for MemoryRelay Python SDK
# Usage: ./release.sh patch|minor|major

if [ -z "$1" ]; then
    echo "Usage: ./release.sh patch|minor|major"
    exit 1
fi

BUMP_TYPE=$1

echo "🚀 MemoryRelay Python SDK Release"
echo "=================================="
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: You have uncommitted changes"
    git status --short
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $CURRENT_VERSION"

# Calculate new version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "❌ Invalid bump type: $BUMP_TYPE"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"
echo ""

# Update version in files
echo "📝 Updating version..."
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" memoryrelay/__init__.py

# Commit and tag
echo "💾 Committing changes..."
git add pyproject.toml memoryrelay/__init__.py
git commit -m "chore: bump version to $NEW_VERSION"

echo "🏷️  Creating tag v$NEW_VERSION..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

echo ""
echo "✅ Release prepared!"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git show HEAD"
echo "  2. Push to GitHub: git push origin main --tags"
echo "  3. GitHub Actions will automatically publish to PyPI"
echo ""
