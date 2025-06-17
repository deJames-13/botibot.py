#!/bin/bash
"""
Build script for raspberry-pi-modules package.
This script handles building, testing, and publishing the package.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install development dependencies
install_dev_deps() {
    print_status "Installing development dependencies..."
    
    if ! command_exists pip; then
        print_error "pip is not installed. Please install Python and pip first."
        exit 1
    fi
    
    pip install --upgrade pip setuptools wheel
    pip install build twine
    
    # Install development dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install package in development mode
    pip install -e ".[dev]"
    
    print_success "Development dependencies installed"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if command_exists pytest; then
        pytest tests/ -v --cov=modules --cov-report=term-missing
        print_success "Tests completed"
    else
        print_warning "pytest not found, skipping tests"
    fi
}

# Function to run linting
run_linting() {
    print_status "Running code quality checks..."
    
    if command_exists black; then
        print_status "Running black formatter..."
        black modules/ --check --diff
    fi
    
    if command_exists flake8; then
        print_status "Running flake8 linter..."
        flake8 modules/
    fi
    
    if command_exists mypy; then
        print_status "Running mypy type checker..."
        mypy modules/ --ignore-missing-imports
    fi
    
    print_success "Code quality checks completed"
}

# Function to build package
build_package() {
    print_status "Building package..."
    
    # Clean previous builds
    rm -rf build/ dist/ *.egg-info/
    
    # Build the package
    python -m build
    
    print_success "Package built successfully"
    
    # List the built files
    print_status "Built files:"
    ls -la dist/
}

# Function to test installation
test_installation() {
    print_status "Testing package installation..."
    
    # Create a temporary virtual environment
    python -m venv test_env
    source test_env/bin/activate
    
    # Install the built package
    pip install dist/*.whl
    
    # Test imports
    python -c "
import modules
from modules import ServoController, OLEDDisplay, RelayController, FlaskServer
print('✅ All modules imported successfully')
print(f'📦 Package version: {modules.__version__}')
"
    
    # Test CLI commands
    print_status "Testing CLI commands..."
    rpi-demo --help > /dev/null && echo "✅ rpi-demo command works"
    rpi-servo --help > /dev/null && echo "✅ rpi-servo command works"
    rpi-oled --help > /dev/null && echo "✅ rpi-oled command works"
    rpi-relay --help > /dev/null && echo "✅ rpi-relay command works"
    rpi-server --help > /dev/null && echo "✅ rpi-server command works"
    
    # Cleanup
    deactivate
    rm -rf test_env/
    
    print_success "Installation test completed"
}

# Function to publish to PyPI
publish_package() {
    print_status "Publishing package to PyPI..."
    
    if [ -z "$PYPI_TOKEN" ]; then
        print_warning "PYPI_TOKEN environment variable not set"
        print_status "Using interactive login..."
        twine upload dist/*
    else
        print_status "Using token authentication..."
        twine upload --username __token__ --password "$PYPI_TOKEN" dist/*
    fi
    
    print_success "Package published to PyPI"
}

# Function to publish to Test PyPI
publish_test_package() {
    print_status "Publishing package to Test PyPI..."
    
    if [ -z "$TEST_PYPI_TOKEN" ]; then
        print_warning "TEST_PYPI_TOKEN environment variable not set"
        print_status "Using interactive login..."
        twine upload --repository testpypi dist/*
    else
        print_status "Using token authentication..."
        twine upload --repository testpypi --username __token__ --password "$TEST_PYPI_TOKEN" dist/*
    fi
    
    print_success "Package published to Test PyPI"
}

# Function to show help
show_help() {
    echo "Raspberry Pi Modules Build Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  install-dev     Install development dependencies" 
    echo "  test           Run tests"
    echo "  lint           Run code quality checks"
    echo "  build          Build the package"
    echo "  test-install   Test package installation"
    echo "  publish        Publish to PyPI"
    echo "  publish-test   Publish to Test PyPI"
    echo "  all            Run all checks and build"
    echo "  help           Show this help message"
    echo
    echo "Environment variables:"
    echo "  PYPI_TOKEN      PyPI API token for publishing"
    echo "  TEST_PYPI_TOKEN Test PyPI API token for publishing"
}

# Main script logic
case "${1:-help}" in
    install-dev)
        install_dev_deps
        ;;
    test)
        run_tests
        ;;
    lint)
        run_linting
        ;;
    build)
        build_package
        ;;
    test-install)
        test_installation
        ;;
    publish)
        publish_package
        ;;
    publish-test)
        publish_test_package
        ;;
    all)
        install_dev_deps
        run_linting
        run_tests
        build_package
        test_installation
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
