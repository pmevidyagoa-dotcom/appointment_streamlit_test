"""
appointment_app.py
------
Entry point: wires the MVC layers together and manages navigation state.

Run with:
    streamlit run appointment_app.py
"""

import sys
import os

# Ensure project root is on the path so imports resolve cleanly
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from models.repository import AppointmentRepository
from controllers.appointment_controller import AppointmentController
from views.dashboard_view import render_dashboard
from views.list_view import render_appointment_list
from views.form_view import render_appointment_form
from views.detail_view import render_appointment_detail
from data.seed import seed_if_empty


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AppointmentPro",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%);
        }
        [data-testid="stSidebar"] * { color: #E0E7FF !important; }
        [data-testid="stSidebar"] .stButton > button {
            background: transparent;
            border: 1px solid #4338CA40;
            border-radius: 8px;
            width: 100%;
            text-align: left;
            padding: 10px 14px;
            font-size: 0.95rem;
            transition: background 0.2s;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: #4338CA40 !important;
        }
        /* Active nav item */
        .nav-active button {
            background: #4338CA !important;
            border-color: #6366F1 !important;
        }
        /* Main area */
        .main .block-container { padding-top: 1.5rem; max-width: 1200px; }
        /* Cards */
        .stContainer { border-radius: 12px; }
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 8px !important;
        }
        /* Hide Streamlit branding */
        #MainMenu, footer { visibility: hidden; }
        header { visibility: hidden; }
        /* Success / error toast style */
        .stAlert { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Bootstrap MVC ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_controller() -> AppointmentController:
    """Singleton controller; cached so the repository isn't re-created each rerun."""
    repo = AppointmentRepository()
    seed_if_empty(repo)
    return AppointmentController(repo)


controller = get_controller()


# ── Session state defaults ────────────────────────────────────────────────────

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "dashboard"
if "edit_appt_id" not in st.session_state:
    st.session_state["edit_appt_id"] = None
if "view_appt_id" not in st.session_state:
    st.session_state["view_appt_id"] = None


# ── Sidebar Navigation ────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0 28px;">
            <div style="font-size:2.2rem;">📅</div>
            <div style="font-size:1.3rem; font-weight:700; margin-top:6px;">
                AppointmentPro
            </div>
            <div style="font-size:0.78rem; opacity:0.6; margin-top:2px;">
                Manage your schedule
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("<small style='opacity:0.5;'>NAVIGATION</small>", unsafe_allow_html=True)
    st.markdown("")

    nav_items = [
        ("dashboard", "📊  Dashboard"),
        ("list",      "📋  All Appointments"),
        ("new",       "➕  New Appointment"),
    ]

    for page_key, label in nav_items:
        is_active = st.session_state["active_page"] == page_key
        btn_style = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{page_key}", type=btn_style, use_container_width=True):
            st.session_state["active_page"]  = page_key
            st.session_state["edit_appt_id"] = None
            st.session_state["view_appt_id"] = None
            st.rerun()

    st.markdown("---")

    # Quick stats in sidebar
    stats = controller.get_dashboard_stats()
    st.markdown("<small style='opacity:0.5;'>QUICK STATS</small>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="font-size:0.85rem; line-height:2; opacity:0.85;">
            📋 Total: <b>{stats['total']}</b><br>
            📅 Today: <b>{stats['today']}</b><br>
            🔜 Upcoming: <b>{stats['upcoming']}</b><br>
            ✅ Completed: <b>{stats['completed']}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem; opacity:0.4; text-align:center;'>"
        "MVC Architecture · JSON Store"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Page Router ───────────────────────────────────────────────────────────────

page = st.session_state["active_page"]

if page == "dashboard":
    render_dashboard(controller)

elif page == "list":
    render_appointment_list(controller)

elif page == "new":
    render_appointment_form(controller, existing=None)

elif page == "edit":
    appt_id = st.session_state.get("edit_appt_id")
    if appt_id:
        appt = controller.get_by_id(appt_id)
        if appt:
            render_appointment_form(controller, existing=appt)
        else:
            st.error(f"Appointment `{appt_id}` not found.")
    else:
        st.warning("No appointment selected for editing.")
        st.session_state["active_page"] = "list"
        st.rerun()

elif page == "detail":
    appt_id = st.session_state.get("view_appt_id")
    if appt_id:
        render_appointment_detail(controller, appt_id)
    else:
        st.session_state["active_page"] = "list"
        st.rerun()

else:
    st.error(f"Unknown page: `{page}`")
