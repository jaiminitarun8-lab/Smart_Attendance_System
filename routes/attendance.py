from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date as date_type

from database.connection import get_db
from database.models import Attendance, Notification

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

LOW_ATTENDANCE_THRESHOLD = 75  # % ke neeche jaane pe warning bhejni hai


class AttendanceMark(BaseModel):
    user_id: str          # student_id ya faculty_id
    user_type: str          # "student" ya "faculty"
    subject: str
    date: date_type
    status: str              # "present" / "absent"
    marked_by: str = "manual"   # "manual" ya "ai_face_recognition"


def _check_and_notify_low_attendance(db: Session, user_id: str, user_type: str):
    total = db.query(Attendance).filter(Attendance.user_id == user_id).count()
    if total == 0:
        return
    present = db.query(Attendance).filter(Attendance.user_id == user_id, Attendance.status == "present").count()
    percentage = round((present / total) * 100, 1)

    if percentage < LOW_ATTENDANCE_THRESHOLD:
        # Bar-bar notification na bheje isliye check karo ki aaj already bheji ja chuki hai ya nahi
        from sqlalchemy import func as sa_func
        today_notif = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.title.like("Your attendance has dropped%"),
            sa_func.date(Notification.created_at) == date_type.today(),
        ).first()
        if not today_notif:
            db.add(Notification(
                user_id=user_id,
                user_type=user_type,
                title=f"Your attendance has dropped to {percentage}% — stay above {LOW_ATTENDANCE_THRESHOLD}%!",
            ))
            db.commit()


@router.post("/mark")
def mark_attendance(data: AttendanceMark, db: Session = Depends(get_db)):
    record = Attendance(
        user_id=data.user_id,
        user_type=data.user_type,
        subject=data.subject,
        date=data.date,
        status=data.status,
        marked_by=data.marked_by,
    )
    db.add(record)
    db.commit()

    if data.user_type == "student":
        _check_and_notify_low_attendance(db, data.user_id, data.user_type)

    return {"success": True, "message": "Attendance marked."}
