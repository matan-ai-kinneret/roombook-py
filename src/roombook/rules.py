"""Booking rules R1–R5. See docs/specs/0000-booking-rules.md."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, time

from .models import Booking, Room

SLOT_MINUTES = 30
MIN_MINUTES = 30
MAX_MINUTES = 180
DAILY_LIMIT = 2

OUTSIDE_HOURS = "OUTSIDE_HOURS"
BAD_LENGTH = "BAD_LENGTH"
NOT_ON_SLOT = "NOT_ON_SLOT"
OVERLAP = "OVERLAP"
DAILY_LIMIT_REACHED = "DAILY_LIMIT"
OVER_CAPACITY = "OVER_CAPACITY"

SATURDAY = 5  # date.weekday(): Monday=0 ... Sunday=6


def opening_hours(day: date) -> tuple[time, time] | None:
    """Return (open, close) for a day, or None when the library is closed (R1)."""
    if day.weekday() == SATURDAY:
        return None
    return (time(8, 0), time(22, 0))


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """True when two time ranges share at least one minute (R3)."""
    return a_start <= b_end and b_start <= a_end


def _on_slot(moment: datetime) -> bool:
    return moment.minute % SLOT_MINUTES == 0 and moment.second == 0 and moment.microsecond == 0


def validate_booking(
    booking: Booking,
    room: Room,
    existing: Iterable[Booking],
    group_size: int | None = None,
) -> list[str]:
    """Return a list of error codes. An empty list means the booking is valid."""
    errors: list[str] = []
    size = booking.group_size if group_size is None else group_size

    # R1 — opening hours
    hours = opening_hours(booking.start.date())
    if (
        hours is None
        or booking.end.date() != booking.start.date()
        or booking.start.time() < hours[0]
        or booking.end.time() > hours[1]
    ):
        errors.append(OUTSIDE_HOURS)

    # R2 — length and 30-minute boundaries
    if booking.end <= booking.start or not (MIN_MINUTES <= booking.minutes <= MAX_MINUTES):
        errors.append(BAD_LENGTH)
    if not (_on_slot(booking.start) and _on_slot(booking.end)):
        errors.append(NOT_ON_SLOT)

    active = [b for b in existing if not b.cancelled and b.id != booking.id]

    # R3 — no overlap in the same room
    if any(
        b.room_id == booking.room_id and overlaps(booking.start, booking.end, b.start, b.end)
        for b in active
    ):
        errors.append(OVERLAP)

    # R4 — at most two bookings per student per day
    same_day = [b for b in active if b.student_id == booking.student_id and b.day == booking.day]
    if len(same_day) >= DAILY_LIMIT:
        errors.append(DAILY_LIMIT_REACHED)

    # R5 — capacity
    if size > room.capacity:
        errors.append(OVER_CAPACITY)

    return errors
