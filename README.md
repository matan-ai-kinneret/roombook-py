# roombook · הזמנת חדרי לימוד בספריית כנרת

מאגר התרגול של סדנת **פיתוח תוכנה בעזרת Claude** (מתן פתרונות טכנולוגיים · Matan AI).
גרסת Python. גרסה זהה ב-TypeScript נמצאת במאגר `roombook-ts`.

## התקנה
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```
נדרש Python 3.11 ומעלה. בזמן ריצה אין תלויות חיצוניות.

## בדיקות ו-lint
```bash
pytest -q          # כל הבדיקות
ruff check .       # lint
```

## שימוש ב-CLI
```bash
roombook rooms
roombook list --room R101 --day 2026-12-06
roombook free --room R101 --day 2026-12-06 --minutes 60
roombook book --room R101 --student 315000111 --start 2026-12-06T12:00 --end 2026-12-06T13:00 --group 3
roombook cancel --id a1b2c3d4
```
בלי התקנה: `python -m roombook.cli rooms` (מתוך תיקיית `src`).

## מפת הפרויקט
```
src/roombook/
  models.py    Room, Booking
  rules.py     כללי R1–R5: opening_hours, overlaps, validate_booking
  service.py   BookingService: create / cancel / list / free_slots
  store.py     JsonStore (קבצים) ו-MemoryStore (בדיקות)
  cli.py       שורת הפקודה
data/          rooms.json, bookings.json — לא עורכים ידנית
tests/         pytest
docs/specs/    מפרטים. 0000 = כללי ההזמנה, TEMPLATE.md = תבנית למפרט חדש
docs/adr/      החלטות ארכיטקטורה
docs/issues/   משימות הסדנה (001–004)
```

## משימות הסדנה
| issue | מפגש | נושא |
| --- | --- | --- |
| 001 | 2 | באג: הזמנות צמודות נדחות |
| 002 | 2 (בונוס) | באג: שעות שישי |
| 003 | 4 | פיצ'ר: רשימת המתנה (מפרט + TDD) |
| 004 | 5 | פיצ'ר: הזמנה שבועית קבועה (בזוגות, PR) |

`CLAUDE.md.example` הוא שלד — במפגש 3 הופכים אותו ל-`CLAUDE.md` אמיתי.
