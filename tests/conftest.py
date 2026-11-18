from datetime import datetime

import pytest

from roombook.models import Booking, Room
from roombook.service import BookingService
from roombook.store import MemoryStore

SUNDAY = "2026-12-06"
FRIDAY = "2026-12-04"
SATURDAY = "2026-12-05"


def at(day: str, hhmm: str) -> datetime:
    return datetime.fromisoformat(f"{day}T{hhmm}")


@pytest.fixture
def rooms() -> list[Room]:
    return [
        Room("R101", "חדר 101", capacity=4, floor=1, has_screen=True),
        Room("R102", "חדר 102", capacity=2, floor=1),
        Room("R201", "חדר 201", capacity=8, floor=2, has_screen=True),
    ]


@pytest.fixture
def service(rooms) -> BookingService:
    return BookingService(MemoryStore(rooms=rooms))


def booking(id="b1", room="R101", student="s1", day=SUNDAY, start="10:00", end="11:00", size=1) -> Booking:
    return Booking(id, room, student, at(day, start), at(day, end), size)
