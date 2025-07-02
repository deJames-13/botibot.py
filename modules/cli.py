#!/usr/bin/env python3
"""
Command-line interface tools for modules.py package.

This module provides CLI commands for quick testing and control of hardware components
using the gpiozero-based modules.
"""

import argparse
import sys
import time

try:
    from modules import (
        ServoController, 
        OLEDDisplay, 
        RelayController, 
        FlaskServer,
        InfraredSensor,
        UltrasonicSensor,
        MotorController,
        DualMotorController
    )
    # Import new modules
    from modules.gsm import SIM800LController
    from modules.ir_temp import MLX90614Sensor
    from modules.scheduler import PillScheduler
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure modules.py is properly installed")
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Modules.py CLI Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  modules-demo                           # Run complete demo
  modules-servo --pin 18 --angle 90     # Set servo to 90 degrees
  modules-oled --text "Hello Pi"        # Display text on OLED
  modules-relay --pin 17 --on           # Turn relay on
  modules-infrared --pin 24 --detect    # Test infrared sensor
  modules-ultrasonic --trigger 23 --echo 24 --measure  # Measure distance
  modules-motor --forward 20 --backward 21 --test      # Test motor
  modules-server --port 8080            # Start web server on port 8080
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run complete hardware demo")
    demo_parser.add_argument("--quick", action="store_true", help="Run quick demo")

    # Servo command
    servo_parser = subparsers.add_parser("servo", help="Control servo motor")
    servo_parser.add_argument("--pin", type=int, default=18, help="GPIO pin number (default: 18)")
    servo_parser.add_argument("--angle", type=float, help="Set servo angle (0-180)")
    servo_parser.add_argument("--sweep", action="store_true", help="Perform sweep")
    servo_parser.add_argument("--center", action="store_true", help="Center servo")

    # OLED command
    oled_parser = subparsers.add_parser("oled", help="Control OLED display")
    oled_parser.add_argument("--text", type=str, help="Text to display")
    oled_parser.add_argument("--clear", action="store_true", help="Clear display")
    oled_parser.add_argument("--demo", action="store_true", help="Run OLED demo")

    # Relay command
    relay_parser = subparsers.add_parser("relay", help="Control relay")
    relay_parser.add_argument("--pin", type=int, default=17, help="GPIO pin number (default: 17)")
    relay_parser.add_argument("--on", action="store_true", help="Turn relay on")
    relay_parser.add_argument("--off", action="store_true", help="Turn relay off")
    relay_parser.add_argument("--toggle", action="store_true", help="Toggle relay")
    relay_parser.add_argument("--pulse", type=float, help="Pulse duration in seconds")

    # Infrared command
    infrared_parser = subparsers.add_parser("infrared", help="Control infrared sensor")
    infrared_parser.add_argument("--pin", type=int, default=24, help="GPIO pin number (default: 24)")
    infrared_parser.add_argument("--detect", action="store_true", help="Test object detection")
    infrared_parser.add_argument("--monitor", type=int, help="Monitor for N seconds")

    # Ultrasonic command
    ultrasonic_parser = subparsers.add_parser("ultrasonic", help="Control ultrasonic sensor")
    ultrasonic_parser.add_argument("--trigger", type=int, default=23, help="Trigger pin (default: 23)")
    ultrasonic_parser.add_argument("--echo", type=int, default=24, help="Echo pin (default: 24)")
    ultrasonic_parser.add_argument("--measure", action="store_true", help="Take distance measurement")
    ultrasonic_parser.add_argument("--monitor", type=int, help="Monitor for N seconds")

    # Motor command
    motor_parser = subparsers.add_parser("motor", help="Control DC motor")
    motor_parser.add_argument("--forward", type=int, default=20, help="Forward pin (default: 20)")
    motor_parser.add_argument("--backward", type=int, default=21, help="Backward pin (default: 21)")
    motor_parser.add_argument("--enable", type=int, help="Enable pin (optional)")
    motor_parser.add_argument("--test", action="store_true", help="Run motor test")
    motor_parser.add_argument("--speed", type=float, default=0.7, help="Motor speed (0-1)")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start web server")
    server_parser.add_argument("--port", type=int, default=5000, help="Port number (default: 5000)")
    server_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")

    # GSM command
    gsm_parser = subparsers.add_parser("gsm", help="Control GSM module (SIM800L)")
    gsm_parser.add_argument("--port", type=str, default="/dev/ttyS0", help="Serial port (default: /dev/ttyS0)")
    gsm_parser.add_argument("--baudrate", type=int, default=9600, help="Baud rate (default: 9600)")
    gsm_parser.add_argument("--phone", type=str, help="Phone number to send SMS")
    gsm_parser.add_argument("--message", type=str, help="SMS message to send")
    gsm_parser.add_argument("--status", action="store_true", help="Check GSM module status")
    gsm_parser.add_argument("--signal", action="store_true", help="Check signal strength")

    # IR Temperature command
    ir_temp_parser = subparsers.add_parser("ir-temp", help="Control IR temperature sensor (GY-906)")
    ir_temp_parser.add_argument("--bus", type=int, default=1, help="I2C bus number (default: 1)")
    ir_temp_parser.add_argument("--address", type=int, default=0x5A, help="I2C address (default: 0x5A)")
    ir_temp_parser.add_argument("--button-pin", type=int, default=21, help="Button GPIO pin (default: 21)")
    ir_temp_parser.add_argument("--read", action="store_true", help="Read temperature once")
    ir_temp_parser.add_argument("--monitor", action="store_true", help="Monitor temperatures continuously")

    # Scheduler command
    scheduler_parser = subparsers.add_parser("scheduler", help="Control pill scheduler")
    scheduler_parser.add_argument("--add", action="store_true", help="Add new medication schedule")
    scheduler_parser.add_argument("--list", action="store_true", help="List all schedules")
    scheduler_parser.add_argument("--start", action="store_true", help="Start scheduler daemon")
    scheduler_parser.add_argument("--name", type=str, help="Medication name")
    scheduler_parser.add_argument("--dosage", type=str, help="Medication dosage")
    scheduler_parser.add_argument("--times", type=str, nargs="+", help="Medication times (HH:MM format)")
    scheduler_parser.add_argument("--days", type=str, nargs="+", help="Days of week")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "demo":
            run_demo(args.quick)
        elif args.command == "servo":
            servo_cli(args)
        elif args.command == "oled":
            oled_cli(args)
        elif args.command == "relay":
            relay_cli(args)
        elif args.command == "infrared":
            infrared_cli(args)
        elif args.command == "ultrasonic":
            ultrasonic_cli(args)
        elif args.command == "motor":
            motor_cli(args)
        elif args.command == "server":
            server_cli(args)
        elif args.command == "gsm":
            gsm_cli(args)
        elif args.command == "ir-temp":
            ir_temp_cli(args)
        elif args.command == "scheduler":
            scheduler_cli(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def run_demo(quick: bool = False):
    """Run complete hardware demonstration."""
    print("🍓 Modules.py Hardware Demo")
    print("=" * 40)
    
    duration = 5 if quick else 10
    
    try:
        # Test servo
        print("\n🔧 Testing Servo Controller...")
        with ServoController(pin=18) as servo:
            servo.center()
            time.sleep(1)
            servo.sweep(0, 180, step=30, delay=0.2, cycles=1)
            servo.center()
        print("✅ Servo test completed")
        
        # Test relay
        print("\n🔌 Testing Relay Controller...")
        with RelayController(pin=17) as relay:
            relay.blink(on_time=0.3, off_time=0.3, cycles=3)
        print("✅ Relay test completed")
        
        # Test infrared sensor
        print("\n🔍 Testing Infrared Sensor...")
        with InfraredSensor(pin=24) as ir_sensor:
            print(f"   Detection status: {'Detected' if ir_sensor.is_detected() else 'Clear'}")
        print("✅ Infrared sensor test completed")
        
        # Test ultrasonic sensor
        print("\n📏 Testing Ultrasonic Sensor...")
        with UltrasonicSensor(trigger_pin=23, echo_pin=24) as us_sensor:
            distance = us_sensor.get_distance()
            if distance:
                print(f"   Distance: {distance:.2f}m ({distance*100:.1f}cm)")
            else:
                print("   Distance: Out of range")
        print("✅ Ultrasonic sensor test completed")
        
        # Test motor
        print("\n⚙️  Testing Motor Controller...")
        with MotorController(forward_pin=20, backward_pin=21) as motor:
            motor.forward(0.5)
            time.sleep(1)
            motor.stop()
            time.sleep(0.5)
            motor.backward(0.5)
            time.sleep(1)
            motor.stop()
        print("✅ Motor test completed")
        
        print("\n🎉 All hardware tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


def servo_cli(args):
    """Servo command line interface."""
    print(f"🔧 Servo Control - Pin {args.pin}")
    
    try:
        with ServoController(pin=args.pin) as servo:
            if args.angle is not None:
                print(f"Setting servo to {args.angle}°...")
                servo.set_angle(args.angle)
                time.sleep(1)
            elif args.sweep:
                print("Performing servo sweep...")
                servo.sweep(0, 180, step=15, delay=0.2, cycles=2)
            elif args.center:
                print("Centering servo...")
                servo.center()
            else:
                print("No action specified. Use --angle, --sweep, or --center")
                
    except Exception as e:
        print(f"❌ Servo error: {e}")


def oled_cli(args):
    """OLED command line interface."""
    print("📺 OLED Control")
    
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
        print(f"❌ OLED error: {e}")


def oled_demo(oled: OLEDDisplay):
    """Run OLED demonstration."""
    # Basic text
    oled.write_text("Modules.py Demo", 0, 0)
    time.sleep(2)
    
    # Multi-line text
    lines = ["Line 1", "Line 2", "Line 3"]
    oled.clear(show=False)
    oled.write_multiline(lines, 0, 0, line_height=12)
    time.sleep(2)
    
    # Graphics
    oled.clear(show=False)
    oled.draw_rectangle(10, 10, 50, 30, outline=255)
    oled.draw_circle(100, 25, 15, outline=255)
    oled.show()
    time.sleep(2)
    
    # Status display
    status = {"Status": "OK", "Temp": "25°C", "Time": time.strftime("%H:%M")}
    oled.display_status("System", status)
    time.sleep(3)
    
    oled.clear()


def relay_cli(args):
    """Relay command line interface."""
    print(f"🔌 Relay Control - Pin {args.pin}")
    
    try:
        with RelayController(pin=args.pin) as relay:
            if args.on:
                print("Turning relay ON...")
                relay.turn_on()
            elif args.off:
                print("Turning relay OFF...")
                relay.turn_off()
            elif args.toggle:
                print("Toggling relay...")
                relay.toggle()
            elif args.pulse:
                print(f"Pulsing relay for {args.pulse}s...")
                relay.pulse(args.pulse)
            else:
                print("No action specified. Use --on, --off, --toggle, or --pulse")
                
    except Exception as e:
        print(f"❌ Relay error: {e}")


def infrared_cli(args):
    """Infrared sensor command line interface."""
    print(f"🔍 Infrared Sensor - Pin {args.pin}")
    
    try:
        with InfraredSensor(pin=args.pin) as ir_sensor:
            if args.detect:
                print("Testing object detection...")
                detected = ir_sensor.is_detected()
                print(f"Result: {'Object detected' if detected else 'No object detected'}")
            elif args.monitor:
                print(f"Monitoring for {args.monitor} seconds...")
                
                def on_detection():
                    print("🚨 Object detected!")
                
                def on_no_detection():
                    print("✅ Object lost")
                
                ir_sensor.set_detection_callback(on_detection)
                ir_sensor.set_no_detection_callback(on_no_detection)
                ir_sensor.start_monitoring(duration=args.monitor)
                
                time.sleep(args.monitor + 1)
            else:
                print("No action specified. Use --detect or --monitor")
                
    except Exception as e:
        print(f"❌ Infrared sensor error: {e}")


def ultrasonic_cli(args):
    """Ultrasonic sensor command line interface."""
    print(f"📏 Ultrasonic Sensor - Trigger: {args.trigger}, Echo: {args.echo}")
    
    try:
        with UltrasonicSensor(trigger_pin=args.trigger, echo_pin=args.echo) as us_sensor:
            if args.measure:
                print("Taking distance measurement...")
                distance = us_sensor.get_distance(samples=5)
                if distance:
                    distance_cm = distance * 100
                    distance_in = distance * 39.3701
                    print(f"Distance: {distance:.3f}m ({distance_cm:.1f}cm, {distance_in:.1f}in)")
                    print(f"Object detected: {'Yes' if us_sensor.is_object_detected() else 'No'}")
                else:
                    print("Distance: Out of range")
            elif args.monitor:
                print(f"Monitoring for {args.monitor} seconds...")
                
                def on_object_detected(distance):
                    print(f"🚨 Object detected at {distance:.3f}m!")
                
                def on_object_lost(distance):
                    print(f"✅ Object lost - distance now {distance:.3f}m")
                
                us_sensor.set_callback('object_detected', on_object_detected)
                us_sensor.set_callback('object_lost', on_object_lost)
                us_sensor.start_monitoring(interval=0.2)
                
                time.sleep(args.monitor)
            else:
                print("No action specified. Use --measure or --monitor")
                
    except Exception as e:
        print(f"❌ Ultrasonic sensor error: {e}")


def motor_cli(args):
    """Motor command line interface."""
    print(f"⚙️  Motor Control - Forward: {args.forward}, Backward: {args.backward}")
    
    try:
        with MotorController(forward_pin=args.forward, backward_pin=args.backward, 
                           enable_pin=args.enable) as motor:
            if args.test:
                print("Running motor test...")
                print(f"Forward at {args.speed} speed...")
                motor.forward(args.speed)
                time.sleep(2)
                
                print("Stopping...")
                motor.stop()
                time.sleep(1)
                
                print(f"Backward at {args.speed} speed...")
                motor.backward(args.speed)
                time.sleep(2)
                
                print("Stopping...")
                motor.stop()
                
                print("Test completed!")
            else:
                print("No action specified. Use --test")
                
    except Exception as e:
        print(f"❌ Motor error: {e}")


def server_cli(args):
    """Web server command line interface."""
    print(f"🌐 Starting web server on {args.host}:{args.port}")
    
    try:
        server = FlaskServer(
            name="Modules.py Demo Server", 
            host=args.host, 
            port=args.port, 
            debug=False
        )
        
        # Add some demo data
        server.set_data("temperature", 25.6)
        server.set_data("humidity", 60.2)
        server.set_data("status", "operational")
        server.set_data("modules", "servo,relay,oled,infrared,ultrasonic,motor")
        
        print(f"✅ Server running at http://{args.host}:{args.port}")
        print("🛑 Press Ctrl+C to stop")
        
        server.run()
        
    except Exception as e:
        print(f"❌ Server error: {e}")


def gsm_cli(args):
    """GSM command line interface."""
    print(f"📱 GSM Control - Port: {args.port}, Baudrate: {args.baudrate}")
    
    try:
        with SIM800LController(port=args.port, baudrate=args.baudrate) as gsm:
            if args.status:
                print("Checking GSM module status...")
                status = gsm.get_status()
                print(f"Status: {status}")
            elif args.signal:
                print("Checking signal strength...")
                signal = gsm.get_signal_strength()
                print(f"Signal strength: {signal} dBm")
            elif args.phone and args.message:
                print(f"Sending SMS to {args.phone}...")
                gsm.send_sms(args.phone, args.message)
                print("SMS sent!")
            else:
                print("No valid action specified. Use --status, --signal, or provide --phone and --message")
                
    except Exception as e:
        print(f"❌ GSM error: {e}")


def ir_temp_cli(args):
    """IR Temperature command line interface."""
    print(f"🌡️ IR Temperature Sensor - Bus: {args.bus}, Address: {args.address}")
    
    try:
        with MLX90614Sensor(bus=args.bus, address=args.address) as ir_temp:
            if args.monitor:
                print("Monitoring temperatures...")
                
                def on_temperature_read(temp):
                    print(f"Temperature: {temp:.2f}°C")
                
                ir_temp.set_temperature_callback(on_temperature_read)
                ir_temp.start_monitoring(interval=1.0)
                
                time.sleep(10)
            elif args.read:
                temp = ir_temp.get_object_1()
                print(f"Object 1 temperature: {temp:.2f}°C")
            else:
                print("No action specified. Use --read or --monitor")
                
    except Exception as e:
        print(f"❌ IR Temperature error: {e}")


def scheduler_cli(args):
    """Scheduler command line interface."""
    print("🗓️ Pill Scheduler")
    
    try:
        scheduler = PillScheduler()
        
        if args.add:
            if not (args.name and args.dosage and args.times and args.days):
                print("❌ Missing required arguments for adding schedule")
                return
            
            times = [time.strip() for time in args.times]
            days = [day.strip() for day in args.days]
            scheduler.add_schedule(args.name, args.dosage, times, days)
            print(f"✅ Added schedule for {args.name}")
        elif args.list:
            schedules = scheduler.list_schedules()
            if schedules:
                print("📋 Current schedules:")
                for sch in schedules:
                    print(f" - {sch['name']}: {sch['dosage']} at {', '.join(sch['times'])} on {', '.join(sch['days'])}")
            else:
                print("No schedules found")
        elif args.start:
            print("Starting scheduler daemon...")
            scheduler.start_daemon()
            print("Scheduler daemon started")
        else:
            print("No action specified. Use --add, --list, or --start")
            
    except Exception as e:
        print(f"❌ Scheduler error: {e}")


# Individual CLI entry points for setuptools console_scripts
def servo_cli_entry():
    """Servo CLI entry point."""
    parser = argparse.ArgumentParser(description="Servo Control")
    parser.add_argument("--pin", type=int, default=18, help="GPIO pin number")
    parser.add_argument("--angle", type=float, help="Set servo angle (0-180)")
    parser.add_argument("--sweep", action="store_true", help="Perform sweep")
    parser.add_argument("--center", action="store_true", help="Center servo")
    
    args = parser.parse_args()
    servo_cli(args)


def oled_cli_entry():
    """OLED CLI entry point."""
    parser = argparse.ArgumentParser(description="OLED Control")
    parser.add_argument("--text", type=str, help="Text to display")
    parser.add_argument("--clear", action="store_true", help="Clear display")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    oled_cli(args)


def relay_cli_entry():
    """Relay CLI entry point."""
    parser = argparse.ArgumentParser(description="Relay Control")
    parser.add_argument("--pin", type=int, default=17, help="GPIO pin number")
    parser.add_argument("--on", action="store_true", help="Turn relay on")
    parser.add_argument("--off", action="store_true", help="Turn relay off")
    parser.add_argument("--toggle", action="store_true", help="Toggle relay")
    parser.add_argument("--pulse", type=float, help="Pulse duration")
    
    args = parser.parse_args()
    relay_cli(args)


def server_cli_entry():
    """Server CLI entry point."""
    parser = argparse.ArgumentParser(description="Web Server")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    
    args = parser.parse_args()
    server_cli(args)


def ir_temp_cli_entry():
    """IR Temperature Sensor CLI entry point."""
    parser = argparse.ArgumentParser(description="IR Temperature Sensor")
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number (default: 1)")
    parser.add_argument("--address", type=int, default=0x5A, help="I2C address (default: 0x5A)")
    parser.add_argument("--button-pin", type=int, default=21, help="Button GPIO pin (default: 21)")
    parser.add_argument("--read", action="store_true", help="Read temperature once")
    parser.add_argument("--monitor", action="store_true", help="Monitor temperatures continuously")
    
    args = parser.parse_args()
    ir_temp_cli(args)


if __name__ == "__main__":
    main()
