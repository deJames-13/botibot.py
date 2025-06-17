from flask import Flask, render_template_string, jsonify, request, send_from_directory
import os
import json
import threading
from datetime import datetime


class FlaskServer:
    """
    A reusable and configurable Flask server class for Raspberry Pi projects.

    This class provides easy setup of web APIs and basic HTML interfaces
    with support for custom routes, static files, and real-time data serving.
    """

    def __init__(
        self, name="RaspberryPi Server", host="0.0.0.0", port=5000, debug=False
    ):
        """
        Initialize the Flask server.

        Args:
            name (str): Server name/title
            host (str): Host address (default: "0.0.0.0" for all interfaces)
            port (int): Port number (default: 5000)
            debug (bool): Enable debug mode
        """
        self.name = name
        self.host = host
        self.port = port
        self.debug = debug

        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "raspberry-pi-server-secret"

        # Data storage for sharing between routes
        self.shared_data = {}

        # Custom routes storage
        self.custom_routes = []

        # Setup default routes
        self._setup_default_routes()

        # Server thread
        self.server_thread = None
        self.is_running = False

    def _setup_default_routes(self):
        """Setup default routes for the server."""

        @self.app.route("/")
        def index():
            """Main dashboard page."""
            return render_template_string(
                self._get_dashboard_template(),
                server_name=self.name,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

        @self.app.route("/api/status")
        def api_status():
            """API endpoint for server status."""
            return jsonify(
                {
                    "status": "running",
                    "server_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "uptime": "Available",  # Could be enhanced with actual uptime
                    "data_keys": list(self.shared_data.keys()),
                }
            )

        @self.app.route("/api/data")
        def api_data():
            """API endpoint to get all shared data."""
            return jsonify(self.shared_data)

        @self.app.route("/api/data/<key>")
        def api_data_key(key):
            """API endpoint to get specific data by key."""
            if key in self.shared_data:
                return jsonify({key: self.shared_data[key]})
            else:
                return jsonify({"error": f'Key "{key}" not found'}), 404

        @self.app.route("/api/data/<key>", methods=["POST"])
        def api_set_data(key):
            """API endpoint to set data."""
            try:
                data = request.get_json()
                if data is None:
                    # If no JSON, try to get from form data
                    value = request.form.get("value", request.args.get("value", ""))
                else:
                    value = data.get("value", data)

                self.shared_data[key] = value
                return jsonify({"success": True, "key": key, "value": value})
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route("/control")
        def control_panel():
            """Control panel page."""
            return render_template_string(
                self._get_control_template(),
                server_name=self.name,
                data_keys=list(self.shared_data.keys()),
            )

    def _get_dashboard_template(self):
        """Get the HTML template for the dashboard."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ server_name }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .status-item {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .status-item h3 {
            margin: 0 0 10px 0;
            color: #FFD700;
        }
        .status-value {
            font-size: 1.5em;
            font-weight: bold;
        }
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
        }
        .btn {
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            opacity: 0.8;
        }
    </style>
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString();
                })
                .catch(error => console.error('Error:', error));
        }
        
        setInterval(updateStatus, 5000); // Update every 5 seconds
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍓 {{ server_name }}</h1>
            <p>Raspberry Pi Web Interface</p>
        </div>
        
        <div class="status-card">
            <h2>📊 System Status</h2>
            <div class="status-grid">
                <div class="status-item">
                    <h3>Status</h3>
                    <div class="status-value">🟢 Online</div>
                </div>
                <div class="status-item">
                    <h3>Current Time</h3>
                    <div class="status-value" id="timestamp">{{ current_time }}</div>
                </div>
                <div class="status-item">
                    <h3>Server</h3>
                    <div class="status-value">Flask/Python</div>
                </div>
                <div class="status-item">
                    <h3>Platform</h3>
                    <div class="status-value">Raspberry Pi</div>
                </div>
            </div>
        </div>
        
        <div class="nav-buttons">
            <a href="/control" class="btn">🎛️ Control Panel</a>
            <a href="/api/status" class="btn">📡 API Status</a>
            <a href="/api/data" class="btn">📊 Data API</a>
        </div>
        
        <div class="footer">
            <p>© 2024 Raspberry Pi Flask Server | Built with Python & Flask</p>
        </div>
    </div>
</body>
</html>
        """

    def _get_control_template(self):
        """Get the HTML template for the control panel."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ server_name }} - Control Panel</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .control-section {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .control-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .form-group {
            margin: 15px 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255,255,255,0.2);
            color: white;
            box-sizing: border-box;
        }
        .form-group input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        .btn {
            padding: 12px 24px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background: #218838;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .data-display {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .nav-link {
            color: #FFD700;
            text-decoration: none;
            margin: 0 10px;
        }
    </style>
    <script>
        function sendData() {
            const key = document.getElementById('dataKey').value;
            const value = document.getElementById('dataValue').value;
            
            if (!key) {
                alert('Please enter a key');
                return;
            }
            
            fetch(`/api/data/${key}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({value: value})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Data saved successfully!');
                    loadData();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to send data');
            });
        }
        
        function loadData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dataDisplay').textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => console.error('Error:', error));
        }
        
        window.onload = loadData;
        setInterval(loadData, 10000); // Refresh every 10 seconds
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ Control Panel</h1>
            <p><a href="/" class="nav-link">← Back to Dashboard</a></p>
        </div>
        
        <div class="control-section">
            <h2>📊 Data Control</h2>
            <div class="control-grid">
                <div>
                    <div class="form-group">
                        <label for="dataKey">Data Key:</label>
                        <input type="text" id="dataKey" placeholder="e.g., temperature, status, message">
                    </div>
                    <div class="form-group">
                        <label for="dataValue">Data Value:</label>
                        <input type="text" id="dataValue" placeholder="Enter value">
                    </div>
                    <button class="btn" onclick="sendData()">💾 Save Data</button>
                    <button class="btn" onclick="loadData()">🔄 Refresh Data</button>
                </div>
                <div>
                    <h3>Current Data:</h3>
                    <div id="dataDisplay" class="data-display">Loading...</div>
                </div>
            </div>
        </div>
        
        <div class="control-section">
            <h2>🔧 Quick Actions</h2>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn" onclick="sendTestData()">📝 Send Test Data</button>
                <button class="btn btn-danger" onclick="clearAllData()">🗑️ Clear All Data</button>
            </div>
        </div>
    </div>
    
    <script>
        function sendTestData() {
            const testData = {
                timestamp: new Date().toISOString(),
                random_value: Math.floor(Math.random() * 100),
                status: 'test_active'
            };
            
            Object.entries(testData).forEach(([key, value]) => {
                fetch(`/api/data/${key}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({value: value})
                });
            });
            
            setTimeout(loadData, 500);
            alert('Test data sent!');
        }
        
        function clearAllData() {
            if (confirm('Are you sure you want to clear all data?')) {
                // Note: This would require implementing a clear endpoint
                alert('Clear function would need to be implemented on server side');
            }
        }
    </script>
</body>
</html>
        """

    def add_route(self, rule, methods=["GET"], name=None):
        """
        Decorator to add custom routes to the server.

        Args:
            rule (str): URL rule (e.g., '/custom')
            methods (list): HTTP methods (default: ['GET'])
            name (str): Route name (optional)

        Usage:
            @server.add_route('/custom')
            def custom_route():
                return "Custom response"
        """

        def decorator(func):
            endpoint = name or func.__name__
            self.app.add_url_rule(rule, endpoint, func, methods=methods)
            self.custom_routes.append(
                {
                    "rule": rule,
                    "methods": methods,
                    "function": func.__name__,
                    "endpoint": endpoint,
                }
            )
            return func

        return decorator

    def set_data(self, key, value):
        """
        Set shared data that can be accessed via API.

        Args:
            key (str): Data key
            value: Data value (will be JSON serializable)
        """
        self.shared_data[key] = value

    def get_data(self, key, default=None):
        """
        Get shared data by key.

        Args:
            key (str): Data key
            default: Default value if key not found

        Returns:
            Data value or default
        """
        return self.shared_data.get(key, default)

    def update_data(self, data_dict):
        """
        Update multiple data values at once.

        Args:
            data_dict (dict): Dictionary of key-value pairs to update
        """
        self.shared_data.update(data_dict)

    def clear_data(self):
        """Clear all shared data."""
        self.shared_data.clear()

    def add_static_folder(self, folder_path, url_path="/static"):
        """
        Add a static folder for serving files.

        Args:
            folder_path (str): Path to the static folder
            url_path (str): URL path prefix (default: '/static')
        """

        @self.app.route(f"{url_path}/<path:filename>")
        def static_files(filename):
            return send_from_directory(folder_path, filename)

    def run(self, threaded=False):
        """
        Start the Flask server.

        Args:
            threaded (bool): Run server in a separate thread (non-blocking)
        """
        if threaded:
            if self.server_thread and self.server_thread.is_alive():
                print("Server is already running")
                return

            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True
            print(f"Server started in background on http://{self.host}:{self.port}")
        else:
            self._run_server()

    def _run_server(self):
        """Internal method to run the Flask server."""
        print(f"Starting {self.name} on http://{self.host}:{self.port}")
        print(f"Debug mode: {'ON' if self.debug else 'OFF'}")
        print("Custom routes:", [route["rule"] for route in self.custom_routes])
        self.app.run(
            host=self.host, port=self.port, debug=self.debug, use_reloader=False
        )

    def stop(self):
        """Stop the server (only works in threaded mode)."""
        if self.server_thread and self.server_thread.is_alive():
            self.is_running = False
            print(
                "Server stop requested (note: Flask dev server cannot be stopped gracefully)"
            )

    def get_url(self, endpoint="index"):
        """
        Get the full URL for an endpoint.

        Args:
            endpoint (str): Endpoint name

        Returns:
            str: Full URL
        """
        return f"http://{self.host}:{self.port}" + (
            f"/{endpoint}" if endpoint != "index" else ""
        )


# Example usage
if __name__ == "__main__":
    # Create Flask server instance
    server = FlaskServer(name="Raspberry Pi Demo Server", port=5000, debug=True)

    # Add some initial data
    server.set_data("temperature", 25.6)
    server.set_data("humidity", 60.2)
    server.set_data("status", "operational")

    # Add custom route
    @server.add_route("/api/sensors")
    def api_sensors():
        """Custom API endpoint for sensor data."""
        return jsonify(
            {
                "sensors": {
                    "temperature": server.get_data("temperature", 0),
                    "humidity": server.get_data("humidity", 0),
                    "timestamp": datetime.now().isoformat(),
                }
            }
        )

    @server.add_route("/gpio/<int:pin>/<action>", methods=["POST"])
    def gpio_control(pin, action):
        """Custom GPIO control endpoint."""
        # This would integrate with actual GPIO control
        result = f"GPIO {pin} -> {action}"
        server.set_data(f"gpio_{pin}", action)
        return jsonify({"success": True, "action": result})

    # Simulate sensor data updates in background
    def update_sensor_data():
        import random
        import time

        while True:
            server.update_data(
                {
                    "temperature": round(20 + random.random() * 15, 1),
                    "humidity": round(40 + random.random() * 40, 1),
                    "last_update": datetime.now().isoformat(),
                }
            )
            time.sleep(5)

    # Start sensor simulation in background
    sensor_thread = threading.Thread(target=update_sensor_data, daemon=True)
    sensor_thread.start()

    try:
        # Start the server
        print("Starting Flask server...")
        print("Visit http://localhost:5000 to see the dashboard")
        print("Visit http://localhost:5000/control to see the control panel")
        print("API endpoints available at /api/status, /api/data, /api/sensors")
        server.run()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
