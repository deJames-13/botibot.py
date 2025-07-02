#!/usr/bin/env python3
"""
Scheduler Module for Pill Dispenser Robot.

This module provides scheduling functionality for medication intake management,
integration with Flask server, and automated pill dispensing routines.
"""

import schedule
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import threading
import sqlite3
import os
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicationStatus(Enum):
    """Medication intake status."""
    SCHEDULED = "scheduled"
    TAKEN = "taken"
    MISSED = "missed"
    SKIPPED = "skipped"


@dataclass
class MedicationSchedule:
    """Medication schedule data structure."""
    id: str
    name: str
    dosage: str
    times: List[str]  # List of times in "HH:MM" format
    days: List[str]   # List of days: ["monday", "tuesday", ...]
    start_date: str   # "YYYY-MM-DD"
    end_date: str     # "YYYY-MM-DD" or None for indefinite
    active: bool = True
    notes: str = ""


@dataclass
class MedicationIntake:
    """Medication intake record."""
    id: str
    schedule_id: str
    medication_name: str
    scheduled_time: str
    actual_time: Optional[str]
    status: MedicationStatus
    notes: str = ""


class PillScheduler:
    """
    Pill dispenser scheduler for automated medication management.
    
    Features:
    - Schedule medication times
    - Track medication intake
    - Send reminders and alerts
    - Integration with Flask server
    - SQLite database storage
    """

    def __init__(self, db_path: str = "pill_schedule.db"):
        """
        Initialize the pill scheduler.

        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.schedules: Dict[str, MedicationSchedule] = {}
        self.intake_records: List[MedicationIntake] = []
        self.is_running = False
        self.scheduler_thread = None
        
        # Callbacks
        self.on_medication_reminder: Optional[Callable] = None
        self.on_medication_missed: Optional[Callable] = None
        self.on_schedule_update: Optional[Callable] = None
        
        self._init_database()
        self._load_schedules()

    def _init_database(self) -> None:
        """Initialize SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medication_schedules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dosage TEXT NOT NULL,
                    times TEXT NOT NULL,
                    days TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    active BOOLEAN DEFAULT 1,
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create intake records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medication_intakes (
                    id TEXT PRIMARY KEY,
                    schedule_id TEXT NOT NULL,
                    medication_name TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    actual_time TEXT,
                    status TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (schedule_id) REFERENCES medication_schedules (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _load_schedules(self) -> None:
        """Load schedules from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM medication_schedules WHERE active = 1")
            rows = cursor.fetchall()
            
            for row in rows:
                schedule = MedicationSchedule(
                    id=row[0],
                    name=row[1],
                    dosage=row[2],
                    times=json.loads(row[3]),
                    days=json.loads(row[4]),
                    start_date=row[5],
                    end_date=row[6],
                    active=bool(row[7]),
                    notes=row[8] or ""
                )
                self.schedules[schedule.id] = schedule
                
            conn.close()
            logger.info(f"Loaded {len(self.schedules)} active schedules")
            
        except Exception as e:
            logger.error(f"Failed to load schedules: {e}")

    def add_schedule(self, schedule: MedicationSchedule) -> bool:
        """
        Add a new medication schedule.

        Args:
            schedule (MedicationSchedule): Medication schedule to add

        Returns:
            bool: True if added successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO medication_schedules 
                (id, name, dosage, times, days, start_date, end_date, active, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule.id,
                schedule.name,
                schedule.dosage,
                json.dumps(schedule.times),
                json.dumps(schedule.days),
                schedule.start_date,
                schedule.end_date,
                schedule.active,
                schedule.notes
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.schedules[schedule.id] = schedule
            
            # Setup scheduler jobs
            self._setup_schedule_jobs(schedule)
            
            logger.info(f"Added schedule: {schedule.name}")
            
            if self.on_schedule_update:
                self.on_schedule_update("ADDED", schedule)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add schedule: {e}")
            return False

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a medication schedule.

        Args:
            schedule_id (str): Schedule ID to remove

        Returns:
            bool: True if removed successfully
        """
        try:
            if schedule_id not in self.schedules:
                logger.warning(f"Schedule {schedule_id} not found")
                return False
            
            # Deactivate in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE medication_schedules SET active = 0 WHERE id = ?",
                (schedule_id,)
            )
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            schedule = self.schedules.pop(schedule_id)
            
            # Clear scheduled jobs for this medication
            schedule.clear(schedule.name)
            
            logger.info(f"Removed schedule: {schedule.name}")
            
            if self.on_schedule_update:
                self.on_schedule_update("REMOVED", schedule)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove schedule: {e}")
            return False

    def _setup_schedule_jobs(self, med_schedule: MedicationSchedule) -> None:
        """Setup scheduler jobs for a medication schedule."""
        for day in med_schedule.days:
            for time_str in med_schedule.times:
                # Setup schedule job
                job = getattr(schedule.every(), day.lower()).at(time_str)
                job.do(self._medication_reminder, med_schedule.id, time_str)
                
                logger.debug(f"Scheduled {med_schedule.name} for {day} at {time_str}")

    def _medication_reminder(self, schedule_id: str, scheduled_time: str) -> None:
        """Handle medication reminder."""
        if schedule_id not in self.schedules:
            return
            
        med_schedule = self.schedules[schedule_id]
        
        # Create intake record
        intake_id = f"{schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        intake = MedicationIntake(
            id=intake_id,
            schedule_id=schedule_id,
            medication_name=med_schedule.name,
            scheduled_time=scheduled_time,
            actual_time=None,
            status=MedicationStatus.SCHEDULED
        )
        
        # Store in database
        self._save_intake_record(intake)
        
        logger.info(f"Medication reminder: {med_schedule.name} at {scheduled_time}")
        
        # Call user callback
        if self.on_medication_reminder:
            self.on_medication_reminder(med_schedule, intake)
        
        # Setup missed medication check (30 minutes later)
        threading.Timer(
            1800,  # 30 minutes
            self._check_missed_medication,
            args=[intake_id]
        ).start()

    def _check_missed_medication(self, intake_id: str) -> None:
        """Check if medication was missed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT status FROM medication_intakes WHERE id = ?",
                (intake_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == MedicationStatus.SCHEDULED.value:
                # Mark as missed
                self.mark_medication_taken(intake_id, MedicationStatus.MISSED)
                
                # Get intake record
                intake = self._get_intake_record(intake_id)
                if intake and self.on_medication_missed:
                    self.on_medication_missed(intake)
                    
        except Exception as e:
            logger.error(f"Failed to check missed medication: {e}")

    def mark_medication_taken(self, intake_id: str, status: MedicationStatus, notes: str = "") -> bool:
        """
        Mark medication as taken/missed/skipped.

        Args:
            intake_id (str): Intake record ID
            status (MedicationStatus): New status
            notes (str): Optional notes

        Returns:
            bool: True if updated successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            actual_time = datetime.now().isoformat() if status == MedicationStatus.TAKEN else None
            
            cursor.execute("""
                UPDATE medication_intakes 
                SET status = ?, actual_time = ?, notes = ?
                WHERE id = ?
            """, (status.value, actual_time, notes, intake_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Marked medication {intake_id} as {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark medication: {e}")
            return False

    def _save_intake_record(self, intake: MedicationIntake) -> None:
        """Save intake record to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO medication_intakes 
                (id, schedule_id, medication_name, scheduled_time, actual_time, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                intake.id,
                intake.schedule_id,
                intake.medication_name,
                intake.scheduled_time,
                intake.actual_time,
                intake.status.value,
                intake.notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save intake record: {e}")

    def _get_intake_record(self, intake_id: str) -> Optional[MedicationIntake]:
        """Get intake record from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM medication_intakes WHERE id = ?", (intake_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return MedicationIntake(
                    id=row[0],
                    schedule_id=row[1],
                    medication_name=row[2],
                    scheduled_time=row[3],
                    actual_time=row[4],
                    status=MedicationStatus(row[5]),
                    notes=row[6] or ""
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get intake record: {e}")
            return None

    def get_today_schedule(self) -> List[Dict[str, Any]]:
        """
        Get today's medication schedule.

        Returns:
            List[Dict]: Today's scheduled medications
        """
        today = datetime.now().strftime("%A").lower()
        today_schedule = []
        
        for schedule in self.schedules.values():
            if today in [day.lower() for day in schedule.days]:
                for time_str in schedule.times:
                    today_schedule.append({
                        'schedule_id': schedule.id,
                        'medication': schedule.name,
                        'dosage': schedule.dosage,
                        'time': time_str,
                        'status': 'scheduled'
                    })
        
        # Sort by time
        today_schedule.sort(key=lambda x: x['time'])
        return today_schedule

    def get_intake_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get medication intake history.

        Args:
            days (int): Number of days to look back

        Returns:
            List[Dict]: Intake history
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT * FROM medication_intakes 
                WHERE created_at >= ?
                ORDER BY created_at DESC
            """, (since_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'medication': row[2],
                    'scheduled_time': row[3],
                    'actual_time': row[4],
                    'status': row[5],
                    'notes': row[6],
                    'created_at': row[7]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get intake history: {e}")
            return []

    def get_compliance_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get medication compliance statistics.

        Args:
            days (int): Number of days to analyze

        Returns:
            Dict: Compliance statistics
        """
        history = self.get_intake_history(days)
        
        total = len(history)
        taken = len([r for r in history if r['status'] == 'taken'])
        missed = len([r for r in history if r['status'] == 'missed'])
        skipped = len([r for r in history if r['status'] == 'skipped'])
        
        compliance_rate = (taken / total * 100) if total > 0 else 0
        
        return {
            'total_scheduled': total,
            'taken': taken,
            'missed': missed,
            'skipped': skipped,
            'compliance_rate': round(compliance_rate, 1),
            'period_days': days
        }

    def start_scheduler(self) -> None:
        """Start the medication scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        def run_scheduler():
            logger.info("Medication scheduler started")
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
            logger.info("Medication scheduler stopped")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self) -> None:
        """Stop the medication scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def get_all_schedules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all medication schedules.

        Returns:
            Dict: All schedules
        """
        return {
            schedule_id: asdict(schedule) 
            for schedule_id, schedule in self.schedules.items()
        }

    def cleanup(self) -> None:
        """Clean up scheduler resources."""
        self.stop_scheduler()
        schedule.clear()


# Example usage
if __name__ == "__main__":
    try:
        # Initialize scheduler
        scheduler = PillScheduler()
        
        # Set up callbacks
        def on_reminder(med_schedule, intake):
            print(f"🔔 REMINDER: Take {med_schedule.name} ({med_schedule.dosage})")
        
        def on_missed(intake):
            print(f"⚠️ MISSED: {intake.medication_name} was not taken at {intake.scheduled_time}")
        
        scheduler.on_medication_reminder = on_reminder
        scheduler.on_medication_missed = on_missed
        
        # Add sample schedule
        sample_schedule = MedicationSchedule(
            id="vitamin_d_001",
            name="Vitamin D",
            dosage="1 tablet",
            times=["08:00", "20:00"],
            days=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            start_date="2025-07-01",
            end_date=None,
            notes="Take with food"
        )
        
        scheduler.add_schedule(sample_schedule)
        
        # Start scheduler
        scheduler.start_scheduler()
        
        # Show today's schedule
        today_schedule = scheduler.get_today_schedule()
        print(f"Today's Schedule: {today_schedule}")
        
        # Show compliance stats
        stats = scheduler.get_compliance_stats()
        print(f"Compliance Stats: {stats}")
        
        # Keep running
        print("Scheduler running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping scheduler...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'scheduler' in locals():
            scheduler.cleanup()
