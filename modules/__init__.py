# Botibot Package
# A python package for Project Botibot

from .servo import ServoController
from .oled import OLEDDisplay
from .relay import RelayController
from .webserver import FlaskServer

# Import version information
try:
    from ._version import __version__, __author__, __email__, __license__, __copyright__
except ImportError:
    __version__ = '1.0.0'
    __author__ = 'deJames-13'
    __email__ = 'de.james013@gmail.com'
    __license__ = 'MIT'
    __copyright__ = 'Copyright 2025 deJames-13'

__all__ = [
    'ServoController',
    'OLEDDisplay', 
    'RelayController',
    'FlaskServer'
]

__description__ = 'A python package for Project Botibot'