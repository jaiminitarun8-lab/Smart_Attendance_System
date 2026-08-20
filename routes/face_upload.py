"""
Face registration via file upload — "Choose File" option ke liye.
Ye camera-based registration (face/register.py) se ALAG hai, dono saath-saath use ho sakte hain.
"""

import os
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Student
from ai.liveness import extract_embedding, serialize_embedding, check_liveness

router = APIRouter(prefix="/api/face", tags=["face-upload"])

FACES_DIR = "faces"


@router.post("/upload-register")
async def upload_register(
    student_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return {"success": False, "message": "Student not found."}

    # Uploaded file ko image me convert karo
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        return {"success": False, "message": "Ye file valid image nahi hai. JPG/PNG try karo."}

    # Liveness check — asli photo hai ya screen/printout
    liveness = check_liveness(img_bgr)
    if not liveness["passed"]:
        return {"success": False, "message": f"Liveness check fail: {liveness['reason']}"}

    # Face embedding nikalo
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    embedding, location = extract_embedding(img_rgb)

    if embedding is None:
        return {"success": False, "message": "Photo me koi face detect nahi hua. Sahi photo try karo (clear, front-facing)."}

    # Embedding ko database me save karo (Student.face_encoding column already hai)
    student.face_encoding = serialize_embedding(embedding)
    db.commit()

    # Original photo bhi faces/{student_id}/ folder me save karo (existing convention follow karte hue)
    student_folder = os.path.join(FACES_DIR, student_id)
    os.makedirs(student_folder, exist_ok=True)
    existing_count = len([f for f in os.listdir(student_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
    photo_path = os.path.join(student_folder, f"{existing_count + 1}.jpg")
    cv2.imwrite(photo_path, img_bgr)

    return {
        "success": True,
        "message": "Face successfully register ho gaya.",
        "liveness_score": liveness["score"],
    }
