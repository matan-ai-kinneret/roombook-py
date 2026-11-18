import json
from datetime import date

import pytest

from conftest import SATURDAY, SUNDAY, at, booking
from roombook import cli
from roombook.service import BookingError, UnknownRoom
from roombook.store import JsonStore


def test_create_booking_is_saved(service):
    b = service.create_booking("R101", "s1", at(SUNDAY, "10:00"), at(SUNDAY, "11:00"))
    assert [x.id for x in service.list_bookings("R101", date.fromisoformat(SUNDAY))] == [b.id]


def test_invalid_booking_raises_with_codes(service):
    with pytest.raises(BookingError) as err:
        service.create_booking("R101", "s1", at(SATURDAY, "10:00"), at(SATURDAY, "11:00"))
    assert "OUTSIDE_HOURS" in err.value.codes


def test_unknown_room(service):
    with pytest.raises(UnknownRoom):
        service.create_booking("R999", "s1", at(SUNDAY, "10:00"), at(SUNDAY, "11:00"))


def test_cancel_twice(service):
    b = service.create_booking("R101", "s1", at(SUNDAY, "10:00"), at(SUNDAY, "11:00"))
    assert service.cancel_booking(b.id) is True
    assert service.cancel_booking(b.id) is False
    assert service.list_bookings("R101", date.fromisoformat(SUNDAY)) == []


def test_list_is_sorted(service):
    service.create_booking("R101", "s1", at(SUNDAY, "15:00"), at(SUNDAY, "16:00"))
    service.create_booking("R101", "s2", at(SUNDAY, "09:00"), at(SUNDAY, "10:00"))
    starts = [b.start.strftime("%H:%M") for b in service.list_bookings("R101", date.fromisoformat(SUNDAY))]
    assert starts == ["09:00", "15:00"]


def test_free_slots_on_empty_day(service):
    slots = service.free_slots("R101", date.fromisoformat(SUNDAY), 60)
    assert slots[0][0].strftime("%H:%M") == "08:00"
    assert slots[-1][1].strftime("%H:%M") == "22:00"
    assert len(slots) == 27


def test_free_slots_skip_taken_time(service):
    service.create_booking("R101", "s1", at(SUNDAY, "10:00"), at(SUNDAY, "11:00"))
    starts = {s.strftime("%H:%M") for s, _ in service.free_slots("R101", date.fromisoformat(SUNDAY), 60)}
    assert "10:30" not in starts
    assert "13:00" in starts


def test_free_slots_saturday_closed(service):
    assert service.free_slots("R101", date.fromisoformat(SATURDAY), 60) == []


def test_json_store_round_trip(tmp_path, rooms):
    (tmp_path / "rooms.json").write_text(
        json.dumps([r.__dict__ for r in rooms], ensure_ascii=False), encoding="utf-8"
    )
    store = JsonStore(tmp_path)
    store.save_bookings([booking()])
    loaded = store.load_bookings()
    assert loaded[0].start == at(SUNDAY, "10:00")
    assert len(store.load_rooms()) == 3


def test_cli_book_and_list(tmp_path, rooms, capsys):
    (tmp_path / "rooms.json").write_text(
        json.dumps([r.__dict__ for r in rooms], ensure_ascii=False), encoding="utf-8"
    )
    data = str(tmp_path)
    code = cli.main(["--data", data, "book", "--room", "R101", "--student", "s1",
                     "--start", f"{SUNDAY}T10:00", "--end", f"{SUNDAY}T11:00"])
    assert code == 0
    cli.main(["--data", data, "list", "--room", "R101", "--day", SUNDAY])
    assert "10:00-11:00" in capsys.readouterr().out
