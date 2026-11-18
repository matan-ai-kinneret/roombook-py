"""Application service: create, cancel and query bookings."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

from .models import Booking, Room
from .rules import OVERLAP, SLOT_MINUTES, opening_hours, validate_booking


class BookingError(Exception):
    def __init__(self, codes: list[str]):
        super().__init__(", ".join(codes))
        self.codes = codes


class UnknownRoom(KeyError):
    pass


class BookingService:
    def __init__(self, store):
        self.store = store

    # ---- rooms ----
    def rooms(self) -> list[Room]:
        return self.store.load_rooms()

    def room(self, room_id: str) -> Room:
        for r in self.rooms():
            if r.id == room_id:
                return r
        raise UnknownRoom(room_id)

    # ---- bookings ----
    def create_booking(
        self,
        room_id: str,
        student_id: str,
        start: datetime,
        end: datetime,
        group_size: int = 1,
    ) -> Booking:
        room = self.room(room_id)
        existing = self.store.load_bookings()
        booking = Booking(
            id=uuid.uuid4().hex[:8],
            room_id=room_id,
            student_id=student_id,
            start=start,
            end=end,
            group_size=group_size,
        )
        errors = validate_booking(booking, room, existing, group_size)
        if errors:
            raise BookingError(errors)
        existing.append(booking)
        self.store.save_bookings(existing)
        return booking

    def cancel_booking(self, booking_id: str) -> bool:
        bookings = self.store.load_bookings()
        for b in bookings:
            if b.id == booking_id and not b.cancelled:
                b.cancelled = True
                self.store.save_bookings(bookings)
                return True
        return False

    def list_bookings(self, room_id: str, day: date) -> list[Booking]:
        return sorted(
            (
                b
                for b in self.store.load_bookings()
                if b.room_id == room_id and b.day == day and not b.cancelled
            ),
            key=lambda b: b.start,
        )

    def free_slots(self, room_id: str, day: date, minutes: int) -> list[tuple[datetime, datetime]]:
        """Every start time (30-minute steps) where a booking of `minutes` would not overlap."""
        self.room(room_id)
        hours = opening_hours(day)
        if hours is None:
            return []
        taken = self.list_bookings(room_id, day)
        start = datetime.combine(day, hours[0])
        close = datetime.combine(day, hours[1])
        length = timedelta(minutes=minutes)
        slots: list[tuple[datetime, datetime]] = []
        while start + length <= close:
            end = start + length
            probe = Booking("probe", room_id, "probe", start, end)
            codes = validate_booking(probe, self.room(room_id), taken)
            if OVERLAP not in codes:
                slots.append((start, end))
            start += timedelta(minutes=SLOT_MINUTES)
        return slots
