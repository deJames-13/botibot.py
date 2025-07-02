# botibot.py

A python package for Project Botibot - A collection of reusable, class-based utility modules for common Raspberry Pi microcontroller projects. These modules provide easy-to-use interfaces for controlling servos, OLED displays, relays, infrared sensors, ultrasonic sensors, motors, and web servers with **gpiozero integration** for better reliability and performance.

## 📦 Modules Overview

### 1. ServoController (`botibot/servo/`)
- **Purpose**: Control servo motors with PWM signals using **gpiozero**
- **Features**: 
  - Precise angle control (0-180°)
  - Smooth movements with gpiozero
  - Context manager support
  - PiGPIO support for better performance

### 2. OLEDDisplay (`botibot/oled/`)
- **Purpose**: Control SSD1306-based I2C OLED displays
- **Features**: 
  - Text and graphics rendering
  - Multi-line text support
  - Scrolling and blinking effects
  - Progress bars and status displays

### 3. RelayController (`botibot/relay/`)
- **Purpose**: Control relay modules using **gpiozero**
- **Features**: 
  - Single and multiple relay control with OutputDevice
  - Timed operations with callback support
  - Pattern sequences (wave, blink)
  - Thread-safe background operations

### 4. FlaskServer (`botibot/webserver/`)
- **Purpose**: Create configurable web interfaces and APIs
- **Features**: 
  - Beautiful responsive web dashboard
  - RESTful API endpoints
  - Real-time data sharing
  - Custom route support

### 5. InfraredSensor (`botibot/infrared/`)
- **Purpose**: Control infrared sensors with gpiozero
- **Features**:
  - Motion detection and proximity sensing
  - Callback functions for detection events
  - Line following capabilities
  - Multiple sensor support

### 6. UltrasonicSensor (`modules/ultrasonic/`)
- **Purpose**: Control ultrasonic distance sensors with gpiozero
- **Features**:
  - Accurate distance measurement
  - Proximity alert callbacks
  - Filtering and averaging options
  - Distance mapping and threshold settings

### 7. MotorController (`modules/motor/`)
- **Purpose**: Control DC motors with gpiozero
- **Features**:
  - Forward, backward, and variable speed control
  - Dual motor control for differential drive
  - Smooth acceleration and deceleration
  - PWM speed control

### 8. SIM800LController (`modules/gsm/`)
- **Purpose**: Control SIM800L GSM module for pill dispenser notifications
- **Features**:
  - SMS sending for medication reminders
  - Network status monitoring
  - Signal strength checking
  - Battery monitoring
  - Emergency SMS alerts

### 9. MLX90614Sensor (`modules/ir_temp/`)
- **Purpose**: Control MLX90614 IR temperature sensor (GY-906) for patient monitoring
- **Features**:
  - Ambient and object temperature measurement
  - Temperature threshold monitoring
  - Button-triggered readings
  - Temperature logging
  - Medication storage temperature safety checks

### 10. PillScheduler (`modules/scheduler/`)
- **Purpose**: Manage medication schedules for pill dispenser
- **Features**:
  - Add, update, and delete medication schedules
  - Database storage with SQLite
  - Flexible scheduling (time, day, date)
  - Next medication notifications
  - Missed medication tracking
  - Integration with SMS notifications

## 🛠 Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install the package
pip install modules.py

# Or install with all optional dependencies
pip install modules.py[full]
```

### Option 2: Install from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/deJames-13/modules.py.git
   cd modules
   ```

2. **Install in development mode**
   ```bash
   pip install -e .
   
   # Or with development dependencies
   pip install -e .[dev]
   ```

### Option 3: Build and Install Local Package

```bash
# Build the package
python -m build

# Install the built package
pip install dist/*.whl
```

### Hardware Setup

3. **Enable I2C and SPI (if needed)**
   ```bash
   sudo raspi-config
   # Navigate to Interfacing Options > I2C > Enable
   # Navigate to Interfacing Options > SPI > Enable
   ```

4. **Test installation**
   ```bash
   # Test CLI commands
   modules-demo --help
   modules-servo --help
   modules-oled --help
   modules-gsm --help
   modules-ir-temp --help
   modules-scheduler --help
   ```

## 🚀 Quick Start

### Basic Usage Examples

#### Servo Control
```python
from botibot import ServoController

# Basic servo control with gpiozero
with ServoController(pin=11) as servo:
    servo.move_to_position(0, delay=1)    # 0 degrees
    servo.move_to_position(90, delay=1)   # 90 degrees
    servo.move_to_position(180, delay=1)  # 180 degrees
    servo.center()                        # Back to center
```

#### OLED Display
```python
from botibot import OLEDDisplay

# Create display and show text
oled = OLEDDisplay(width=128, height=64)
oled.write_text("Hello, Pi!", 0, 0)

# Multi-line display
lines = ["Line 1", "Line 2", "Line 3"]
oled.write_multiline(lines, 0, 0, line_height=12)

# Graphics
oled.draw_rectangle(10, 10, 50, 30)
oled.draw_circle(100, 25, 15)
oled.show()
```

#### Relay Control
```python
from botibot import RelayController

# Basic relay control with gpiozero
with RelayController(pin=17) as relay:
    relay.turn_on()
    time.sleep(2)
    relay.turn_off()
    
    # Pulse operation
    relay.pulse(duration=3.0)
    
    # Blinking
    relay.blink(on_time=0.5, off_time=0.5, cycles=5)
```

#### Infrared Sensor
```python
from botibot import InfraredSensor

# Motion detection with gpiozero
sensor = InfraredSensor(pin=18)

def motion_detected():
    print("Motion detected!")

sensor.when_motion = motion_detected
sensor.start_monitoring()
```

#### Ultrasonic Sensor
```python
from botibot import UltrasonicSensor

# Distance measurement with gpiozero
sensor = UltrasonicSensor(trigger_pin=23, echo_pin=24)

# Get single reading
distance = sensor.get_distance()
print(f"Distance: {distance:.2f} cm")

# Continuous monitoring
sensor.start_monitoring()
```

#### Motor Control
```python
from botibot import MotorController, DualMotorController

# Single motor control
motor = MotorController(forward_pin=20, backward_pin=21)
motor.forward(speed=0.7)
motor.stop()

# Dual motor for robotics
robot = DualMotorController(
    left_motor=(20, 21), 
    right_motor=(22, 23)
)
robot.forward(speed=0.5)
robot.turn_left(speed=0.3)
```

#### Web Server
```python
from botibot import FlaskServer

# Create web server
server = FlaskServer(name="My Pi Server", port=5000)

# Add data
server.set_data("temperature", 25.6)
server.set_data("status", "online")

# Add custom route
@server.add_route('/api/custom')
def custom_api():
    return {"message": "Hello from custom API!"}

# Start server
server.run()  # Visit http://localhost:5000
```

### Complete Integration Example

```python
from modules import ServoController, OLEDDisplay, RelayController, FlaskServer
from modules import InfraredSensor, UltrasonicSensor, MotorController
from modules.gsm import SIM800LController
from modules.ir_temp import MLX90614Sensor
from modules.scheduler import PillScheduler
import time
import threading

# Initialize components with gpiozero
servo = ServoController(pin=11)
oled = OLEDDisplay()
relay = RelayController(pin=17)
server = FlaskServer(name="Pill Dispenser Controller")
ir_sensor = InfraredSensor(pin=18)
ultrasonic = UltrasonicSensor(trigger_pin=23, echo_pin=24)
motor = MotorController(forward_pin=20, backward_pin=21)
gsm = SIM800LController(port="/dev/ttyS0", baudrate=9600)
ir_temp = MLX90614Sensor(bus_number=1, address=0x5A)
scheduler = PillScheduler()

# Add web API routes
@server.add_route('/api/servo/<int:angle>', methods=['POST'])
def control_servo(angle):
    servo.set_angle(angle)
    return {"success": True, "angle": angle}

@server.add_route('/api/relay/<action>', methods=['POST'])
def control_relay(action):
    if action == 'on':
        relay.turn_on()
    elif action == 'off':
        relay.turn_off()
    return {"success": True, "action": action}

@server.add_route('/api/distance')
def get_distance():
    distance = ultrasonic.get_distance()
    return {"distance": distance}

# Setup sensor callbacks
def motion_detected():
    oled.write_text("Motion Detected!", 0, 20)
    server.set_data("motion", True)

ir_sensor.when_motion = motion_detected

# Start web server in background
server.run(threaded=True)

# Update display with status
while True:
    oled.clear(show=False)
    oled.write_text("Pi Controller", 0, 0, show=False)
    oled.write_text(f"Time: {time.strftime('%H:%M:%S')}", 0, 20, show=True)
    time.sleep(1)
```

## 🎯 Running the Complete Demo

Run the comprehensive demo that showcases all modules:

```bash
python tests/demo_all_modules.py
```

This demo will:
- Initialize all hardware components
- Start a web server with control interface
- Run demonstration sequences
- Provide real-time status updates
- Enable remote control via web browser

**Web Interface URLs:**
- Dashboard: `http://your-pi-ip:5000`
- Control Panel: `http://your-pi-ip:5000/control`
- API Status: `http://your-pi-ip:5000/api/status`

## 🖥️ Command Line Interface

The package includes CLI tools for quick hardware testing:

### Main Demo Command
```bash
# Run complete hardware demo
modules-demo

# Run quick demo
modules-demo --quick
```

### Individual Component Commands

**Servo Control:**
```bash
# Set servo to specific angle
modules-servo --pin 11 --angle 90

# Perform sweep operation
modules-servo --pin 11 --sweep

# Center servo
modules-servo --pin 11 --center
```

**OLED Display:**
```bash
# Display text
modules-oled --text "Hello Raspberry Pi!"

# Clear display
modules-oled --clear

# Run OLED demo
modules-oled --demo
```

**Relay Control:**
```bash
# Turn relay on
modules-relay --pin 17 --on

# Turn relay off
modules-relay --pin 17 --off

# Toggle relay
modules-relay --pin 17 --toggle

# Pulse relay for 3 seconds
modules-relay --pin 17 --pulse 3.0
```

**Web Server:**
```bash
# Start web server
modules-server --port 5000 --host 0.0.0.0

# Start with debug mode
modules-server --port 8080 --debug
```

**GSM Module (SIM800L):**
```bash
# Send SMS
modules-gsm --phone "+1234567890" --message "Time to take your medication"

# Check GSM status
modules-gsm --status

# Check signal strength
modules-gsm --signal
```

**IR Temperature Sensor:**
```bash
# Read temperature once
modules-ir-temp --read

# Monitor temperature continuously
modules-ir-temp --monitor
```

**Pill Scheduler:**
```bash
# Add new medication schedule
modules-scheduler --add --name "Aspirin" --dosage "1 pill" --times "08:00 20:00" --days "monday wednesday friday"

# List all medication schedules
modules-scheduler --list

# Show next scheduled medication
modules-scheduler --next

# Start scheduler in background
modules-scheduler --start
```

## 🔧 Hardware Connections

### Servo Motor
- **Signal Pin**: GPIO 11 (Physical pin 23)
- **Power**: 5V (Physical pin 2)
- **Ground**: GND (Physical pin 6)

### OLED Display (I2C)
- **VCC**: 3.3V (Physical pin 1)
- **GND**: GND (Physical pin 9)
- **SDA**: GPIO 2 (Physical pin 3)
- **SCL**: GPIO 3 (Physical pin 5)

### Relay Module
- **Signal Pin**: GPIO 17 (Physical pin 11)
- **VCC**: 5V (Physical pin 4)
- **GND**: GND (Physical pin 14)

### SIM800L GSM Module (UART)
- **VCC**: 5V via level converter or dedicated power supply (3.7-4.2V)
- **GND**: GND (Physical pin 20)
- **TX**: GPIO 14 (UART0_TXD, Physical pin 8)
- **RX**: GPIO 15 (UART0_RXD, Physical pin 10)
- **RST**: GPIO 4 (Optional, Physical pin 7)

### MLX90614 IR Temperature Sensor (GY-906, I2C)
- **VCC**: 3.3V (Physical pin 1)
- **GND**: GND (Physical pin 6)
- **SDA**: GPIO 2 (I2C1 SDA, Physical pin 3)
- **SCL**: GPIO 3 (I2C1 SCL, Physical pin 5)
- **Button**: GPIO 21 (Optional for triggering readings, Physical pin 40)

## 📚 API Reference

### ServoController (gpiozero-based)
- `__init__(pin, min_pulse_width=1/1000, max_pulse_width=2/1000)`
- `set_angle(angle)` - Set servo to specific angle (0-180°)
- `move_to_position(angle, delay=0.5)` - Move with delay
- `sweep(start_angle=0, end_angle=180, step=10, delay=0.1, cycles=1)`
- `center(delay=0.5)` - Move to 90° position
- `cleanup()` - Clean up resources

### OLEDDisplay
- `__init__(width=128, height=64, i2c_address=0x3C)`
- `write_text(text, x=0, y=0, font=None, fill=255, show=True)`
- `write_multiline(lines, x=0, y=0, line_height=10, ...)`
- `draw_rectangle(x, y, width, height, outline=255, fill=None)`
- `draw_circle(x, y, radius, outline=255, fill=None)`
- `scroll_text(text, y=0, delay=0.1, cycles=1)`
- `progress_bar(progress, x=0, y=30, width=100, height=10)`

### RelayController (gpiozero-based)
- `__init__(pin, active_high=False, initial_value=False)`
- `turn_on()` - Turn relay ON
- `turn_off()` - Turn relay OFF
- `toggle()` - Toggle relay state
- `pulse(duration=1.0)` - Turn ON for duration then OFF
- `blink(on_time=0.5, off_time=0.5, cycles=5)`
- `timed_on(duration, callback=None)` - Non-blocking timed operation

### InfraredSensor (gpiozero-based)
- `__init__(pin, pull_up=True, bounce_time=0.1)`
- `when_motion` - Callback for motion detection
- `when_no_motion` - Callback for no motion
- `start_monitoring()` - Start continuous monitoring
- `stop_monitoring()` - Stop monitoring
- `get_detection_count()` - Get number of detections

### UltrasonicSensor (gpiozero-based) 
- `__init__(trigger_pin, echo_pin, max_distance=4.0)`
- `get_distance()` - Get single distance reading
- `start_monitoring()` - Start continuous monitoring
- `stop_monitoring()` - Stop monitoring
- `when_in_range` - Callback for object in range
- `when_out_of_range` - Callback for object out of range

### MotorController (gpiozero-based)
- `__init__(forward_pin, backward_pin, enable_pin=None)`
- `forward(speed=1.0)` - Move forward at speed
- `backward(speed=1.0)` - Move backward at speed
- `stop()` - Stop motor
- `set_speed(speed)` - Set motor speed (-1.0 to 1.0)

### SIM800LController
- `__init__(port="/dev/ttyS0", baudrate=9600, timeout=10)`
- `send_sms(phone_number, message)` - Send SMS message
- `send_medication_reminder(phone, medication, dosage=None)` - Send medication reminder
- `send_emergency_alert(phone, message)` - Send emergency alert
- `get_network_status()` - Get network registration status
- `get_signal_strength()` - Get signal strength in dBm
- `get_battery_status()` - Get battery level and voltage
- `cleanup()` - Close connection and clean up

### MLX90614Sensor
- `__init__(bus_number=1, address=0x5A, button_pin=21, retries=3)`
- `get_temperatures()` - Get ambient and object temperatures
- `get_ambient_temperature()` - Get ambient temperature
- `get_object_temperature()` - Get object temperature
- `is_temperature_safe(temp)` - Check if temperature is in safe range
- `start_monitoring(interval=1.0)` - Start continuous monitoring
- `stop_monitoring()` - Stop monitoring
- `cleanup()` - Clean up resources

### PillScheduler
- `__init__(db_path=None)`
- `add_schedule(name, dosage, times, days, start_date=None, end_date=None)` - Add schedule
- `get_schedule(schedule_id)` - Get schedule by ID
- `get_all_schedules()` - Get all schedules
- `update_schedule(schedule_id, **kwargs)` - Update schedule
- `delete_schedule(schedule_id)` - Delete schedule
- `get_next_medication()` - Get next scheduled medication
- `record_intake(schedule_id, status)` - Record medication intake
- `start_scheduler(daemon=True)` - Start scheduler daemon
- `stop_scheduler()` - Stop scheduler daemon

### FlaskServer
- `__init__(name="RaspberryPi Server", host="0.0.0.0", port=5000)`
- `set_data(key, value)` - Set shared data
- `get_data(key, default=None)` - Get shared data
- `add_route(rule, methods=['GET'])` - Add custom route decorator
- `run(threaded=False)` - Start server

## 🔍 Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   sudo usermod -a -G gpio,i2c,spi $USER
   # Then log out and back in
   ```

2. **I2C Not Working**
   ```bash
   sudo raspi-config  # Enable I2C
   sudo i2cdetect -y 1  # Check for devices
   ```

3. **GPIO Already in Use**
   ```python
   import RPi.GPIO as GPIO
   GPIO.cleanup()  # Clean up before running
   ```

4. **Web Server Port in Use**
   ```bash
   sudo lsof -i :5000  # Check what's using port 5000
   # Or use a different port in FlaskServer(port=8080)
   ```

## 📝 Examples Directory

Check the `tests/` directory for demo and test files:
- `demo_all_modules.py` - Comprehensive demo showcasing all modules
- `test_basic.py` - Basic import and functionality tests

## 🤝 Contributing

1. Fork the repository at https://github.com/deJames-13/modules.py
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

**Author:** deJames-13  
**Email:** de.james013@gmail.com  
**GitHub:** https://github.com/deJames-13/modules.py

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify hardware connections
3. Check the tests directory for reference implementations
4. Ensure all dependencies are installed
5. Open an issue at https://github.com/deJames-13/modules.py/issues

---

**Happy coding with your Raspberry Pi! 🍓**

*modules.py - A python package for Project Botibot by deJames-13*
