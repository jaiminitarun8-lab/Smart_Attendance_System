from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import Student, Faculty
from utils.security import verify_password

router = APIRouter(prefix="/api", tags=["auth"])


class LoginRequest(BaseModel):
    role: str        # "student" ya "faculty"
    user_id: str      # student_id ya faculty_id
    password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    role = data.role.lower().strip()

    if role == "student":
        user = db.query(Student).filter(Student.student_id == data.user_id).first()
    elif role == "faculty":
        user = db.query(Faculty).filter(Faculty.faculty_id == data.user_id).first()
    else:
        return {"success": False, "message": "Invalid role."}

    if not user:
        return {"success": False, "message": "Incorrect ID or password."}

    if not verify_password(data.password, user.password_hash):
        return {"success": False, "message": "Incorrect ID or password."}

    return {
        "success": True,
        "message": "Login successful.",
        "role": role,
        "id": data.user_id,
        "name": user.name,
    }
