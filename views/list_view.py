"""
views/list_view.py
------------------
List view: searchable, filterable table of appointments with
inline quick-actions (edit, cancel, delete, status toggle).
"""

import streamlit as st
from datetime import date

from controllers.appointment_controller import AppointmentController
from models.appointment import Appointment, AppointmentStatus


STATUS_BADGE = {
    AppointmentStatus.SCHEDULED: ("🔵", "#3B82F6"),
    AppointmentStatus.COMPLETED: ("✅", "#10B981"),
    AppointmentStatus.CANCELLED: ("❌", "#EF4444"),
    AppointmentStatus.NO_SHOW:   ("⚠️", "#F59E0B"),
}


def _render_status_badge(status: str) -> str:
    icon, color = STATUS_BADGE.get(status, ("•", "#6B7280"))
    return (
        f'<span style="'
        f'background:{color}20; color:{color}; border:1px solid {color}60;'
        f'padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600;">'
        f'{icon} {status}</span>'
    )


def render_appointment_list(controller: AppointmentController) -> None:
    """Full appointment list with search/filter controls and per-row actions."""

    st.markdown("## 📋 All Appointments")
    st.markdown("---")

    # ── Toolbar ───────────────────────────────────────────────────────────────
    toolbar_left, toolbar_mid, toolbar_right = st.columns([3, 2, 2])

    with toolbar_left:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Name, title, email…",
            label_visibility="collapsed",
            key="list_search",
        )
    with toolbar_mid:
        status_filter = st.selectbox(
            "Filter by status",
            options=["All"] + AppointmentStatus.ALL,
            key="list_status_filter",
            label_visibility="collapsed",
        )
    with toolbar_right:
        sort_by = st.selectbox(
            "Sort by",
            options=["date", "client_name", "status", "title"],
            format_func=lambda x: {"date": "📅 Date", "client_name": "👤 Client",
                                    "status": "🏷 Status", "title": "📝 Title"}[x],
            key="list_sort",
            label_visibility="collapsed",
        )

    # Date range filter
    with st.expander("📆 Filter by date range", expanded=False):
        dr_col1, dr_col2, dr_col3 = st.columns([1, 1, 1])
        with dr_col1:
            use_date_filter = st.checkbox("Enable date filter", key="use_date_filter")
        if use_date_filter:
            with dr_col2:
                date_from = st.date_input("From", value=date.today(), key="date_from")
            with dr_col3:
                date_to = st.date_input("To", value=date.today(), key="date_to")

    # ── Fetch & Filter ────────────────────────────────────────────────────────
    if search_query.strip():
        appointments = controller.search(search_query)
    elif status_filter != "All":
        appointments = controller.filter_by_status(status_filter)
    elif "use_date_filter" in st.session_state and st.session_state.use_date_filter:
        appointments = controller.filter_by_date_range(
            st.session_state.get("date_from", date.today()),
            st.session_state.get("date_to", date.today()),
        )
    else:
        appointments = controller.list_all(sort_by=sort_by)

    # ── Result count + New button ─────────────────────────────────────────────
    count_col, new_col = st.columns([4, 1])
    with count_col:
        st.markdown(f"**{len(appointments)}** appointment(s) found")
    with new_col:
        if st.button("➕ New", type="primary", use_container_width=True):
            st.session_state["active_page"]  = "new"
            st.session_state["edit_appt_id"] = None
            st.rerun()

    st.markdown("")

    # ── Empty state ───────────────────────────────────────────────────────────
    if not appointments:
        st.markdown(
            """
            <div style="text-align:center; padding: 60px 20px; color:#9CA3AF;">
                <div style="font-size:3rem;">📭</div>
                <div style="font-size:1.1rem; margin-top:12px;">No appointments found</div>
                <div style="font-size:0.85rem; margin-top:4px;">
                    Try adjusting your search or filters.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Table Header ──────────────────────────────────────────────────────────
    hdr_cols = st.columns([0.6, 1.8, 1.5, 1.5, 1.2, 1.2, 1.2, 1.5])
    headers  = ["ID", "Title", "Client", "Email", "Date", "Time", "Status", "Actions"]
    for col, hdr in zip(hdr_cols, headers):
        col.markdown(f"<small><b>{hdr}</b></small>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)

    # ── Rows ─────────────────────────────────────────────────────────────────
    for appt in appointments:
        cols = st.columns([0.6, 1.8, 1.5, 1.5, 1.2, 1.2, 1.2, 1.5])

        cols[0].markdown(f"<small style='color:#9CA3AF;'>`{appt.id}`</small>", unsafe_allow_html=True)
        cols[1].markdown(f"**{appt.title}**")
        cols[2].markdown(appt.client_name)
        cols[3].markdown(f"<small>{appt.client_email}</small>", unsafe_allow_html=True)
        cols[4].markdown(f"<small>{appt.date.strftime('%b %d, %Y')}</small>", unsafe_allow_html=True)
        cols[5].markdown(
            f"<small>{appt.start_time.strftime('%H:%M')}–{appt.end_time.strftime('%H:%M')}</small>",
            unsafe_allow_html=True,
        )
        cols[6].markdown(_render_status_badge(appt.status), unsafe_allow_html=True)

        # Action buttons
        with cols[7]:
            btn1, btn2, btn3 = st.columns(3)
            with btn1:
                if st.button("✏️", key=f"edit_{appt.id}", help="Edit"):
                    st.session_state["active_page"]  = "edit"
                    st.session_state["edit_appt_id"] = appt.id
                    st.rerun()
            with btn2:
                # Quick complete / re-schedule toggle
                if appt.status == AppointmentStatus.SCHEDULED:
                    if st.button("✅", key=f"done_{appt.id}", help="Mark Complete"):
                        controller.update_status(appt.id, AppointmentStatus.COMPLETED)
                        st.rerun()
                elif appt.status == AppointmentStatus.COMPLETED:
                    if st.button("🔄", key=f"resched_{appt.id}", help="Re-schedule"):
                        controller.update_status(appt.id, AppointmentStatus.SCHEDULED)
                        st.rerun()
                else:
                    st.button("–", key=f"noop_{appt.id}", disabled=True)
            with btn3:
                if st.button("🗑️", key=f"del_{appt.id}", help="Delete"):
                    st.session_state[f"confirm_delete_{appt.id}"] = True

        # Inline delete confirmation
        if st.session_state.get(f"confirm_delete_{appt.id}"):
            with st.container():
                st.warning(
                    f"⚠️ Delete **{appt.title}** for **{appt.client_name}**? This cannot be undone."
                )
                c1, c2, _ = st.columns([1, 1, 4])
                with c1:
                    if st.button("Yes, delete", key=f"confirm_yes_{appt.id}", type="primary"):
                        controller.delete_appointment(appt.id)
                        st.session_state[f"confirm_delete_{appt.id}"] = False
                        st.success(f"Appointment `{appt.id}` deleted.")
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"confirm_no_{appt.id}"):
                        st.session_state[f"confirm_delete_{appt.id}"] = False
                        st.rerun()

        st.markdown("<hr style='margin:2px 0; border-color:#F3F4F6;'>", unsafe_allow_html=True)
