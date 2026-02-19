"""
models/appointment.py
---------------------
Model layer: pure data classes + validation logic.
No UI, no DB calls — just structure and rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional
import uuid


# ─── Status constants ────────────────────────────────────────────────────────

class AppointmentStatus:
    SCHEDULED  = "Scheduled"
    COMPLETED  = "Completed"
    CANCELLED  = "Cancelled"
    NO_SHOW    = "No Show"

    ALL = [SCHEDULED, COMPLETED, CANCELLED, NO_SHOW]


# ─── Data class ──────────────────────────────────────────────────────────────

@dataclass
class Appointment:
    """Represents a single appointment record."""

    id:           str
    title:        str
    client_name:  str
    client_email: str
    client_phone: str
    date:         date
    start_time:   time
    end_time:     time
    status:       str
    notes:        str          = ""
    created_at:   datetime    = field(default_factory=datetime.now)
    updated_at:   datetime    = field(default_factory=datetime.now)

    # ── Computed helpers ──────────────────────────────────────────────────────

    @property
    def duration_minutes(self) -> int:
        """Total duration of the appointment in minutes."""
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt   = datetime.combine(self.date, self.end_time)
        delta    = end_dt - start_dt
        return int(delta.total_seconds() // 60)

    @property
    def is_upcoming(self) -> bool:
        appt_dt = datetime.combine(self.date, self.start_time)
        return appt_dt > datetime.now() and self.status == AppointmentStatus.SCHEDULED

    @property
    def is_past(self) -> bool:
        appt_dt = datetime.combine(self.date, self.start_time)
        return appt_dt < datetime.now()

    @property
    def start_datetime(self) -> datetime:
        return datetime.combine(self.date, self.start_time)

    @property
    def end_datetime(self) -> datetime:
        return datetime.combine(self.date, self.end_time)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "title":        self.title,
            "client_name":  self.client_name,
            "client_email": self.client_email,
            "client_phone": self.client_phone,
            "date":         self.date.isoformat(),
            "start_time":   self.start_time.strftime("%H:%M"),
            "end_time":     self.end_time.strftime("%H:%M"),
            "status":       self.status,
            "notes":        self.notes,
            "created_at":   self.created_at.isoformat(),
            "updated_at":   self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Appointment":
        return cls(
            id           = d["id"],
            title        = d["title"],
            client_name  = d["client_name"],
            client_email = d["client_email"],
            client_phone = d["client_phone"],
            date         = date.fromisoformat(d["date"]),
            start_time   = time.fromisoformat(d["start_time"]),
            end_time     = time.fromisoformat(d["end_time"]),
            status       = d["status"],
            notes        = d.get("notes", ""),
            created_at   = datetime.fromisoformat(d.get("created_at", datetime.now().isoformat())),
            updated_at   = datetime.fromisoformat(d.get("updated_at", datetime.now().isoformat())),
        )

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())[:8].upper()


# ─── Validation ───────────────────────────────────────────────────────────────

class AppointmentValidator:
    """Pure validation logic — returns list of error strings."""

    @staticmethod
    def validate(
        title: str,
        client_name: str,
        client_email: str,
        client_phone: str,
        appt_date: date,
        start_time: time,
        end_time: time,
        status: str,
    ) -> list[str]:
        errors = []

        if not title.strip():
            errors.append("Title is required.")
        if not client_name.strip():
            errors.append("Client name is required.")
        if not client_email.strip():
            errors.append("Client email is required.")
        elif "@" not in client_email or "." not in client_email.split("@")[-1]:
            errors.append("Please enter a valid email address.")
        if not client_phone.strip():
            errors.append("Client phone is required.")
        if status not in AppointmentStatus.ALL:
            errors.append(f"Invalid status: {status}")

        # Time logic
        start_dt = datetime.combine(appt_date, start_time)
        end_dt   = datetime.combine(appt_date, end_time)
        if end_dt <= start_dt:
            errors.append("End time must be after start time.")
        if (end_dt - start_dt).total_seconds() < 15 * 60:
            errors.append("Appointment must be at least 15 minutes long.")

        return errors
