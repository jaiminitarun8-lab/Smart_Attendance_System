from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Timetable

router = APIRouter(prefix="/api/timetable", tags=["timetable"])

DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri"]


class TimetableRow(BaseModel):
    section: str
    time_slot: str
    monday: str | None = None
    tuesday: str | None = None
    wednesday: str | None = None
    thursday: str | None = None
    friday: str | None = None
    sort_order: int | None = None


class TimetableUpdate(BaseModel):
    section: str | None = None
    time_slot: str | None = None
    monday: str | None = None
    tuesday: str | None = None
    wednesday: str | None = None
    thursday: str | None = None
    friday: str | None = None
    sort_order: int | None = None


def _time_sort_key(time_slot: str):
    try:
        from datetime import datetime
        return datetime.strptime(time_slot.strip(), "%I:%M %p")
    except ValueError:
        return time_slot


@router.get("/section/{section}")
def get_timetable(section: str, db: Session = Depends(get_db)):
    rows = db.query(Timetable).filter(Timetable.section == section).all()

    rows = sorted(rows, key=lambda row: (
        row.sort_order if row.sort_order is not None else 0,
        _time_sort_key(row.time_slot),
    ))

    result_rows = [
        {
            "id": row.id,
            "time": row.time_slot,
            "Mon": row.monday or "—",
            "Tue": row.tuesday or "—",
            "Wed": row.wednesday or "—",
            "Thu": row.thursday or "—",
            "Fri": row.friday or "—",
        }
        for row in rows
    ]

    return {"success": True, "rows": result_rows}


@router.post("")
def add_row(data: TimetableRow, db: Session = Depends(get_db)):
    """Create or update a timetable row for a section + time slot."""
    existing = (
        db.query(Timetable)
        .filter(Timetable.section == data.section, Timetable.time_slot == data.time_slot)
        .first()
    )

    if existing:
        if data.monday is not None:
            existing.monday = data.monday
        if data.tuesday is not None:
            existing.tuesday = data.tuesday
        if data.wednesday is not None:
            existing.wednesday = data.wednesday
        if data.thursday is not None:
            existing.thursday = data.thursday
        if data.friday is not None:
            existing.friday = data.friday
        if data.sort_order is not None:
            existing.sort_order = data.sort_order
        db.commit()
        return {"success": True, "id": existing.id, "message": "Timetable row updated."}

    row = Timetable(
        section=data.section,
        time_slot=data.time_slot,
        monday=data.monday,
        tuesday=data.tuesday,
        wednesday=data.wednesday,
        thursday=data.thursday,
        friday=data.friday,
        sort_order=data.sort_order or 0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"success": True, "id": row.id, "message": "Timetable row added."}


@router.put("/{row_id}")
@router.patch("/{row_id}")
def update_row(row_id: int, data: TimetableUpdate, db: Session = Depends(get_db)):
    row = db.query(Timetable).filter(Timetable.id == row_id).first()
    if not row:
        return {"success": False, "message": "Row not found."}

    if data.section is not None:
        row.section = data.section
    if data.time_slot is not None:
        row.time_slot = data.time_slot
    if data.monday is not None:
        row.monday = data.monday
    if data.tuesday is not None:
        row.tuesday = data.tuesday
    if data.wednesday is not None:
        row.wednesday = data.wednesday
    if data.thursday is not None:
        row.thursday = data.thursday
    if data.friday is not None:
        row.friday = data.friday
    if data.sort_order is not None:
        row.sort_order = data.sort_order

    db.commit()
    return {"success": True, "id": row.id, "message": "Timetable row updated."}


@router.delete("/{row_id}")
def delete_row(row_id: int, db: Session = Depends(get_db)):
    row = db.query(Timetable).filter(Timetable.id == row_id).first()
    if not row:
        return {"success": False, "message": "Row not found."}
    db.delete(row)
    db.commit()
    return {"success": True}
