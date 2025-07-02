#!/usr/bin/env python3
"""
Pill Dispenser Dashboard Server Runner.

This script runs the Flask server with the pill dispenser dashboard.
"""

import os
import sys
import logging
from flask import Flask

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from modules.webserver.flask_server import FlaskServer
from modules.webserver.pill_dispenser_dashboard import register_with_app, cleanup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the pill dispenser dashboard server."""
    try:
        # Create Flask server instance
        server = FlaskServer(
            name="Pill Dispenser Dashboard", 
            port=5000, 
            debug=True
        )
        
        # Register the pill dispenser dashboard with the server
        register_with_app(server.app)
        
        # Add some initial data
        server.set_data("server_status", "running")
        server.set_data("pill_dispenser_status", "ready")
        
        # Start the server
        print("=" * 50)
        print("Starting Pill Dispenser Dashboard Server")
        print("=" * 50)
        print(f"Dashboard URL: http://{server.host}:{server.port}/pill-dispenser")
        print(f"Control Panel: http://{server.host}:{server.port}/control")
        print(f"API Endpoints:")
        print(f"  - http://{server.host}:{server.port}/api/heart-rate")
        print(f"  - http://{server.host}:{server.port}/api/temperature")
        print(f"  - http://{server.host}:{server.port}/api/alcohol-level")
        print(f"  - http://{server.host}:{server.port}/api/send-sms (POST)")
        print(f"  - http://{server.host}:{server.port}/api/session (POST)")
        print("=" * 50)
        
        server.run()
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    main()
