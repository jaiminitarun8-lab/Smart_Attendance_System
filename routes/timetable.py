from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import Timetable

router = APIRouter(prefix="/api/timetable", tags=["timetable"])


class TimetableRow(BaseModel):
    section: str
    time_slot: str
    monday: str = ""
    tuesday: str = ""
    wednesday: str = ""
    thursday: str = ""
    friday: str = ""
    sort_order: int = 0


@router.get("/section/{section}")
def get_timetable(section: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Timetable)
        .filter(Timetable.section == section)
        .order_by(Timetable.sort_order, Timetable.time_slot)
        .all()
    )
    return {
        "success": True,
        "rows": [
            {
                "time": r.time_slot,
                "Mon": r.monday or "—",
                "Tue": r.tuesday or "—",
                "Wed": r.wednesday or "—",
                "Thu": r.thursday or "—",
                "Fri": r.friday or "—",
            }
            for r in rows
        ],
    }


@router.post("")
def add_row(data: TimetableRow, db: Session = Depends(get_db)):
    """Faculty/admin ek naya timetable row add kare (abhi UI form nahi hai, /docs se test kar sakte ho)."""
    row = Timetable(
        section=data.section,
        time_slot=data.time_slot,
        monday=data.monday,
        tuesday=data.tuesday,
        wednesday=data.wednesday,
        thursday=data.thursday,
        friday=data.friday,
        sort_order=data.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"success": True, "id": row.id}


@router.delete("/{row_id}")
def delete_row(row_id: int, db: Session = Depends(get_db)):
    row = db.query(Timetable).filter(Timetable.id == row_id).first()
    if not row:
        return {"success": False, "message": "Row not found."}
    db.delete(row)
    db.commit()
    return {"success": True}
