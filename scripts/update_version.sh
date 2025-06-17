#!/bin/bash

# Quick Version Update Script for botibot.py
# This script updates the version in both setup.py and creates a git tag

set -e

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

echo "🔄 Updating version to $NEW_VERSION..."

# Update setup.py
sed -i "s/version=\"[^\"]*\"/version=\"$NEW_VERSION\"/" setup.py

echo "✅ Version updated in setup.py"
echo "📝 Current version info:"
python setup.py --version

echo ""
echo "🚀 Next steps:"
echo "1. Test your changes: python -m build"
echo "2. Manual publish: ./scripts/build_and_publish.sh $NEW_VERSION [testpypi|pypi]"
echo "3. Or create GitHub release for automatic publishing:"
echo "   git add ."
echo "   git commit -m \"Bump version to $NEW_VERSION\""
echo "   git tag v$NEW_VERSION"
echo "   git push origin main --tags"
echo "   # Then create a release on GitHub"
