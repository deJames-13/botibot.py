# Changelog

All notable changes to the raspberry-pi-modules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-07-02

### Added
- SIM800L GSM module for SMS notifications and pill reminders
  - SMS sending for medication reminders
  - Network status and signal strength monitoring
  - Battery monitoring capabilities
  - Emergency SMS alerts
  - CLI interface for sending messages
- MLX90614 IR Temperature sensor (GY-906) support
  - Ambient and object temperature measurement
  - Button-triggered temperature readings
  - Temperature threshold monitoring for medication storage
  - Patient temperature monitoring capabilities
  - CLI interface for temperature readings
- Pill Scheduler for medication management
  - Medication scheduling with SQLite database
  - Schedule management with multiple time/day options
  - Medication intake tracking
  - Integration with Flask server for web interface
  - Command-line interface for schedule management
- Updated CLI commands for new modules
- Comprehensive documentation for new hardware components
- Integration examples for pill dispenser applications

### Updated
- Improved Flask server with new endpoints for medication management
- Updated demo_all_modules.py to showcase new modules
- Enhanced test suite with mocks for new hardware
- Updated README.md with new module documentation
- Updated requirements.txt with new dependencies

## [1.1.0] - 2025-07-01

### Changed
- **BREAKING**: Renamed package from `botibot.py` to `modules.py`
- **BREAKING**: Replaced manual GPIO control with gpiozero library for better reliability
- Updated ServoController to use gpiozero.Servo with PiGPIO support
- Updated RelayController to use gpiozero.OutputDevice
- Updated CLI commands from `botibot-*` to `modules-*`
- Updated all import statements and examples in documentation

### Added
- InfraredSensor class for infrared motion detection
  - Motion detection with callback support
  - Proximity sensing capabilities
  - Line following functionality
  - Multiple sensor support
- UltrasonicSensor class for distance measurement
  - HC-SR04 sensor support with gpiozero.DistanceSensor
  - Accurate distance measurement with PiGPIO
  - Object detection and tracking
  - Real-time monitoring with callbacks
- MotorController class for DC motor control
  - PWM speed control with gpiozero.Motor
  - Direction control and advanced movement patterns
  - DualMotorController for robotics applications
  - Support for separate enable pins
- gpiozero library integration for all GPIO-based modules
- PiGPIO support for better performance when available

### Removed
- **BREAKING**: Removed `botibot` folder structure
- Removed TFT display references from configuration files
- Removed manual PWM and GPIO control code

### Fixed
- Improved servo control accuracy with gpiozero
- Better error handling for GPIO initialization
- More reliable relay switching with proper debouncing

## [1.0.0] - 2024-06-18

### Added
- Initial release of raspberry-pi-modules package
- ServoController class for servo motor control
  - Precise angle control (0-180°)
  - Sweep operations and pattern sequences
  - Context manager support for automatic cleanup
  - Background timer operations
- OLEDDisplay class for SSD1306 I2C displays
  - Text and graphics rendering capabilities
  - Multi-line text support with customizable spacing
  - Special effects: scrolling, blinking, progress bars
  - Status display templates and real-time updates
- RelayController class for relay module control
  - Single and multi-relay support
  - Timed operations with callback support
  - Pattern sequences (wave, blink, sequential)
  - Thread-safe background operations
- FlaskServer class for web interfaces and APIs
  - Beautiful responsive web dashboard
  - RESTful API endpoints for data management
  - Custom route support with decorators
  - Real-time data sharing between components
  - Control panel for remote hardware management
- Comprehensive documentation and examples
- CLI tools for quick hardware testing
- Complete demo application showcasing all modules
- Professional package structure with proper dependencies

### Documentation
- Complete README.md with installation and usage examples
- API reference documentation for all classes
- Hardware connection diagrams and troubleshooting guide
- Integration examples showing module combinations

### Development
- Professional Python package structure
- setuptools and pyproject.toml configuration
- Development tools integration (black, flake8, mypy, pytest)
- CI/CD ready configuration
- MIT License for open source distribution

## [Unreleased]

### Planned Features
- Support for additional hardware components (sensors, motors)
- Enhanced web interface with real-time charts
- Configuration file support
- Plugin system for custom extensions
- Docker container support
- Automated testing on actual hardware
- Performance optimizations
- Additional display drivers support
