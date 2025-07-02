#!/usr/bin/env python3
"""
Servo motor controller using gpiozero library.

This module provides easy control of servo motors using the gpiozero library
instead of manual PWM control.
"""

from gpiozero import Servo, Device
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to use pigpio for better performance, fallback to default
try:
    Device.pin_factory = PiGPIOFactory()
    logger.info("Using PiGPIO pin factory for better servo control")
except Exception as e:
    logger.warning(f"PiGPIO not available, using default pin factory: {e}")


class ServoController:
    """
    A reusable servo motor controller class using gpiozero.

    This class provides easy control of servo motors with smooth movements
    and various positioning methods using the gpiozero library.
    """

    def __init__(self, pin, min_pulse_width=1/1000, max_pulse_width=2/1000, frame_width=20/1000):
        """
        Initialize the servo controller.

        Args:
            pin (int): GPIO pin number for the servo (BCM numbering)
            min_pulse_width (float): Minimum pulse width in seconds (default: 1ms)
            max_pulse_width (float): Maximum pulse width in seconds (default: 2ms)
            frame_width (float): Frame width in seconds (default: 20ms)
        """
        self.pin = pin
        self.servo = None
        self.is_initialized = False

        try:
            # Initialize servo with custom pulse widths for better control
            self.servo = Servo(
                pin,
                min_pulse_width=min_pulse_width,
                max_pulse_width=max_pulse_width,
                frame_width=frame_width
            )
            self.is_initialized = True
            logger.info(f"Servo controller initialized on GPIO pin {pin}")
        except Exception as e:
            logger.error(f"Failed to initialize servo on pin {pin}: {e}")
            raise

    def set_angle(self, angle):
        """
        Set servo to a specific angle.

        Args:
            angle (float): Angle in degrees (0-180)
        """
        if not self.is_initialized or not self.servo:
            raise RuntimeError("Servo not initialized")

        if not 0 <= angle <= 180:
            raise ValueError(f"Angle must be between 0 and 180 degrees, got {angle}")

        # Convert angle to servo value (-1 to 1)
        # 0 degrees = -1, 90 degrees = 0, 180 degrees = 1
        servo_value = (angle - 90) / 90
        
        try:
            self.servo.value = servo_value
            logger.debug(f"Servo set to {angle}° (value: {servo_value:.3f})")
        except Exception as e:
            logger.error(f"Failed to set servo angle: {e}")
            raise

    def move_to_position(self, angle, delay=0.5):
        """
        Move servo to position with optional delay.

        Args:
            angle (float): Target angle in degrees
            delay (float): Delay after movement in seconds
        """
        self.set_angle(angle)
        if delay > 0:
            sleep(delay)

    def sweep(self, start_angle=0, end_angle=180, step=10, delay=0.1, cycles=1):
        """
        Sweep servo between two angles.

        Args:
            start_angle (float): Starting angle
            end_angle (float): Ending angle
            step (float): Step size in degrees
            delay (float): Delay between steps
            cycles (int): Number of sweep cycles
        """
        if not self.is_initialized:
            raise RuntimeError("Servo not initialized")

        logger.info(f"Starting servo sweep: {start_angle}° to {end_angle}°, {cycles} cycles")
        
        for cycle in range(cycles):
            logger.debug(f"Sweep cycle {cycle + 1}/{cycles}")
            
            # Forward sweep
            for angle in range(int(start_angle), int(end_angle) + 1, int(step)):
                self.set_angle(angle)
                sleep(delay)
            
            # Backward sweep
            for angle in range(int(end_angle), int(start_angle) - 1, -int(step)):
                self.set_angle(angle)
                sleep(delay)

    def smooth_move(self, target_angle, duration=1.0, steps=50):
        """
        Move servo smoothly to target angle over specified duration.

        Args:
            target_angle (float): Target angle in degrees
            duration (float): Duration of movement in seconds
            steps (int): Number of steps for smooth movement
        """
        if not self.is_initialized:
            raise RuntimeError("Servo not initialized")

        current_value = self.servo.value if self.servo.value is not None else 0
        current_angle = (current_value * 90) + 90
        
        angle_diff = target_angle - current_angle
        step_size = angle_diff / steps
        step_delay = duration / steps

        logger.info(f"Smooth move from {current_angle:.1f}° to {target_angle}° over {duration}s")

        for i in range(steps + 1):
            angle = current_angle + (step_size * i)
            self.set_angle(angle)
            sleep(step_delay)

    def center(self, delay=0.5):
        """
        Move servo to center position (90 degrees).

        Args:
            delay (float): Delay after centering
        """
        logger.info("Centering servo to 90°")
        self.move_to_position(90, delay)

    def min_position(self, delay=0.5):
        """
        Move servo to minimum position (0 degrees).

        Args:
            delay (float): Delay after movement
        """
        logger.info("Moving servo to minimum position (0°)")
        self.move_to_position(0, delay)

    def max_position(self, delay=0.5):
        """
        Move servo to maximum position (180 degrees).

        Args:
            delay (float): Delay after movement
        """
        logger.info("Moving servo to maximum position (180°)")
        self.move_to_position(180, delay)

    def get_current_angle(self):
        """
        Get the current servo angle.

        Returns:
            float: Current angle in degrees (0-180)
        """
        if not self.is_initialized or not self.servo:
            return None
        
        if self.servo.value is None:
            return None
        
        # Convert servo value (-1 to 1) back to angle (0-180)
        return (self.servo.value * 90) + 90

    def stop(self):
        """
        Stop servo and release control (servo will lose holding torque).
        """
        if self.servo and self.is_initialized:
            self.servo.value = None
            logger.info("Servo stopped and released")

    def detach(self):
        """
        Detach servo (alias for stop method).
        """
        self.stop()

    def cleanup(self):
        """
        Clean up servo resources.
        """
        if self.servo and self.is_initialized:
            try:
                self.servo.close()
                logger.info(f"Servo on pin {self.pin} cleaned up")
            except Exception as e:
                logger.error(f"Error during servo cleanup: {e}")
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

    def demo_servo(pin=18, duration=30):
        """Run servo demonstration."""
        print(f"🔧 Servo Demo on GPIO {pin}")
        print("-" * 30)

        try:
            with ServoController(pin=pin) as servo:
                print("✅ Servo initialized successfully!")
                
                # Center servo
                print("📍 Centering servo...")
                servo.center(1)
                
                # Test specific angles
                test_angles = [0, 45, 90, 135, 180, 90]
                print("🎯 Testing specific angles...")
                for angle in test_angles:
                    print(f"   → Moving to {angle}°")
                    servo.move_to_position(angle, 1)
                
                # Smooth movement demo
                print("🌊 Demonstrating smooth movement...")
                servo.smooth_move(45, duration=2)
                servo.smooth_move(135, duration=2)
                servo.smooth_move(90, duration=1)
                
                # Sweep demo
                print("🔄 Demonstrating sweep...")
                servo.sweep(30, 150, step=15, delay=0.2, cycles=2)
                
                # Return to center
                print("🏠 Returning to center...")
                servo.center(1)
                
                print("✅ Demo completed successfully!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("🧹 Servo demo finished")

    # CLI interface
    parser = argparse.ArgumentParser(description="Servo Controller Demo")
    parser.add_argument("--pin", type=int, default=18, help="GPIO pin number (default: 18)")
    parser.add_argument("--duration", type=int, default=30, help="Demo duration in seconds")
    parser.add_argument("--angle", type=float, help="Set specific angle and exit")
    
    args = parser.parse_args()
    
    if args.angle is not None:
        # Just set angle and exit
        try:
            with ServoController(pin=args.pin) as servo:
                print(f"Setting servo to {args.angle}°...")
                servo.set_angle(args.angle)
                print("✅ Angle set successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        # Run full demo
        demo_servo(args.pin, args.duration)
