"""Basic import tests for botibot.py package."""

import pytest
import sys
import os


# Mock GPIO for testing on non-Raspberry Pi systems
class MockGPIO:
    BCM = "BCM"
    BOARD = "BOARD"
    OUT = "OUT"
    IN = "IN"
    HIGH = 1
    LOW = 0

    @staticmethod
    def setmode(mode):
        pass

    @staticmethod
    def setup(pin, mode):
        pass

    @staticmethod
    def output(pin, value):
        pass

    @staticmethod
    def input(pin):
        return 0

    @staticmethod
    def cleanup():
        pass

    class PWM:
        def __init__(self, pin, frequency):
            self.pin = pin
            self.frequency = frequency

        def start(self, duty_cycle):
            pass

        def ChangeDutyCycle(self, duty_cycle):
            pass

        def stop(self):
            pass


# Mock other hardware-specific modules
class MockBoard:
    SCL = "SCL"
    SDA = "SDA"


class MockBusio:
    class I2C:
        def __init__(self, scl, sda):
            pass


class MockSSD1306:
    def __init__(self, width, height, i2c, addr=0x3C):
        pass

    def fill(self, color):
        pass

    def show(self):
        pass

    def image(self, img):
        pass


# Apply mocks before importing modules
sys.modules["RPi.GPIO"] = MockGPIO
sys.modules["board"] = MockBoard
sys.modules["busio"] = MockBusio
sys.modules["adafruit_ssd1306"] = type("MockModule", (), {"SSD1306_I2C": MockSSD1306})


def test_import_modules():
    """Test that all main modules can be imported."""
    try:
        import modules

        assert modules.__version__ == "1.0.0"
        assert "ServoController" in modules.__all__
        assert "OLEDDisplay" in modules.__all__
        assert "RelayController" in modules.__all__
        assert "FlaskServer" in modules.__all__
    except ImportError as e:
        pytest.fail(f"Failed to import modules package: {e}")


def test_import_servo_controller():
    """Test importing ServoController."""
    try:
        from botibot import ServoController

        assert ServoController is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ServoController: {e}")


def test_import_oled_display():
    """Test importing OLEDDisplay."""
    try:
        from botibot import OLEDDisplay

        assert OLEDDisplay is not None
    except ImportError as e:
        pytest.fail(f"Failed to import OLEDDisplay: {e}")


def test_import_relay_controller():
    """Test importing RelayController."""
    try:
        from botibot import RelayController

        assert RelayController is not None
    except ImportError as e:
        pytest.fail(f"Failed to import RelayController: {e}")


def test_import_flask_server():
    """Test importing FlaskServer."""
    try:
        from botibot import FlaskServer

        assert FlaskServer is not None
    except ImportError as e:
        pytest.fail(f"Failed to import FlaskServer: {e}")


def test_servo_controller_basic():
    """Test basic ServoController functionality."""
    from botibot import ServoController

    # Test initialization (should not raise error with mocked GPIO)
    servo = ServoController(pin=11)
    assert servo.pin == 11
    assert servo.frequency == 50
    assert servo.is_initialized == True

    # Test cleanup
    servo.cleanup()
    assert servo.is_initialized == False


def test_flask_server_basic():
    """Test basic FlaskServer functionality."""
    from botibot import FlaskServer

    # Test initialization
    server = FlaskServer(name="Test Server", port=5001)
    assert server.name == "Test Server"
    assert server.port == 5001
    assert server.host == "0.0.0.0"

    # Test data methods
    server.set_data("test_key", "test_value")
    assert server.get_data("test_key") == "test_value"
    assert server.get_data("nonexistent", "default") == "default"

    # Test update data
    server.update_data({"key1": "value1", "key2": "value2"})
    assert server.get_data("key1") == "value1"
    assert server.get_data("key2") == "value2"

    # Test clear data
    server.clear_data()
    assert server.get_data("key1") is None


if __name__ == "__main__":
    pytest.main([__file__])
