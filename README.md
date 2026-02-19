# 📅 AppointmentPro — MVC Streamlit App

A production-grade appointment management system built with **Streamlit** following a clean **Model–View–Controller (MVC)** architecture.

---

## 🏗 Architecture

```
appointment_app/
│
├── app.py                          # Entry point & page router (wires MVC)
│
├── models/                         # ── MODEL LAYER ──────────────────────
│   ├── appointment.py              #   Appointment dataclass + validator
│   └── repository.py              #   JSON-backed CRUD repository
│
├── controllers/                    # ── CONTROLLER LAYER ─────────────────
│   └── appointment_controller.py  #   Business logic & orchestration
│
├── views/                          # ── VIEW LAYER ───────────────────────
│   ├── dashboard_view.py           #   KPI cards + today/upcoming panels
│   ├── list_view.py                #   Searchable / filterable table
│   ├── form_view.py                #   Create & Edit form (shared)
│   └── detail_view.py             #   Full appointment detail panel
│
├── data/
│   ├── seed.py                     #   Demo data seeder
│   └── appointments.json           #   Auto-created JSON datastore
│
└── requirements.txt
```

### Layer Responsibilities

| Layer | Files | Responsibility |
|---|---|---|
| **Model** | `appointment.py`, `repository.py` | Data structure, validation rules, persistence I/O |
| **Controller** | `appointment_controller.py` | Business logic, conflict detection, orchestration |
| **View** | `dashboard_view.py`, `list_view.py`, `form_view.py`, `detail_view.py` | Rendering only — calls controller, never touches repo directly |

---

## ✨ Features

- **Dashboard** — KPI cards (total / scheduled / completed / cancelled / no-show), today's schedule, upcoming appointments, status breakdown bar chart
- **Appointment List** — full-text search, status filter, date-range filter, sort by date / client / status / title, inline edit / complete / delete
- **Create / Edit Form** — real-time duration preview, 15-minute time slot picker, validation with inline error messages
- **Detail View** — full appointment summary with quick-action buttons
- **Business Rules** — time-overlap conflict detection, minimum 15-minute duration, email format validation
- **Demo Data** — 10 seed appointments auto-inserted on first run
- **Persistent Storage** — JSON file-based (swap to SQLite/PostgreSQL by replacing `repository.py` only)

---

## 🚀 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501** and pre-populates with 10 demo appointments.

---

## 🔄 Extending the App

### Swap the datastore
Replace `models/repository.py` with a SQLAlchemy / SQLite version.
The controller and views require **zero changes**.

### Add a new view
Create `views/my_view.py`, import it in `app.py`, and add a nav item in the sidebar.

### Add business rules
Modify `controllers/appointment_controller.py` — no view or model changes needed.

---

## 🧱 MVC Data Flow

```
User Action (Streamlit widget)
        ↓
    View calls Controller method
        ↓
    Controller validates + applies business rules
        ↓
    Controller calls Repository (Model)
        ↓
    Repository reads/writes JSON
        ↓
    Controller returns result dict to View
        ↓
    View renders success / error / data
```
