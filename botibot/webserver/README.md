# Pill Dispenser Dashboard

A web-based dashboard for the Botibot Pill Dispenser Robot that integrates with various sensors and the GSM module to provide a complete patient health monitoring and medication management system.

## Features

- **Step-by-step Patient Session**:
  1. Heart Rate Monitoring (mock data)
  2. Temperature Measurement (using IR temperature sensor)
  3. Alcohol Level Detection (mock data)
  4. Session Summary
  5. SMS Notification with Results

- **Hardware Integration**:
  - GSM Module (SIM800L) for SMS notifications
  - IR Temperature Sensor (MLX90614/GY-906) for patient temperature
  - Mock sensors for heart rate and alcohol level

- **Responsive Web Interface**:
  - Mobile-friendly design
  - Real-time sensor readings
  - Progress tracking
  - Session history

## Setup Requirements

1. Raspberry Pi with Python 3.6+
2. Flask web framework
3. Connected hardware:
   - SIM800L GSM module (connected to serial port)
   - MLX90614/GY-906 IR temperature sensor (connected to I2C)

## Installation

1. Install required Python packages:

```bash
pip install -r requirements.txt
```

2. Connect the hardware:
   - Connect SIM800L to UART pins (default: /dev/ttyS0)
   - Connect MLX90614 to I2C pins (SCL, SDA)

## Running the Dashboard

1. Navigate to the project directory:

```bash
cd /path/to/botibot
```

2. Run the dashboard server:

```bash
python -m modules.webserver.run_dashboard
```

3. Access the dashboard in a web browser:
   - Dashboard URL: `http://[raspberry_pi_ip]:5000/pill-dispenser`
   - Control Panel: `http://[raspberry_pi_ip]:5000/control`

## API Endpoints

The dashboard exposes the following REST API endpoints:

- `GET /api/heart-rate` - Get heart rate reading (mock)
- `GET /api/temperature` - Get temperature reading from IR sensor
- `GET /api/alcohol-level` - Get alcohol level reading (mock)
- `POST /api/send-sms` - Send SMS with session results
- `POST /api/session` - Save a complete session

## Hardware Configuration

### GSM Module (SIM800L)

The GSM module is configured for:
- Serial port: `/dev/ttyS0` (default)
- Baud rate: 9600
- Text mode for SMS

### IR Temperature Sensor (MLX90614)

The IR temperature sensor is configured for:
- I2C address: 0x5A (default)
- Button trigger pin: GPIO 21
- Ambient and object temperature readings

## Troubleshooting

- **SMS not sending**: Check SIM card balance, signal strength, and serial connection
- **Temperature sensor not working**: Verify I2C connection and address
- **Web dashboard not loading**: Ensure Flask server is running and check network connectivity

## Development

To extend or modify this dashboard:

1. Main dashboard code: `modules/webserver/pill_dispenser_dashboard.py`
2. Server runner: `modules/webserver/run_dashboard.py`
3. HTML/CSS/JS: Located within the dashboard template in `pill_dispenser_dashboard.py`

## License

This project is part of the Botibot system and is licensed under the terms included in the project's LICENSE file.
