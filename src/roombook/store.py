"""Storage. JSON files on disk (see docs/adr/0001-json-file-storage.md) and an in-memory store for tests."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Booking, Room


class MemoryStore:
    def __init__(self, rooms: list[Room] | None = None, bookings: list[Booking] | None = None):
        self._rooms = list(rooms or [])
        self._bookings = list(bookings or [])

    def load_rooms(self) -> list[Room]:
        return list(self._rooms)

    def load_bookings(self) -> list[Booking]:
        return list(self._bookings)

    def save_bookings(self, bookings: list[Booking]) -> None:
        self._bookings = list(bookings)


class JsonStore:
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self.rooms_path = self.data_dir / "rooms.json"
        self.bookings_path = self.data_dir / "bookings.json"

    def load_rooms(self) -> list[Room]:
        raw = json.loads(self.rooms_path.read_text(encoding="utf-8"))
        return [Room(**r) for r in raw]

    def load_bookings(self) -> list[Booking]:
        if not self.bookings_path.exists():
            return []
        raw = json.loads(self.bookings_path.read_text(encoding="utf-8") or "[]")
        return [Booking.from_dict(b) for b in raw]

    def save_bookings(self, bookings: list[Booking]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = [b.to_dict() for b in bookings]
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        self.bookings_path.write_text(text, encoding="utf-8")
