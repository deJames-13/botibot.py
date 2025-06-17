# botibot.py

A python package for Project Botibot - A collection of reusable, class-based utility modules for common Raspberry Pi microcontroller projects. These modules provide easy-to-use interfaces for controlling servos, OLED displays, relays, and web servers.

## 📦 Modules Overview

### 1. ServoController (`modules/servo/`)
- **Purpose**: Control servo motors with PWM signals
- **Features**: 
  - Precise angle control (0-180°)
  - Sweep operations
  - Context manager support
  - Multiple positioning methods

### 2. OLEDDisplay (`modules/oled/`)
- **Purpose**: Control SSD1306-based I2C OLED displays
- **Features**: 
  - Text and graphics rendering
  - Multi-line text support
  - Scrolling and blinking effects
  - Progress bars and status displays

### 3. RelayController (`modules/relay/`)
- **Purpose**: Control relay modules for switching circuits
- **Features**: 
  - Single and multiple relay control
  - Timed operations
  - Pattern sequences (wave, blink)
  - Background timer support

### 4. FlaskServer (`modules/webserver/`)
- **Purpose**: Create configurable web interfaces and APIs
- **Features**: 
  - Beautiful responsive web dashboard
  - RESTful API endpoints
  - Real-time data sharing
  - Custom route support

## 🛠 Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install the package
pip install raspberry-pi-modules

# Or install with all optional dependencies
pip install raspberry-pi-modules[full]
```

### Option 2: Install from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/raspberrypi-lab/raspberry-pi-modules.git
   cd raspberry-pi-modules
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
   rpi-demo --help
   rpi-servo --help
   rpi-oled --help
   ```

## 🚀 Quick Start

### Basic Usage Examples

#### Servo Control
```python
from modules import ServoController

# Basic servo control
with ServoController(pin=11) as servo:
    servo.move_to_position(0, delay=1)    # 0 degrees
    servo.move_to_position(90, delay=1)   # 90 degrees
    servo.move_to_position(180, delay=1)  # 180 degrees
    servo.center()                        # Back to center
```

#### OLED Display
```python
from modules import OLEDDisplay

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
from modules import RelayController

# Basic relay control
with RelayController(pin=17) as relay:
    relay.turn_on()
    time.sleep(2)
    relay.turn_off()
    
    # Pulse operation
    relay.pulse(duration=3.0)
    
    # Blinking
    relay.blink(on_time=0.5, off_time=0.5, cycles=5)
```

#### Web Server
```python
from modules import FlaskServer

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
import time
import threading

# Initialize components
servo = ServoController(pin=11)
oled = OLEDDisplay()
relay = RelayController(pin=17)
server = FlaskServer(name="Pi Lab Controller")

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
python demo_all_modules.py
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
rpi-demo

# Run quick demo
rpi-demo --quick
```

### Individual Component Commands

**Servo Control:**
```bash
# Set servo to specific angle
rpi-servo --pin 11 --angle 90

# Perform sweep operation
rpi-servo --pin 11 --sweep

# Center servo
rpi-servo --pin 11 --center
```

**OLED Display:**
```bash
# Display text
rpi-oled --text "Hello Raspberry Pi!"

# Clear display
rpi-oled --clear

# Run OLED demo
rpi-oled --demo
```

**Relay Control:**
```bash
# Turn relay on
rpi-relay --pin 17 --on

# Turn relay off
rpi-relay --pin 17 --off

# Toggle relay
rpi-relay --pin 17 --toggle

# Pulse relay for 3 seconds
rpi-relay --pin 17 --pulse 3.0
```

**Web Server:**
```bash
# Start web server
rpi-server --port 5000 --host 0.0.0.0

# Start with debug mode
rpi-server --port 8080 --debug
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

## 📚 API Reference

### ServoController
- `__init__(pin, pin_mode=GPIO.BOARD, frequency=50)`
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

### RelayController
- `__init__(pin, pin_mode=GPIO.BCM, active_low=True)`
- `turn_on()` - Turn relay ON
- `turn_off()` - Turn relay OFF
- `toggle()` - Toggle relay state
- `pulse(duration=1.0)` - Turn ON for duration then OFF
- `blink(on_time=0.5, off_time=0.5, cycles=5)`
- `timed_on(duration, callback=None)` - Non-blocking timed operation

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

Check the `examples/` directory for the original sample codes that these modules are based on:
- `servo.py` - Original servo example
- `oled.py` - Original OLED example  
- `relay.py` - Original relay example
- `webserver.py` - Original web server example

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes as part of the Microcontroller Lab course.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify hardware connections
3. Check the examples directory for reference
4. Ensure all dependencies are installed

---

**Happy coding with your Raspberry Pi! 🍓**
