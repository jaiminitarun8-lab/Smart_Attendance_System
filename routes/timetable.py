class TimetableGridRow(BaseModel):
    time: str
    Mon: str | None = None
    Tue: str | None = None
    Wed: str | None = None
    Thu: str | None = None
    Fri: str | None = None


class TimetableGridPayload(BaseModel):
    rows: list[TimetableGridRow]
    faculty_id: str | None = None   # optional: teacher jo edit kar raha hai


@router.put("/section/{section}")
def update_timetable(section: str, payload: TimetableGridPayload, db: Session = Depends(get_db)):
    """Frontend Mon-Fri wide grid bhejta hai ({"rows": [{"time": "...", "Mon": "...", ...}]}).
    Hum use row-per-day format me convert karke DB me daalte hain — GET /section/{section}
    isi data ko wapas grid me assemble karta hai, isliye dono functions mirror hain.

    Poore section ka purana timetable delete karke naya insert kiya jaata hai, taaki
    edit me hataye gaye ya khaali chhode gaye periods bhi DB se remove ho jaayein."""
    db.query(Timetable).filter(Timetable.section == section).delete()

    for grid_row in payload.rows:
        time_slot = (grid_row.time or "").strip()
        if not time_slot:
            continue

        for day in DAY_ORDER[:5]:  # Mon..Fri
            subject = (getattr(grid_row, day) or "").strip()
            if not subject or subject == "—":
                continue

            db.add(Timetable(
                section=section,
                day=day,
                time_slot=time_slot,
                subject=subject,
                faculty_id=payload.faculty_id,
            ))

    db.commit()
    return {"success": True, "message": "Timetable updated."}
