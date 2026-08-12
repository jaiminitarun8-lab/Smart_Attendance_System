from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import Timetable

router = APIRouter(prefix="/api/timetable", tags=["timetable"])


class TimetableGridRow(BaseModel):
    time: str
    Mon: str | None = None
    Tue: str | None = None
    Wed: str | None = None
    Thu: str | None = None
    Fri: str | None = None


class TimetableGridPayload(BaseModel):
    rows: list[TimetableGridRow]
    faculty_id: str | None = None


@router.get("/section/{section}")
def get_timetable(section: str, db: Session = Depends(get_db)):
    rows = db.query(Timetable).filter(Timetable.section == section).order_by(Timetable.sort_order).all()
    result = [
        {
            "time": r.time_slot,
            "Mon": r.monday or "—",
            "Tue": r.tuesday or "—",
            "Wed": r.wednesday or "—",
            "Thu": r.thursday or "—",
            "Fri": r.friday or "—",
        }
        for r in rows
    ]
    return {"success": True, "rows": result}


@router.put("/section/{section}")
def update_timetable(section: str, payload: TimetableGridPayload, db: Session = Depends(get_db)):
    db.query(Timetable).filter(Timetable.section == section).delete()

    for idx, grid_row in enumerate(payload.rows):
        time_slot = (grid_row.time or "").strip()
        if not time_slot:
            continue

        db.add(Timetable(
            section=section,
            time_slot=time_slot,
            monday=grid_row.Mon,
            tuesday=grid_row.Tue,
            wednesday=grid_row.Wed,
            thursday=grid_row.Thu,
            friday=grid_row.Fri,
            sort_order=idx,
        ))

    db.commit()
    return {"success": True, "message": "Timetable updated."}