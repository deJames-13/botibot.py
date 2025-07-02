#!/usr/bin/env python3
"""
Pill Dispenser Dashboard Flask Application for Botibot.

This module extends the Flask server to provide a web dashboard for the pill dispenser robot,
integrating with GSM module and other sensors for a complete patient session workflow.
"""

import os
import time
import random
import json
from datetime import datetime
from flask import render_template_string, jsonify, request, Blueprint, send_from_directory
import logging
import threading

# Import botibot modules
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from modules.gsm.sim800L import SIM800LController
from modules.ir_temp.gy906 import MLX90614Sensor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint for pill dispenser dashboard
pill_dispenser_bp = Blueprint('pill_dispenser', __name__)

# Global variables for module instances
gsm_module = None
ir_temp_sensor = None

# Default phone number for SMS notifications
DEFAULT_PHONE_NUMBER = "+639465454148"  # Update with your default number

# Mock data for heart rate and alcohol sensor
def get_mock_heart_rate():
    """Generate mock heart rate data."""
    return {
        "rate": random.randint(65, 85),
        "status": "normal",
        "timestamp": datetime.now().isoformat()
    }

def get_mock_alcohol_level():
    """Generate mock alcohol level data."""
    return {
        "level": round(random.uniform(0, 0.3), 2),
        "status": "low",
        "timestamp": datetime.now().isoformat()
    }

# Initialize hardware modules
def init_hardware():
    """Initialize hardware modules for the dashboard."""
    global gsm_module, ir_temp_sensor
    
    try:
        # Initialize GSM module
        logger.info("Initializing GSM module...")
        try:
            gsm_module = SIM800LController(port='/dev/ttyS0', baudrate=9600)
            logger.info("GSM module initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GSM module: {e}")
            gsm_module = None
        
        # Initialize IR temperature sensor
        logger.info("Initializing IR temperature sensor...")
        try:
            ir_temp_sensor = MLX90614Sensor(button_pin=21)
            logger.info("IR temperature sensor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize IR temperature sensor: {e}")
            ir_temp_sensor = None
            
    except Exception as e:
        logger.error(f"Error initializing hardware: {e}")

# Initialize hardware in a separate thread to avoid blocking
def init_hardware_async():
    """Initialize hardware modules in a separate thread."""
    init_thread = threading.Thread(target=init_hardware)
    init_thread.daemon = True
    init_thread.start()

# Dashboard routes
@pill_dispenser_bp.route('/pill-dispenser')
def dashboard():
    """Render the pill dispenser dashboard."""
    return render_template_string(
        _get_dashboard_template(),
        page_title="Pill Dispenser Dashboard",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        default_phone=DEFAULT_PHONE_NUMBER
    )

# API routes
@pill_dispenser_bp.route('/api/heart-rate', methods=['GET'])
def api_heart_rate():
    """API endpoint for getting heart rate (mock data)."""
    try:
        heart_rate_data = get_mock_heart_rate()
        return jsonify(heart_rate_data)
    except Exception as e:
        logger.error(f"Error in heart rate API: {e}")
        return jsonify({"error": str(e)}), 500

@pill_dispenser_bp.route('/api/temperature', methods=['GET'])
def api_temperature():
    """API endpoint for getting temperature from IR sensor."""
    try:
        if ir_temp_sensor:
            # Get patient temperature data
            temp_data = ir_temp_sensor.take_patient_temperature()
            return jsonify(temp_data)
        else:
            # Provide mock data if sensor not available
            mock_temp = {
                'status': 'NORMAL',
                'temperature': round(random.uniform(36.5, 37.2), 1),
                'fever': False,
                'message': 'Normal temperature (MOCK DATA)',
                'fever_threshold': 38.0
            }
            return jsonify(mock_temp)
    except Exception as e:
        logger.error(f"Error in temperature API: {e}")
        return jsonify({"error": str(e)}), 500

@pill_dispenser_bp.route('/api/alcohol-level', methods=['GET'])
def api_alcohol_level():
    """API endpoint for getting alcohol level (mock data)."""
    try:
        alcohol_data = get_mock_alcohol_level()
        return jsonify(alcohol_data)
    except Exception as e:
        logger.error(f"Error in alcohol level API: {e}")
        return jsonify({"error": str(e)}), 500

@pill_dispenser_bp.route('/api/send-sms', methods=['POST'])
def api_send_sms():
    """API endpoint for sending SMS with session results."""
    try:
        data = request.get_json()
        
        # Get phone number from request or use default
        phone_number = data.get('phone_number', DEFAULT_PHONE_NUMBER)
        heart_rate = data.get('heart_rate', {})
        temperature = data.get('temperature', {})
        alcohol_level = data.get('alcohol_level', {})
        
        # Prepare message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"📊 PILL DISPENSER SESSION RESULTS\n"
        message += f"Time: {timestamp}\n"
        message += f"Heart Rate: {heart_rate.get('rate', 'N/A')} bpm ({heart_rate.get('status', 'N/A')})\n"
        message += f"Temperature: {temperature.get('temperature', 'N/A')}°C ({temperature.get('status', 'N/A')})\n"
        message += f"Alcohol Level: {alcohol_level.get('level', 'N/A')} ({alcohol_level.get('status', 'N/A')})\n"
        
        # Add additional notes if provided
        if 'notes' in data and data['notes']:
            message += f"\nNotes: {data['notes']}\n"
            
        message += f"\n- Botibot Pill Dispenser"
        
        # Send SMS via GSM module
        if gsm_module:
            success = gsm_module.send_sms(phone_number, message)
            if success:
                return jsonify({"success": True, "message": "SMS sent successfully"})
            else:
                return jsonify({"success": False, "error": "Failed to send SMS"}), 500
        else:
            # Mock SMS sending if GSM module not available
            logger.info(f"Mock SMS to {phone_number}: {message}")
            return jsonify({
                "success": True, 
                "message": "SMS sent successfully (MOCK)",
                "phone": phone_number,
                "content": message
            })
            
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return jsonify({"error": str(e)}), 500

@pill_dispenser_bp.route('/api/session', methods=['POST'])
def api_save_session():
    """API endpoint for saving a complete session."""
    try:
        data = request.get_json()
        
        # Save session data with timestamp
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "heart_rate": data.get("heart_rate", {}),
            "temperature": data.get("temperature", {}),
            "alcohol_level": data.get("alcohol_level", {}),
            "notes": data.get("notes", ""),
            "phone_number": data.get("phone_number", DEFAULT_PHONE_NUMBER)
        }
        
        # Here you would normally save to a database
        # For now, just log it
        logger.info(f"Session saved: {json.dumps(session_data)}")
        
        return jsonify({"success": True, "session_id": datetime.now().strftime("%Y%m%d%H%M%S")})
        
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        return jsonify({"error": str(e)}), 500

def _get_dashboard_template():
    """Return the HTML template for the pill dispenser dashboard."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #ff6b6b;
            --bg-color: #f9f9f9;
            --text-color: #333;
            --border-radius: 10px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #4a6fa5 0%, #3f5f8a 100%);
            color: white;
            padding: 20px;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.2em;
        }
        
        .header p {
            margin: 10px 0 0;
            opacity: 0.9;
        }
        
        .session-container {
            background: white;
            border-radius: var(--border-radius);
            padding: 20px;
            box-shadow: var(--box-shadow);
            margin-bottom: 20px;
        }
        
        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            position: relative;
        }
        
        .step-indicator::before {
            content: '';
            position: absolute;
            top: 24px;
            left: 0;
            right: 0;
            height: 4px;
            background-color: #ddd;
            z-index: 1;
        }
        
        .step {
            position: relative;
            z-index: 2;
            text-align: center;
            width: 20%;
        }
        
        .step-circle {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px;
            font-weight: bold;
            color: #555;
            transition: all 0.3s;
        }
        
        .step.active .step-circle {
            background-color: var(--primary-color);
            color: white;
        }
        
        .step.completed .step-circle {
            background-color: #4CAF50;
            color: white;
        }
        
        .step-title {
            font-size: 14px;
            color: #777;
        }
        
        .step.active .step-title {
            color: var(--primary-color);
            font-weight: bold;
        }
        
        .step.completed .step-title {
            color: #4CAF50;
        }
        
        .step-content {
            display: none;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: var(--border-radius);
            margin-bottom: 20px;
        }
        
        .step-content.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #3d5d8a;
        }
        
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background-color: #218838;
        }
        
        .btn-navigation {
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
        }
        
        .sensor-reading {
            background-color: #f8f9fa;
            border-radius: var(--border-radius);
            padding: 15px;
            margin: 20px 0;
            border-left: 5px solid var(--primary-color);
        }
        
        .sensor-value {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--primary-color);
            margin: 10px 0;
        }
        
        .sensor-status {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .status-normal {
            color: #28a745;
        }
        
        .status-warning {
            color: #ffc107;
        }
        
        .status-danger {
            color: #dc3545;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .summary-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .summary-table th, .summary-table td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        
        .summary-table th {
            background-color: #f2f2f2;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px 0;
            color: #777;
            font-size: 0.9em;
        }
        
        .notification {
            padding: 15px;
            margin: 15px 0;
            border-radius: var(--border-radius);
            display: none;
        }
        
        .notification-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .notification-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Pill Dispenser Dashboard</h1>
            <p>Patient Health Monitoring & Medication Management System</p>
        </div>
        
        <div id="notification" class="notification">
            <span id="notification-message"></span>
        </div>
        
        <div class="session-container">
            <h2>Patient Health Session</h2>
            <p>Complete the following steps to check your health status and dispense medication.</p>
            
            <div class="step-indicator">
                <div class="step active" data-step="1">
                    <div class="step-circle">1</div>
                    <div class="step-title">Heart Rate</div>
                </div>
                <div class="step" data-step="2">
                    <div class="step-circle">2</div>
                    <div class="step-title">Temperature</div>
                </div>
                <div class="step" data-step="3">
                    <div class="step-circle">3</div>
                    <div class="step-title">Alcohol Level</div>
                </div>
                <div class="step" data-step="4">
                    <div class="step-circle">4</div>
                    <div class="step-title">Summary</div>
                </div>
                <div class="step" data-step="5">
                    <div class="step-circle">5</div>
                    <div class="step-title">Complete</div>
                </div>
            </div>
            
            <!-- Step 1: Heart Rate -->
            <div id="step-1" class="step-content active">
                <h3>Step 1: Heart Rate Measurement</h3>
                <p>Click the button below to measure your heart rate.</p>
                
                <button id="check-heart-rate" class="btn btn-primary">
                    Check Heart Rate
                </button>
                
                <div id="heart-rate-result" class="sensor-reading" style="display: none;">
                    <h4>Heart Rate Reading</h4>
                    <div class="sensor-value">
                        <span id="heart-rate-value">--</span> <span>bpm</span>
                    </div>
                    <div class="sensor-status">
                        Status: <span id="heart-rate-status">--</span>
                    </div>
                </div>
                
                <div class="btn-navigation">
                    <button class="btn btn-secondary" disabled>Previous</button>
                    <button id="next-step-1" class="btn btn-primary" disabled>Next</button>
                </div>
            </div>
            
            <!-- Step 2: Temperature -->
            <div id="step-2" class="step-content">
                <h3>Step 2: Temperature Reading</h3>
                <p>Please place the temperature sensor close to your forehead and click the button.</p>
                
                <button id="check-temperature" class="btn btn-primary">
                    Check Temperature
                </button>
                
                <div id="temperature-result" class="sensor-reading" style="display: none;">
                    <h4>Temperature Reading</h4>
                    <div class="sensor-value">
                        <span id="temperature-value">--</span> <span>°C</span>
                    </div>
                    <div class="sensor-status">
                        Status: <span id="temperature-status">--</span>
                    </div>
                </div>
                
                <div class="btn-navigation">
                    <button class="btn btn-secondary prev-step">Previous</button>
                    <button id="next-step-2" class="btn btn-primary" disabled>Next</button>
                </div>
            </div>
            
            <!-- Step 3: Alcohol Level -->
            <div id="step-3" class="step-content">
                <h3>Step 3: Alcohol Level Check</h3>
                <p>Click the button to check your alcohol level.</p>
                
                <button id="check-alcohol" class="btn btn-primary">
                    Check Alcohol Level
                </button>
                
                <div id="alcohol-result" class="sensor-reading" style="display: none;">
                    <h4>Alcohol Level Reading</h4>
                    <div class="sensor-value">
                        <span id="alcohol-value">--</span>
                    </div>
                    <div class="sensor-status">
                        Status: <span id="alcohol-status">--</span>
                    </div>
                </div>
                
                <div class="btn-navigation">
                    <button class="btn btn-secondary prev-step">Previous</button>
                    <button id="next-step-3" class="btn btn-primary" disabled>Next</button>
                </div>
            </div>
            
            <!-- Step 4: Summary -->
            <div id="step-4" class="step-content">
                <h3>Step 4: Session Summary</h3>
                <p>Review your health metrics below and add any notes before finalizing the session.</p>
                
                <table class="summary-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Status</th>
                    </tr>
                    <tr>
                        <td>Heart Rate</td>
                        <td id="summary-heart-rate">--</td>
                        <td id="summary-heart-rate-status">--</td>
                    </tr>
                    <tr>
                        <td>Temperature</td>
                        <td id="summary-temperature">--</td>
                        <td id="summary-temperature-status">--</td>
                    </tr>
                    <tr>
                        <td>Alcohol Level</td>
                        <td id="summary-alcohol">--</td>
                        <td id="summary-alcohol-status">--</td>
                    </tr>
                </table>
                
                <div class="form-group">
                    <label for="phone-number">Phone Number for SMS Results:</label>
                    <input type="tel" id="phone-number" value="{{ default_phone }}" placeholder="+1234567890">
                </div>
                
                <div class="form-group">
                    <label for="session-notes">Additional Notes:</label>
                    <textarea id="session-notes" rows="3" placeholder="Add any notes about your current health status..."></textarea>
                </div>
                
                <div class="btn-navigation">
                    <button class="btn btn-secondary prev-step">Previous</button>
                    <button id="send-results" class="btn btn-success">Send Results & Complete</button>
                </div>
            </div>
            
            <!-- Step 5: Complete -->
            <div id="step-5" class="step-content">
                <h3>Session Completed</h3>
                <div style="text-align: center; padding: 30px 0;">
                    <div style="font-size: 80px; margin-bottom: 20px;">✅</div>
                    <h2>Thank You!</h2>
                    <p>Your health session has been completed successfully.</p>
                    <p>A summary has been sent to your phone via SMS.</p>
                    
                    <div style="margin-top: 30px;">
                        <button id="start-new-session" class="btn btn-primary">Start New Session</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 Botibot Pill Dispenser Dashboard | <a href="/">Back to Main Dashboard</a></p>
        </div>
    </div>
    
    <script>
        // Store session data
        const sessionData = {
            heart_rate: null,
            temperature: null,
            alcohol_level: null
        };
        
        // Current step
        let currentStep = 1;
        
        // DOM Ready
        document.addEventListener('DOMContentLoaded', function() {
            // Heart Rate Check
            document.getElementById('check-heart-rate').addEventListener('click', checkHeartRate);
            
            // Temperature Check
            document.getElementById('check-temperature').addEventListener('click', checkTemperature);
            
            // Alcohol Check
            document.getElementById('check-alcohol').addEventListener('click', checkAlcoholLevel);
            
            // Next buttons
            document.getElementById('next-step-1').addEventListener('click', () => goToStep(2));
            document.getElementById('next-step-2').addEventListener('click', () => goToStep(3));
            document.getElementById('next-step-3').addEventListener('click', () => goToStep(4));
            
            // Previous buttons
            document.querySelectorAll('.prev-step').forEach(button => {
                button.addEventListener('click', () => goToStep(currentStep - 1));
            });
            
            // Send results
            document.getElementById('send-results').addEventListener('click', sendResults);
            
            // Start new session
            document.getElementById('start-new-session').addEventListener('click', startNewSession);
        });
        
        // Go to specific step
        function goToStep(step) {
            // Hide all step content
            document.querySelectorAll('.step-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Update step indicators
            document.querySelectorAll('.step').forEach(stepEl => {
                const stepNum = parseInt(stepEl.dataset.step);
                stepEl.classList.remove('active', 'completed');
                
                if (stepNum < step) {
                    stepEl.classList.add('completed');
                } else if (stepNum === step) {
                    stepEl.classList.add('active');
                }
            });
            
            // Show current step content
            document.getElementById(`step-${step}`).classList.add('active');
            
            // Update current step
            currentStep = step;
            
            // If step 4 (summary), update summary
            if (step === 4) {
                updateSummary();
            }
        }
        
        // Check heart rate
        function checkHeartRate() {
            const button = document.getElementById('check-heart-rate');
            const result = document.getElementById('heart-rate-result');
            
            // Show loading state
            button.innerHTML = '<span class="loading"></span> Checking...';
            button.disabled = true;
            
            // Call API
            fetch('/api/heart-rate')
                .then(response => response.json())
                .then(data => {
                    // Store data
                    sessionData.heart_rate = data;
                    
                    // Update UI
                    document.getElementById('heart-rate-value').textContent = data.rate;
                    document.getElementById('heart-rate-status').textContent = data.status;
                    document.getElementById('heart-rate-status').className = getStatusClass(data.status);
                    
                    // Show result and enable next button
                    result.style.display = 'block';
                    document.getElementById('next-step-1').disabled = false;
                })
                .catch(error => {
                    showNotification('Error checking heart rate: ' + error.message, 'error');
                    console.error('Error:', error);
                })
                .finally(() => {
                    // Reset button
                    button.innerHTML = 'Check Heart Rate';
                    button.disabled = false;
                });
        }
        
        // Check temperature
        function checkTemperature() {
            const button = document.getElementById('check-temperature');
            const result = document.getElementById('temperature-result');
            
            // Show loading state
            button.innerHTML = '<span class="loading"></span> Checking...';
            button.disabled = true;
            
            // Call API
            fetch('/api/temperature')
                .then(response => response.json())
                .then(data => {
                    // Store data
                    sessionData.temperature = data;
                    
                    // Update UI
                    document.getElementById('temperature-value').textContent = data.temperature;
                    document.getElementById('temperature-status').textContent = data.status;
                    document.getElementById('temperature-status').className = getStatusClass(data.status);
                    
                    // Show result and enable next button
                    result.style.display = 'block';
                    document.getElementById('next-step-2').disabled = false;
                })
                .catch(error => {
                    showNotification('Error checking temperature: ' + error.message, 'error');
                    console.error('Error:', error);
                })
                .finally(() => {
                    // Reset button
                    button.innerHTML = 'Check Temperature';
                    button.disabled = false;
                });
        }
        
        // Check alcohol level
        function checkAlcoholLevel() {
            const button = document.getElementById('check-alcohol');
            const result = document.getElementById('alcohol-result');
            
            // Show loading state
            button.innerHTML = '<span class="loading"></span> Checking...';
            button.disabled = true;
            
            // Call API
            fetch('/api/alcohol-level')
                .then(response => response.json())
                .then(data => {
                    // Store data
                    sessionData.alcohol_level = data;
                    
                    // Update UI
                    document.getElementById('alcohol-value').textContent = data.level;
                    document.getElementById('alcohol-status').textContent = data.status;
                    document.getElementById('alcohol-status').className = getStatusClass(data.status);
                    
                    // Show result and enable next button
                    result.style.display = 'block';
                    document.getElementById('next-step-3').disabled = false;
                })
                .catch(error => {
                    showNotification('Error checking alcohol level: ' + error.message, 'error');
                    console.error('Error:', error);
                })
                .finally(() => {
                    // Reset button
                    button.innerHTML = 'Check Alcohol Level';
                    button.disabled = false;
                });
        }
        
        // Update summary
        function updateSummary() {
            if (sessionData.heart_rate) {
                document.getElementById('summary-heart-rate').textContent = sessionData.heart_rate.rate + ' bpm';
                document.getElementById('summary-heart-rate-status').textContent = sessionData.heart_rate.status;
                document.getElementById('summary-heart-rate-status').className = getStatusClass(sessionData.heart_rate.status);
            }
            
            if (sessionData.temperature) {
                document.getElementById('summary-temperature').textContent = sessionData.temperature.temperature + '°C';
                document.getElementById('summary-temperature-status').textContent = sessionData.temperature.status;
                document.getElementById('summary-temperature-status').className = getStatusClass(sessionData.temperature.status);
            }
            
            if (sessionData.alcohol_level) {
                document.getElementById('summary-alcohol').textContent = sessionData.alcohol_level.level;
                document.getElementById('summary-alcohol-status').textContent = sessionData.alcohol_level.status;
                document.getElementById('summary-alcohol-status').className = getStatusClass(sessionData.alcohol_level.status);
            }
        }
        
        // Send results
        function sendResults() {
            const button = document.getElementById('send-results');
            const phoneNumber = document.getElementById('phone-number').value.trim();
            const notes = document.getElementById('session-notes').value.trim();
            
            // Validate phone number
            if (!phoneNumber) {
                showNotification('Please enter a phone number for SMS results', 'error');
                return;
            }
            
            // Prepare data
            const data = {
                heart_rate: sessionData.heart_rate,
                temperature: sessionData.temperature,
                alcohol_level: sessionData.alcohol_level,
                notes: notes,
                phone_number: phoneNumber
            };
            
            // Show loading state
            button.innerHTML = '<span class="loading"></span> Sending...';
            button.disabled = true;
            
            // First save the session
            fetch('/api/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(sessionResult => {
                // Now send SMS
                return fetch('/api/send-sms', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
            })
            .then(response => response.json())
            .then(smsResult => {
                if (smsResult.success) {
                    showNotification('Results saved and SMS sent successfully', 'success');
                    // Go to final step
                    goToStep(5);
                } else {
                    showNotification('Error sending SMS: ' + (smsResult.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                showNotification('Error processing results: ' + error.message, 'error');
                console.error('Error:', error);
            })
            .finally(() => {
                // Reset button
                button.innerHTML = 'Send Results & Complete';
                button.disabled = false;
            });
        }
        
        // Start new session
        function startNewSession() {
            // Reset session data
            sessionData.heart_rate = null;
            sessionData.temperature = null;
            sessionData.alcohol_level = null;
            
            // Reset all result displays
            document.getElementById('heart-rate-result').style.display = 'none';
            document.getElementById('temperature-result').style.display = 'none';
            document.getElementById('alcohol-result').style.display = 'none';
            
            // Reset next buttons
            document.getElementById('next-step-1').disabled = true;
            document.getElementById('next-step-2').disabled = true;
            document.getElementById('next-step-3').disabled = true;
            
            // Clear notes
            document.getElementById('session-notes').value = '';
            
            // Go to first step
            goToStep(1);
        }
        
        // Helper to get status class
        function getStatusClass(status) {
            status = status.toLowerCase();
            if (status === 'normal' || status === 'low') {
                return 'status-normal';
            } else if (status === 'warning' || status === 'elevated') {
                return 'status-warning';
            } else if (status === 'danger' || status === 'high' || status === 'fever') {
                return 'status-danger';
            }
            return '';
        }
        
        // Show notification
        function showNotification(message, type) {
            const notification = document.getElementById('notification');
            const messageEl = document.getElementById('notification-message');
            
            // Set message and type
            messageEl.textContent = message;
            notification.className = 'notification';
            notification.classList.add(`notification-${type}`);
            
            // Show notification
            notification.style.display = 'block';
            
            // Hide after 5 seconds
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
    """

# Register blueprint with Flask server
def register_with_app(app):
    """Register the pill dispenser blueprint with a Flask app."""
    app.register_blueprint(pill_dispenser_bp)
    
    # Initialize hardware modules asynchronously
    init_hardware_async()
    
    # Add static route for any static files
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(static_folder, filename)
    
    logger.info("Pill dispenser dashboard registered with Flask app")

# Clean up resources
def cleanup():
    """Clean up hardware resources."""
    global gsm_module, ir_temp_sensor
    
    if gsm_module:
        try:
            gsm_module.cleanup()
            logger.info("GSM module cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up GSM module: {e}")
    
    if ir_temp_sensor:
        try:
            ir_temp_sensor.cleanup()
            logger.info("IR temperature sensor cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up IR temperature sensor: {e}")
