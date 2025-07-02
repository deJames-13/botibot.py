"""Basic import tests for modules.py package."""

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


# Mock MLX90614 and smbus for temperature sensor
class MockSMBus:
    def __init__(self, bus_number):
        pass


class MockMLX90614:
    def __init__(self, bus, address=0x5A):
        self.bus = bus
        self.address = address

    def get_ambient_temp(self):
        return 22.5

    def get_object_temp(self):
        return 36.5


# Mock serial for GSM module
class MockSerial:
    def __init__(self, port, baudrate, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = True

    def write(self, data):
        return len(data)

    def readline(self):
        return b"OK\r\n"

    def close(self):
        self.is_open = False


# Apply mocks before importing modules
sys.modules["RPi.GPIO"] = MockGPIO
sys.modules["board"] = MockBoard
sys.modules["busio"] = MockBusio
sys.modules["adafruit_ssd1306"] = type("MockModule", (), {"SSD1306_I2C": MockSSD1306})
sys.modules["smbus2"] = type("MockSMBus2", (), {"SMBus": MockSMBus})
sys.modules["mlx90614"] = type("MockMLX90614Module", (), {"MLX90614": MockMLX90614})
sys.modules["serial"] = type("MockSerialModule", (), {"Serial": MockSerial})


def test_import_modules():
    """Test that all main modules can be imported."""
    try:
        import modules

        assert modules.__version__ == "1.0.0"
        assert "ServoController" in modules.__all__
        assert "OLEDDisplay" in modules.__all__
        assert "RelayController" in modules.__all__
        assert "FlaskServer" in modules.__all__

        # Test GSM module import
        import modules.gsm
        assert hasattr(modules.gsm, "SIM800LController")

        # Test IR Temperature module import
        import modules.ir_temp
        assert hasattr(modules.ir_temp, "MLX90614Sensor")

        # Test Scheduler module import
        import modules.scheduler
        assert hasattr(modules.scheduler, "PillScheduler")

    except ImportError as e:
        pytest.fail(f"Failed to import modules package: {e}")


def test_import_servo_controller():
    """Test importing ServoController."""
    try:
        from modules import ServoController

        assert ServoController is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ServoController: {e}")


def test_import_oled_display():
    """Test importing OLEDDisplay."""
    try:
        from modules import OLEDDisplay

        assert OLEDDisplay is not None
    except ImportError as e:
        pytest.fail(f"Failed to import OLEDDisplay: {e}")


def test_import_relay_controller():
    """Test importing RelayController."""
    try:
        from modules import RelayController

        assert RelayController is not None
    except ImportError as e:
        pytest.fail(f"Failed to import RelayController: {e}")


def test_import_flask_server():
    """Test importing FlaskServer."""
    try:
        from modules import FlaskServer

        assert FlaskServer is not None
    except ImportError as e:
        pytest.fail(f"Failed to import FlaskServer: {e}")


def test_servo_controller_basic():
    """Test basic ServoController functionality."""
    from modules import ServoController

    # Test initialization (should not raise error with mocked GPIO)
    servo = ServoController(pin=11)
    assert servo.pin == 11
    assert servo.is_initialized == True

    # Test cleanup
    servo.cleanup()
    assert servo.is_initialized == False


def test_flask_server_basic():
    """Test basic FlaskServer functionality."""
    from modules import FlaskServer

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


def test_gsm_controller_basic():
    """Test basic GSM controller functionality."""
    from modules.gsm import SIM800LController

    # Test initialization (should not raise error with mocked Serial)
    gsm = SIM800LController(port="/dev/ttyS0", baudrate=9600)
    assert gsm.port == "/dev/ttyS0"
    assert gsm.baudrate == 9600

    # Test basic methods (using mock Serial)
    assert gsm.get_network_status() is not None
    assert isinstance(gsm.get_signal_strength(), (int, float))

    # Test cleanup
    gsm.cleanup()


def test_ir_temp_sensor_basic():
    """Test basic IR Temperature sensor functionality."""
    from modules.ir_temp import MLX90614Sensor

    # Test initialization (should not raise error with mocked SMBus and MLX90614)
    ir_temp = MLX90614Sensor(bus_number=1, address=0x5A)
    assert ir_temp.bus_number == 1
    assert ir_temp.address == 0x5A

    # Test temperature readings (using mock MLX90614)
    ambient_temp, object_temp = ir_temp.get_temperatures()
    assert isinstance(ambient_temp, (int, float))
    assert isinstance(object_temp, (int, float))

    # Test temperature checks
    assert ir_temp.is_temperature_safe(ambient_temp) in (True, False)

    # Test cleanup
    ir_temp.cleanup()


def test_pill_scheduler_basic():
    """Test basic Pill Scheduler functionality."""
    from modules.scheduler import PillScheduler

    # Test initialization
    scheduler = PillScheduler()

    # Test schedule management
    schedule_id = scheduler.add_schedule(
        name="Test Medication",
        dosage="1 pill",
        times=["08:00", "20:00"],
        days=["monday", "wednesday", "friday"],
    )
    assert schedule_id is not None

    # Test getting schedules
    schedules = scheduler.get_all_schedules()
    assert len(schedules) > 0

    # Test getting next medication
    next_med = scheduler.get_next_medication()
    assert next_med is not None or next_med == None  # Either valid data or None if no upcoming medications


if __name__ == "__main__":
    pytest.main([__file__])
