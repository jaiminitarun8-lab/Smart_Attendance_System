from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import datetime

from database.connection import get_db
from database.models import Student, Faculty
from utils.security import hash_password

router = APIRouter(prefix="/api/register", tags=["register"])


class StudentRegister(BaseModel):
    name: str
    email: str
    password: str
    college_id: str


class FacultyRegister(BaseModel):
    name: str
    email: str
    password: str
    department: str


def _generate_id(db: Session, model, id_field: str, prefix: str) -> str:
    """Agle available ID ka pata lagata hai, jaise S2026-0026 ya F2026-0007."""
    year = datetime.now().year
    year_prefix = f"{prefix}{year}-"

    existing = db.query(model).filter(getattr(model, id_field).like(f"{year_prefix}%")).all()
    max_num = 0
    for row in existing:
        raw_id = getattr(row, id_field)
        try:
            num = int(raw_id.split("-")[-1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            continue

    next_num = max_num + 1
    return f"{year_prefix}{next_num:04d}"


@router.post("/student")
def register_student(data: StudentRegister, db: Session = Depends(get_db)):
    name = data.name.strip()
    email = data.email.strip().lower()
    college_id = data.college_id.strip()

    if not name or not email or not college_id or len(data.password) < 6:
        return {"success": False, "message": "Saari fields sahi se bharo (password kam se kam 6 characters)."}

    existing = db.query(Student).filter(Student.email == email).first()
    if existing:
        return {"success": False, "message": "Iss email se pehle se ek account bana hua hai."}

    student_id = _generate_id(db, Student, "student_id", "S")

    student = Student(
        student_id=student_id,
        name=name,
        email=email,
        password_hash=hash_password(data.password),
        department=college_id,   # college ID yahan store ho raha hai
    )
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"success": False, "message": "Account create nahi ho paya. Dobara try karo."}

    return {"success": True, "message": "Account created.", "id": student_id, "role": "student"}


@router.post("/faculty")
def register_faculty(data: FacultyRegister, db: Session = Depends(get_db)):
    name = data.name.strip()
    email = data.email.strip().lower()
    department = data.department.strip()

    if not name or not email or not department or len(data.password) < 6:
        return {"success": False, "message": "Saari fields sahi se bharo (password kam se kam 6 characters)."}

    existing = db.query(Faculty).filter(Faculty.email == email).first()
    if existing:
        return {"success": False, "message": "Iss email se pehle se ek account bana hua hai."}

    faculty_id = _generate_id(db, Faculty, "faculty_id", "F")

    faculty = Faculty(
        faculty_id=faculty_id,
        name=name,
        email=email,
        password_hash=hash_password(data.password),
        department=department,
    )
    db.add(faculty)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"success": False, "message": "Account create nahi ho paya. Dobara try karo."}

    return {"success": True, "message": "Account created.", "id": faculty_id, "role": "faculty"}
