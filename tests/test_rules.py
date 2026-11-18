from conftest import FRIDAY, SATURDAY, SUNDAY, at, booking
from roombook.rules import (
    BAD_LENGTH,
    DAILY_LIMIT_REACHED,
    NOT_ON_SLOT,
    OUTSIDE_HOURS,
    OVER_CAPACITY,
    OVERLAP,
    overlaps,
    validate_booking,
)


def test_overlaps_partial():
    assert overlaps(at(SUNDAY, "10:00"), at(SUNDAY, "11:00"), at(SUNDAY, "10:30"), at(SUNDAY, "11:30"))


def test_overlaps_with_gap_is_false():
    assert not overlaps(at(SUNDAY, "10:00"), at(SUNDAY, "11:00"), at(SUNDAY, "11:30"), at(SUNDAY, "12:00"))


def test_overlaps_containment():
    assert overlaps(at(SUNDAY, "09:00"), at(SUNDAY, "12:00"), at(SUNDAY, "10:00"), at(SUNDAY, "10:30"))


def test_valid_booking_has_no_errors(rooms):
    assert validate_booking(booking(), rooms[0], []) == []


def test_saturday_is_closed(rooms):
    assert OUTSIDE_HOURS in validate_booking(booking(day=SATURDAY), rooms[0], [])


def test_before_opening(rooms):
    assert OUTSIDE_HOURS in validate_booking(booking(start="07:30", end="08:30"), rooms[0], [])


def test_after_closing_on_weekday(rooms):
    assert OUTSIDE_HOURS in validate_booking(booking(start="21:30", end="22:30"), rooms[0], [])


def test_friday_morning_is_open(rooms):
    assert validate_booking(booking(day=FRIDAY, start="09:00", end="10:00"), rooms[0], []) == []


def test_too_short(rooms):
    assert BAD_LENGTH in validate_booking(booking(start="10:00", end="10:00"), rooms[0], [])


def test_too_long(rooms):
    assert BAD_LENGTH in validate_booking(booking(start="09:00", end="12:30"), rooms[0], [])


def test_must_start_on_half_hour(rooms):
    assert NOT_ON_SLOT in validate_booking(booking(start="10:15", end="11:15"), rooms[0], [])


def test_overlap_in_same_room(rooms):
    existing = [booking(id="old", student="s2", start="10:30", end="12:00")]
    assert OVERLAP in validate_booking(booking(), rooms[0], existing)


def test_same_time_other_room_is_fine(rooms):
    existing = [booking(id="old", room="R201", student="s2")]
    assert validate_booking(booking(), rooms[0], existing) == []


def test_cancelled_bookings_are_ignored(rooms):
    old = booking(id="old", student="s2")
    old.cancelled = True
    assert validate_booking(booking(), rooms[0], [old]) == []


def test_daily_limit_two_per_student(rooms):
    existing = [
        booking(id="a", room="R201", start="08:00", end="09:00"),
        booking(id="b", room="R201", start="13:00", end="14:00"),
    ]
    assert DAILY_LIMIT_REACHED in validate_booking(booking(start="16:00", end="17:00"), rooms[0], existing)


def test_over_capacity(rooms):
    assert OVER_CAPACITY in validate_booking(booking(size=5), rooms[0], [])
