#!/usr/bin/env python3
"""
SIM800L GSM Module Controller for Pill Dispenser Robot.

This module provides SMS functionality for medication reminders and notifications
using the SIM800L GSM module with serial communication.
"""

import serial
import time
import logging
from typing import Optional, List, Dict
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SIM800LController:
    """
    A controller class for SIM800L GSM module for pill dispenser notifications.
    
    Features:
    - Send SMS notifications for medication reminders
    - Check network status
    - Battery and signal monitoring
    - Emergency SMS alerts
    """

    def __init__(self, port: str = '/dev/ttyS0', baudrate: int = 9600, timeout: int = 10):
        """
        Initialize SIM800L GSM controller.

        Args:
            port (str): Serial port for SIM800L (default: /dev/ttyS0)
            baudrate (int): Communication baud rate (default: 9600)
            timeout (int): Command timeout in seconds (default: 10)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_initialized = False
        self.network_registered = False

        self._initialize_connection()

    def _initialize_connection(self) -> None:
        """Initialize serial connection to SIM800L module."""
        try:
            # Use more complete serial parameters from original code
            self.serial_conn = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=self.timeout
            )
            
            # Wait for module to be ready
            time.sleep(2)
            
            # Test AT command
            if self._send_at_command("AT") == "OK":
                logger.info("SIM800L module initialized successfully")
                self.is_initialized = True
                self._setup_module()
            else:
                raise RuntimeError("Failed to communicate with SIM800L module")
                
        except Exception as e:
            logger.error(f"Failed to initialize SIM800L: {e}")
            raise

    def _setup_module(self) -> None:
        """Configure SIM800L module settings."""
        # Configure the module with commands from both implementations
        commands = [
            "AT+CMGF=1",        # Set text mode for SMS
            "ATE0",             # Disable echo
            "AT+CSCS=\"GSM\"",  # Set character set
            "AT+CNMI=2,1,0,0,0" # Enable new SMS notifications
        ]
        
        for cmd in commands:
            self._send_at_command(cmd)
        
        # Check network registration
        self._check_network_status()

    def _send_at_command(self, command: str, wait_time: float = 1.0, expected_response: str = None) -> str:
        """
        Send AT command to SIM800L module.

        Args:
            command (str): AT command to send
            wait_time (float): Time to wait for response
            expected_response (str, optional): Expected response to verify success

        Returns:
            str: Response from module
        """
        if not self.serial_conn:
            raise RuntimeError("Serial connection not initialized")

        try:
            # Clear input buffer
            self.serial_conn.flushInput()
            
            # Send command
            self.serial_conn.write((command + '\r\n').encode())
            
            # Wait for response
            time.sleep(wait_time)
            
            # Read response
            response = ""
            while self.serial_conn.in_waiting > 0:
                response += self.serial_conn.read(self.serial_conn.in_waiting).decode('latin1', errors='ignore')
                time.sleep(0.1)
            
            response = response.strip()
            logger.debug(f"AT Command: {command} -> Response: {response}")
            
            # Check for expected response if provided
            if expected_response and expected_response not in response:
                logger.warning(f"Expected '{expected_response}' but got: {response}")
                return ""
                
            return response
            
        except Exception as e:
            logger.error(f"AT command failed: {e}")
            return ""

    def _check_network_status(self) -> bool:
        """
        Check if module is registered to network.

        Returns:
            bool: True if registered to network
        """
        response = self._send_at_command("AT+CREG?", 2.0)
        
        # Parse response: +CREG: 0,1 means registered
        if "+CREG: 0,1" in response or "+CREG: 0,5" in response:
            self.network_registered = True
            logger.info("Module registered to network")
            return True
        else:
            self.network_registered = False
            logger.warning("Module not registered to network")
            return False

    def get_signal_strength(self) -> int:
        """
        Get signal strength from module.

        Returns:
            int: Signal strength (0-31, or 99 if unknown)
        """
        response = self._send_at_command("AT+CSQ", 2.0)
        
        # Parse response: +CSQ: 15,99
        match = re.search(r'\+CSQ: (\d+),\d+', response)
        if match:
            signal = int(match.group(1))
            logger.info(f"Signal strength: {signal}")
            return signal
        return 99  # Unknown

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS message for medication reminders.

        Args:
            phone_number (str): Recipient phone number
            message (str): SMS message content

        Returns:
            bool: True if SMS sent successfully
        """
        if not self.is_initialized:
            logger.error("SIM800L not initialized")
            return False

        if not self.network_registered:
            logger.warning("Not registered to network, attempting to send anyway")

        try:
            # Set recipient
            cmd = f'AT+CMGS="{phone_number}"'
            response = self._send_at_command(cmd, 2.0)
            
            if ">" not in response:
                logger.error("Failed to set SMS recipient")
                return False

            # Send message content with Ctrl+Z (ASCII 26)
            self.serial_conn.write((message + chr(26)).encode())
            
            # Wait for send confirmation with better timeout handling
            full_response = ""
            timeout = time.time() + 10  # 10 second timeout
            
            while time.time() < timeout:
                if self.serial_conn.in_waiting > 0:
                    new_data = self.serial_conn.read(self.serial_conn.in_waiting).decode('latin1', errors='ignore')
                    full_response += new_data
                    
                    # Check for success or error
                    if "+CMGS:" in full_response:
                        logger.info(f"SMS sent successfully to {phone_number}")
                        return True
                    elif "ERROR" in full_response:
                        logger.error(f"SMS sending failed: {full_response}")
                        return False
                        
                time.sleep(0.1)  # Prevent CPU spike

            logger.error("SMS sending timeout")
            return False

        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False

    def send_medication_reminder(self, phone_number: str, medication_name: str, dosage: str = "") -> bool:
        """
        Send medication reminder SMS.

        Args:
            phone_number (str): Patient or caregiver phone number
            medication_name (str): Name of medication
            dosage (str): Dosage information (optional)

        Returns:
            bool: True if reminder sent successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        message = f"🤖 PILL REMINDER\n"
        message += f"Time: {timestamp}\n"
        message += f"Medication: {medication_name}\n"
        
        if dosage:
            message += f"Dosage: {dosage}\n"
            
        message += f"Please take your medication as prescribed.\n"
        message += f"- Botibot Pill Dispenser"

        return self.send_sms(phone_number, message)

    def send_emergency_alert(self, phone_number: str, alert_type: str, details: str = "") -> bool:
        """
        Send emergency alert SMS.

        Args:
            phone_number (str): Emergency contact number
            alert_type (str): Type of emergency (e.g., "MISSED_DOSE", "SYSTEM_ERROR")
            details (str): Additional details (optional)

        Returns:
            bool: True if alert sent successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        message = f"🚨 EMERGENCY ALERT\n"
        message += f"Time: {timestamp}\n"
        message += f"Alert: {alert_type}\n"
        
        if details:
            message += f"Details: {details}\n"
            
        message += f"Please check on the patient immediately.\n"
        message += f"- Botibot Emergency System"

        return self.send_sms(phone_number, message)

    def send_status_report(self, phone_number: str, pills_remaining: int, battery_level: str = "OK") -> bool:
        """
        Send system status report SMS.

        Args:
            phone_number (str): Contact number for status updates
            pills_remaining (int): Number of pills remaining
            battery_level (str): Battery status

        Returns:
            bool: True if status sent successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        signal = self.get_signal_strength()
        
        message = f"📊 BOTIBOT STATUS\n"
        message += f"Time: {timestamp}\n"
        message += f"Pills Remaining: {pills_remaining}\n"
        message += f"Battery: {battery_level}\n"
        message += f"Signal: {signal}/31\n"
        message += f"System: Operational\n"
        message += f"- Botibot Status Report"

        return self.send_sms(phone_number, message)

    def get_module_info(self) -> Dict[str, str]:
        """
        Get module information.

        Returns:
            Dict[str, str]: Module information
        """
        info = {}
        
        # Module version
        response = self._send_at_command("ATI", 2.0)
        info['version'] = response.split('\n')[1] if '\n' in response else response
        
        # SIM card status
        response = self._send_at_command("AT+CPIN?", 2.0)
        info['sim_status'] = "READY" if "READY" in response else "NOT_READY"
        
        # Signal strength
        info['signal_strength'] = str(self.get_signal_strength())
        
        # Network registration
        info['network_registered'] = str(self.network_registered)
        
        return info

    def cleanup(self) -> None:
        """Close the serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("SIM800L connection closed")
            self.is_initialized = False
            
    def close(self) -> None:
        """Alias for cleanup() for compatibility."""
        self.cleanup()
        
    def __enter__(self):
        """Support for context manager."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up on context manager exit."""
        self.cleanup()


# Example usage
if __name__ == "__main__":
    try:
        # Initialize GSM controller
        gsm = SIM800LController(port='/dev/ttyS0', baudrate=9600)
        
        # Basic SMS sending (simple usage)
        print("\n=== Basic SMS Example ===")
        phone_number = input("Enter phone number (with country code): ")
        if not phone_number:
            phone_number = "+639465454148"  # Default for testing
            print(f"Using default number: {phone_number}")
            
        basic_message = "Hello from Botibot Pill Dispenser!"
        print(f"Sending message: '{basic_message}'")
        if gsm.send_sms(phone_number, basic_message):
            print("✅ Basic SMS sent successfully!")
        else:
            print("❌ Failed to send basic SMS")
        
        # Advanced features (if desired)
        use_advanced = input("\nTest advanced features? (y/n): ").lower() == 'y'
        if use_advanced:
            print("\n=== Advanced Features ===")
            # Send medication reminder
            print("Sending medication reminder...")
            if gsm.send_medication_reminder(phone_number, "Vitamin D", "1 tablet"):
                print("✅ Medication reminder sent successfully!")
            
            # Send status report
            print("Sending system status report...")
            if gsm.send_status_report(phone_number, 25, "85%"):
                print("✅ Status report sent successfully!")
            
            # Get module info
            print("Getting module information...")
            info = gsm.get_module_info()
            print(f"Module info: {info}")
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'gsm' in locals():
            gsm.cleanup()
            print("GSM connection closed")
