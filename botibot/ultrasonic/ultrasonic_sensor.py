#!/usr/bin/env python3
"""
Ultrasonic distance sensor controller using gpiozero library.

This module provides easy control of ultrasonic distance sensors like HC-SR04
using the gpiozero library for accurate distance measurements.
"""

from gpiozero import DistanceSensor, Device
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep, time
import threading
import logging
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to use pigpio for better performance
try:
    Device.pin_factory = PiGPIOFactory()
    logger.info("Using PiGPIO pin factory for better ultrasonic sensor accuracy")
except Exception as e:
    logger.warning(f"PiGPIO not available, using default pin factory: {e}")


class UltrasonicSensor:
    """
    A reusable ultrasonic distance sensor controller using gpiozero.

    This class provides easy control of ultrasonic sensors with distance
    measurement, object detection, and various monitoring capabilities.
    """

    def __init__(self, trigger_pin, echo_pin, max_distance=4.0, threshold_distance=0.3):
        """
        Initialize the ultrasonic sensor controller.

        Args:
            trigger_pin (int): GPIO pin for trigger signal (BCM numbering)
            echo_pin (int): GPIO pin for echo signal (BCM numbering)
            max_distance (float): Maximum detection distance in meters (default: 4.0m)
            threshold_distance (float): Threshold for object detection in meters (default: 0.3m)
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance
        self.threshold_distance = threshold_distance
        self.sensor = None
        self.is_initialized = False
        self._monitoring = False
        self._monitor_thread = None
        self._measurements = []
        self._callbacks = {
            'object_detected': None,
            'object_lost': None,
            'distance_changed': None
        }
        self._last_distance = None
        self._object_detected = False

        try:
            # Initialize distance sensor
            self.sensor = DistanceSensor(
                echo=echo_pin,
                trigger=trigger_pin,
                max_distance=max_distance
            )
            
            self.is_initialized = True
            logger.info(f"Ultrasonic sensor initialized - Trigger: {trigger_pin}, Echo: {echo_pin}")
            logger.debug(f"Max distance: {max_distance}m, Threshold: {threshold_distance}m")
            
        except Exception as e:
            logger.error(f"Failed to initialize ultrasonic sensor: {e}")
            raise

    def get_distance(self, samples=1):
        """
        Get distance measurement.

        Args:
            samples (int): Number of samples to take for averaging (default: 1)

        Returns:
            float: Distance in meters (None if out of range)
        """
        if not self.is_initialized or not self.sensor:
            raise RuntimeError("Sensor not initialized")

        if samples == 1:
            try:
                distance = self.sensor.distance
                return distance if distance < self.max_distance else None
            except Exception as e:
                logger.error(f"Error reading distance: {e}")
                return None
        else:
            # Take multiple samples for better accuracy
            distances = []
            for _ in range(samples):
                try:
                    distance = self.sensor.distance
                    if distance < self.max_distance:
                        distances.append(distance)
                    sleep(0.01)  # Small delay between samples
                except:
                    continue
            
            if distances:
                return statistics.median(distances)
            else:
                return None

    def get_distance_cm(self, samples=1):
        """
        Get distance measurement in centimeters.

        Args:
            samples (int): Number of samples to take for averaging

        Returns:
            float: Distance in centimeters (None if out of range)
        """
        distance_m = self.get_distance(samples)
        return distance_m * 100 if distance_m is not None else None

    def get_distance_inches(self, samples=1):
        """
        Get distance measurement in inches.

        Args:
            samples (int): Number of samples to take for averaging

        Returns:
            float: Distance in inches (None if out of range)
        """
        distance_m = self.get_distance(samples)
        return distance_m * 39.3701 if distance_m is not None else None

    def is_object_detected(self, custom_threshold=None):
        """
        Check if an object is detected within threshold distance.

        Args:
            custom_threshold (float): Custom threshold distance in meters

        Returns:
            bool: True if object detected within threshold
        """
        threshold = custom_threshold if custom_threshold is not None else self.threshold_distance
        distance = self.get_distance()
        
        if distance is None:
            return False
        
        return distance <= threshold

    def wait_for_object(self, timeout=None, threshold=None):
        """
        Wait for an object to be detected within threshold.

        Args:
            timeout (float): Maximum time to wait in seconds (None for indefinite)
            threshold (float): Custom threshold distance

        Returns:
            bool: True if object detected, False if timeout
        """
        threshold = threshold if threshold is not None else self.threshold_distance
        start_time = time()
        
        logger.info(f"Waiting for object within {threshold}m...")
        
        while True:
            if self.is_object_detected(threshold):
                return True
            
            if timeout and (time() - start_time) >= timeout:
                return False
            
            sleep(0.1)

    def wait_for_clear(self, timeout=None, threshold=None):
        """
        Wait for path to be clear (no object within threshold).

        Args:
            timeout (float): Maximum time to wait in seconds
            threshold (float): Custom threshold distance

        Returns:
            bool: True if path clear, False if timeout
        """
        threshold = threshold if threshold is not None else self.threshold_distance
        start_time = time()
        
        logger.info(f"Waiting for path to clear (>{threshold}m)...")
        
        while True:
            if not self.is_object_detected(threshold):
                return True
            
            if timeout and (time() - start_time) >= timeout:
                return False
            
            sleep(0.1)

    def set_callback(self, event, callback):
        """
        Set callback function for events.

        Args:
            event (str): Event type ('object_detected', 'object_lost', 'distance_changed')
            callback (callable): Callback function
        """
        if event in self._callbacks:
            self._callbacks[event] = callback
            logger.debug(f"Callback set for event: {event}")
        else:
            raise ValueError(f"Unknown event type: {event}")

    def start_monitoring(self, interval=0.1, distance_change_threshold=0.05):
        """
        Start continuous monitoring with callbacks.

        Args:
            interval (float): Monitoring interval in seconds
            distance_change_threshold (float): Minimum distance change to trigger callback
        """
        if self._monitoring:
            logger.warning("Already monitoring")
            return

        self._monitoring = True
        
        def monitor():
            logger.info("Started ultrasonic sensor monitoring")
            
            try:
                while self._monitoring:
                    current_distance = self.get_distance(samples=3)
                    current_time = time()
                    
                    # Store measurement
                    self._measurements.append({
                        'distance': current_distance,
                        'timestamp': current_time
                    })
                    
                    # Keep only recent measurements (last 100)
                    if len(self._measurements) > 100:
                        self._measurements.pop(0)
                    
                    # Check for object detection/loss
                    object_now = self.is_object_detected()
                    
                    if object_now != self._object_detected:
                        self._object_detected = object_now
                        
                        if object_now and self._callbacks['object_detected']:
                            try:
                                self._callbacks['object_detected'](current_distance)
                            except Exception as e:
                                logger.error(f"Error in object_detected callback: {e}")
                        
                        elif not object_now and self._callbacks['object_lost']:
                            try:
                                self._callbacks['object_lost'](current_distance)
                            except Exception as e:
                                logger.error(f"Error in object_lost callback: {e}")
                    
                    # Check for significant distance change
                    if (self._last_distance is not None and 
                        current_distance is not None and 
                        abs(current_distance - self._last_distance) >= distance_change_threshold):
                        
                        if self._callbacks['distance_changed']:
                            try:
                                self._callbacks['distance_changed'](current_distance, self._last_distance)
                            except Exception as e:
                                logger.error(f"Error in distance_changed callback: {e}")
                    
                    self._last_distance = current_distance
                    sleep(interval)
                    
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
            finally:
                self._monitoring = False
                logger.info("Ultrasonic sensor monitoring stopped")

        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring."""
        if self._monitoring:
            self._monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=1.0)
            logger.info("Monitoring stopped")

    def get_measurement_history(self, last_n=10):
        """
        Get recent measurement history.

        Args:
            last_n (int): Number of recent measurements to return

        Returns:
            list: List of recent measurements
        """
        return self._measurements[-last_n:]

    def get_average_distance(self, last_n=10):
        """
        Get average distance from recent measurements.

        Args:
            last_n (int): Number of recent measurements to average

        Returns:
            float: Average distance in meters (None if no valid measurements)
        """
        recent = self.get_measurement_history(last_n)
        valid_distances = [m['distance'] for m in recent if m['distance'] is not None]
        
        if valid_distances:
            return statistics.mean(valid_distances)
        else:
            return None

    def get_distance_variance(self, last_n=10):
        """
        Get distance variance from recent measurements (for stability check).

        Args:
            last_n (int): Number of recent measurements to analyze

        Returns:
            float: Distance variance (None if insufficient data)
        """
        recent = self.get_measurement_history(last_n)
        valid_distances = [m['distance'] for m in recent if m['distance'] is not None]
        
        if len(valid_distances) >= 2:
            return statistics.variance(valid_distances)
        else:
            return None

    def is_stable(self, last_n=5, max_variance=0.01):
        """
        Check if distance readings are stable.

        Args:
            last_n (int): Number of recent measurements to check
            max_variance (float): Maximum allowed variance for stability

        Returns:
            bool: True if readings are stable
        """
        variance = self.get_distance_variance(last_n)
        return variance is not None and variance <= max_variance

    def get_status(self):
        """
        Get sensor status information.

        Returns:
            dict: Dictionary containing sensor status
        """
        current_distance = self.get_distance()
        
        return {
            'trigger_pin': self.trigger_pin,
            'echo_pin': self.echo_pin,
            'max_distance': self.max_distance,
            'threshold_distance': self.threshold_distance,
            'current_distance': current_distance,
            'current_distance_cm': current_distance * 100 if current_distance else None,
            'object_detected': self.is_object_detected(),
            'is_monitoring': self._monitoring,
            'measurement_count': len(self._measurements),
            'average_distance': self.get_average_distance(),
            'is_stable': self.is_stable()
        }

    def cleanup(self):
        """Clean up sensor resources."""
        self.stop_monitoring()
        
        if self.sensor and self.is_initialized:
            try:
                self.sensor.close()
                logger.info(f"Ultrasonic sensor cleaned up")
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


# Example usage and testing
if __name__ == "__main__":
    import sys
    import argparse

    def demo_basic_measurement(trigger_pin=23, echo_pin=24, duration=30):
        """Basic distance measurement demonstration."""
        print(f"📏 Ultrasonic Sensor Basic Demo")
        print(f"📍 Trigger: {trigger_pin}, Echo: {echo_pin}")
        print("-" * 40)

        try:
            with UltrasonicSensor(trigger_pin=trigger_pin, echo_pin=echo_pin) as sensor:
                print("✅ Sensor initialized successfully!")
                
                print(f"📊 Taking measurements for {duration} seconds...")
                print("📏 Distance readings (press Ctrl+C to stop early):")
                print()
                
                start_time = time()
                try:
                    while (time() - start_time) < duration:
                        distance = sensor.get_distance(samples=3)
                        distance_cm = sensor.get_distance_cm(samples=3)
                        distance_in = sensor.get_distance_inches(samples=3)
                        
                        if distance is not None:
                            status = "🔴 OBJECT DETECTED" if sensor.is_object_detected() else "✅ Clear"
                            print(f"\r📏 {distance:.3f}m | {distance_cm:.1f}cm | {distance_in:.1f}in | {status}", 
                                  end="", flush=True)
                        else:
                            print(f"\r📏 Out of range (>{sensor.max_distance}m) | ⚠️  No object", 
                                  end="", flush=True)
                        
                        sleep(0.2)
                        
                except KeyboardInterrupt:
                    print("\n⚠️  Stopping early...")
                
                print("\n✅ Basic measurement demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    def demo_object_detection(trigger_pin=23, echo_pin=24, threshold=0.3):
        """Object detection demonstration."""
        print(f"🎯 Object Detection Demo")
        print(f"📍 Trigger: {trigger_pin}, Echo: {echo_pin}")
        print(f"🎚️  Threshold: {threshold}m")
        print("-" * 40)

        try:
            with UltrasonicSensor(trigger_pin=trigger_pin, echo_pin=echo_pin, 
                                threshold_distance=threshold) as sensor:
                print("✅ Sensor initialized successfully!")
                
                # Set up callbacks
                def on_object_detected(distance):
                    print(f"\n🚨 OBJECT DETECTED at {distance:.3f}m!")
                
                def on_object_lost(distance):
                    print(f"\n✅ Object lost - distance now {distance:.3f}m")
                
                def on_distance_changed(new_distance, old_distance):
                    change = new_distance - old_distance
                    direction = "closer" if change < 0 else "farther"
                    print(f"\n📏 Distance changed: {abs(change):.3f}m {direction}")
                
                sensor.set_callback('object_detected', on_object_detected)
                sensor.set_callback('object_lost', on_object_lost)
                sensor.set_callback('distance_changed', on_distance_changed)
                
                print("🔍 Starting monitoring...")
                print("💡 Move objects in front of the sensor")
                print("🛑 Press Ctrl+C to stop")
                
                sensor.start_monitoring(interval=0.1, distance_change_threshold=0.05)
                
                try:
                    # Keep main thread alive
                    while True:
                        sleep(1)
                        
                        # Show status periodically
                        status = sensor.get_status()
                        if status['current_distance']:
                            stability = "Stable" if status['is_stable'] else "Unstable"
                            avg_dist = status['average_distance']
                            print(f"\r📊 Avg: {avg_dist:.3f}m | Measurements: {status['measurement_count']} | {stability}",
                                  end="", flush=True)
                        
                except KeyboardInterrupt:
                    print("\n⚠️  Stopping monitoring...")
                
                sensor.stop_monitoring()
                
                # Show final statistics
                print(f"\n📈 Final Statistics:")
                final_status = sensor.get_status()
                print(f"   Total measurements: {final_status['measurement_count']}")
                if final_status['average_distance']:
                    print(f"   Average distance: {final_status['average_distance']:.3f}m")
                
                print("✅ Object detection demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    # CLI interface
    parser = argparse.ArgumentParser(description="Ultrasonic Sensor Demo")
    parser.add_argument("--trigger", type=int, default=23, help="Trigger pin (default: 23)")
    parser.add_argument("--echo", type=int, default=24, help="Echo pin (default: 24)")
    parser.add_argument("--threshold", type=float, default=0.3, help="Detection threshold in meters")
    parser.add_argument("--duration", type=int, default=30, help="Demo duration in seconds")
    parser.add_argument("--detection", action="store_true", help="Run object detection demo")
    parser.add_argument("--measure", action="store_true", help="Single measurement and exit")
    
    args = parser.parse_args()
    
    if args.measure:
        # Single measurement
        try:
            with UltrasonicSensor(trigger_pin=args.trigger, echo_pin=args.echo) as sensor:
                distance = sensor.get_distance(samples=5)
                if distance is not None:
                    print(f"Distance: {distance:.3f}m ({distance*100:.1f}cm)")
                    print(f"Object detected: {'Yes' if sensor.is_object_detected() else 'No'}")
                else:
                    print("Out of range")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        # Run demos
        if args.detection:
            demo_object_detection(args.trigger, args.echo, args.threshold)
        else:
            demo_basic_measurement(args.trigger, args.echo, args.duration)
