from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Student

router = APIRouter(prefix="/api/profile", tags=["profile"])


class StudentProfileUpdate(BaseModel):
    name: str
    email: str
    department: str | None = None
    phone: str | None = None


@router.get("/student/{student_id}")
def get_student_profile(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return {"success": False, "message": "Student not found."}

    return {
        "success": True,
        "profile": {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email or "",
            "department": student.department or "",
            "phone": student.phone or "",
        },
    }


@router.put("/student/{student_id}")
def update_student_profile(
    student_id: str,
    data: StudentProfileUpdate,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return {"success": False, "message": "Student not found."}

    student.name = data.name.strip() or student.name
    student.email = data.email.strip().lower() or student.email
    student.department = data.department.strip() if data.department else student.department
    student.phone = data.phone.strip() if data.phone else student.phone

    db.commit()
    db.refresh(student)

    return {
        "success": True,
        "message": "Profile updated successfully.",
        "profile": {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email or "",
            "department": student.department or "",
            "phone": student.phone or "",
        },
    }
