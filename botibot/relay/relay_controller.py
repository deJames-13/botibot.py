import RPi.GPIO as GPIO
import time
import threading


class RelayController:
    """
    A reusable relay controller class for Raspberry Pi.

    This class provides easy control of relay modules with support for
    multiple relays, timing operations, and various switching modes.
    """

    def __init__(self, pin, pin_mode=GPIO.BCM, active_low=True):
        """
        Initialize the relay controller.

        Args:
            pin (int): GPIO pin number for the relay
            pin_mode (int): GPIO pin mode (GPIO.BOARD or GPIO.BCM)
            active_low (bool): True if relay is activated by LOW signal (default: True)
        """
        self.pin = pin
        self.active_low = active_low
        self.is_initialized = False
        self._timer = None

        # Set up GPIO
        GPIO.setmode(pin_mode)
        GPIO.setup(self.pin, GPIO.OUT)

        # Initialize relay to OFF state
        self.turn_off()
        self.is_initialized = True

    def _get_on_state(self):
        """Get the GPIO state for relay ON."""
        return GPIO.LOW if self.active_low else GPIO.HIGH

    def _get_off_state(self):
        """Get the GPIO state for relay OFF."""
        return GPIO.HIGH if self.active_low else GPIO.LOW

    def turn_on(self):
        """Turn the relay ON."""
        if not self.is_initialized:
            raise RuntimeError("Relay not initialized")

        GPIO.output(self.pin, self._get_on_state())
        print(f"Relay ON (Pin {self.pin})")

    def turn_off(self):
        """Turn the relay OFF."""
        if not self.is_initialized:
            raise RuntimeError("Relay not initialized")

        GPIO.output(self.pin, self._get_off_state())
        print(f"Relay OFF (Pin {self.pin})")

    def toggle(self):
        """Toggle the relay state."""
        if self.is_on():
            self.turn_off()
        else:
            self.turn_on()

    def is_on(self):
        """
        Check if the relay is currently ON.

        Returns:
            bool: True if relay is ON, False otherwise
        """
        if not self.is_initialized:
            return False

        current_state = GPIO.input(self.pin)
        return current_state == self._get_on_state()

    def pulse(self, duration=1.0):
        """
        Turn relay ON for a specific duration, then turn OFF.

        Args:
            duration (float): Duration in seconds to keep relay ON
        """
        self.turn_on()
        time.sleep(duration)
        self.turn_off()

    def blink(self, on_time=0.5, off_time=0.5, cycles=5):
        """
        Blink the relay on and off for specified cycles.

        Args:
            on_time (float): Time relay stays ON in seconds
            off_time (float): Time relay stays OFF in seconds
            cycles (int): Number of blink cycles
        """
        for i in range(cycles):
            self.turn_on()
            time.sleep(on_time)
            self.turn_off()
            if i < cycles - 1:  # Don't wait after the last cycle
                time.sleep(off_time)

    def timed_on(self, duration, callback=None):
        """
        Turn relay ON for a specific duration using a timer (non-blocking).

        Args:
            duration (float): Duration in seconds to keep relay ON
            callback (function): Optional callback function to call when timer expires
        """
        # Cancel any existing timer
        if self._timer and self._timer.is_alive():
            self._timer.cancel()

        self.turn_on()

        def _turn_off_after_delay():
            self.turn_off()
            if callback:
                callback()

        self._timer = threading.Timer(duration, _turn_off_after_delay)
        self._timer.start()

    def cancel_timer(self):
        """Cancel any active timer."""
        if self._timer and self._timer.is_alive():
            self._timer.cancel()
            print(f"Timer cancelled for relay on pin {self.pin}")

    def cleanup(self):
        """Clean up GPIO resources and cancel any active timers."""
        if self._timer and self._timer.is_alive():
            self._timer.cancel()

        if self.is_initialized:
            self.turn_off()
            self.is_initialized = False

        GPIO.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


class MultiRelayController:
    """
    Controller for multiple relays.

    This class allows easy control of multiple relays with group operations
    and individual relay access.
    """

    def __init__(self, pins, pin_mode=GPIO.BCM, active_low=True):
        """
        Initialize multiple relay controllers.

        Args:
            pins (list): List of GPIO pin numbers for relays
            pin_mode (int): GPIO pin mode (GPIO.BOARD or GPIO.BCM)
            active_low (bool): True if relays are activated by LOW signal
        """
        self.relays = {}
        self.pin_mode = pin_mode
        self.active_low = active_low

        # Initialize all relays
        for pin in pins:
            self.relays[pin] = RelayController(pin, pin_mode, active_low)

    def get_relay(self, pin):
        """
        Get a specific relay controller.

        Args:
            pin (int): GPIO pin number

        Returns:
            RelayController: The relay controller for the specified pin
        """
        if pin not in self.relays:
            raise ValueError(f"No relay found on pin {pin}")
        return self.relays[pin]

    def turn_on_all(self):
        """Turn ON all relays."""
        for relay in self.relays.values():
            relay.turn_on()

    def turn_off_all(self):
        """Turn OFF all relays."""
        for relay in self.relays.values():
            relay.turn_off()

    def turn_on_pins(self, pins):
        """
        Turn ON specific relays.

        Args:
            pins (list): List of pin numbers to turn ON
        """
        for pin in pins:
            if pin in self.relays:
                self.relays[pin].turn_on()

    def turn_off_pins(self, pins):
        """
        Turn OFF specific relays.

        Args:
            pins (list): List of pin numbers to turn OFF
        """
        for pin in pins:
            if pin in self.relays:
                self.relays[pin].turn_off()

    def sequential_on(self, delay=0.5):
        """
        Turn ON relays sequentially with delay between each.

        Args:
            delay (float): Delay between each relay activation
        """
        for pin, relay in self.relays.items():
            relay.turn_on()
            time.sleep(delay)

    def sequential_off(self, delay=0.5):
        """
        Turn OFF relays sequentially with delay between each.

        Args:
            delay (float): Delay between each relay deactivation
        """
        for pin, relay in self.relays.items():
            relay.turn_off()
            time.sleep(delay)

    def wave_pattern(self, cycles=3, delay=0.3):
        """
        Create a wave pattern by turning relays on and off in sequence.

        Args:
            cycles (int): Number of wave cycles
            delay (float): Delay between relay state changes
        """
        pins = list(self.relays.keys())

        for _ in range(cycles):
            # Forward wave
            for pin in pins:
                self.relays[pin].turn_on()
                time.sleep(delay)
                self.relays[pin].turn_off()

            # Backward wave
            for pin in reversed(pins):
                self.relays[pin].turn_on()
                time.sleep(delay)
                self.relays[pin].turn_off()

    def get_status(self):
        """
        Get the status of all relays.

        Returns:
            dict: Dictionary with pin numbers as keys and status as values
        """
        return {pin: relay.is_on() for pin, relay in self.relays.items()}

    def cleanup(self):
        """Clean up all relay controllers."""
        for relay in self.relays.values():
            relay.cleanup()


# Example usage
if __name__ == "__main__":
    try:
        print("=== Single Relay Demo ===")
        # Single relay demo
        with RelayController(pin=17) as relay:
            print("Basic on/off operations:")
            relay.turn_on()
            time.sleep(1)
            relay.turn_off()
            time.sleep(1)

            print("Pulse operation (2 seconds):")
            relay.pulse(2.0)
            time.sleep(0.5)

            print("Blinking (3 cycles):")
            relay.blink(on_time=0.3, off_time=0.3, cycles=3)

            print("Timed operation (3 seconds, non-blocking):")
            relay.timed_on(3.0, callback=lambda: print("Timer expired!"))
            time.sleep(4)  # Wait for timer to complete

        print("\n=== Multiple Relay Demo ===")
        # Multiple relay demo
        multi_relay = MultiRelayController([17, 18, 19, 20])

        try:
            print("Sequential activation:")
            multi_relay.sequential_on(delay=0.5)
            time.sleep(1)

            print("All OFF:")
            multi_relay.turn_off_all()
            time.sleep(1)

            print("Wave pattern:")
            multi_relay.wave_pattern(cycles=2, delay=0.2)

            print("Status check:")
            status = multi_relay.get_status()
            for pin, is_on in status.items():
                print(f"  Pin {pin}: {'ON' if is_on else 'OFF'}")

        finally:
            multi_relay.cleanup()

    except KeyboardInterrupt:
        print("Demo stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Relay controller demo completed")
