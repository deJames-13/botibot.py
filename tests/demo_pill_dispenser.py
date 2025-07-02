#!/usr/bin/env python3
"""
Pill Dispenser Dashboard Demo.

This script runs a demo of the Pill Dispenser Dashboard with mock hardware.
It allows testing the dashboard interface without physical sensors or GSM module.
"""

import os
import sys
import time
import logging
import threading
import random
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from botibot.webserver.flask_server import FlaskServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockGSM:
    """Mock GSM module for testing."""
    
    def send_sms(self, phone_number, message):
        """Mock sending an SMS."""
        logger.info(f"MOCK SMS to {phone_number}:")
        logger.info("-" * 40)
        logger.info(message)
        logger.info("-" * 40)
        return True
    
    def cleanup(self):
        """Mock cleanup."""
        logger.info("Mock GSM module cleaned up")

class MockTempSensor:
    """Mock temperature sensor for testing."""
    
    def get_temperatures(self):
        """Get mock ambient and object temperatures."""
        return 25.0, 36.8
    
    def get_ambient_temperature(self):
        """Get mock ambient temperature."""
        return 25.0
    
    def get_object_temperature(self):
        """Get mock object temperature."""
        return 36.8
    
    def take_patient_temperature(self):
        """Take mock patient temperature reading."""
        temp = random.uniform(36.5, 37.5)
        has_fever = temp >= 38.0
        
        if has_fever:
            status = 'FEVER'
            message = f'Fever detected: {temp:.1f}°C'
        else:
            status = 'NORMAL'
            message = f'Normal temperature: {temp:.1f}°C'
        
        return {
            'status': status,
            'temperature': temp,
            'fever': has_fever,
            'message': message,
            'fever_threshold': 38.0
        }
    
    def cleanup(self):
        """Mock cleanup."""
        logger.info("Mock temperature sensor cleaned up")

def patch_modules():
    """Patch hardware modules with mock versions for demo."""
    # First, back up original module imports
    import modules.webserver.pill_dispenser_dashboard as pd
    
    # Save original module references
    original_gsm = pd.SIM800LController
    original_temp = pd.MLX90614Sensor
    
    # Replace with mocks
    pd.SIM800LController = MockGSM
    pd.MLX90614Sensor = MockTempSensor
    
    # Return original modules for restoration
    return (original_gsm, original_temp)

def restore_modules(originals):
    """Restore original module imports."""
    import modules.webserver.pill_dispenser_dashboard as pd
    
    # Restore original modules
    pd.SIM800LController = originals[0]
    pd.MLX90614Sensor = originals[1]

def simulate_sensor_data(server):
    """Simulate changing sensor data in background."""
    while True:
        # Update random mock sensor data
        heart_rate = random.randint(65, 85)
        temperature = round(random.uniform(36.5, 37.5), 1)
        alcohol_level = round(random.uniform(0, 0.3), 2)
        
        # Update server data
        server.update_data({
            "last_heart_rate": heart_rate,
            "last_temperature": temperature,
            "last_alcohol_level": alcohol_level,
            "last_update": datetime.now().isoformat()
        })
        
        # Sleep for a while
        time.sleep(10)

def main():
    """Run the demo dashboard."""
    try:
        logger.info("Starting Pill Dispenser Dashboard Demo")
        
        # Patch hardware modules with mocks
        original_modules = patch_modules()
        
        # Import after patching
        from botibot.webserver.pill_dispenser_dashboard import register_with_app, cleanup
        
        # Create Flask server instance
        server = FlaskServer(
            name="Pill Dispenser Demo Dashboard", 
            port=5000, 
            debug=True
        )
        
        # Register the pill dispenser dashboard with the server
        register_with_app(server.app)
        
        # Add some initial data
        server.set_data("server_status", "running")
        server.set_data("pill_dispenser_status", "demo_mode")
        server.set_data("is_demo", True)
        
        # Start simulating sensor data in background
        sim_thread = threading.Thread(target=simulate_sensor_data, args=(server,), daemon=True)
        sim_thread.start()
        
        # Display info
        print("=" * 60)
        print(" 🤖 PILL DISPENSER DASHBOARD DEMO 🤖")
        print("=" * 60)
        print("This is running with mock hardware for demonstration")
        print(f"Dashboard URL: http://{server.host}:{server.port}/pill-dispenser")
        print(f"Control Panel: http://{server.host}:{server.port}/control")
        print(f"Main Dashboard: http://{server.host}:{server.port}/")
        print("=" * 60)
        print("Press CTRL+C to exit")
        
        # Start the server
        server.run()
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        # Clean up
        cleanup()
        
        # Restore original modules
        restore_modules(original_modules)
        
        logger.info("Demo cleaned up")

if __name__ == "__main__":
    main()
