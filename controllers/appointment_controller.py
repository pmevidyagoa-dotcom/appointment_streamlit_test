"""
controllers/appointment_controller.py
--------------------------------------
Controller layer: orchestrates Model ↔ View communication.
Applies business rules, delegates persistence to the repository,
and returns plain dicts / typed results to the View.
"""

from datetime import date, time, datetime
from typing import Optional

from models.appointment import Appointment, AppointmentStatus, AppointmentValidator
from models.repository import AppointmentRepository


class AppointmentController:
    """
    Mediates all user actions that touch appointment data.
    Views call these methods; controllers never call View code.
    """

    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    # ── Read operations ───────────────────────────────────────────────────────

    def list_all(self, sort_by: str = "date") -> list[Appointment]:
        """Return all appointments, sorted."""
        appts = self._repo.get_all()
        key_map = {
            "date":        lambda a: (a.date, a.start_time),
            "client_name": lambda a: a.client_name.lower(),
            "status":      lambda a: a.status,
            "title":       lambda a: a.title.lower(),
        }
        return sorted(appts, key=key_map.get(sort_by, key_map["date"]))

    def get_by_id(self, appt_id: str) -> Optional[Appointment]:
        return self._repo.get_by_id(appt_id)

    def get_upcoming(self) -> list[Appointment]:
        return self._repo.get_upcoming()

    def get_today(self) -> list[Appointment]:
        return self._repo.get_by_date(date.today())

    def search(self, query: str) -> list[Appointment]:
        return self._repo.search(query)

    def filter_by_status(self, status: str) -> list[Appointment]:
        return self._repo.get_by_status(status)

    def filter_by_date_range(self, start: date, end: date) -> list[Appointment]:
        return self._repo.get_by_date_range(start, end)

    def get_dashboard_stats(self) -> dict:
        return self._repo.get_stats()

    # ── Write operations ──────────────────────────────────────────────────────

    def create_appointment(
        self,
        title:        str,
        client_name:  str,
        client_email: str,
        client_phone: str,
        appt_date:    date,
        start_time:   time,
        end_time:     time,
        status:       str = AppointmentStatus.SCHEDULED,
        notes:        str = "",
    ) -> dict:
        """
        Validate inputs, create appointment.
        Returns {"success": True, "appointment": Appointment}
             or {"success": False, "errors": [str]}
        """
        errors = AppointmentValidator.validate(
            title, client_name, client_email, client_phone,
            appt_date, start_time, end_time, status,
        )
        if errors:
            return {"success": False, "errors": errors}

        # Check for time conflicts on the same day
        conflict = self._check_conflict(appt_date, start_time, end_time)
        if conflict:
            return {
                "success": False,
                "errors": [
                    f"Time conflict with appointment '{conflict.title}' "
                    f"({conflict.start_time.strftime('%H:%M')} – {conflict.end_time.strftime('%H:%M')})."
                ],
            }

        appt = Appointment(
            id=Appointment.generate_id(),
            title=title,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            date=appt_date,
            start_time=start_time,
            end_time=end_time,
            status=status,
            notes=notes,
        )
        self._repo.create(appt)
        return {"success": True, "appointment": appt}

    def update_appointment(
        self,
        appt_id:      str,
        title:        str,
        client_name:  str,
        client_email: str,
        client_phone: str,
        appt_date:    date,
        start_time:   time,
        end_time:     time,
        status:       str,
        notes:        str = "",
    ) -> dict:
        errors = AppointmentValidator.validate(
            title, client_name, client_email, client_phone,
            appt_date, start_time, end_time, status,
        )
        if errors:
            return {"success": False, "errors": errors}

        existing = self._repo.get_by_id(appt_id)
        if not existing:
            return {"success": False, "errors": ["Appointment not found."]}

        # Conflict check (excluding self)
        conflict = self._check_conflict(appt_date, start_time, end_time, exclude_id=appt_id)
        if conflict:
            return {
                "success": False,
                "errors": [
                    f"Time conflict with appointment '{conflict.title}' "
                    f"({conflict.start_time.strftime('%H:%M')} – {conflict.end_time.strftime('%H:%M')})."
                ],
            }

        existing.title        = title
        existing.client_name  = client_name
        existing.client_email = client_email
        existing.client_phone = client_phone
        existing.date         = appt_date
        existing.start_time   = start_time
        existing.end_time     = end_time
        existing.status       = status
        existing.notes        = notes

        updated = self._repo.update(existing)
        return {"success": True, "appointment": updated}

    def delete_appointment(self, appt_id: str) -> dict:
        success = self._repo.delete(appt_id)
        if success:
            return {"success": True}
        return {"success": False, "errors": ["Appointment not found."]}

    def update_status(self, appt_id: str, new_status: str) -> dict:
        appt = self._repo.get_by_id(appt_id)
        if not appt:
            return {"success": False, "errors": ["Appointment not found."]}
        if new_status not in AppointmentStatus.ALL:
            return {"success": False, "errors": [f"Invalid status: {new_status}"]}
        appt.status = new_status
        self._repo.update(appt)
        return {"success": True, "appointment": appt}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _check_conflict(
        self,
        appt_date:  date,
        start_time: time,
        end_time:   time,
        exclude_id: Optional[str] = None,
    ) -> Optional[Appointment]:
        """Return first conflicting appointment, or None."""
        same_day = self._repo.get_by_date(appt_date)
        for existing in same_day:
            if exclude_id and existing.id == exclude_id:
                continue
            if existing.status == AppointmentStatus.CANCELLED:
                continue
            # Overlap check: new starts before existing ends AND new ends after existing starts
            if start_time < existing.end_time and end_time > existing.start_time:
                return existing
        return None
