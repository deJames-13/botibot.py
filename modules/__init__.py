# Modules.py Package
# A python package for Project Botibot

from .servo import ServoController
from .oled import OLEDDisplay
from .relay import RelayController
from .webserver import FlaskServer
from .infrared import InfraredSensor
from .ultrasonic import UltrasonicSensor
from .motor import MotorController, DualMotorController

# Import new modules
from .gsm import SIM800LController
from .ir_temp import MLX90614Sensor
from .scheduler import PillScheduler

# Import version information
try:
    from ._version import __version__, __author__, __email__, __license__, __copyright__
except ImportError:
    __version__ = "1.0.0"
    __author__ = "deJames-13"
    __email__ = "de.james013@gmail.com"
    __license__ = "MIT"
    __copyright__ = "Copyright 2025 deJames-13"

__all__ = [
    "ServoController", 
    "OLEDDisplay", 
    "RelayController", 
    "FlaskServer",
    "InfraredSensor",
    "UltrasonicSensor",
    "MotorController",
    "DualMotorController",
    "SIM800LController",
    "MLX90614Sensor",
    "PillScheduler"
]

__description__ = "A python package for Project Botibot pill dispenser with gpiozero integration"
