from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date as date_type, timedelta

from database.connection import get_db
from database.models import Attendance, Student

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


class MarkOne(BaseModel):
    user_id: str
    user_type: str = "student"
    subject: str
    date: date_type
    status: str          # "present" / "absent"


class MarkRecord(BaseModel):
    student_id: str
    status: str


class MarkBulk(BaseModel):
    section: str
    subject: str
    date: date_type
    records: list[MarkRecord]
    marked_by: str = "manual"   # "manual" ya "ai_face_recognition" — teammate isi field ko use karega


def _upsert(db: Session, user_id: str, user_type: str, subject: str, date_val, status: str, marked_by: str = "manual"):
    existing = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            Attendance.subject == subject,
            Attendance.date == date_val,
        )
        .first()
    )
    if existing:
        existing.status = status
        existing.marked_by = marked_by
        return existing

    record = Attendance(
        user_id=user_id, user_type=user_type, subject=subject,
        date=date_val, status=status, marked_by=marked_by,
    )
    db.add(record)
    return record


@router.post("/mark")
def mark_one(data: MarkOne, db: Session = Depends(get_db)):
    _upsert(db, data.user_id, data.user_type, data.subject, data.date, data.status)
    db.commit()
    return {"success": True, "message": "Attendance marked."}


@router.post("/mark-bulk")
def mark_bulk(data: MarkBulk, db: Session = Depends(get_db)):
    """Faculty ek saath poore section ka attendance mark kare."""
    for rec in data.records:
        _upsert(db, rec.student_id, "student", data.subject, data.date, rec.status, data.marked_by)
    db.commit()
    return {"success": True, "message": f"{len(data.records)} students marked.", "count": len(data.records)}


@router.get("/section/{section}/today")
def get_section_today(section: str, subject: str = "General", db: Session = Depends(get_db)):
    """Faculty roster — aaj ke liye har student ka status (mark hua ya pending)."""
    today = date_type.today()
    students = db.query(Student).filter(Student.section == section).all()

    today_records = {
        r.user_id: r.status
        for r in db.query(Attendance).filter(
            Attendance.date == today, Attendance.subject == subject,
            Attendance.user_id.in_([s.student_id for s in students]) if students else False,
        ).all()
    }

    roster = [
        {
            "student_id": s.student_id,
            "name": s.name,
            "roll_no": s.roll_no,
            "status": today_records.get(s.student_id, "pending"),
        }
        for s in students
    ]
    return {"success": True, "date": today.isoformat(), "roster": roster}


@router.get("/section/{section}/summary")
def get_section_summary(section: str, db: Session = Depends(get_db)):
    """Faculty dashboard stat cards — students present/absent today, avg attendance."""
    today = date_type.today()
    students = db.query(Student).filter(Student.section == section).all()
    student_ids = [s.student_id for s in students]
    total_students = len(student_ids)

    if not student_ids:
        return {"success": True, "present_today": 0, "absent_today": 0, "total_students": 0, "avg_attendance_pct": 0}

    today_records = db.query(Attendance).filter(
        Attendance.date == today, Attendance.user_id.in_(student_ids)
    ).all()
    present_today = sum(1 for r in today_records if r.status == "present")
    absent_today = sum(1 for r in today_records if r.status == "absent")

    thirty_days_ago = today - timedelta(days=30)
    recent_records = db.query(Attendance).filter(
        Attendance.user_id.in_(student_ids), Attendance.date >= thirty_days_ago
    ).all()
    total_marks = len(recent_records)
    present_marks = sum(1 for r in recent_records if r.status == "present")
    avg_pct = round((present_marks / total_marks) * 100) if total_marks else 0

    return {
        "success": True,
        "present_today": present_today,
        "absent_today": absent_today,
        "total_students": total_students,
        "avg_attendance_pct": avg_pct,
    }


@router.get("/student/{student_id}/summary")
def get_student_summary(student_id: str, db: Session = Depends(get_db)):
    """Student dashboard/reports — This month %, present/absent days, weekly bars."""
    today = date_type.today()
    all_records = db.query(Attendance).filter(Attendance.user_id == student_id).order_by(Attendance.date).all()

    total = len(all_records)
    present = sum(1 for r in all_records if r.status == "present")
    absent = sum(1 for r in all_records if r.status == "absent")
    pct = round((present / total) * 100) if total else 0

    week_start = today - timedelta(days=today.weekday())  # Monday
    week_map = {(week_start + timedelta(days=i)).isoformat(): 0 for i in range(7)}
    for r in all_records:
        key = r.date.isoformat()
        if key in week_map and r.status == "present":
            week_map[key] = 100

    weekly = list(week_map.values())

    recent = all_records[-5:][::-1]
    recent_log = [{"subject": r.subject, "date": r.date.isoformat(), "status": r.status} for r in recent]

    return {
        "success": True,
        "total_classes": total,
        "present_days": present,
        "absent_days": absent,
        "percentage": pct,
        "weekly": weekly,
        "recent_log": recent_log,
    }


def _month_label(d: date_type) -> str:
    return d.strftime("%B")   # "March", "April" ...


def _monthly_breakdown(records: list) -> dict:
    """Common helper — records ko month-wise group karke present/absent/rate nikalta hai."""
    by_month = {}   # "2026-03" -> {"present": n, "absent": n, "order": date}
    for r in records:
        key = r.date.strftime("%Y-%m")
        if key not in by_month:
            by_month[key] = {"present": 0, "absent": 0, "order": r.date.replace(day=1)}
        if r.status == "present":
            by_month[key]["present"] += 1
        elif r.status == "absent":
            by_month[key]["absent"] += 1

    sorted_months = sorted(by_month.items(), key=lambda kv: kv[1]["order"])

    months = []
    total_present = 0
    total_absent = 0
    best_rate = 0
    for _, m in sorted_months:
        total = m["present"] + m["absent"]
        rate = round((m["present"] / total) * 100) if total else 0
        best_rate = max(best_rate, rate)
        months.append({
            "month": _month_label(m["order"]),
            "present": m["present"],
            "absent": m["absent"],
            "rate": rate,
        })
        total_present += m["present"]
        total_absent += m["absent"]

    overall_total = total_present + total_absent
    overall_pct = round((total_present / overall_total) * 100) if overall_total else 0

    return {
        "months": months,
        "present_days": total_present,
        "absent_days": total_absent,
        "overall_pct": overall_pct,
        "best_rate": best_rate,
    }


@router.get("/student/{student_id}/monthly")
def get_student_monthly(student_id: str, db: Session = Depends(get_db)):
    """Student Reports page — month-wise breakdown."""
    records = db.query(Attendance).filter(Attendance.user_id == student_id).order_by(Attendance.date).all()
    return {"success": True, **_monthly_breakdown(records)}


@router.get("/section/{section}/monthly")
def get_section_monthly(section: str, db: Session = Depends(get_db)):
    """Faculty Reports page — month-wise breakdown across the whole section."""
    students = db.query(Student).filter(Student.section == section).all()
    student_ids = [s.student_id for s in students]
    if not student_ids:
        return {"success": True, "months": [], "present_days": 0, "absent_days": 0, "overall_pct": 0, "best_rate": 0}

    records = db.query(Attendance).filter(Attendance.user_id.in_(student_ids)).order_by(Attendance.date).all()
    return {"success": True, **_monthly_breakdown(records)}
