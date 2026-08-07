from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date as date_type

from database.connection import get_db
from database.models import Leave, Student, Notification

router = APIRouter(prefix="/api/leave", tags=["leave"])


class LeaveCreate(BaseModel):
    user_id: str          # student_id ya faculty_id
    user_type: str         # "student" ya "faculty"
    start_date: date_type
    end_date: date_type
    reason: str


class LeaveDecision(BaseModel):
    decided_by: str = "faculty"   # abhi ke liye simple audit field


def _serialize(lv: Leave, student_name: str = None, student_meta: dict = None):
    data = {
        "id": lv.id,
        "user_id": lv.user_id,
        "user_type": lv.user_type,
        "student_name": student_name,
        "start_date": lv.start_date.isoformat() if lv.start_date else None,
        "end_date": lv.end_date.isoformat() if lv.end_date else None,
        "reason": lv.reason,
        "status": lv.status,
        "created_at": lv.created_at.isoformat() if lv.created_at else None,
    }
    if student_meta:
        data.update(student_meta)
    return data


@router.get("/student/{student_id}")
def get_student_leaves(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    student_meta = None
    if student:
        student_meta = {
            "section": student.section,
            "class_name": student.class_name,
            "department": student.department,
        }

    leaves = (
        db.query(Leave)
        .filter(Leave.user_id == student_id, Leave.user_type == "student")
        .order_by(Leave.created_at.desc())
        .all()
    )

    total = len(leaves)
    approved = sum(1 for lv in leaves if lv.status == "approved")
    pending = sum(1 for lv in leaves if lv.status == "pending")
    rejected = sum(1 for lv in leaves if lv.status == "rejected")

    return {
        "success": True,
        "leaves": [_serialize(lv, student_meta=student_meta) for lv in leaves],
        "summary": {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
        },
    }


@router.get("/section/{section}")
def get_section_leaves(section: str, db: Session = Depends(get_db)):
    """Faculty view — sabhi leave requests jo iss section ke students ne bheji hain."""
    students = db.query(Student).filter(Student.section == section).all()
    student_map = {
        s.student_id: {
            "student_name": s.name,
            "section": s.section,
            "class_name": s.class_name,
            "department": s.department,
        }
        for s in students
    }
    if not student_map:
        return {"success": True, "leaves": [], "summary": {"total": 0, "approved": 0, "pending": 0, "rejected": 0}}

    leaves = (
        db.query(Leave)
        .filter(Leave.user_type == "student", Leave.user_id.in_(student_map.keys()))
        .order_by(Leave.created_at.desc())
        .all()
    )

    total = len(leaves)
    approved = sum(1 for lv in leaves if lv.status == "approved")
    pending = sum(1 for lv in leaves if lv.status == "pending")
    rejected = sum(1 for lv in leaves if lv.status == "rejected")

    result = []
    for lv in leaves:
        meta = student_map.get(lv.user_id, {})
        result.append(_serialize(lv, student_name=meta.get("student_name"), student_meta={
            "section": meta.get("section"),
            "class_name": meta.get("class_name"),
            "department": meta.get("department"),
        }))

    return {
        "success": True,
        "leaves": result,
        "summary": {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
        },
    }


@router.post("")
def apply_leave(data: LeaveCreate, db: Session = Depends(get_db)):
    leave = Leave(
        user_id=data.user_id,
        user_type=data.user_type,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason,
        status="pending",
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return {"success": True, "id": leave.id, "leave": _serialize(leave)}


@router.post("/{leave_id}/approve")
def approve_leave(leave_id: int, data: LeaveDecision, db: Session = Depends(get_db)):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        return {"success": False, "message": "Leave request not found."}
    leave.status = "approved"
    db.add(Notification(
        user_id=leave.user_id,
        user_type=leave.user_type,
        title=f"Your leave request ({leave.start_date}) was approved",
    ))
    db.commit()
    return {"success": True, "message": "Leave approved.", "leave": _serialize(leave)}


@router.post("/{leave_id}/reject")
def reject_leave(leave_id: int, data: LeaveDecision, db: Session = Depends(get_db)):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        return {"success": False, "message": "Leave request not found."}
    leave.status = "rejected"
    db.add(Notification(
        user_id=leave.user_id,
        user_type=leave.user_type,
        title=f"Your leave request ({leave.start_date}) was rejected",
    ))
    db.commit()
    return {"success": True, "message": "Leave rejected.", "leave": _serialize(leave)}
