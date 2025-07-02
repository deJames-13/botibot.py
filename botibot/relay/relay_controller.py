#!/usr/bin/env python3
"""
Relay controller using gpiozero library.

This module provides easy control of relay modules using the gpiozero library
for better reliability and cleaner code.
"""

from gpiozero import OutputDevice, LED
from time import sleep
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelayController:
    """
    A reusable relay controller class using gpiozero.

    This class provides easy control of relay modules with support for
    multiple relays, timing operations, and various switching modes.
    """

    def __init__(self, pin, active_high=False, initial_value=False):
        """
        Initialize the relay controller.

        Args:
            pin (int): GPIO pin number for the relay (BCM numbering)
            active_high (bool): True if relay is activated by HIGH signal (default: False)
            initial_value (bool): Initial state of the relay (default: False)
        """
        self.pin = pin
        self.active_high = active_high
        self.relay = None
        self.is_initialized = False
        self._timer = None

        try:
            # Initialize relay using OutputDevice for more control
            self.relay = OutputDevice(
                pin, 
                active_high=active_high, 
                initial_value=initial_value
            )
            self.is_initialized = True
            logger.info(f"Relay controller initialized on GPIO pin {pin}")
            logger.debug(f"Active high: {active_high}, Initial state: {'ON' if initial_value else 'OFF'}")
        except Exception as e:
            logger.error(f"Failed to initialize relay on pin {pin}: {e}")
            raise

    def turn_on(self):
        """Turn the relay ON."""
        if not self.is_initialized or not self.relay:
            raise RuntimeError("Relay not initialized")

        try:
            self.relay.on()
            logger.info(f"Relay ON (Pin {self.pin})")
        except Exception as e:
            logger.error(f"Failed to turn relay on: {e}")
            raise

    def turn_off(self):
        """Turn the relay OFF."""
        if not self.is_initialized or not self.relay:
            raise RuntimeError("Relay not initialized")

        try:
            self.relay.off()
            logger.info(f"Relay OFF (Pin {self.pin})")
        except Exception as e:
            logger.error(f"Failed to turn relay off: {e}")
            raise

    def toggle(self):
        """Toggle the relay state."""
        if not self.is_initialized or not self.relay:
            raise RuntimeError("Relay not initialized")

        try:
            if self.is_on():
                self.turn_off()
            else:
                self.turn_on()
        except Exception as e:
            logger.error(f"Failed to toggle relay: {e}")
            raise

    def is_on(self):
        """
        Check if the relay is currently ON.

        Returns:
            bool: True if relay is ON, False otherwise
        """
        if not self.is_initialized or not self.relay:
            return False

        return self.relay.is_active

    def is_off(self):
        """
        Check if the relay is currently OFF.

        Returns:
            bool: True if relay is OFF, False otherwise
        """
        return not self.is_on()

    def pulse(self, duration=1.0):
        """
        Pulse the relay (turn on, wait, turn off).

        Args:
            duration (float): Duration to keep relay on in seconds
        """
        if not self.is_initialized:
            raise RuntimeError("Relay not initialized")

        logger.info(f"Pulsing relay for {duration}s")
        
        try:
            self.turn_on()
            sleep(duration)
            self.turn_off()
        except Exception as e:
            logger.error(f"Failed to pulse relay: {e}")
            # Ensure relay is off even if there was an error
            try:
                self.turn_off()
            except:
                pass
            raise

    def blink(self, on_time=0.5, off_time=0.5, cycles=5):
        """
        Blink the relay for specified cycles.

        Args:
            on_time (float): Time to keep relay on
            off_time (float): Time to keep relay off
            cycles (int): Number of blink cycles
        """
        if not self.is_initialized:
            raise RuntimeError("Relay not initialized")

        logger.info(f"Blinking relay: {cycles} cycles, on={on_time}s, off={off_time}s")
        
        try:
            for cycle in range(cycles):
                logger.debug(f"Blink cycle {cycle + 1}/{cycles}")
                self.turn_on()
                sleep(on_time)
                self.turn_off()
                if cycle < cycles - 1:  # Don't sleep after the last cycle
                    sleep(off_time)
        except Exception as e:
            logger.error(f"Failed to blink relay: {e}")
            # Ensure relay is off
            try:
                self.turn_off()
            except:
                pass
            raise

    def timed_on(self, duration, callback=None):
        """
        Turn relay on for a specific duration (non-blocking).

        Args:
            duration (float): Duration to keep relay on
            callback (callable): Optional callback when timer expires
        """
        if not self.is_initialized:
            raise RuntimeError("Relay not initialized")

        # Cancel any existing timer
        self.cancel_timer()

        def timer_callback():
            try:
                self.turn_off()
                if callback:
                    callback()
            except Exception as e:
                logger.error(f"Error in timed_on callback: {e}")

        logger.info(f"Starting timed relay on for {duration}s")
        self.turn_on()
        self._timer = threading.Timer(duration, timer_callback)
        self._timer.start()

    def cancel_timer(self):
        """Cancel any running timer."""
        if self._timer and self._timer.is_alive():
            self._timer.cancel()
            logger.debug("Relay timer cancelled")

    def get_state(self):
        """
        Get the current state of the relay.

        Returns:
            dict: Dictionary containing relay state information
        """
        return {
            'pin': self.pin,
            'is_on': self.is_on(),
            'active_high': self.active_high,
            'has_timer': self._timer is not None and self._timer.is_alive()
        }

    def cleanup(self):
        """Clean up relay resources."""
        if self._timer:
            self.cancel_timer()

        if self.relay and self.is_initialized:
            try:
                self.turn_off()  # Ensure relay is off
                self.relay.close()
                logger.info(f"Relay on pin {self.pin} cleaned up")
            except Exception as e:
                logger.error(f"Error during relay cleanup: {e}")
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


class MultiRelayController:
    """
    Controller for multiple relays.

    This class allows easy control of multiple relays with group operations
    and individual relay access.
    """

    def __init__(self, pins, active_high=False, initial_value=False):
        """
        Initialize multiple relay controllers.

        Args:
            pins (list): List of GPIO pin numbers
            active_high (bool): True if relays are activated by HIGH signal
            initial_value (bool): Initial state of all relays
        """
        self.pins = pins if isinstance(pins, (list, tuple)) else [pins]
        self.relays = {}
        self.active_high = active_high

        logger.info(f"Initializing multi-relay controller for pins: {self.pins}")

        for pin in self.pins:
            try:
                self.relays[pin] = RelayController(
                    pin=pin, 
                    active_high=active_high, 
                    initial_value=initial_value
                )
            except Exception as e:
                logger.error(f"Failed to initialize relay on pin {pin}: {e}")
                # Clean up any successfully initialized relays
                self.cleanup()
                raise

    def get_relay(self, pin):
        """
        Get individual relay controller.

        Args:
            pin (int): GPIO pin number

        Returns:
            RelayController: Relay controller for the specified pin
        """
        if pin not in self.relays:
            raise ValueError(f"Pin {pin} not in relay list")
        return self.relays[pin]

    def turn_on_all(self):
        """Turn on all relays."""
        logger.info("Turning on all relays")
        for relay in self.relays.values():
            relay.turn_on()

    def turn_off_all(self):
        """Turn off all relays."""
        logger.info("Turning off all relays")
        for relay in self.relays.values():
            relay.turn_off()

    def turn_on_pins(self, pins):
        """
        Turn on specific relays.

        Args:
            pins (list): List of pin numbers to turn on
        """
        pins = pins if isinstance(pins, (list, tuple)) else [pins]
        logger.info(f"Turning on relays on pins: {pins}")
        for pin in pins:
            if pin in self.relays:
                self.relays[pin].turn_on()

    def turn_off_pins(self, pins):
        """
        Turn off specific relays.

        Args:
            pins (list): List of pin numbers to turn off
        """
        pins = pins if isinstance(pins, (list, tuple)) else [pins]
        logger.info(f"Turning off relays on pins: {pins}")
        for pin in pins:
            if pin in self.relays:
                self.relays[pin].turn_off()

    def sequential_on(self, delay=0.5):
        """
        Turn on relays sequentially.

        Args:
            delay (float): Delay between each relay activation
        """
        logger.info(f"Sequential relay activation with {delay}s delay")
        for pin in sorted(self.pins):
            self.relays[pin].turn_on()
            sleep(delay)

    def sequential_off(self, delay=0.5):
        """
        Turn off relays sequentially.

        Args:
            delay (float): Delay between each relay deactivation
        """
        logger.info(f"Sequential relay deactivation with {delay}s delay")
        for pin in sorted(self.pins):
            self.relays[pin].turn_off()
            sleep(delay)

    def wave_pattern(self, cycles=3, delay=0.3):
        """
        Create a wave pattern across relays.

        Args:
            cycles (int): Number of wave cycles
            delay (float): Delay between relay activations
        """
        logger.info(f"Wave pattern: {cycles} cycles with {delay}s delay")
        
        for cycle in range(cycles):
            # Forward wave
            for pin in sorted(self.pins):
                self.relays[pin].turn_on()
                sleep(delay)
                self.relays[pin].turn_off()
            
            # Backward wave
            for pin in sorted(self.pins, reverse=True):
                self.relays[pin].turn_on()
                sleep(delay)
                self.relays[pin].turn_off()

    def get_status(self):
        """
        Get status of all relays.

        Returns:
            dict: Dictionary with pin numbers as keys and states as values
        """
        return {pin: relay.get_state() for pin, relay in self.relays.items()}

    def cleanup(self):
        """Clean up all relay resources."""
        logger.info("Cleaning up multi-relay controller")
        for relay in self.relays.values():
            relay.cleanup()
        self.relays.clear()

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

    def demo_single_relay(pin=17, duration=10):
        """Single relay demonstration."""
        print(f"🔌 Single Relay Demo on GPIO {pin}")
        print("-" * 30)

        try:
            with RelayController(pin=pin) as relay:
                print("✅ Relay initialized successfully!")
                
                # Basic operations
                print("🔋 Testing basic operations...")
                relay.turn_on()
                sleep(1)
                relay.turn_off()
                sleep(1)
                
                # Toggle test
                print("🔄 Testing toggle...")
                for _ in range(3):
                    relay.toggle()
                    sleep(0.5)
                
                # Pulse test
                print("⚡ Testing pulse...")
                relay.pulse(2.0)
                sleep(1)
                
                # Blink test
                print("💫 Testing blink...")
                relay.blink(on_time=0.3, off_time=0.3, cycles=5)
                
                # Timed operation
                print("⏰ Testing timed operation...")
                relay.timed_on(3.0, lambda: print("  Timer callback executed!"))
                sleep(4)
                
                print("✅ Single relay demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    def demo_multi_relay(pins=[17, 18, 19], duration=15):
        """Multi-relay demonstration."""
        print(f"🔌 Multi-Relay Demo on GPIO pins: {pins}")
        print("-" * 40)

        try:
            with MultiRelayController(pins=pins) as multi_relay:
                print("✅ Multi-relay controller initialized!")
                
                # All on/off
                print("🔋 Testing all on/off...")
                multi_relay.turn_on_all()
                sleep(1)
                multi_relay.turn_off_all()
                sleep(1)
                
                # Sequential activation
                print("🔄 Testing sequential activation...")
                multi_relay.sequential_on(0.5)
                sleep(1)
                multi_relay.sequential_off(0.5)
                sleep(1)
                
                # Wave pattern
                print("🌊 Testing wave pattern...")
                multi_relay.wave_pattern(cycles=2, delay=0.3)
                
                # Individual control
                print("🎯 Testing individual control...")
                multi_relay.turn_on_pins([pins[0], pins[-1]])
                sleep(2)
                multi_relay.turn_off_all()
                
                # Status check
                print("📊 Current status:")
                status = multi_relay.get_status()
                for pin, state in status.items():
                    print(f"  Pin {pin}: {'ON' if state['is_on'] else 'OFF'}")
                
                print("✅ Multi-relay demo completed!")

        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")

    # CLI interface
    parser = argparse.ArgumentParser(description="Relay Controller Demo")
    parser.add_argument("--pin", type=int, default=17, help="GPIO pin number for single relay (default: 17)")
    parser.add_argument("--pins", nargs='+', type=int, default=[17, 18, 19], help="GPIO pins for multi-relay demo")
    parser.add_argument("--multi", action="store_true", help="Run multi-relay demo")
    parser.add_argument("--on", action="store_true", help="Turn relay on and exit")
    parser.add_argument("--off", action="store_true", help="Turn relay off and exit")
    parser.add_argument("--toggle", action="store_true", help="Toggle relay and exit")
    parser.add_argument("--pulse", type=float, help="Pulse relay for specified seconds")
    
    args = parser.parse_args()
    
    # Quick operations
    if args.on or args.off or args.toggle or args.pulse:
        try:
            with RelayController(pin=args.pin) as relay:
                if args.on:
                    print(f"Turning relay ON on pin {args.pin}")
                    relay.turn_on()
                elif args.off:
                    print(f"Turning relay OFF on pin {args.pin}")
                    relay.turn_off()
                elif args.toggle:
                    print(f"Toggling relay on pin {args.pin}")
                    relay.toggle()
                elif args.pulse:
                    print(f"Pulsing relay for {args.pulse}s on pin {args.pin}")
                    relay.pulse(args.pulse)
                print("✅ Operation completed!")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        # Run demos
        if args.multi:
            demo_multi_relay(args.pins)
        else:
            demo_single_relay(args.pin)
