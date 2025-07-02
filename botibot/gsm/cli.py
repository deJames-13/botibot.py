#!/usr/bin/env python3
"""
CLI tool for SIM800L GSM module in pill dispenser robot.

This script provides command-line interface for sending SMS notifications,
medication reminders, and emergency alerts.
"""

import argparse
import sys
import json
from datetime import datetime
from .sim800L import SIM800LController


def send_sms_command(args):
    """Send a basic SMS message."""
    try:
        gsm = SIM800LController(port=args.port, baudrate=args.baudrate)
        
        if gsm.send_sms(args.phone, args.message):
            print(f"✅ SMS sent successfully to {args.phone}")
            return True
        else:
            print(f"❌ Failed to send SMS to {args.phone}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'gsm' in locals():
            gsm.cleanup()


def send_reminder_command(args):
    """Send medication reminder SMS."""
    try:
        gsm = SIM800LController(port=args.port, baudrate=args.baudrate)
        
        if gsm.send_medication_reminder(args.phone, args.medication, args.dosage):
            print(f"✅ Medication reminder sent to {args.phone}")
            print(f"   Medication: {args.medication}")
            if args.dosage:
                print(f"   Dosage: {args.dosage}")
            return True
        else:
            print(f"❌ Failed to send medication reminder")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'gsm' in locals():
            gsm.cleanup()


def send_alert_command(args):
    """Send emergency alert SMS."""
    try:
        gsm = SIM800LController(port=args.port, baudrate=args.baudrate)
        
        if gsm.send_emergency_alert(args.phone, args.alert_type, args.details):
            print(f"🚨 Emergency alert sent to {args.phone}")
            print(f"   Alert Type: {args.alert_type}")
            if args.details:
                print(f"   Details: {args.details}")
            return True
        else:
            print(f"❌ Failed to send emergency alert")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'gsm' in locals():
            gsm.cleanup()


def send_status_command(args):
    """Send status report SMS."""
    try:
        gsm = SIM800LController(port=args.port, baudrate=args.baudrate)
        
        if gsm.send_status_report(args.phone, args.pills_remaining, args.battery):
            print(f"📊 Status report sent to {args.phone}")
            print(f"   Pills Remaining: {args.pills_remaining}")
            print(f"   Battery: {args.battery}")
            return True
        else:
            print(f"❌ Failed to send status report")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'gsm' in locals():
            gsm.cleanup()


def check_status_command(args):
    """Check GSM module status."""
    try:
        gsm = SIM800LController(port=args.port, baudrate=args.baudrate)
        
        print("📡 GSM Module Status:")
        print(f"   Initialized: {gsm.is_initialized}")
        print(f"   Network Registered: {gsm.network_registered}")
        
        signal = gsm.get_signal_strength()
        print(f"   Signal Strength: {signal}/31")
        
        info = gsm.get_module_info()
        for key, value in info.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'gsm' in locals():
            gsm.cleanup()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GSM SMS Controller for Botibot Pill Dispenser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send basic SMS
  python -m modules.gsm.cli sms --phone "+1234567890" --message "Hello from Botibot!"
  
  # Send medication reminder
  python -m modules.gsm.cli reminder --phone "+1234567890" --medication "Vitamin D" --dosage "1 tablet"
  
  # Send emergency alert
  python -m modules.gsm.cli alert --phone "+1234567890" --alert-type "MISSED_DOSE" --details "Patient missed 2 doses"
  
  # Send status report
  python -m modules.gsm.cli status --phone "+1234567890" --pills-remaining 25 --battery "85%"
  
  # Check module status
  python -m modules.gsm.cli check
        """
    )
    
    # Global arguments
    parser.add_argument('--port', default='/dev/ttyS0', help='Serial port (default: /dev/ttyS0)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate (default: 9600)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # SMS command
    sms_parser = subparsers.add_parser('sms', help='Send basic SMS message')
    sms_parser.add_argument('--phone', required=True, help='Phone number (with country code)')
    sms_parser.add_argument('--message', required=True, help='SMS message content')
    sms_parser.set_defaults(func=send_sms_command)
    
    # Medication reminder command
    reminder_parser = subparsers.add_parser('reminder', help='Send medication reminder')
    reminder_parser.add_argument('--phone', required=True, help='Phone number (with country code)')
    reminder_parser.add_argument('--medication', required=True, help='Medication name')
    reminder_parser.add_argument('--dosage', default='', help='Dosage information (optional)')
    reminder_parser.set_defaults(func=send_reminder_command)
    
    # Emergency alert command
    alert_parser = subparsers.add_parser('alert', help='Send emergency alert')
    alert_parser.add_argument('--phone', required=True, help='Emergency contact number')
    alert_parser.add_argument('--alert-type', required=True, 
                             choices=['MISSED_DOSE', 'SYSTEM_ERROR', 'LOW_PILLS', 'BATTERY_LOW', 'OTHER'],
                             help='Type of emergency alert')
    alert_parser.add_argument('--details', default='', help='Additional details (optional)')
    alert_parser.set_defaults(func=send_alert_command)
    
    # Status report command
    status_parser = subparsers.add_parser('status', help='Send status report')
    status_parser.add_argument('--phone', required=True, help='Phone number for status updates')
    status_parser.add_argument('--pills-remaining', type=int, required=True, help='Number of pills remaining')
    status_parser.add_argument('--battery', default='OK', help='Battery status (default: OK)')
    status_parser.set_defaults(func=send_status_command)
    
    # Check module status command
    check_parser = subparsers.add_parser('check', help='Check GSM module status')
    check_parser.set_defaults(func=check_status_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Set logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Execute command
    try:
        success = args.func(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
