"""
views/form_view.py
------------------
Form view: reusable create / edit appointment form.
Purely presentational — collects inputs, hands them to the controller.
"""

import streamlit as st
from datetime import date, time, datetime, timedelta

from controllers.appointment_controller import AppointmentController
from models.appointment import Appointment, AppointmentStatus


def _time_options() -> list[time]:
    """Generate 15-minute interval time options for the whole day."""
    options = []
    for h in range(0, 24):
        for m in (0, 15, 30, 45):
            options.append(time(h, m))
    return options


def _format_time(t: time) -> str:
    return t.strftime("%H:%M")


def render_appointment_form(
    controller: AppointmentController,
    existing: Appointment | None = None,
) -> None:
    """
    Renders the create/edit form.
    If `existing` is provided, the form pre-fills with that appointment's data.
    """
    is_edit = existing is not None
    title_label = "✏️ Edit Appointment" if is_edit else "➕ New Appointment"

    st.markdown(f"## {title_label}")
    st.markdown("---")

    # Defaults
    def_title        = existing.title        if is_edit else ""
    def_client_name  = existing.client_name  if is_edit else ""
    def_client_email = existing.client_email if is_edit else ""
    def_client_phone = existing.client_phone if is_edit else ""
    def_date         = existing.date         if is_edit else date.today()
    def_start        = existing.start_time   if is_edit else time(9, 0)
    def_end          = existing.end_time     if is_edit else time(10, 0)
    def_status       = existing.status       if is_edit else AppointmentStatus.SCHEDULED
    def_notes        = existing.notes        if is_edit else ""

    time_opts   = _time_options()
    time_labels = [_format_time(t) for t in time_opts]

    # ── Section 1: Appointment Details ────────────────────────────────────────
    st.markdown("### 📋 Appointment Details")
    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input(
            "Title *",
            value=def_title,
            placeholder="e.g. Annual Check-up, Strategy Meeting…",
            key="form_title",
        )
    with col2:
        status_idx = AppointmentStatus.ALL.index(def_status)
        status = st.selectbox(
            "Status *",
            options=AppointmentStatus.ALL,
            index=status_idx,
            key="form_status",
        )

    # ── Section 2: Date & Time ────────────────────────────────────────────────
    st.markdown("### 🕐 Date & Time")
    col3, col4, col5 = st.columns(3)

    with col3:
        appt_date = st.date_input("Date *", value=def_date, key="form_date")

    with col4:
        start_idx = time_labels.index(_format_time(def_start)) if def_start in time_opts else 36  # 9:00
        start_label = st.selectbox(
            "Start Time *",
            options=time_labels,
            index=start_idx,
            key="form_start",
        )
        start_time = time_opts[time_labels.index(start_label)]

    with col5:
        end_idx = time_labels.index(_format_time(def_end)) if def_end in time_opts else 40  # 10:00
        end_label = st.selectbox(
            "End Time *",
            options=time_labels,
            index=end_idx,
            key="form_end",
        )
        end_time = time_opts[time_labels.index(end_label)]

    # Live duration preview
    start_dt = datetime.combine(appt_date, start_time)
    end_dt   = datetime.combine(appt_date, end_time)
    if end_dt > start_dt:
        dur_min = int((end_dt - start_dt).total_seconds() // 60)
        dur_h, dur_m = divmod(dur_min, 60)
        label = f"{dur_h}h {dur_m}min" if dur_h else f"{dur_m} min"
        st.caption(f"⏱ Duration: **{label}**")
    else:
        st.caption("⚠️ End time must be after start time.")

    # ── Section 3: Client Info ────────────────────────────────────────────────
    st.markdown("### 👤 Client Information")
    col6, col7, col8 = st.columns(3)

    with col6:
        client_name = st.text_input(
            "Full Name *",
            value=def_client_name,
            placeholder="Jane Doe",
            key="form_client_name",
        )
    with col7:
        client_email = st.text_input(
            "Email *",
            value=def_client_email,
            placeholder="jane@example.com",
            key="form_client_email",
        )
    with col8:
        client_phone = st.text_input(
            "Phone *",
            value=def_client_phone,
            placeholder="+1 555 000 0000",
            key="form_client_phone",
        )

    # ── Section 4: Notes ──────────────────────────────────────────────────────
    st.markdown("### 📝 Notes")
    notes = st.text_area(
        "Additional notes (optional)",
        value=def_notes,
        height=100,
        placeholder="Any relevant details, prep instructions, follow-ups…",
        key="form_notes",
    )

    st.markdown("---")

    # ── Action Buttons ────────────────────────────────────────────────────────
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])

    with btn_col1:
        submit_label = "💾 Update Appointment" if is_edit else "✅ Book Appointment"
        submitted = st.button(submit_label, type="primary", use_container_width=True)

    with btn_col3:
        cancelled = st.button("Cancel", use_container_width=True)

    # ── Handle Submit ─────────────────────────────────────────────────────────
    if submitted:
        if is_edit:
            result = controller.update_appointment(
                appt_id      = existing.id,
                title        = title,
                client_name  = client_name,
                client_email = client_email,
                client_phone = client_phone,
                appt_date    = appt_date,
                start_time   = start_time,
                end_time     = end_time,
                status       = status,
                notes        = notes,
            )
        else:
            result = controller.create_appointment(
                title        = title,
                client_name  = client_name,
                client_email = client_email,
                client_phone = client_phone,
                appt_date    = appt_date,
                start_time   = start_time,
                end_time     = end_time,
                status       = status,
                notes        = notes,
            )

        if result["success"]:
            action = "updated" if is_edit else "booked"
            appt   = result["appointment"]
            st.success(
                f"✅ Appointment **{appt.title}** successfully {action}!  "
                f"(ID: `{appt.id}`)",
                icon="🎉",
            )
            # Clear form state
            for key in ["form_title", "form_client_name", "form_client_email",
                        "form_client_phone", "form_notes"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["active_page"]    = "list"
            st.session_state["edit_appt_id"]   = None
            st.rerun()
        else:
            for err in result["errors"]:
                st.error(f"❌ {err}")

    if cancelled:
        st.session_state["active_page"]  = "list"
        st.session_state["edit_appt_id"] = None
        st.rerun()
