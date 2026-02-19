"""
views/dashboard_view.py
------------------------
Dashboard view: KPI cards, today's schedule, upcoming appointments.
Purely presentational — calls controller for data, renders to Streamlit.
"""

import streamlit as st
from datetime import datetime

from controllers.appointment_controller import AppointmentController
from models.appointment import AppointmentStatus


STATUS_COLORS = {
    AppointmentStatus.SCHEDULED:  "#3B82F6",
    AppointmentStatus.COMPLETED:  "#10B981",
    AppointmentStatus.CANCELLED:  "#EF4444",
    AppointmentStatus.NO_SHOW:    "#F59E0B",
}

STATUS_ICONS = {
    AppointmentStatus.SCHEDULED:  "🔵",
    AppointmentStatus.COMPLETED:  "✅",
    AppointmentStatus.CANCELLED:  "❌",
    AppointmentStatus.NO_SHOW:    "⚠️",
}


def render_kpi_card(label: str, value: int, icon: str, color: str) -> None:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}15, {color}30);
            border: 1.5px solid {color}60;
            border-radius: 12px;
            padding: 20px 16px;
            text-align: center;
            box-shadow: 0 2px 8px {color}20;
        ">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: {color}; line-height: 1.1;">
                {value}
            </div>
            <div style="font-size: 0.85rem; color: #6B7280; margin-top: 4px; font-weight: 500;">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_appointment_row(appt, controller: AppointmentController) -> None:
    """Compact appointment row with quick-status buttons."""
    color  = STATUS_COLORS.get(appt.status, "#6B7280")
    icon   = STATUS_ICONS.get(appt.status, "•")
    dur    = appt.duration_minutes

    with st.container():
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {color};
                background: #F9FAFB;
                border-radius: 0 8px 8px 0;
                padding: 12px 16px;
                margin-bottom: 8px;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-weight:600; font-size:1rem;">{appt.title}</span>
                        <span style="color:#6B7280; font-size:0.85rem; margin-left:8px;">
                            {icon} {appt.status}
                        </span>
                    </div>
                    <div style="color:#374151; font-size:0.9rem; font-weight:500;">
                        {appt.start_time.strftime('%H:%M')} – {appt.end_time.strftime('%H:%M')}
                        <span style="color:#9CA3AF; font-size:0.8rem;"> ({dur} min)</span>
                    </div>
                </div>
                <div style="color:#4B5563; font-size:0.85rem; margin-top:4px;">
                    👤 {appt.client_name} &nbsp;|&nbsp; ✉️ {appt.client_email}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard(controller: AppointmentController) -> None:
    """Main dashboard view."""

    st.markdown("## 📊 Dashboard")
    st.markdown(f"*{datetime.now().strftime('%A, %B %d, %Y')}*")
    st.markdown("---")

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    stats = controller.get_dashboard_stats()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: render_kpi_card("Total",     stats["total"],     "📋", "#6366F1")
    with col2: render_kpi_card("Scheduled", stats["scheduled"], "🔵", "#3B82F6")
    with col3: render_kpi_card("Completed", stats["completed"], "✅", "#10B981")
    with col4: render_kpi_card("Cancelled", stats["cancelled"], "❌", "#EF4444")
    with col5: render_kpi_card("No Show",   stats["no_show"],   "⚠️", "#F59E0B")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Today + Upcoming ──────────────────────────────────────────────────────
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        today_appts = controller.get_today()
        st.markdown(f"### 📅 Today's Appointments ({len(today_appts)})")
        if not today_appts:
            st.info("No appointments scheduled for today.", icon="🗓️")
        else:
            for appt in sorted(today_appts, key=lambda a: a.start_time):
                render_appointment_row(appt, controller)

    with right_col:
        upcoming = controller.get_upcoming()[:5]
        st.markdown(f"### 🔜 Upcoming ({stats['upcoming']} total)")
        if not upcoming:
            st.info("No upcoming appointments.", icon="📭")
        else:
            for appt in upcoming:
                render_appointment_row(appt, controller)

    # ── Compact Status Summary ────────────────────────────────────────────────
    if stats["total"] > 0:
        st.markdown("---")
        st.markdown("### 📈 Status Breakdown")
        for status in AppointmentStatus.ALL:
            key = status.lower().replace(" ", "_")
            count = stats.get(key, 0)
            pct   = (count / stats["total"]) * 100 if stats["total"] else 0
            color = STATUS_COLORS[status]
            icon  = STATUS_ICONS[status]
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    <span style="min-width:90px; font-size:0.85rem;">{icon} {status}</span>
                    <div style="
                        flex:1; background:#E5E7EB; border-radius:999px; height:12px;
                        overflow:hidden;
                    ">
                        <div style="
                            width:{pct:.1f}%; background:{color};
                            height:100%; border-radius:999px;
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                    <span style="min-width:40px; text-align:right; font-size:0.85rem;
                                 font-weight:600; color:{color};">{count}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
