#!/usr/bin/env python3
"""
Command-line interface tools for botibot.

This module provides CLI commands for quick testing and control of hardware components.
"""

import argparse
import sys
import time
import threading
from typing import Optional

try:
    from modules import ServoController, OLEDDisplay, RelayController, FlaskServer
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure botibot is properly installed")
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Botibot CLI Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  botibot-demo                    # Run complete demo
  botibot-servo --pin 11 --angle 90  # Set servo to 90 degrees
  botibot-oled --text "Hello Pi"      # Display text on OLED
  botibot-relay --pin 17 --on         # Turn relay on
  botibot-server --port 8080          # Start web server on port 8080
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run complete hardware demo')
    demo_parser.add_argument('--quick', action='store_true', help='Run quick demo')
    
    # Servo command
    servo_parser = subparsers.add_parser('servo', help='Control servo motor')
    servo_parser.add_argument('--pin', type=int, default=11, help='GPIO pin number')
    servo_parser.add_argument('--angle', type=float, help='Set servo angle (0-180)')
    servo_parser.add_argument('--sweep', action='store_true', help='Perform sweep')
    servo_parser.add_argument('--center', action='store_true', help='Center servo')
    
    # OLED command
    oled_parser = subparsers.add_parser('oled', help='Control OLED display')
    oled_parser.add_argument('--text', type=str, help='Text to display')
    oled_parser.add_argument('--clear', action='store_true', help='Clear display')
    oled_parser.add_argument('--demo', action='store_true', help='Run OLED demo')
    
    # Relay command
    relay_parser = subparsers.add_parser('relay', help='Control relay')
    relay_parser.add_argument('--pin', type=int, default=17, help='GPIO pin number')
    relay_parser.add_argument('--on', action='store_true', help='Turn relay on')
    relay_parser.add_argument('--off', action='store_true', help='Turn relay off')
    relay_parser.add_argument('--toggle', action='store_true', help='Toggle relay')
    relay_parser.add_argument('--pulse', type=float, help='Pulse duration in seconds')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start web server')
    server_parser.add_argument('--port', type=int, default=5000, help='Port number')
    server_parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    server_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'demo':
            run_demo(args.quick)
        elif args.command == 'servo':
            servo_cli(args)
        elif args.command == 'oled':
            oled_cli(args)
        elif args.command == 'relay':
            relay_cli(args)
        elif args.command == 'server':
            server_cli(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_demo(quick: bool = False):
    """Run hardware demonstration."""
    print("🍓 Raspberry Pi Modules Demo")
    print("=" * 40)
    
    # Import demo function
    try:
        from demo_all_modules import RaspberryPiController
        
        if quick:
            print("Running quick demo...")
            controller = RaspberryPiController()
            controller.run_demo_sequence()
        else:
            print("Running full demo...")
            controller = RaspberryPiController()
            controller.run()
    except ImportError:
        print("Demo module not found. Running basic component tests...")
        run_basic_tests()


def run_basic_tests():
    """Run basic tests for all components."""
    print("\n🔧 Testing Components...")
    
    # Test servo
    try:
        print("Testing servo...")
        with ServoController(pin=11) as servo:
            servo.center()
            time.sleep(1)
        print("✅ Servo test passed")
    except Exception as e:
        print(f"❌ Servo test failed: {e}")
    
    # Test OLED
    try:
        print("Testing OLED...")
        oled = OLEDDisplay()
        oled.write_text("CLI Test", 0, 0)
        time.sleep(2)
        oled.clear()
        print("✅ OLED test passed")
    except Exception as e:
        print(f"❌ OLED test failed: {e}")
    
    # Test relay
    try:
        print("Testing relay...")
        with RelayController(pin=17) as relay:
            relay.pulse(1.0)
        print("✅ Relay test passed")
    except Exception as e:
        print(f"❌ Relay test failed: {e}")


def servo_cli(args):
    """Servo CLI command handler."""
    print(f"🎯 Servo Control (Pin {args.pin})")
    
    try:
        with ServoController(pin=args.pin) as servo:
            if args.angle is not None:
                print(f"Setting servo to {args.angle}°")
                servo.set_angle(args.angle)
                time.sleep(1)
            elif args.sweep:
                print("Performing sweep...")
                servo.sweep(cycles=2)
            elif args.center:
                print("Centering servo...")
                servo.center()
            else:
                print("No action specified. Use --angle, --sweep, or --center")
    except Exception as e:
        print(f"Servo error: {e}")


def oled_cli(args):
    """OLED CLI command handler.""" 
    print("📺 OLED Display Control")
    
    try:
        oled = OLEDDisplay()
        
        if args.text:
            print(f"Displaying text: {args.text}")
            oled.write_text(args.text, 0, 0)
        elif args.clear:
            print("Clearing display...")
            oled.clear()
        elif args.demo:
            print("Running OLED demo...")
            oled_demo(oled)
        else:
            print("No action specified. Use --text, --clear, or --demo")
    except Exception as e:
        print(f"OLED error: {e}")


def oled_demo(oled: OLEDDisplay):
    """Run OLED demonstration."""
    # Text demo
    oled.write_text("CLI Demo", 0, 0)
    time.sleep(2)
    
    # Multi-line demo
    lines = ["Line 1", "Line 2", "Line 3"]
    oled.clear(show=False)
    oled.write_multiline(lines, 0, 0, line_height=12)
    time.sleep(2)
    
    # Graphics demo
    oled.clear(show=False)
    oled.draw_rectangle(10, 10, 50, 20, outline=255)
    oled.draw_circle(100, 25, 10, outline=255)
    oled.show()
    time.sleep(2)
    
    # Progress bar demo
    oled.clear(show=False)
    oled.write_text("Loading...", 0, 0, show=False)
    for i in range(0, 101, 20):
        oled.progress_bar(i, 10, 20, 80, 10)
        time.sleep(0.3)
    
    time.sleep(1)
    oled.clear()


def relay_cli(args):
    """Relay CLI command handler."""
    print(f"⚡ Relay Control (Pin {args.pin})")
    
    try:
        with RelayController(pin=args.pin) as relay:
            if args.on:
                print("Turning relay ON")
                relay.turn_on()
            elif args.off:
                print("Turning relay OFF")
                relay.turn_off()
            elif args.toggle:
                print("Toggling relay")
                relay.toggle()
            elif args.pulse:
                print(f"Pulsing relay for {args.pulse} seconds")
                relay.pulse(args.pulse)
            else:
                print("No action specified. Use --on, --off, --toggle, or --pulse")
    except Exception as e:
        print(f"Relay error: {e}")


def server_cli(args):
    """Web server CLI command handler."""
    print(f"🌐 Starting web server on {args.host}:{args.port}")
    
    try:
        server = FlaskServer(
            name="CLI Web Server",
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
        # Add some demo data
        server.set_data("status", "running")
        server.set_data("started_at", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        print(f"🌍 Web interface: http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop server")
        
        server.run()
    except Exception as e:
        print(f"Server error: {e}")


# Individual CLI entry points for setuptools console_scripts
def servo_cli_entry():
    """Entry point for rpi-servo command."""
    parser = argparse.ArgumentParser(description="Control servo motor")
    parser.add_argument('--pin', type=int, default=11, help='GPIO pin number')
    parser.add_argument('--angle', type=float, help='Set servo angle (0-180)')
    parser.add_argument('--sweep', action='store_true', help='Perform sweep')
    parser.add_argument('--center', action='store_true', help='Center servo')
    
    args = parser.parse_args()
    servo_cli(args)


def oled_cli_entry():
    """Entry point for rpi-oled command."""
    parser = argparse.ArgumentParser(description="Control OLED display")
    parser.add_argument('--text', type=str, help='Text to display')
    parser.add_argument('--clear', action='store_true', help='Clear display')
    parser.add_argument('--demo', action='store_true', help='Run OLED demo')
    
    args = parser.parse_args()
    oled_cli(args)


def relay_cli_entry():
    """Entry point for rpi-relay command."""
    parser = argparse.ArgumentParser(description="Control relay")
    parser.add_argument('--pin', type=int, default=17, help='GPIO pin number')
    parser.add_argument('--on', action='store_true', help='Turn relay on')
    parser.add_argument('--off', action='store_true', help='Turn relay off')
    parser.add_argument('--toggle', action='store_true', help='Toggle relay')
    parser.add_argument('--pulse', type=float, help='Pulse duration in seconds')
    
    args = parser.parse_args()
    relay_cli(args)


def server_cli_entry():
    """Entry point for rpi-server command."""
    parser = argparse.ArgumentParser(description="Start web server")
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    server_cli(args)


if __name__ == "__main__":
    main()
