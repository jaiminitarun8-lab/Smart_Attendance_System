from fastapi import APIRouter
from pydantic import BaseModel
import subprocess

router = APIRouter()


class FaceAttendance(BaseModel):
    subject: str


@router.post("/start-face-attendance")
def start_face_attendance(data: FaceAttendance):

    subprocess.Popen([
        "python",
        "face/recognize.py",
        data.subject
    ])

    return {
        "message": "✅ Face Attendance Started Successfully"
    }