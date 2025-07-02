#!/usr/bin/env python3
"""
Infrared sensor controller using gpiozero library.

This module provides easy control of infrared sensors including
motion detection, proximity sensing, and line following capabilities.
"""

from gpiozero import DigitalInputDevice, MCP3008
from time import sleep, time
import threading
import logging
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfraredSensor:
    """
    A reusable infrared sensor controller class using gpiozero.

    This class provides easy control of infrared sensors with support for
    motion detection, proximity sensing, and various callback functions.
    """

    def __init__(self, pin, pull_up=True, bounce_time=0.1):
        """
        Initialize the infrared sensor controller.

        Args:
            pin (int): GPIO pin number for the sensor (BCM numbering)
            pull_up (bool): Use pull-up resistor (default: True)
            bounce_time (float): Debounce time in seconds (default: 0.1)
        """
        self.pin = pin
        self.bounce_time = bounce_time
        self.sensor = None
        self.is_initialized = False
        self._detection_callback = None
        self._no_detection_callback = None
        self._monitoring = False
        self._monitor_thread = None
        self._detection_count = 0
        self._last_detection_time = None

        try:
            # Initialize sensor
            self.sensor = DigitalInputDevice(
                pin, 
                pull_up=pull_up,
                bounce_time=bounce_time
            )
            
            # Set up event handlers
            self.sensor.when_activated = self._on_detection
            self.sensor.when_deactivated = self._on_no_detection
            
            self.is_initialized = True
            logger.info(f"Infrared sensor initialized on GPIO pin {pin}")
            
        except Exception as e:
            logger.error(f"Failed to initialize infrared sensor on pin {pin}: {e}")
            raise

    def _on_detection(self):
        """Internal method called when motion is detected."""
        self._detection_count += 1
        self._last_detection_time = time()
        
        logger.debug(f"Motion detected on pin {self.pin}")
        
        if self._detection_callback:
            try:
                self._detection_callback()
            except Exception as e:
                logger.error(f"Error in detection callback: {e}")

    def _on_no_detection(self):
        """Internal method called when motion stops."""
        logger.debug(f"Motion stopped on pin {self.pin}")
        
        if self._no_detection_callback:
            try:
                self._no_detection_callback()
            except Exception as e:
                logger.error(f"Error in no detection callback: {e}")

    def is_detected(self):
        """
        Check if motion/object is currently detected.

        Returns:
            bool: True if motion/object is detected, False otherwise
        """
        if not self.is_initialized or not self.sensor:
            return False
        
        return self.sensor.is_active

    def wait_for_detection(self, timeout=None):
        """
        Wait for motion detection.

        Args:
            timeout (float): Maximum time to wait in seconds (None for indefinite)

        Returns:
            bool: True if motion detected, False if timeout
        """
        if not self.is_initialized:
            raise RuntimeError("Sensor not initialized")

        logger.info(f"Waiting for detection on pin {self.pin}...")
        
        try:
            return self.sensor.wait_for_active(timeout=timeout)
        except Exception as e:
            logger.error(f"Error waiting for detection: {e}")
            return False

    def wait_for_no_detection(self, timeout=None):
        """
        Wait for motion to stop.

        Args:
            timeout (float): Maximum time to wait in seconds (None for indefinite)

        Returns:
            bool: True if motion stopped, False if timeout
        """
        if not self.is_initialized:
            raise RuntimeError("Sensor not initialized")

        logger.info(f"Waiting for no detection on pin {self.pin}...")
        
        try:
            return self.sensor.wait_for_inactive(timeout=timeout)
        except Exception as e:
            logger.error(f"Error waiting for no detection: {e}")
            return False

    def set_detection_callback(self, callback):
        """
        Set callback function for motion detection.

        Args:
            callback (callable): Function to call when motion is detected
        """
        self._detection_callback = callback
        logger.debug("Detection callback set")

    def set_no_detection_callback(self, callback):
        """
        Set callback function for when motion stops.

        Args:
            callback (callable): Function to call when motion stops
        """
        self._no_detection_callback = callback
        logger.debug("No detection callback set")

    def get_detection_count(self):
        """
        Get the total number of detections since initialization.

        Returns:
            int: Number of detections
        """
        return self._detection_count

    def get_last_detection_time(self):
        """
        Get the timestamp of the last detection.

        Returns:
            float: Timestamp of last detection (None if no detections)
        """
        return self._last_detection_time

    def reset_detection_count(self):
        """Reset the detection counter."""
        self._detection_count = 0
        self._last_detection_time = None
        logger.debug("Detection count reset")

    def start_monitoring(self, duration=None, callback=None):
        """
        Start monitoring in a separate thread.

        Args:
            duration (float): Duration to monitor in seconds (None for indefinite)
            callback (callable): Callback with detection statistics when monitoring ends
        """
        if self._monitoring:
            logger.warning("Already monitoring")
            return

        self._monitoring = True
        
        def monitor():
            start_time = time()
            detections = 0
            
            logger.info(f"Started monitoring on pin {self.pin}")
            
            try:
                while self._monitoring:
                    if duration and (time() - start_time) >= duration:
                        break
                    
                    if self.is_detected():
                        detections += 1
                        sleep(self.bounce_time)
                    
                    sleep(0.01)  # Small sleep to prevent busy waiting
                    
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
            finally:
                self._monitoring = False
                end_time = time()
                
                if callback:
                    stats = {
                        'duration': end_time - start_time,
                        'detections': detections,
                        'total_detections': self._detection_count
                    }
                    try:
                        callback(stats)
                    except Exception as e:
                        logger.error(f"Error in monitoring callback: {e}")
                
                logger.info(f"Monitoring stopped on pin {self.pin}")

        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring."""
        if self._monitoring:
            self._monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=1.0)
            logger.info("Monitoring stopped")

    def get_status(self):
        """
        Get sensor status information.

        Returns:
            dict: Dictionary containing sensor status
        """
        return {
            'pin': self.pin,
            'is_detected': self.is_detected(),
            'detection_count': self._detection_count,
            'last_detection_time': self._last_detection_time,
            'is_monitoring': self._monitoring
        }

    def cleanup(self):
        """Clean up sensor resources."""
        self.stop_monitoring()
        
        if self.sensor and self.is_initialized:
            try:
                self.sensor.close()
                logger.info(f"Infrared sensor on pin {self.pin} cleaned up")
            except Exception as e:
                logger.error(f"Error during sensor cleanup: {e}")
            finally:
                self.is_initialized = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def __del__(self):
        """Destructor to ensure cleanup."""
        if hasattr(self, 'is_initialized') and self.is_initialized:
            self.cleanup()


class InfraredArray:
    """
    Controller for multiple infrared sensors (useful for line following).
    """

    def __init__(self, pins, pull_up=True, bounce_time=0.1):
        """
        Initialize multiple infrared sensors.

        Args:
            pins (list): List of GPIO pin numbers
            pull_up (bool): Use pull-up resistors
            bounce_time (float): Debounce time in seconds
        """
        self.pins = pins if isinstance(pins, (list, tuple)) else [pins]
        self.sensors = {}
        self.pull_up = pull_up
        self.bounce_time = bounce_time

        logger.info(f"Initializing infrared sensor array on pins: {self.pins}")

        for pin in self.pins:
            try:
                self.sensors[pin] = InfraredSensor(
                    pin=pin,
                    pull_up=pull_up,
                    bounce_time=bounce_time
                )
            except Exception as e:
                logger.error(f"Failed to initialize sensor on pin {pin}: {e}")
                self.cleanup()
                raise

    def get_sensor(self, pin):
        """
        Get individual sensor.

        Args:
            pin (int): GPIO pin number

        Returns:
            InfraredSensor: Sensor for the specified pin
        """
        if pin not in self.sensors:
            raise ValueError(f"Pin {pin} not in sensor list")
        return self.sensors[pin]

    def get_detections(self):
        """
        Get detection status for all sensors.

        Returns:
            dict: Pin numbers as keys, detection status as values
        """
        return {pin: sensor.is_detected() for pin, sensor in self.sensors.items()}

    def get_detection_pattern(self):
        """
        Get detection pattern as a binary string.

        Returns:
            str: Binary string representing detection pattern
        """
        pattern = ""
        for pin in sorted(self.pins):
            pattern += "1" if self.sensors[pin].is_detected() else "0"
        return pattern

    def wait_for_any_detection(self, timeout=None):
        """
        Wait for detection on any sensor.

        Args:
            timeout (float): Maximum time to wait

        Returns:
            int: Pin number of first sensor to detect, None if timeout
        """
        start_time = time()
        
        while True:
            for pin in self.pins:
                if self.sensors[pin].is_detected():
                    return pin
            
            if timeout and (time() - start_time) >= timeout:
                return None
            
            sleep(0.01)

    def get_line_position(self):
        """
        Calculate line position for line following (center-weighted).

        Returns:
            float: Position value (-1.0 to 1.0, 0 is center)
        """
        detections = self.get_detections()
        total_sensors = len(self.pins)
        
        if total_sensors == 0:
            return 0.0
        
        # Calculate weighted position
        total_weight = 0
        position_sum = 0
        
        for i, pin in enumerate(sorted(self.pins)):
            if detections[pin]:
                # Position from -1 to 1
                position = (i / (total_sensors - 1)) * 2 - 1
                position_sum += position
                total_weight += 1
        
        if total_weight == 0:
            return 0.0  # No detection
        
        return position_sum / total_weight

    def get_status(self):
        """
        Get status of all sensors.

        Returns:
            dict: Status information for all sensors
        """
        return {
            'sensors': {pin: sensor.get_status() for pin, sensor in self.sensors.items()},
            'detections': self.get_detections(),
            'pattern': self.get_detection_pattern(),
            'line_position': self.get_line_position()
        }

    def cleanup(self):
        """Clean up all sensor resources."""
        logger.info("Cleaning up infrared sensor array")
        for sensor in self.sensors.values():
            sensor.cleanup()
        self.sensors.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


# Example usage and testing
if __name__ == "__main__":
    import sys
    import argparse

    def demo_single_sensor(pin=24, duration=30):
        """Single sensor demonstration."""
        print(f"🔍 Infrared Sensor Demo on GPIO {pin}")
        print("-" * 35)

        try:
            with InfraredSensor(pin=pin) as sensor:
                print("✅ Sensor initialized successfully!")
                
                # Set up callbacks
                def on_detection():
                    print("🚨 Motion detected!")
                
                def on_no_detection():
                    print("✅ Motion stopped")
                
                sensor.set_detection_callback(on_detection)
                sensor.set_no_detection_callback(on_no_detection)
                
                print(f"🔍 Monitoring for {duration} seconds...")
                print("💡 Move in front of the sensor to test detection")
                print("🛑 Press Ctrl+C to stop early")
                
                # Start monitoring
                def monitor_callback(stats):
                    print(f"\n📊 Monitoring Statistics:")
                    print(f"   Duration: {stats['duration']:.1f}s")
                    print(f"   Detections: {stats['detections']}")
                
                sensor.start_monitoring(duration=duration, callback=monitor_callback)
                
                # Keep main thread alive
                try:
                    sleep(duration + 1)
                except KeyboardInterrupt:
                    print("\n⚠️  Stopping early...")
                
                print(f"\n📈 Final Stats:")
                status = sensor.get_status()
                print(f"   Total detections: {status['detection_count']}")
                if status['last_detection_time']:
                    print(f"   Last detection: {time() - status['last_detection_time']:.1f}s ago")
                
                print("✅ Single sensor demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    def demo_sensor_array(pins=[22, 23, 24], duration=30):
        """Sensor array demonstration."""
        print(f"🔍 Infrared Sensor Array Demo")
        print(f"📍 Pins: {pins}")
        print("-" * 40)

        try:
            with InfraredArray(pins=pins) as sensor_array:
                print("✅ Sensor array initialized successfully!")
                
                print(f"🔍 Monitoring for {duration} seconds...")
                print("💡 Move objects across the sensor array")
                print("🛑 Press Ctrl+C to stop early")
                
                start_time = time()
                try:
                    while (time() - start_time) < duration:
                        detections = sensor_array.get_detections()
                        pattern = sensor_array.get_detection_pattern()
                        line_pos = sensor_array.get_line_position()
                        
                        # Display status
                        status_line = f"Pattern: {pattern} | Position: {line_pos:+.2f} | "
                        status_line += " ".join([f"Pin{pin}:{'●' if det else '○'}" 
                                               for pin, det in detections.items()])
                        
                        print(f"\r{status_line}", end="", flush=True)
                        sleep(0.1)
                        
                except KeyboardInterrupt:
                    print("\n⚠️  Stopping early...")
                
                print(f"\n📊 Final Status:")
                status = sensor_array.get_status()
                for pin, sensor_status in status['sensors'].items():
                    print(f"   Pin {pin}: {sensor_status['detection_count']} detections")
                
                print("✅ Sensor array demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    # CLI interface
    parser = argparse.ArgumentParser(description="Infrared Sensor Demo")
    parser.add_argument("--pin", type=int, default=24, help="GPIO pin for single sensor (default: 24)")
    parser.add_argument("--pins", nargs='+', type=int, default=[22, 23, 24], help="GPIO pins for array demo")
    parser.add_argument("--array", action="store_true", help="Run sensor array demo")
    parser.add_argument("--duration", type=int, default=30, help="Demo duration in seconds")
    parser.add_argument("--test", action="store_true", help="Quick detection test")
    
    args = parser.parse_args()
    
    if args.test:
        # Quick test
        try:
            with InfraredSensor(pin=args.pin) as sensor:
                print(f"Testing sensor on pin {args.pin}...")
                print(f"Current detection: {'YES' if sensor.is_detected() else 'NO'}")
                print("Waiting for detection (10s timeout)...")
                if sensor.wait_for_detection(timeout=10):
                    print("✅ Detection successful!")
                else:
                    print("⏰ Timeout - no detection")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        # Run demos
        if args.array:
            demo_sensor_array(args.pins, args.duration)
        else:
            demo_single_sensor(args.pin, args.duration)
