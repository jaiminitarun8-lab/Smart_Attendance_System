from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import Timetable

router = APIRouter(prefix="/api/timetable", tags=["timetable"])

DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class TimetableRow(BaseModel):
    section: str
    day: str            # "Mon" / "Tue" / "Wed" / "Thu" / "Fri"
    time_slot: str
    subject: str
    faculty_id: str | None = None


@router.get("/section/{section}")
def get_timetable(section: str, db: Session = Depends(get_db)):
    """attendance.db me timetable row-per-day format me stored hai
    (section, day, time_slot, subject, faculty_id) — is function ka kaam
    unhe time_slot ke hisaab se group karke Mon..Fri wide grid banana hai,
    jaisa frontend expect karta hai."""
    rows = db.query(Timetable).filter(Timetable.section == section).all()

    # time_slot -> {"Mon": subject, "Tue": subject, ...}
    grid: dict[str, dict[str, str]] = {}
    for r in rows:
        if r.time_slot not in grid:
            grid[r.time_slot] = {}
        grid[r.time_slot][r.day] = r.subject

    def sort_key(time_slot: str):
        # "9:00 AM" jaise strings ko sahi time order me sort karne ke liye
        try:
            from datetime import datetime
            return datetime.strptime(time_slot.strip(), "%I:%M %p")
        except ValueError:
            return time_slot

    sorted_slots = sorted(grid.keys(), key=sort_key)

    result_rows = [
        {
            "time": slot,
            "Mon": grid[slot].get("Mon", "—"),
            "Tue": grid[slot].get("Tue", "—"),
            "Wed": grid[slot].get("Wed", "—"),
            "Thu": grid[slot].get("Thu", "—"),
            "Fri": grid[slot].get("Fri", "—"),
        }
        for slot in sorted_slots
    ]

    return {"success": True, "rows": result_rows}


@router.post("")
def add_row(data: TimetableRow, db: Session = Depends(get_db)):
    """Ek naya (section, day, time_slot) ka period add/update kare.
    Agar wahi section+day+time_slot pehle se hai to subject overwrite ho jayega
    (duplicate periods na banein isliye)."""
    existing = (
        db.query(Timetable)
        .filter(
            Timetable.section == data.section,
            Timetable.day == data.day,
            Timetable.time_slot == data.time_slot,
        )
        .first()
    )

    if existing:
        existing.subject = data.subject
        existing.faculty_id = data.faculty_id
        db.commit()
        return {"success": True, "id": existing.id, "message": "Period updated."}

    row = Timetable(
        section=data.section,
        day=data.day,
        time_slot=data.time_slot,
        subject=data.subject,
        faculty_id=data.faculty_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"success": True, "id": row.id, "message": "Period added."}


@router.delete("/{row_id}")
def delete_row(row_id: int, db: Session = Depends(get_db)):
    row = db.query(Timetable).filter(Timetable.id == row_id).first()
    if not row:
        return {"success": False, "message": "Row not found."}
    db.delete(row)
    db.commit()
    return {"success": True}
