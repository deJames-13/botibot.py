#!/usr/bin/env python3
"""
DC Motor controller using gpiozero library.

This module provides easy control of DC motors with support for
speed control, direction, and advanced movement patterns.
"""

from gpiozero import Motor, Robot
from time import sleep
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MotorController:
    """
    A reusable DC motor controller class using gpiozero.

    This class provides easy control of DC motors with PWM speed control
    and direction control using the gpiozero Motor class.
    """

    def __init__(self, forward_pin, backward_pin, enable_pin=None, pwm=True):
        """
        Initialize the motor controller.

        Args:
            forward_pin (int): GPIO pin for forward direction
            backward_pin (int): GPIO pin for backward direction  
            enable_pin (int): GPIO pin for enable/speed control (optional)
            pwm (bool): Enable PWM for speed control (default: True)
        """
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin
        self.enable_pin = enable_pin
        self.pwm = pwm
        self.motor = None
        self.is_initialized = False
        self._current_speed = 0
        self._direction = "stopped"

        try:
            # Initialize motor
            if enable_pin:
                # Use Motor with separate enable pin
                self.motor = Motor(
                    forward=forward_pin,
                    backward=backward_pin,
                    enable=enable_pin,
                    pwm=pwm
                )
            else:
                # Use Motor without enable pin
                self.motor = Motor(
                    forward=forward_pin,
                    backward=backward_pin,
                    pwm=pwm
                )
            
            self.is_initialized = True
            logger.info(f"Motor controller initialized - Forward: {forward_pin}, Backward: {backward_pin}")
            
        except Exception as e:
            logger.error(f"Failed to initialize motor controller: {e}")
            raise

    def forward(self, speed=1.0):
        """
        Move motor forward.

        Args:
            speed (float): Speed value (0.0 to 1.0)
        """
        if not self.is_initialized or not self.motor:
            raise RuntimeError("Motor not initialized")

        if not 0.0 <= speed <= 1.0:
            raise ValueError(f"Speed must be between 0.0 and 1.0, got {speed}")

        try:
            self.motor.forward(speed)
            self._current_speed = speed
            self._direction = "forward"
            logger.debug(f"Motor forward at speed {speed:.2f}")
        except Exception as e:
            logger.error(f"Failed to move motor forward: {e}")
            raise

    def backward(self, speed=1.0):
        """
        Move motor backward.

        Args:
            speed (float): Speed value (0.0 to 1.0)
        """
        if not self.is_initialized or not self.motor:
            raise RuntimeError("Motor not initialized")

        if not 0.0 <= speed <= 1.0:
            raise ValueError(f"Speed must be between 0.0 and 1.0, got {speed}")

        try:
            self.motor.backward(speed)
            self._current_speed = speed
            self._direction = "backward"
            logger.debug(f"Motor backward at speed {speed:.2f}")
        except Exception as e:
            logger.error(f"Failed to move motor backward: {e}")
            raise

    def stop(self):
        """Stop the motor."""
        if not self.is_initialized or not self.motor:
            raise RuntimeError("Motor not initialized")

        try:
            self.motor.stop()
            self._current_speed = 0
            self._direction = "stopped"
            logger.debug("Motor stopped")
        except Exception as e:
            logger.error(f"Failed to stop motor: {e}")
            raise

    def set_speed(self, speed):
        """
        Set motor speed while maintaining current direction.

        Args:
            speed (float): Speed value (0.0 to 1.0)
        """
        if not 0.0 <= speed <= 1.0:
            raise ValueError(f"Speed must be between 0.0 and 1.0, got {speed}")

        if self._direction == "forward":
            self.forward(speed)
        elif self._direction == "backward":
            self.backward(speed)
        elif speed > 0:
            # If stopped and speed > 0, default to forward
            self.forward(speed)

    def reverse(self):
        """Reverse the current direction."""
        current_speed = self._current_speed
        
        if self._direction == "forward":
            self.backward(current_speed)
        elif self._direction == "backward":
            self.forward(current_speed)

    def pulse(self, duration=1.0, speed=1.0, direction="forward"):
        """
        Run motor for a specific duration then stop.

        Args:
            duration (float): Duration in seconds
            speed (float): Speed value (0.0 to 1.0)
            direction (str): Direction ("forward" or "backward")
        """
        logger.info(f"Pulsing motor {direction} for {duration}s at speed {speed}")
        
        try:
            if direction == "forward":
                self.forward(speed)
            elif direction == "backward":
                self.backward(speed)
            else:
                raise ValueError("Direction must be 'forward' or 'backward'")
            
            sleep(duration)
            self.stop()
            
        except Exception as e:
            logger.error(f"Failed to pulse motor: {e}")
            self.stop()  # Ensure motor is stopped
            raise

    def gradual_start(self, target_speed=1.0, direction="forward", duration=2.0, steps=20):
        """
        Gradually increase motor speed to target.

        Args:
            target_speed (float): Target speed (0.0 to 1.0)
            direction (str): Direction ("forward" or "backward")
            duration (float): Duration to reach target speed
            steps (int): Number of steps for gradual increase
        """
        if not 0.0 <= target_speed <= 1.0:
            raise ValueError("Target speed must be between 0.0 and 1.0")

        logger.info(f"Gradual start {direction} to speed {target_speed} over {duration}s")
        
        step_delay = duration / steps
        speed_increment = target_speed / steps

        try:
            for step in range(steps + 1):
                current_speed = speed_increment * step
                
                if direction == "forward":
                    self.forward(current_speed)
                elif direction == "backward":
                    self.backward(current_speed)
                else:
                    raise ValueError("Direction must be 'forward' or 'backward'")
                
                sleep(step_delay)
                
        except Exception as e:
            logger.error(f"Failed during gradual start: {e}")
            self.stop()
            raise

    def gradual_stop(self, duration=2.0, steps=20):
        """
        Gradually decrease motor speed to stop.

        Args:
            duration (float): Duration to stop
            steps (int): Number of steps for gradual decrease
        """
        if self._current_speed == 0:
            return  # Already stopped

        logger.info(f"Gradual stop over {duration}s")
        
        step_delay = duration / steps
        speed_decrement = self._current_speed / steps
        direction = self._direction

        try:
            for step in range(steps):
                remaining_speed = self._current_speed - (speed_decrement * (step + 1))
                remaining_speed = max(0, remaining_speed)
                
                if remaining_speed <= 0:
                    self.stop()
                    break
                    
                if direction == "forward":
                    self.forward(remaining_speed)
                elif direction == "backward":
                    self.backward(remaining_speed)
                
                sleep(step_delay)
            
            self.stop()
            
        except Exception as e:
            logger.error(f"Failed during gradual stop: {e}")
            self.stop()
            raise

    def get_speed(self):
        """
        Get current motor speed.

        Returns:
            float: Current speed (0.0 to 1.0)
        """
        return self._current_speed

    def get_direction(self):
        """
        Get current motor direction.

        Returns:
            str: Current direction ("forward", "backward", or "stopped")
        """
        return self._direction

    def is_moving(self):
        """
        Check if motor is currently moving.

        Returns:
            bool: True if motor is moving, False if stopped
        """
        return self._current_speed > 0 and self._direction != "stopped"

    def get_status(self):
        """
        Get motor status information.

        Returns:
            dict: Dictionary containing motor status
        """
        return {
            'forward_pin': self.forward_pin,
            'backward_pin': self.backward_pin,
            'enable_pin': self.enable_pin,
            'speed': self._current_speed,
            'direction': self._direction,
            'is_moving': self.is_moving()
        }

    def cleanup(self):
        """Clean up motor resources."""
        if self.motor and self.is_initialized:
            try:
                self.stop()
                self.motor.close()
                logger.info("Motor controller cleaned up")
            except Exception as e:
                logger.error(f"Error during motor cleanup: {e}")
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


class DualMotorController:
    """
    Controller for dual motor setup (like a robot car).
    
    This class uses gpiozero's Robot class for coordinated control
    of two motors for differential drive robots.
    """

    def __init__(self, left_forward, left_backward, right_forward, right_backward,
                 left_enable=None, right_enable=None, pwm=True):
        """
        Initialize dual motor controller.

        Args:
            left_forward (int): Left motor forward pin
            left_backward (int): Left motor backward pin
            right_forward (int): Right motor forward pin  
            right_backward (int): Right motor backward pin
            left_enable (int): Left motor enable pin (optional)
            right_enable (int): Right motor enable pin (optional)
            pwm (bool): Enable PWM for speed control
        """
        self.left_forward = left_forward
        self.left_backward = left_backward
        self.right_forward = right_forward
        self.right_backward = right_backward
        self.left_enable = left_enable
        self.right_enable = right_enable
        self.pwm = pwm
        self.robot = None
        self.is_initialized = False

        try:
            # Create motor objects
            if left_enable and right_enable:
                left_motor = Motor(left_forward, left_backward, enable=left_enable, pwm=pwm)
                right_motor = Motor(right_forward, right_backward, enable=right_enable, pwm=pwm)
            else:
                left_motor = Motor(left_forward, left_backward, pwm=pwm)
                right_motor = Motor(right_forward, right_backward, pwm=pwm)

            # Create robot with both motors
            self.robot = Robot(left=left_motor, right=right_motor)
            self.is_initialized = True
            
            logger.info("Dual motor controller initialized")
            logger.debug(f"Left motor: {left_forward}/{left_backward}, Right motor: {right_forward}/{right_backward}")
            
        except Exception as e:
            logger.error(f"Failed to initialize dual motor controller: {e}")
            raise

    def forward(self, speed=1.0, duration=None):
        """
        Move robot forward.

        Args:
            speed (float): Speed value (0.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        if not self.is_initialized or not self.robot:
            raise RuntimeError("Robot not initialized")

        if not 0.0 <= speed <= 1.0:
            raise ValueError(f"Speed must be between 0.0 and 1.0, got {speed}")

        try:
            self.robot.forward(speed)
            logger.debug(f"Robot moving forward at speed {speed:.2f}")
            
            if duration:
                sleep(duration)
                self.stop()
                
        except Exception as e:
            logger.error(f"Failed to move robot forward: {e}")
            raise

    def backward(self, speed=1.0, duration=None):
        """
        Move robot backward.

        Args:
            speed (float): Speed value (0.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        if not self.is_initialized or not self.robot:
            raise RuntimeError("Robot not initialized")

        if not 0.0 <= speed <= 1.0:
            raise ValueError(f"Speed must be between 0.0 and 1.0, got {speed}")

        try:
            self.robot.backward(speed)
            logger.debug(f"Robot moving backward at speed {speed:.2f}")
            
            if duration:
                sleep(duration)
                self.stop()
                
        except Exception as e:
            logger.error(f"Failed to move robot backward: {e}")
            raise

    def turn_left(self, speed=1.0, duration=None):
        """
        Turn robot left.

        Args:
            speed (float): Speed value (0.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        if not self.is_initialized or not self.robot:
            raise RuntimeError("Robot not initialized")

        try:
            self.robot.left(speed)
            logger.debug(f"Robot turning left at speed {speed:.2f}")
            
            if duration:
                sleep(duration)
                self.stop()
                
        except Exception as e:
            logger.error(f"Failed to turn robot left: {e}")
            raise

    def turn_right(self, speed=1.0, duration=None):
        """
        Turn robot right.

        Args:
            speed (float): Speed value (0.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        if not self.is_initialized or not self.robot:
            raise RuntimeError("Robot not initialized")

        try:
            self.robot.right(speed)
            logger.debug(f"Robot turning right at speed {speed:.2f}")
            
            if duration:
                sleep(duration)
                self.stop()
                
        except Exception as e:
            logger.error(f"Failed to turn robot right: {e}")
            raise

    def stop(self):
        """Stop the robot."""
        if not self.is_initialized or not self.robot:
            raise RuntimeError("Robot not initialized")

        try:
            self.robot.stop()
            logger.debug("Robot stopped")
        except Exception as e:
            logger.error(f"Failed to stop robot: {e}")
            raise

    def set_motor_speeds(self, left_speed, right_speed):
        """
        Set individual motor speeds for custom movements.

        Args:
            left_speed (float): Left motor speed (-1.0 to 1.0)
            right_speed (float): Right motor speed (-1.0 to 1.0)
        """
        if not self.is_initialized or not self.robot:
            raise RuntimeError("Robot not initialized")

        if not -1.0 <= left_speed <= 1.0 or not -1.0 <= right_speed <= 1.0:
            raise ValueError("Motor speeds must be between -1.0 and 1.0")

        try:
            self.robot.value = (left_speed, right_speed)
            logger.debug(f"Motor speeds set - Left: {left_speed:.2f}, Right: {right_speed:.2f}")
        except Exception as e:
            logger.error(f"Failed to set motor speeds: {e}")
            raise

    def curve(self, left_speed, right_speed, duration=None):
        """
        Move in a curve with different wheel speeds.

        Args:
            left_speed (float): Left motor speed (-1.0 to 1.0)
            right_speed (float): Right motor speed (-1.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        try:
            self.set_motor_speeds(left_speed, right_speed)
            logger.debug(f"Robot curving - Left: {left_speed:.2f}, Right: {right_speed:.2f}")
            
            if duration:
                sleep(duration)
                self.stop()
                
        except Exception as e:
            logger.error(f"Failed to curve robot: {e}")
            raise

    def spin_left(self, speed=1.0, duration=None):
        """
        Spin robot left in place.

        Args:
            speed (float): Speed value (0.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        self.set_motor_speeds(-speed, speed)
        logger.debug(f"Robot spinning left at speed {speed:.2f}")
        
        if duration:
            sleep(duration)
            self.stop()

    def spin_right(self, speed=1.0, duration=None):
        """
        Spin robot right in place.

        Args:
            speed (float): Speed value (0.0 to 1.0)
            duration (float): Duration in seconds (None for continuous)
        """
        self.set_motor_speeds(speed, -speed)
        logger.debug(f"Robot spinning right at speed {speed:.2f}")
        
        if duration:
            sleep(duration)
            self.stop()

    def square_pattern(self, side_duration=2.0, turn_duration=1.0, speed=0.7):
        """
        Move robot in a square pattern.

        Args:
            side_duration (float): Duration for each side
            turn_duration (float): Duration for each turn
            speed (float): Movement speed
        """
        logger.info("Executing square pattern")
        
        try:
            for i in range(4):
                logger.debug(f"Square side {i+1}/4")
                self.forward(speed, side_duration)
                sleep(0.2)
                self.turn_right(speed, turn_duration)
                sleep(0.2)
            
            self.stop()
            logger.info("Square pattern completed")
            
        except Exception as e:
            logger.error(f"Failed during square pattern: {e}")
            self.stop()
            raise

    def figure_eight(self, curve_duration=3.0, speed=0.6):
        """
        Move robot in a figure-eight pattern.

        Args:
            curve_duration (float): Duration for each curve
            speed (float): Movement speed
        """
        logger.info("Executing figure-eight pattern")
        
        try:
            # First loop (clockwise)
            self.curve(speed, speed * 0.3, curve_duration)
            # Second loop (counter-clockwise)  
            self.curve(speed * 0.3, speed, curve_duration)
            
            self.stop()
            logger.info("Figure-eight pattern completed")
            
        except Exception as e:
            logger.error(f"Failed during figure-eight pattern: {e}")
            self.stop()
            raise

    def get_status(self):
        """
        Get robot status information.

        Returns:
            dict: Dictionary containing robot status
        """
        return {
            'left_motor': {
                'forward_pin': self.left_forward,
                'backward_pin': self.left_backward,
                'enable_pin': self.left_enable
            },
            'right_motor': {
                'forward_pin': self.right_forward,
                'backward_pin': self.right_backward,
                'enable_pin': self.right_enable
            },
            'pwm_enabled': self.pwm,
            'is_initialized': self.is_initialized
        }

    def cleanup(self):
        """Clean up robot resources."""
        if self.robot and self.is_initialized:
            try:
                self.stop()
                self.robot.close()
                logger.info("Dual motor controller cleaned up")
            except Exception as e:
                logger.error(f"Error during robot cleanup: {e}")
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

    def demo_single_motor(forward_pin=20, backward_pin=21, enable_pin=None):
        """Single motor demonstration."""
        print(f"🔧 Single Motor Demo")
        print(f"📍 Forward: {forward_pin}, Backward: {backward_pin}, Enable: {enable_pin}")
        print("-" * 40)

        try:
            with MotorController(forward_pin, backward_pin, enable_pin) as motor:
                print("✅ Motor initialized successfully!")
                
                # Test basic movements
                print("⬆️  Testing forward movement...")
                motor.forward(0.7)
                sleep(2)
                motor.stop()
                sleep(1)
                
                print("⬇️  Testing backward movement...")
                motor.backward(0.7)
                sleep(2)
                motor.stop()
                sleep(1)
                
                # Test speed control
                print("🎛️  Testing speed control...")
                speeds = [0.3, 0.6, 1.0, 0.6, 0.3]
                for speed in speeds:
                    print(f"   Speed: {speed}")
                    motor.forward(speed)
                    sleep(1)
                motor.stop()
                sleep(1)
                
                # Test gradual start/stop
                print("🌊 Testing gradual start/stop...")
                motor.gradual_start(target_speed=0.8, direction="forward", duration=3)
                sleep(2)
                motor.gradual_stop(duration=3)
                
                print("✅ Single motor demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    def demo_dual_motor(left_pins=(20, 21), right_pins=(19, 26)):
        """Dual motor demonstration."""
        print(f"🤖 Dual Motor (Robot) Demo")
        print(f"📍 Left: {left_pins}, Right: {right_pins}")
        print("-" * 40)

        try:
            with DualMotorController(
                left_forward=left_pins[0], left_backward=left_pins[1],
                right_forward=right_pins[0], right_backward=right_pins[1]
            ) as robot:
                print("✅ Robot initialized successfully!")
                
                # Basic movements
                print("⬆️  Moving forward...")
                robot.forward(0.7, duration=2)
                sleep(0.5)
                
                print("⬇️  Moving backward...")
                robot.backward(0.7, duration=2)
                sleep(0.5)
                
                print("⬅️  Turning left...")
                robot.turn_left(0.7, duration=1)
                sleep(0.5)
                
                print("➡️  Turning right...")
                robot.turn_right(0.7, duration=1)
                sleep(0.5)
                
                print("🔄 Spinning left...")
                robot.spin_left(0.6, duration=1)
                sleep(0.5)
                
                print("🔄 Spinning right...")
                robot.spin_right(0.6, duration=1)
                sleep(0.5)
                
                # Pattern demonstrations
                print("⬜ Square pattern...")
                robot.square_pattern(side_duration=1.5, turn_duration=0.8, speed=0.6)
                sleep(1)
                
                print("∞ Figure-eight pattern...")
                robot.figure_eight(curve_duration=2, speed=0.5)
                
                print("✅ Dual motor demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    # CLI interface
    parser = argparse.ArgumentParser(description="Motor Controller Demo")
    parser.add_argument("--dual", action="store_true", help="Run dual motor demo")
    parser.add_argument("--forward", type=int, default=20, help="Forward pin (default: 20)")
    parser.add_argument("--backward", type=int, default=21, help="Backward pin (default: 21)")
    parser.add_argument("--enable", type=int, help="Enable pin (optional)")
    parser.add_argument("--left-forward", type=int, default=20, help="Left motor forward pin")
    parser.add_argument("--left-backward", type=int, default=21, help="Left motor backward pin")
    parser.add_argument("--right-forward", type=int, default=19, help="Right motor forward pin")
    parser.add_argument("--right-backward", type=int, default=26, help="Right motor backward pin")
    
    args = parser.parse_args()
    
    if args.dual:
        demo_dual_motor(
            left_pins=(args.left_forward, args.left_backward),
            right_pins=(args.right_forward, args.right_backward)
        )
    else:
        demo_single_motor(args.forward, args.backward, args.enable)
