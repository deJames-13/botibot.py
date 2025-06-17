#!/bin/bash

# Build and Publish Script for botibot.py
# Usage: ./scripts/build_and_publish.sh [version] [target]
# 
# Parameters:
#   version: new version number (e.g., 1.0.1, 1.1.0)
#   target: 'testpypi' or 'pypi' (default: testpypi)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Parse arguments
NEW_VERSION=$1
TARGET=${2:-testpypi}

if [ -z "$NEW_VERSION" ]; then
    print_error "Please provide a version number"
    echo "Usage: $0 <version> [target]"
    echo "Example: $0 1.0.1 pypi"
    exit 1
fi

# Validate target
if [ "$TARGET" != "testpypi" ] && [ "$TARGET" != "pypi" ]; then
    print_error "Target must be 'testpypi' or 'pypi'"
    exit 1
fi

print_info "Building and publishing botibot.py version $NEW_VERSION to $TARGET"

# Step 1: Update version in setup.py
print_info "Updating version in setup.py..."
sed -i "s/version=\"[^\"]*\"/version=\"$NEW_VERSION\"/" setup.py

# Step 2: Clean previous builds
print_info "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Step 3: Build the package
print_info "Building package..."
python -m build

# Step 4: Check the package
print_info "Checking package integrity..."
python -m twine check dist/*

# Step 5: Load environment variables
if [ -f ".env" ]; then
    print_info "Loading environment variables..."
    source .env
else
    print_warning ".env file not found. Make sure API tokens are set as environment variables."
fi

# Step 6: Upload to PyPI
print_info "Uploading to $TARGET..."

if [ "$TARGET" = "testpypi" ]; then
    if [ -z "$TEST_PYPI_API_TOKEN" ]; then
        print_error "TEST_PYPI_API_TOKEN not found in environment"
        exit 1
    fi
    python -m twine upload --repository testpypi --username __token__ --password "$TEST_PYPI_API_TOKEN" dist/*
    print_success "Package uploaded to Test PyPI!"
    echo "View at: https://test.pypi.org/project/botibot.py/$NEW_VERSION/"
    echo "Install with: pip install -i https://test.pypi.org/simple/ botibot.py==$NEW_VERSION"
else
    if [ -z "$PYPI_API_TOKEN" ]; then
        print_error "PYPI_API_TOKEN not found in environment"
        exit 1
    fi
    python -m twine upload --username __token__ --password "$PYPI_API_TOKEN" dist/*
    print_success "Package uploaded to PyPI!"
    echo "View at: https://pypi.org/project/botibot.py/$NEW_VERSION/"
    echo "Install with: pip install botibot.py==$NEW_VERSION"
fi

print_success "Build and publish completed successfully!"
print_info "Don't forget to commit and tag your changes:"
echo "  git add ."
echo "  git commit -m \"Release version $NEW_VERSION\""
echo "  git tag v$NEW_VERSION"
echo "  git push origin main --tags"
