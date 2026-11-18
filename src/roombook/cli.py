"""Command line: roombook rooms | list | free | book | cancel."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from .service import BookingError, BookingService, UnknownRoom
from .store import JsonStore

MESSAGES = {
    "OUTSIDE_HOURS": "מחוץ לשעות הפתיחה של הספרייה",
    "BAD_LENGTH": "אורך הזמנה חייב להיות בין 30 דקות ל-3 שעות",
    "NOT_ON_SLOT": "הזמנה מתחילה ומסתיימת רק בחצאי שעות (‎:00 / ‎:30)",
    "OVERLAP": "החדר כבר תפוס בזמן הזה",
    "DAILY_LIMIT": "אפשר להחזיק עד 2 הזמנות ביום",
    "OVER_CAPACITY": "הקבוצה גדולה מקיבולת החדר",
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="roombook", description="הזמנת חדרי לימוד בספריית כנרת")
    p.add_argument("--data", default="data", help="תיקיית הנתונים (ברירת מחדל: data)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("rooms", help="רשימת חדרים")

    ls = sub.add_parser("list", help="הזמנות לחדר ביום")
    ls.add_argument("--room", required=True)
    ls.add_argument("--day", required=True, help="YYYY-MM-DD")

    fr = sub.add_parser("free", help="חלונות פנויים")
    fr.add_argument("--room", required=True)
    fr.add_argument("--day", required=True)
    fr.add_argument("--minutes", type=int, default=60)

    bk = sub.add_parser("book", help="הזמנה חדשה")
    bk.add_argument("--room", required=True)
    bk.add_argument("--student", required=True)
    bk.add_argument("--start", required=True, help="YYYY-MM-DDTHH:MM")
    bk.add_argument("--end", required=True, help="YYYY-MM-DDTHH:MM")
    bk.add_argument("--group", type=int, default=1)

    cn = sub.add_parser("cancel", help="ביטול הזמנה")
    cn.add_argument("--id", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    svc = BookingService(JsonStore(args.data))
    try:
        if args.cmd == "rooms":
            for r in svc.rooms():
                screen = "מסך" if r.has_screen else "—"
                print(f"{r.id}\t{r.name}\tקומה {r.floor}\tעד {r.capacity}\t{screen}")
        elif args.cmd == "list":
            for b in svc.list_bookings(args.room, date.fromisoformat(args.day)):
                print(f"{b.id}\t{b.start:%H:%M}-{b.end:%H:%M}\t{b.student_id}\t{b.group_size}")
        elif args.cmd == "free":
            for s, e in svc.free_slots(args.room, date.fromisoformat(args.day), args.minutes):
                print(f"{s:%H:%M}-{e:%H:%M}")
        elif args.cmd == "book":
            b = svc.create_booking(
                args.room,
                args.student,
                datetime.fromisoformat(args.start),
                datetime.fromisoformat(args.end),
                args.group,
            )
            print(f"נקבע: {b.id} · {b.room_id} · {b.start:%d/%m %H:%M}-{b.end:%H:%M}")
        elif args.cmd == "cancel":
            print("בוטל" if svc.cancel_booking(args.id) else "לא נמצאה הזמנה פעילה עם המזהה הזה")
    except BookingError as err:
        for code in err.codes:
            print(f"שגיאה {code}: {MESSAGES.get(code, code)}", file=sys.stderr)
        return 2
    except UnknownRoom as err:
        print(f"חדר לא קיים: {err.args[0]}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
