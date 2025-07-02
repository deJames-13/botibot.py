#!/usr/bin/env python3
"""
MLX90614 IR Temperature Sensor Controller for Pill Dispenser Robot.

This module provides temperature monitoring for medication storage and patient health
using the MLX90614 infrared temperature sensor (GY-906 module) with gpiozero integration.

Based on Adafruit's MLX90614 library:
https://www.adafruit.com/product/1747
https://www.adafruit.com/product/1748
"""

import board
import adafruit_mlx90614
from gpiozero import Button
import time
import logging
from typing import Optional, Tuple, Dict, Callable, List
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLX90614Sensor:
    """
    A controller for MLX90614 IR temperature sensor with button trigger for pill dispenser.
    
    Features:
    - Monitor ambient and object temperatures
    - Button-triggered temperature readings
    - Temperature thresholds for medication storage
    - Patient body temperature monitoring
    - Data logging and alerts
    """

    def __init__(self, button_pin: int = 21, address: int = 0x5A, 
                 retries: int = 3, retry_delay: float = 0.1,
                 use_stemma_qt: bool = False):
        """
        Initialize the MLX90614 sensor and button input.

        Args:
            button_pin (int): GPIO pin for the button using gpiozero (default: 21)
            address (int): I2C address of the sensor (default: 0x5A)
            retries (int): Number of retries for I2C communication
            retry_delay (float): Delay between retries in seconds
            use_stemma_qt (bool): Use STEMMA QT connector instead of standard I2C pins
        """
        self.address = address
        self.button_pin = button_pin
        self.retries = retries
        self.retry_delay = retry_delay
        self.use_stemma_qt = use_stemma_qt
        self.i2c = None
        self.sensor = None
        self.button = None
        self.logger = logging.getLogger(__name__)
        
        # Temperature thresholds for medication storage (Celsius)
        self.med_temp_min = 15.0  # Minimum safe temperature for pills
        self.med_temp_max = 25.0  # Maximum safe temperature for pills
        self.fever_threshold = 38.0  # Fever threshold for patient monitoring
        
        # Callbacks
        self.on_button_press: Optional[Callable] = None
        self.on_temperature_alert: Optional[Callable] = None
        self.on_fever_detected: Optional[Callable] = None
        
        # Temperature history
        self.temperature_history = []
        self.max_history_size = 100

        self._initialize_sensor()
        self._initialize_button()

    def _initialize_sensor(self) -> None:
        """Initialize the I2C bus and sensor connection."""
        try:
            # The MLX90614 only works at the default I2C bus speed of 100kHz
            if self.use_stemma_qt:
                i2c = board.STEMMA_I2C()  # For using built-in STEMMA QT connector
                self.logger.info("Using STEMMA QT connector for I2C")
            else:
                i2c = board.I2C()  # Uses board.SCL and board.SDA
                self.logger.info("Using standard I2C pins")
                
            # Try to connect with retries
            for attempt in range(self.retries):
                try:
                    self.sensor = adafruit_mlx90614.MLX90614(i2c, address=self.address)
                    # Test the connection by reading temperatures
                    _ = self.sensor.ambient_temperature
                    _ = self.sensor.object_temperature
                    self.logger.info("MLX90614 sensor initialized successfully")
                    self.i2c = i2c  # Save reference for cleanup
                    return
                except Exception as e:
                    self.logger.warning(f"Sensor connection attempt {attempt+1}/{self.retries} failed: {str(e)}")
                    if attempt < self.retries - 1:
                        time.sleep(self.retry_delay)
                    
            raise RuntimeError("Failed to connect to MLX90614 after multiple attempts")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize MLX90614 sensor: {str(e)}")
            raise RuntimeError(f"Sensor initialization failed: {str(e)}")

    def _initialize_button(self) -> None:
        """Initialize the button using gpiozero."""
        try:
            self.button = Button(self.button_pin, pull_up=False)
            self.button.when_pressed = self._on_button_pressed
            self.logger.info(f"Button initialized on GPIO {self.button_pin} with gpiozero")
        except Exception as e:
            self.logger.error(f"Failed to initialize button: {str(e)}")
            raise RuntimeError(f"Button initialization failed: {str(e)}")
    def _on_button_pressed(self) -> None:
        """Handle button press event."""
        self.logger.info("Button pressed - taking temperature reading")
        
        # Get temperature readings
        ambient_temp, object_temp = self.get_temperatures()
        
        if ambient_temp is not None and object_temp is not None:
            # Store in history
            timestamp = datetime.now()
            reading = {
                'timestamp': timestamp.isoformat(),
                'ambient': ambient_temp,
                'object': object_temp,
                'type': 'button_triggered'
            }
            
            self._add_to_history(reading)
            
            # Check for alerts
            self._check_temperature_alerts(ambient_temp, object_temp)
            
            # Call user callback if set
            if self.on_button_press:
                self.on_button_press(ambient_temp, object_temp)
        else:
            self.logger.error("Failed to read temperatures on button press")

    def _add_to_history(self, reading: Dict) -> None:
        """Add temperature reading to history."""
        self.temperature_history.append(reading)
        
        # Keep only recent readings
        if len(self.temperature_history) > self.max_history_size:
            self.temperature_history = self.temperature_history[-self.max_history_size:]

    def _check_temperature_alerts(self, ambient_temp: float, object_temp: float) -> None:
        """Check temperature readings against thresholds and trigger alerts."""
        # Check medication storage temperature
        if ambient_temp < self.med_temp_min or ambient_temp > self.med_temp_max:
            alert_msg = f"Medication storage temperature alert: {ambient_temp:.1f}°C (safe range: {self.med_temp_min}-{self.med_temp_max}°C)"
            self.logger.warning(alert_msg)
            
            if self.on_temperature_alert:
                self.on_temperature_alert('STORAGE_TEMP', ambient_temp, alert_msg)
        
        # Check for fever (assuming object temp is body temperature)
        if object_temp >= self.fever_threshold:
            alert_msg = f"Fever detected: {object_temp:.1f}°C (threshold: {self.fever_threshold}°C)"
            self.logger.warning(alert_msg)
            
            if self.on_fever_detected:
                self.on_fever_detected(object_temp, alert_msg)

    def get_medication_storage_status(self) -> Dict[str, any]:
        """
        Get medication storage temperature status.

        Returns:
            Dict: Storage status information
        """
        ambient_temp = self.get_ambient_temperature()
        
        if ambient_temp is None:
            return {
                'status': 'ERROR',
                'temperature': None,
                'safe': False,
                'message': 'Failed to read temperature'
            }
        
        safe_temp = self.med_temp_min <= ambient_temp <= self.med_temp_max
        
        if safe_temp:
            status = 'SAFE'
            message = f'Storage temperature optimal: {ambient_temp:.1f}°C'
        else:
            status = 'WARNING'
            if ambient_temp < self.med_temp_min:
                message = f'Storage too cold: {ambient_temp:.1f}°C (min: {self.med_temp_min}°C)'
            else:
                message = f'Storage too warm: {ambient_temp:.1f}°C (max: {self.med_temp_max}°C)'
        
        return {
            'status': status,
            'temperature': ambient_temp,
            'safe': safe_temp,
            'message': message,
            'min_safe_temp': self.med_temp_min,
            'max_safe_temp': self.med_temp_max
        }

    def take_patient_temperature(self) -> Dict[str, any]:
        """
        Take patient body temperature reading.

        Returns:
            Dict: Patient temperature information
        """
        object_temp = self.get_object_temperature()
        
        if object_temp is None:
            return {
                'status': 'ERROR',
                'temperature': None,
                'fever': False,
                'message': 'Failed to read temperature'
            }
        
        has_fever = object_temp >= self.fever_threshold
        
        # Store reading
        reading = {
            'timestamp': datetime.now().isoformat(),
            'ambient': self.get_ambient_temperature(),
            'object': object_temp,
            'type': 'patient_reading'
        }
        self._add_to_history(reading)
        
        if has_fever:
            status = 'FEVER'
            message = f'Fever detected: {object_temp:.1f}°C'
        else:
            status = 'NORMAL'
            message = f'Normal temperature: {object_temp:.1f}°C'
        
        return {
            'status': status,
            'temperature': object_temp,
            'fever': has_fever,
            'message': message,
            'fever_threshold': self.fever_threshold
        }

    def get_temperature_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get temperature reading history.

        Args:
            limit (Optional[int]): Maximum number of readings to return

        Returns:
            List[Dict]: Temperature readings
        """
        if limit:
            return self.temperature_history[-limit:]
        return self.temperature_history.copy()

    def continuous_monitoring(self, interval: float = 60.0, duration: Optional[float] = None) -> None:
        """
        Start continuous temperature monitoring.

        Args:
            interval (float): Time between readings in seconds
            duration (Optional[float]): Total monitoring duration in seconds (None for indefinite)
        """
        def monitor():
            start_time = time.time()
            self.logger.info(f"Starting continuous monitoring (interval: {interval}s)")
            
            try:
                while True:
                    # Check if duration exceeded
                    if duration and (time.time() - start_time) >= duration:
                        break
                    
                    # Take reading
                    ambient_temp, object_temp = self.get_temperatures()
                    
                    if ambient_temp is not None and object_temp is not None:
                        # Store reading
                        reading = {
                            'timestamp': datetime.now().isoformat(),
                            'ambient': ambient_temp,
                            'object': object_temp,
                            'type': 'continuous_monitoring'
                        }
                        self._add_to_history(reading)
                        
                        # Check alerts
                        self._check_temperature_alerts(ambient_temp, object_temp)
                        
                        self.logger.debug(f"Ambient: {ambient_temp:.1f}°C, Object: {object_temp:.1f}°C")
                    
                    time.sleep(interval)
                    
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def wait_for_button_press(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for button press with gpiozero.

        Args:
            timeout (Optional[float]): Maximum time to wait for button press in seconds

        Returns:
            bool: True if button was pressed, False if timed out
        """
        try:
            self.logger.info("Waiting for button press...")
            if timeout:
                # Use button.wait_for_press with timeout
                return self.button.wait_for_press(timeout)
            else:
                # Wait indefinitely
                self.button.wait_for_press()
                return True
        except Exception as e:
            self.logger.error(f"Error waiting for button press: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Close the I2C bus and cleanup resources."""
        # Adafruit CircuitPython devices typically don't need explicit cleanup,
        # but we'll set the reference to None to help garbage collection
        if self.sensor:
            try:
                self.sensor = None
                self.logger.info("MLX90614 sensor reference cleared")
            except Exception as e:
                self.logger.error(f"Error cleaning up sensor: {str(e)}")
        
        if self.button:
            try:
                self.button.close()
                self.logger.info("Button GPIO cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up button: {str(e)}")

    def get_temperatures(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get both ambient and object temperatures.

        Returns:
            Tuple[Optional[float], Optional[float]]: Ambient and object temperatures in Celsius
        """
        try:
            if not self.sensor:
                self.logger.error("Sensor not initialized")
                return None, None
                
            ambient_temp = self.sensor.ambient_temperature
            object_temp = self.sensor.object_temperature
            
            return ambient_temp, object_temp
        except Exception as e:
            self.logger.error(f"Error reading temperatures: {str(e)}")
            return None, None
            
    def get_ambient_temperature(self) -> Optional[float]:
        """
        Get ambient temperature.

        Returns:
            Optional[float]: Ambient temperature in Celsius
        """
        try:
            if not self.sensor:
                self.logger.error("Sensor not initialized")
                return None
                
            return self.sensor.ambient_temperature
        except Exception as e:
            self.logger.error(f"Error reading ambient temperature: {str(e)}")
            return None
            
    def get_object_temperature(self) -> Optional[float]:
        """
        Get object temperature.

        Returns:
            Optional[float]: Object temperature in Celsius
        """
        try:
            if not self.sensor:
                self.logger.error("Sensor not initialized")
                return None
                
            return self.sensor.object_temperature
        except Exception as e:
            self.logger.error(f"Error reading object temperature: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    try:
        print("=== MLX90614 Temperature Sensor Demo ===")
        print("Initializing sensor with Adafruit library...")
        
        # Initialize temperature sensor
        # For Raspberry Pi with standard I2C pins
        temp_sensor = MLX90614Sensor(button_pin=21)
        
        # For devices with STEMMA QT connector
        # temp_sensor = MLX90614Sensor(button_pin=21, use_stemma_qt=True)
        
        # Basic temperature reading (Adafruit example)
        ambient_temp = temp_sensor.get_ambient_temperature()
        object_temp = temp_sensor.get_object_temperature()
        print(f"Basic Reading:")
        print(f"  Ambient Temperature: {ambient_temp:.2f}°C")
        print(f"  Object Temperature: {object_temp:.2f}°C")
        print()
        
        # Set up callbacks for advanced features
        def on_button_callback(ambient, object):
            print(f"Button pressed! Ambient: {ambient:.1f}°C, Object: {object:.1f}°C")
        
        def on_fever_callback(temp, message):
            print(f"FEVER ALERT: {message}")
        
        def on_temp_alert_callback(alert_type, temp, message):
            print(f"TEMPERATURE ALERT ({alert_type}): {message}")
        
        temp_sensor.on_button_press = on_button_callback
        temp_sensor.on_fever_detected = on_fever_callback
        temp_sensor.on_temperature_alert = on_temp_alert_callback
        
        # Check medication storage status
        print("Checking medication storage conditions...")
        storage_status = temp_sensor.get_medication_storage_status()
        print(f"Storage Status: {storage_status['status']}")
        print(f"Temperature: {storage_status['temperature']:.1f}°C")
        print(f"Safe: {storage_status['safe']}")
        print(f"Message: {storage_status['message']}")
        print()
        
        # Start continuous monitoring for 2 minutes
        print("Starting continuous monitoring (2 minutes)...")
        temp_sensor.continuous_monitoring(interval=10.0, duration=120.0)
        
        # Wait for button press
        print("Press the button to take a patient temperature reading (30 sec timeout)...")
        if temp_sensor.wait_for_button_press(timeout=30.0):
            patient_temp = temp_sensor.take_patient_temperature()
            print(f"Patient Temperature: {patient_temp['temperature']:.1f}°C")
            print(f"Status: {patient_temp['status']}")
            print(f"Fever: {patient_temp['fever']}")
        else:
            print("No button press detected within timeout")
        
        # Show temperature history
        history = temp_sensor.get_temperature_history(limit=5)
        print(f"\nRecent readings: {len(history)} entries")
        for reading in history:
            print(f"  {reading['timestamp']}: Ambient={reading['ambient']:.1f}°C, Object={reading['object']:.1f}°C")
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'temp_sensor' in locals():
            temp_sensor.cleanup()
            print("Sensor resources cleaned up")