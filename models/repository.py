"""
models/repository.py
--------------------
Repository pattern: handles all read/write operations to the JSON datastore.
Keeps persistence logic fully separate from business logic and UI.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from models.appointment import Appointment, AppointmentStatus


DATA_FILE = Path(__file__).parent.parent / "data" / "appointments.json"


class AppointmentRepository:
    """
    JSON-backed repository for appointments.
    All I/O goes through this class — swap for SQLite/Postgres later
    without touching controllers or views.
    """

    def __init__(self, filepath: Path = DATA_FILE):
        self._filepath = filepath
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self._filepath.exists():
            self._write([])

    # ── Private helpers ────────────────────────────────────────────────────────

    def _read(self) -> list[dict]:
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, records: list[dict]) -> None:
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, default=str)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def get_all(self) -> list[Appointment]:
        records = self._read()
        return [Appointment.from_dict(r) for r in records]

    def get_by_id(self, appt_id: str) -> Optional[Appointment]:
        for record in self._read():
            if record["id"] == appt_id:
                return Appointment.from_dict(record)
        return None

    def create(self, appt: Appointment) -> Appointment:
        records = self._read()
        records.append(appt.to_dict())
        self._write(records)
        return appt

    def update(self, appt: Appointment) -> Optional[Appointment]:
        records = self._read()
        for i, record in enumerate(records):
            if record["id"] == appt.id:
                appt.updated_at = datetime.now()
                records[i] = appt.to_dict()
                self._write(records)
                return appt
        return None

    def delete(self, appt_id: str) -> bool:
        records = self._read()
        new_records = [r for r in records if r["id"] != appt_id]
        if len(new_records) == len(records):
            return False
        self._write(new_records)
        return True

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_status(self, status: str) -> list[Appointment]:
        return [a for a in self.get_all() if a.status == status]

    def get_by_date(self, target_date: date) -> list[Appointment]:
        return [a for a in self.get_all() if a.date == target_date]

    def get_by_date_range(self, start: date, end: date) -> list[Appointment]:
        return [a for a in self.get_all() if start <= a.date <= end]

    def get_upcoming(self) -> list[Appointment]:
        now = datetime.now()
        return sorted(
            [a for a in self.get_all() if a.start_datetime > now
             and a.status == AppointmentStatus.SCHEDULED],
            key=lambda a: a.start_datetime,
        )

    def search(self, query: str) -> list[Appointment]:
        q = query.lower().strip()
        return [
            a for a in self.get_all()
            if q in a.title.lower()
            or q in a.client_name.lower()
            or q in a.client_email.lower()
            or q in a.notes.lower()
        ]

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        all_appts = self.get_all()
        now = datetime.now()
        today = now.date()

        return {
            "total":     len(all_appts),
            "scheduled": sum(1 for a in all_appts if a.status == AppointmentStatus.SCHEDULED),
            "completed": sum(1 for a in all_appts if a.status == AppointmentStatus.COMPLETED),
            "cancelled": sum(1 for a in all_appts if a.status == AppointmentStatus.CANCELLED),
            "no_show":   sum(1 for a in all_appts if a.status == AppointmentStatus.NO_SHOW),
            "today":     sum(1 for a in all_appts if a.date == today),
            "upcoming":  len(self.get_upcoming()),
        }
