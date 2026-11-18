"""Domain models for roombook — study-room booking at the Kinneret library."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int
    floor: int
    has_screen: bool = False


@dataclass
class Booking:
    id: str
    room_id: str
    student_id: str
    start: datetime
    end: datetime
    group_size: int = 1
    cancelled: bool = field(default=False)

    @property
    def day(self):
        return self.start.date()

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "student_id": self.student_id,
            "start": self.start.isoformat(timespec="minutes"),
            "end": self.end.isoformat(timespec="minutes"),
            "group_size": self.group_size,
            "cancelled": self.cancelled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Booking:
        return cls(
            id=data["id"],
            room_id=data["room_id"],
            student_id=data["student_id"],
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            group_size=int(data.get("group_size", 1)),
            cancelled=bool(data.get("cancelled", False)),
        )
