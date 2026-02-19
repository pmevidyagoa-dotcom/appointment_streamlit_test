"""
views/detail_view.py
--------------------
Detail view: full read-only summary of one appointment,
with quick action buttons (Edit, Cancel, Delete).
"""

import streamlit as st
from datetime import datetime

from controllers.appointment_controller import AppointmentController
from models.appointment import Appointment, AppointmentStatus


STATUS_STYLES = {
    AppointmentStatus.SCHEDULED: ("#3B82F6", "🔵"),
    AppointmentStatus.COMPLETED: ("#10B981", "✅"),
    AppointmentStatus.CANCELLED: ("#EF4444", "❌"),
    AppointmentStatus.NO_SHOW:   ("#F59E0B", "⚠️"),
}


def _info_row(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div style="display:flex; gap:16px; padding:8px 0;
                    border-bottom:1px solid #F3F4F6;">
            <span style="min-width:140px; color:#6B7280; font-size:0.85rem;
                         font-weight:500;">{label}</span>
            <span style="color:#111827; font-size:0.9rem;">{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_appointment_detail(
    controller: AppointmentController,
    appt_id: str,
) -> None:
    """Display full detail of a single appointment."""

    appt = controller.get_by_id(appt_id)
    if appt is None:
        st.error(f"Appointment `{appt_id}` not found.")
        if st.button("← Back to list"):
            st.session_state["active_page"] = "list"
            st.rerun()
        return

    color, icon = STATUS_STYLES.get(appt.status, ("#6B7280", "•"))

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}10, {color}20);
            border: 2px solid {color}50;
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 24px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-size:1.6rem; font-weight:700; color:#111827;">
                        {appt.title}
                    </div>
                    <div style="color:#6B7280; margin-top:6px;">
                        ID: <code>{appt.id}</code>
                    </div>
                </div>
                <div style="
                    background:{color}20; color:{color};
                    border:1.5px solid {color}60;
                    border-radius:999px; padding:6px 18px;
                    font-weight:700; font-size:0.9rem;
                ">
                    {icon} {appt.status}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Two-column detail panel ────────────────────────────────────────────────
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("#### 📅 Appointment Info")
        _info_row("Date",      appt.date.strftime("%A, %B %d, %Y"))
        _info_row("Start",     appt.start_time.strftime("%H:%M"))
        _info_row("End",       appt.end_time.strftime("%H:%M"))
        _info_row("Duration",  f"{appt.duration_minutes} minutes")
        _info_row("Status",    appt.status)

    with right:
        st.markdown("#### 👤 Client Info")
        _info_row("Name",  appt.client_name)
        _info_row("Email", appt.client_email)
        _info_row("Phone", appt.client_phone)

    if appt.notes:
        st.markdown("#### 📝 Notes")
        st.markdown(
            f"""
            <div style="
                background:#F9FAFB; border-left:4px solid {color};
                border-radius:0 8px 8px 0; padding:14px 16px;
                color:#374151; font-size:0.9rem; white-space:pre-wrap;
            ">{appt.notes}</div>
            """,
            unsafe_allow_html=True,
        )

    # Timestamps
    st.markdown(
        f"""
        <div style="color:#9CA3AF; font-size:0.75rem; margin-top:16px;">
            Created: {appt.created_at.strftime('%b %d, %Y %H:%M')} &nbsp;|&nbsp;
            Updated: {appt.updated_at.strftime('%b %d, %Y %H:%M')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Action Buttons ────────────────────────────────────────────────────────
    btn1, btn2, btn3, btn4, _ = st.columns([1.2, 1.2, 1.2, 1.2, 2])

    with btn1:
        if st.button("← Back", use_container_width=True):
            st.session_state["active_page"]  = "list"
            st.session_state["view_appt_id"] = None
            st.rerun()

    with btn2:
        if st.button("✏️ Edit", type="primary", use_container_width=True):
            st.session_state["active_page"]  = "edit"
            st.session_state["edit_appt_id"] = appt.id
            st.rerun()

    with btn3:
        if appt.status == AppointmentStatus.SCHEDULED:
            if st.button("✅ Complete", use_container_width=True):
                controller.update_status(appt.id, AppointmentStatus.COMPLETED)
                st.success("Marked as Completed.")
                st.rerun()
        elif appt.status != AppointmentStatus.CANCELLED:
            if st.button("❌ Cancel", use_container_width=True):
                controller.update_status(appt.id, AppointmentStatus.CANCELLED)
                st.success("Appointment cancelled.")
                st.rerun()

    with btn4:
        if st.button("🗑️ Delete", use_container_width=True):
            st.session_state["confirm_delete_detail"] = True

    if st.session_state.get("confirm_delete_detail"):
        st.warning(f"⚠️ Permanently delete **{appt.title}**?")
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            if st.button("Yes, delete", type="primary", key="detail_confirm_yes"):
                controller.delete_appointment(appt.id)
                st.session_state["confirm_delete_detail"] = False
                st.session_state["active_page"]           = "list"
                st.session_state["view_appt_id"]          = None
                st.rerun()
        with c2:
            if st.button("Cancel", key="detail_confirm_no"):
                st.session_state["confirm_delete_detail"] = False
                st.rerun()
