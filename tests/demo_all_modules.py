#!/usr/bin/env python3
"""
Comprehensive example demonstrating all the modules.py modules.

This example shows how to use:
- ServoController for servo motor control
- OLEDDisplay for display management
- RelayController for relay switching
- FlaskServer for web interface
- InfraredSensor for infrared detection
- UltrasonicSensor for distance measurement
- MotorController for motor control

Author: deJames-13
Email: de.james013@gmail.com
GitHub: github.com/deJames-13/modules
Date: 2025
"""

import time
import threading
from datetime import datetime
import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modules"))

from botibot import ServoController, OLEDDisplay, RelayController, FlaskServer
from botibot.gsm import SIM800LController
from botibot.ir_temp import MLX90614Sensor
from botibot.scheduler import PillScheduler


class RaspberryPiController:
    """
    Main controller class that integrates all modules.
    """

    def __init__(self):
        """Initialize all components."""
        print("🍓 Initializing Raspberry Pi Controller...")

        # Initialize components
        self.servo = None
        self.oled = None
        self.relay = None
        self.web_server = None
        
        # New components
        self.gsm = None
        self.ir_temp = None
        self.pill_scheduler = None

        # System status
        self.system_status = {
            "temperature": 25.0,
            "humidity": 60.0,
            "servo_angle": 90,
            "relay_state": False,
            "ambient_temp": 22.0,
            "object_temp": 37.0,
            "gsm_signal": "Unknown",
            "next_pill": "None scheduled",
            "last_update": datetime.now().isoformat(),
        }

        self.setup_components()
        self.setup_web_server()

    def setup_components(self):
        """Setup hardware components."""
        try:
            # Initialize servo (GPIO pin 11)
            print("🔧 Setting up servo controller...")
            self.servo = ServoController(pin=11)
            self.servo.center()  # Start at center position

            # Initialize OLED display
            print("📺 Setting up OLED display...")
            self.oled = OLEDDisplay(width=128, height=64)
            self.oled.write_text("System Starting...", 0, 0)

            # Initialize relay (GPIO pin 17)
            print("⚡ Setting up relay controller...")
            self.relay = RelayController(pin=17)
            
            # Initialize GSM module
            print("📱 Setting up GSM module...")
            try:
                self.gsm = SIM800LController(port="/dev/ttyS0", baudrate=9600)
                print(f"GSM Status: {self.gsm.get_network_status()}")
                self.system_status["gsm_signal"] = f"{self.gsm.get_signal_strength()} dBm"
            except Exception as e:
                print(f"⚠️ GSM module initialization warning: {e}")
                print("GSM features will be disabled")
                
            # Initialize IR Temperature sensor
            print("🌡️ Setting up IR Temperature sensor...")
            try:
                self.ir_temp = MLX90614Sensor(bus_number=1, address=0x5A)
                ambient_temp, object_temp = self.ir_temp.get_temperatures()
                self.system_status["ambient_temp"] = ambient_temp
                self.system_status["object_temp"] = object_temp
                print(f"Ambient: {ambient_temp:.1f}°C, Object: {object_temp:.1f}°C")
            except Exception as e:
                print(f"⚠️ IR Temperature sensor warning: {e}")
                print("Temperature measurement features will be disabled")
                
            # Initialize Pill Scheduler
            print("🗓️ Setting up Pill Scheduler...")
            try:
                self.pill_scheduler = PillScheduler()
                next_med = self.pill_scheduler.get_next_medication()
                if next_med:
                    self.system_status["next_pill"] = f"{next_med['name']} at {next_med['time']}"
                    print(f"Next medication: {next_med['name']} at {next_med['time']}")
                else:
                    print("No upcoming medications scheduled")
            except Exception as e:
                print(f"⚠️ Pill Scheduler warning: {e}")
                print("Scheduling features will be disabled")

            print("✅ All components initialized successfully!")

        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            # Continue with available components

    def setup_web_server(self):
        """Setup web server with custom routes."""
        print("🌐 Setting up web server...")

        self.web_server = FlaskServer(
            name="Raspberry Pi Lab Controller", port=5000, debug=False
        )

        # Set initial data
        self.web_server.update_data(self.system_status)

        # Add custom routes
        self.add_custom_routes()

        print("✅ Web server configured!")

    def add_custom_routes(self):
        """Add custom web routes."""

        @self.web_server.add_route("/api/servo/<int:angle>", methods=["POST"])
        def control_servo(angle):
            """Control servo angle via web API."""
            try:
                if self.servo:
                    self.servo.set_angle(angle)
                    self.system_status["servo_angle"] = angle
                    self.web_server.set_data("servo_angle", angle)
                    return {"success": True, "angle": angle}
                else:
                    return {"error": "Servo not available"}, 500
            except Exception as e:
                return {"error": str(e)}, 500
                
        @self.web_server.add_route("/api/temperature", methods=["GET"])
        def get_temperature():
            """Get IR temperature readings."""
            try:
                if self.ir_temp:
                    ambient, object_temp = self.ir_temp.get_temperatures()
                    self.system_status["ambient_temp"] = ambient
                    self.system_status["object_temp"] = object_temp
                    self.web_server.set_data("ambient_temp", ambient)
                    self.web_server.set_data("object_temp", object_temp)
                    return {
                        "success": True, 
                        "ambient": ambient,
                        "object": object_temp,
                        "unit": "celsius"
                    }
                else:
                    return {"error": "IR Temperature sensor not available"}, 500
            except Exception as e:
                return {"error": str(e)}, 500
                
        @self.web_server.add_route("/api/sms", methods=["POST"])
        def send_sms():
            """Send SMS notification."""
            from flask import request
            try:
                if self.gsm:
                    data = request.json
                    if not data or "phone" not in data or "message" not in data:
                        return {"error": "Missing required fields (phone, message)"}, 400
                        
                    result = self.gsm.send_sms(data["phone"], data["message"])
                    return {
                        "success": result, 
                        "phone": data["phone"]
                    }
                else:
                    return {"error": "GSM module not available"}, 500
            except Exception as e:
                return {"error": str(e)}, 500
                
        @self.web_server.add_route("/api/schedule", methods=["GET"])
        def get_schedule():
            """Get medication schedule."""
            try:
                if self.pill_scheduler:
                    schedules = self.pill_scheduler.get_all_schedules()
                    return {
                        "success": True, 
                        "schedules": schedules
                    }
                else:
                    return {"error": "Pill scheduler not available"}, 500
            except Exception as e:
                return {"error": str(e)}, 500
                
        @self.web_server.add_route("/api/schedule", methods=["POST"])
        def add_schedule():
            """Add medication schedule."""
            from flask import request
            try:
                if self.pill_scheduler:
                    data = request.json
                    if not data or not all(k in data for k in ["name", "dosage", "times", "days"]):
                        return {"error": "Missing required fields"}, 400
                        
                    schedule_id = self.pill_scheduler.add_schedule(
                        name=data["name"],
                        dosage=data["dosage"],
                        times=data["times"],
                        days=data["days"],
                        start_date=data.get("start_date"),
                        end_date=data.get("end_date"),
                        notes=data.get("notes", "")
                    )
                    
                    next_med = self.pill_scheduler.get_next_medication()
                    if next_med:
                        self.system_status["next_pill"] = f"{next_med['name']} at {next_med['time']}"
                        self.web_server.set_data("next_pill", self.system_status["next_pill"])
                        
                    return {
                        "success": True, 
                        "id": schedule_id
                    }
                else:
                    return {"error": "Pill scheduler not available"}, 500
            except Exception as e:
                return {"error": str(e)}, 500

        @self.web_server.add_route("/api/status/hardware")
        def hardware_status():
            """Get hardware component status."""
            return {
                "servo": self.servo is not None,
                "oled": self.oled is not None,
                "relay": self.relay is not None,
                "servo_angle": self.system_status.get("servo_angle", 0),
                "relay_state": self.system_status.get("relay_state", False),
            }

    def update_display_status(self):
        """Update OLED display with current status."""
        if not self.oled:
            return

        try:
            status_lines = [
                "🍓 Pi Controller",
                f"Servo: {self.system_status['servo_angle']}°",
                f"Relay: {'ON' if self.system_status['relay_state'] else 'OFF'}",
                f"Temp: {self.system_status['temperature']:.1f}°C",
                datetime.now().strftime("%H:%M:%S"),
            ]

            self.oled.clear(show=False)
            self.oled.write_multiline(status_lines, x=0, y=0, line_height=10)

        except Exception as e:
            print(f"Display update error: {e}")

    def simulate_sensor_data(self):
        """Simulate sensor data updates."""
        import random

        while True:
            try:
                # Simulate temperature and humidity readings
                self.system_status["temperature"] = round(20 + random.random() * 15, 1)
                self.system_status["humidity"] = round(40 + random.random() * 40, 1)
                self.system_status["last_update"] = datetime.now().isoformat()

                # Update web server data
                self.web_server.update_data(self.system_status)

                # Update OLED display
                self.update_display_status()

                time.sleep(5)  # Update every 5 seconds

            except Exception as e:
                print(f"Sensor simulation error: {e}")
                time.sleep(5)

    def run_demo_sequence(self):
        """Run a demonstration sequence."""
        print("🎬 Starting demo sequence...")

        try:
            if self.oled:
                self.oled.write_text("Demo Starting...", 0, 0)
                time.sleep(2)

            # Servo demo
            if self.servo:
                print("🎯 Servo demo...")
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("Servo Demo", 0, 0, show=True)

                for angle in [0, 45, 90, 135, 180, 90]:
                    self.servo.move_to_position(angle, delay=1)
                    self.system_status["servo_angle"] = angle
                    print(f"  Servo at {angle}°")

            # Relay demo
            if self.relay:
                print("⚡ Relay demo...")
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("Relay Demo", 0, 0, show=True)

                for i in range(3):
                    self.relay.turn_on()
                    self.system_status["relay_state"] = True
                    print("  Relay ON")
                    time.sleep(1)

                    self.relay.turn_off()
                    self.system_status["relay_state"] = False
                    print("  Relay OFF")
                    time.sleep(1)
                    
            # IR Temperature demo
            if self.ir_temp:
                print("🌡️ IR Temperature demo...")
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("IR Temp Demo", 0, 0, show=True)
                
                for i in range(3):
                    ambient, object_temp = self.ir_temp.get_temperatures()
                    self.system_status["ambient_temp"] = ambient
                    self.system_status["object_temp"] = object_temp
                    print(f"  Ambient: {ambient:.1f}°C, Object: {object_temp:.1f}°C")
                    
                    if self.oled:
                        self.oled.clear(show=False)
                        self.oled.write_text("IR Temperature", 0, 0, show=False)
                        self.oled.write_text(f"Ambient: {ambient:.1f}C", 0, 16, show=False)
                        self.oled.write_text(f"Object: {object_temp:.1f}C", 0, 32, show=True)
                    
                    time.sleep(2)
                    
            # GSM demo
            if self.gsm:
                print("📱 GSM demo...")
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("GSM Demo", 0, 0, show=True)
                
                # Just check status, don't send SMS in demo
                network_status = self.gsm.get_network_status()
                signal_strength = self.gsm.get_signal_strength()
                self.system_status["gsm_signal"] = f"{signal_strength} dBm"
                
                print(f"  Network: {network_status}")
                print(f"  Signal: {signal_strength} dBm")
                
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("GSM Status", 0, 0, show=False)
                    self.oled.write_text(f"Network: {network_status}", 0, 16, show=False)
                    self.oled.write_text(f"Signal: {signal_strength}dBm", 0, 32, show=True)
                
                time.sleep(2)
                
            # Scheduler demo
            if self.pill_scheduler:
                print("🗓️ Scheduler demo...")
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("Scheduler Demo", 0, 0, show=True)
                
                next_med = self.pill_scheduler.get_next_medication()
                if next_med:
                    print(f"  Next: {next_med['name']} at {next_med['time']}")
                    self.system_status["next_pill"] = f"{next_med['name']} at {next_med['time']}"
                    
                    if self.oled:
                        self.oled.clear(show=False)
                        self.oled.write_text("Next Medication", 0, 0, show=False)
                        self.oled.write_text(f"{next_med['name']}", 0, 16, show=False)
                        self.oled.write_text(f"Time: {next_med['time']}", 0, 32, show=True)
                else:
                    print("  No upcoming medications")
                    
                    if self.oled:
                        self.oled.clear(show=False)
                        self.oled.write_text("Medications", 0, 0, show=False)
                        self.oled.write_text("No upcoming", 0, 16, show=False)
                        self.oled.write_text("medications", 0, 32, show=True)
                
                time.sleep(2)

            # Display demo
            if self.oled:
                print("📺 Display demo...")
                self.oled.clear()
                self.oled.blink_text("DEMO COMPLETE!", 10, 25, blinks=3, delay=0.5)

            print("✅ Demo sequence completed!")

        except Exception as e:
            print(f"Demo error: {e}")

    def start_web_server(self):
        """Start the web server in background."""
        print("🌐 Starting web server...")
        self.web_server.run(threaded=True)
        print(f"🌍 Web interface available at: http://localhost:5000")
        print("   - Dashboard: http://localhost:5000")
        print("   - Control Panel: http://localhost:5000/control")
        print("   - API Status: http://localhost:5000/api/status")

    def run(self):
        """Main run method."""
        try:
            # Start web server
            self.start_web_server()

            # Start sensor simulation in background
            sensor_thread = threading.Thread(
                target=self.simulate_sensor_data, daemon=True
            )
            sensor_thread.start()

            # Run demo sequence
            self.run_demo_sequence()

            # Keep running and updating display
            print("🔄 System running... (Press Ctrl+C to stop)")
            print("💡 Try the web interface for remote control!")

            while True:
                self.update_display_status()
                time.sleep(10)  # Update display every 10 seconds

        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.cleanup()
        except Exception as e:
            print(f"❌ Runtime error: {e}")
            self.cleanup()

    def cleanup(self):
        """Clean up all resources."""
        print("🧹 Cleaning up resources...")

        try:
            if self.servo:
                self.servo.cleanup()
                print("  ✓ Servo cleaned up")

            if self.oled:
                self.oled.clear()
                print("  ✓ OLED cleared")

            if self.relay:
                self.relay.cleanup()
                print("  ✓ Relay cleaned up")

            print("✅ Cleanup complete!")

        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")


def main():
    """Main function."""
    print("=" * 50)
    print("🍓 RASPBERRY PI LAB MODULE DEMO")
    print("=" * 50)
    print()

    # Check if running on Raspberry Pi
    try:
        with open("/proc/cpuinfo", "r") as f:
            if "Raspberry Pi" not in f.read():
                print("⚠️  Warning: Not running on Raspberry Pi")
                print("   Some hardware features may not work properly")
        print()
    except:
        print("⚠️  Could not detect Raspberry Pi")
        print()

    # Create and run controller
    controller = RaspberryPiController()
    controller.run()


if __name__ == "__main__":
    main()
