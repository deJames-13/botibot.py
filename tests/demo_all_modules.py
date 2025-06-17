#!/usr/bin/env python3
"""
Comprehensive example demonstrating all the reusable modules.

This example shows how to use:
- ServoController for servo motor control
- OLEDDisplay for display management
- RelayController for relay switching
- FlaskServer for web interface

Author: Raspberry Pi Lab
Date: 2024
"""

import time
import threading
from datetime import datetime
import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules import ServoController, OLEDDisplay, RelayController, FlaskServer


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
        
        # System status
        self.system_status = {
            'temperature': 25.0,
            'humidity': 60.0,
            'servo_angle': 90,
            'relay_state': False,
            'last_update': datetime.now().isoformat()
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
            
            print("✅ All components initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            # Continue with available components
    
    def setup_web_server(self):
        """Setup web server with custom routes."""
        print("🌐 Setting up web server...")
        
        self.web_server = FlaskServer(
            name="Raspberry Pi Lab Controller",
            port=5000,
            debug=False
        )
        
        # Set initial data
        self.web_server.update_data(self.system_status)
        
        # Add custom routes
        self.add_custom_routes()
        
        print("✅ Web server configured!")
    
    def add_custom_routes(self):
        """Add custom web routes."""
        
        @self.web_server.add_route('/api/servo/<int:angle>', methods=['POST'])
        def control_servo(angle):
            """Control servo angle via web API."""
            try:
                if self.servo:
                    self.servo.set_angle(angle)
                    self.system_status['servo_angle'] = angle
                    self.web_server.set_data('servo_angle', angle)
                    return {'success': True, 'angle': angle}
                else:
                    return {'error': 'Servo not available'}, 500
            except Exception as e:
                return {'error': str(e)}, 400
        
        @self.web_server.add_route('/api/relay/<action>', methods=['POST'])
        def control_relay(action):
            """Control relay via web API."""
            try:
                if self.relay:
                    if action.lower() == 'on':
                        self.relay.turn_on()
                        state = True
                    elif action.lower() == 'off':
                        self.relay.turn_off()
                        state = False
                    elif action.lower() == 'toggle':
                        self.relay.toggle()
                        state = self.relay.is_on()
                    else:
                        return {'error': 'Invalid action'}, 400
                    
                    self.system_status['relay_state'] = state
                    self.web_server.set_data('relay_state', state)
                    return {'success': True, 'state': state}
                else:
                    return {'error': 'Relay not available'}, 500
            except Exception as e:
                return {'error': str(e)}, 400
        
        @self.web_server.add_route('/api/display', methods=['POST'])
        def control_display():
            """Update OLED display via web API."""
            try:
                from flask import request
                data = request.get_json()
                
                if not data or 'text' not in data:
                    return {'error': 'Text required'}, 400
                
                if self.oled:
                    text = data['text']
                    x = data.get('x', 0)
                    y = data.get('y', 0)
                    
                    self.oled.clear(show=False)
                    self.oled.write_text(text, x, y)
                    return {'success': True, 'text': text}
                else:
                    return {'error': 'Display not available'}, 500
            except Exception as e:
                return {'error': str(e)}, 400
        
        @self.web_server.add_route('/api/status/hardware')
        def hardware_status():
            """Get hardware component status."""
            return {
                'servo': self.servo is not None,
                'oled': self.oled is not None,
                'relay': self.relay is not None,
                'servo_angle': self.system_status.get('servo_angle', 0),
                'relay_state': self.system_status.get('relay_state', False)
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
                datetime.now().strftime("%H:%M:%S")
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
                self.system_status['temperature'] = round(20 + random.random() * 15, 1)
                self.system_status['humidity'] = round(40 + random.random() * 40, 1)
                self.system_status['last_update'] = datetime.now().isoformat()
                
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
                    self.system_status['servo_angle'] = angle
                    print(f"  Servo at {angle}°")
            
            # Relay demo
            if self.relay:
                print("⚡ Relay demo...")
                if self.oled:
                    self.oled.clear(show=False)
                    self.oled.write_text("Relay Demo", 0, 0, show=True)
                
                for i in range(3):
                    self.relay.turn_on()
                    self.system_status['relay_state'] = True
                    print("  Relay ON")
                    time.sleep(1)
                    
                    self.relay.turn_off()
                    self.system_status['relay_state'] = False
                    print("  Relay OFF")
                    time.sleep(1)
            
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
            sensor_thread = threading.Thread(target=self.simulate_sensor_data, daemon=True)
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
    print("="*50)
    print("🍓 RASPBERRY PI LAB MODULE DEMO")
    print("="*50)
    print()
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' not in f.read():
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
