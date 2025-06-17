"""Test package for raspberry-pi-modules."""

import sys
import os
import pytest

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Test configuration
pytest_plugins = []
