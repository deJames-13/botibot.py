#!/usr/bin/env python3
"""
CLI tool for Pill Scheduler in pill dispenser robot.

This script provides command-line interface for managing medication schedules,
viewing upcoming medications, and controlling the pill dispenser scheduler.
"""

import argparse
import sys
import json
from datetime import datetime
from . import PillScheduler, MedicationStatus


def add_schedule_command(args):
    """Add a new medication schedule."""
    try:
        scheduler = PillScheduler()
        
        # Convert times from space-separated string if needed
        times = args.times
        if isinstance(times, str):
            times = times.split()
            
        # Convert days from space-separated string if needed
        days = args.days
        if isinstance(days, str):
            days = days.split()
            
        schedule_id = scheduler.add_schedule(
            name=args.name,
            dosage=args.dosage,
            times=times,
            days=days,
            start_date=args.start_date,
            end_date=args.end_date,
            notes=args.notes or ""
        )
        
        print(f"✅ Schedule added successfully with ID: {schedule_id}")
        print(f"   Medication: {args.name}")
        print(f"   Dosage: {args.dosage}")
        print(f"   Times: {', '.join(times)}")
        print(f"   Days: {', '.join(days)}")
        if args.start_date:
            print(f"   Start date: {args.start_date}")
        if args.end_date:
            print(f"   End date: {args.end_date}")
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_schedules_command(args):
    """List all medication schedules."""
    try:
        scheduler = PillScheduler()
        schedules = scheduler.get_all_schedules()
        
        if not schedules:
            print("🗓️ No medication schedules found")
            return True
            
        print(f"🗓️ Found {len(schedules)} medication schedules:")
        for i, schedule in enumerate(schedules, 1):
            print(f"\n{i}. {schedule['name']} ({schedule['id']})")
            print(f"   Dosage: {schedule['dosage']}")
            print(f"   Times: {', '.join(schedule['times'])}")
            print(f"   Days: {', '.join(schedule['days'])}")
            if schedule.get('start_date'):
                print(f"   Start date: {schedule['start_date']}")
            if schedule.get('end_date'):
                print(f"   End date: {schedule['end_date']}")
            if schedule.get('notes'):
                print(f"   Notes: {schedule['notes']}")
            print(f"   Active: {'Yes' if schedule['active'] else 'No'}")
        
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def next_medication_command(args):
    """Show next scheduled medication."""
    try:
        scheduler = PillScheduler()
        next_med = scheduler.get_next_medication()
        
        if not next_med:
            print("🗓️ No upcoming medications scheduled")
            return True
            
        print(f"⏰ Next medication: {next_med['name']}")
        print(f"   Time: {next_med['time']}")
        print(f"   Date: {next_med['date']}")
        print(f"   Dosage: {next_med['dosage']}")
            
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def start_scheduler_command(args):
    """Start the scheduler daemon."""
    try:
        scheduler = PillScheduler()
        
        print("🚀 Starting pill scheduler daemon...")
        if args.foreground:
            print("Running in foreground mode (press Ctrl+C to stop)")
            scheduler.start_scheduler(daemon=False)
        else:
            print("Running in background mode")
            scheduler.start_scheduler(daemon=True)
            print("✅ Scheduler daemon started successfully")
            
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point for the scheduler CLI."""
    parser = argparse.ArgumentParser(
        description="Pill Scheduler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scheduler-add --name "Aspirin" --dosage "1 pill" --times "08:00 20:00" --days "monday wednesday friday"
  scheduler-list
  scheduler-next
  scheduler-start --foreground
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add schedule command
    add_parser = subparsers.add_parser("add", help="Add a new medication schedule")
    add_parser.add_argument("--name", required=True, help="Medication name")
    add_parser.add_argument("--dosage", required=True, help="Medication dosage")
    add_parser.add_argument("--times", required=True, nargs="+", help="Medication times (HH:MM format)")
    add_parser.add_argument("--days", required=True, nargs="+", help="Days of week")
    add_parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    add_parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    add_parser.add_argument("--notes", help="Additional notes")
    
    # List schedules command
    list_parser = subparsers.add_parser("list", help="List all medication schedules")
    
    # Next medication command
    next_parser = subparsers.add_parser("next", help="Show next scheduled medication")
    
    # Start scheduler command
    start_parser = subparsers.add_parser("start", help="Start the scheduler daemon")
    start_parser.add_argument("--foreground", action="store_true", help="Run in foreground (not as daemon)")
    
    # Delete schedule command
    delete_parser = subparsers.add_parser("delete", help="Delete a medication schedule")
    delete_parser.add_argument("--id", required=True, help="Schedule ID to delete")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "add":
            add_schedule_command(args)
        elif args.command == "list":
            list_schedules_command(args)
        elif args.command == "next":
            next_medication_command(args)
        elif args.command == "start":
            start_scheduler_command(args)
        elif args.command == "delete":
            delete_schedule_command(args)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def delete_schedule_command(args):
    """Delete a medication schedule."""
    try:
        scheduler = PillScheduler()
        
        if scheduler.delete_schedule(args.id):
            print(f"✅ Schedule {args.id} deleted successfully")
            return True
        else:
            print(f"❌ Schedule {args.id} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    main()