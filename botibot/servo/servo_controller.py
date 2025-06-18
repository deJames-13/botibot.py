import RPi.GPIO as GPIO
from time import sleep


class ServoController:
    """
    A reusable servo motor controller class for Raspberry Pi.

    This class provides easy control of servo motors with PWM signal generation
    and various positioning methods.
    """

    def __init__(self, pin, pin_mode=GPIO.BOARD, frequency=50):
        """
        Initialize the servo controller.

        Args:
            pin (int): GPIO pin number for the servo
            pin_mode (int): GPIO pin mode (GPIO.BOARD or GPIO.BCM)
            frequency (int): PWM frequency in Hz (default: 50Hz)
        """
        self.pin = pin
        self.frequency = frequency
        self.pwm = None
        self.is_initialized = False

        # Set up GPIO
        GPIO.setmode(pin_mode)
        GPIO.setup(self.pin, GPIO.OUT)

        # Initialize PWM
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)
        self.is_initialized = True

    def set_angle(self, angle):
        """
        Set servo to a specific angle.

        Args:
            angle (float): Angle in degrees (0-180)
        """
        if not self.is_initialized:
            raise RuntimeError("Servo not initialized")

        if not 0 <= angle <= 180:
            raise ValueError("Angle must be between 0 and 180 degrees")

        # Convert angle to duty cycle (2-12% for 0-180 degrees)
        duty_cycle = 2 + (angle / 180) * 10
        self.pwm.ChangeDutyCycle(duty_cycle)

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
        for _ in range(cycles):
            # Forward sweep
            for angle in range(int(start_angle), int(end_angle) + 1, int(step)):
                self.move_to_position(angle, delay)

            # Backward sweep
            for angle in range(int(end_angle), int(start_angle) - 1, -int(step)):
                self.move_to_position(angle, delay)

    def center(self, delay=0.5):
        """
        Move servo to center position (90 degrees).

        Args:
            delay (float): Delay after centering
        """
        self.move_to_position(90, delay)

    def stop(self):
        """
        Stop PWM signal (servo will lose holding torque).
        """
        if self.pwm and self.is_initialized:
            self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        if self.pwm and self.is_initialized:
            self.pwm.stop()
            self.is_initialized = False
        GPIO.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


# Example usage
if __name__ == "__main__":
    try:
        # Create servo controller for pin 11
        with ServoController(pin=11) as servo:
            print("Moving servo to various positions...")

            # Move to specific angles
            servo.move_to_position(0, 1)  # 0 degrees, wait 1 second
            print("Servo at 0 degrees")

            servo.move_to_position(90, 1)  # 90 degrees, wait 1 second
            print("Servo at 90 degrees")

            servo.move_to_position(180, 1)  # 180 degrees, wait 1 second
            print("Servo at 180 degrees")

            # Return to center
            servo.center()
            print("Servo centered")

            # Perform a sweep
            print("Performing sweep...")
            servo.sweep(start_angle=0, end_angle=180, step=30, delay=0.5, cycles=2)

    except KeyboardInterrupt:
        print("Stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Servo controller demo completed")
