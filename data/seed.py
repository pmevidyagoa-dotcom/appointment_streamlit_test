"""
data/seed.py
------------
Populates the repository with demo appointments so the app
is immediately useful when first launched.
"""

from datetime import date, time, timedelta, datetime
from models.appointment import Appointment, AppointmentStatus
from models.repository import AppointmentRepository


SEEDS = [
    {
        "id": "A001",
        "title": "Annual Physical Exam",
        "client_name": "Alice Johnson",
        "client_email": "alice@example.com",
        "client_phone": "+1 555 100 2001",
        "date": (date.today() + timedelta(days=1)).isoformat(),
        "start_time": "09:00",
        "end_time": "10:00",
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Bring previous lab results. Fasting required.",
    },
    {
        "id": "A002",
        "title": "Product Strategy Review",
        "client_name": "Bob Martinez",
        "client_email": "bob.m@acme.com",
        "client_phone": "+1 555 200 3002",
        "date": (date.today() + timedelta(days=2)).isoformat(),
        "start_time": "14:00",
        "end_time": "15:30",
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Review Q3 roadmap and discuss feature prioritisation.",
    },
    {
        "id": "A003",
        "title": "Tax Consultation",
        "client_name": "Carol White",
        "client_email": "carol.white@gmail.com",
        "client_phone": "+1 555 300 4003",
        "date": date.today().isoformat(),
        "start_time": "11:00",
        "end_time": "12:00",
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Bring 2024 W-2 and investment statements.",
    },
    {
        "id": "A004",
        "title": "Dental Cleaning",
        "client_name": "David Lee",
        "client_email": "david.lee@email.com",
        "client_phone": "+1 555 400 5004",
        "date": (date.today() - timedelta(days=3)).isoformat(),
        "start_time": "10:00",
        "end_time": "10:45",
        "status": AppointmentStatus.COMPLETED,
        "notes": "Follow-up: recommend whitening treatment.",
    },
    {
        "id": "A005",
        "title": "Legal Advice - Contract Review",
        "client_name": "Emma Davis",
        "client_email": "emma.davis@corp.io",
        "client_phone": "+1 555 500 6005",
        "date": (date.today() - timedelta(days=7)).isoformat(),
        "start_time": "15:00",
        "end_time": "16:00",
        "status": AppointmentStatus.COMPLETED,
        "notes": "NDA and service agreement reviewed. Sent amended copy.",
    },
    {
        "id": "A006",
        "title": "Career Coaching Session",
        "client_name": "Frank Brown",
        "client_email": "frank.b@hotmail.com",
        "client_phone": "+1 555 600 7006",
        "date": (date.today() - timedelta(days=2)).isoformat(),
        "start_time": "13:00",
        "end_time": "14:00",
        "status": AppointmentStatus.CANCELLED,
        "notes": "Client cancelled due to illness. Reschedule next week.",
    },
    {
        "id": "A007",
        "title": "Home Inspection Follow-up",
        "client_name": "Grace Kim",
        "client_email": "grace.kim@realty.com",
        "client_phone": "+1 555 700 8007",
        "date": (date.today() - timedelta(days=5)).isoformat(),
        "start_time": "09:30",
        "end_time": "10:30",
        "status": AppointmentStatus.NO_SHOW,
        "notes": "Client did not show. Third missed appointment.",
    },
    {
        "id": "A008",
        "title": "Personal Training Session",
        "client_name": "Henry Wilson",
        "client_email": "henry.w@fitlife.com",
        "client_phone": "+1 555 800 9008",
        "date": (date.today() + timedelta(days=3)).isoformat(),
        "start_time": "07:00",
        "end_time": "08:00",
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Focus on strength training. Adjust lower-back program.",
    },
    {
        "id": "A009",
        "title": "Marketing Campaign Kickoff",
        "client_name": "Iris Chang",
        "client_email": "iris.chang@brand.co",
        "client_phone": "+1 555 900 0009",
        "date": (date.today() + timedelta(days=5)).isoformat(),
        "start_time": "10:00",
        "end_time": "11:30",
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Present Q4 social media plan and influencer budget.",
    },
    {
        "id": "A010",
        "title": "Therapy Session",
        "client_name": "James Carter",
        "client_email": "james.c@personal.me",
        "client_phone": "+1 555 010 1110",
        "date": date.today().isoformat(),
        "start_time": "16:00",
        "end_time": "17:00",
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Bi-weekly check-in. Discuss progress on anxiety management.",
    },
]


def seed_if_empty(repo: AppointmentRepository) -> int:
    """Insert seed data only if the repository is empty. Returns count inserted."""
    if repo.get_all():
        return 0  # Already has data

    count = 0
    for seed in SEEDS:
        appt = Appointment(
            id           = seed["id"],
            title        = seed["title"],
            client_name  = seed["client_name"],
            client_email = seed["client_email"],
            client_phone = seed["client_phone"],
            date         = date.fromisoformat(seed["date"]),
            start_time   = time.fromisoformat(seed["start_time"]),
            end_time     = time.fromisoformat(seed["end_time"]),
            status       = seed["status"],
            notes        = seed.get("notes", ""),
            created_at   = datetime.now(),
            updated_at   = datetime.now(),
        )
        repo.create(appt)
        count += 1

    return count
