from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Mark, Student

router = APIRouter(prefix="/api/marks", tags=["marks"])


def grade_for(percentage: float) -> str:
    if percentage >= 90: return "A+"
    if percentage >= 80: return "A"
    if percentage >= 70: return "B"
    if percentage >= 60: return "C"
    if percentage >= 50: return "D"
    return "F"


@router.get("/student/{student_id}")
def get_student_marks(student_id: str, db: Session = Depends(get_db)):
    marks = db.query(Mark).filter(Mark.student_id == student_id).all()
    if not marks:
        return {"success": True, "marks": [], "overall_pct": 0, "overall_grade": "—"}

    rows = []
    total_obtained, total_max = 0, 0
    for m in marks:
        pct = round((m.obtained / m.max_marks) * 100, 1)
        rows.append({
            "subject": m.subject, "obtained": m.obtained, "max_marks": m.max_marks,
            "percentage": pct, "grade": grade_for(pct),
        })
        total_obtained += m.obtained
        total_max += m.max_marks

    overall_pct = round((total_obtained / total_max) * 100, 1) if total_max else 0
    best = max(rows, key=lambda r: r["percentage"])
    worst = min(rows, key=lambda r: r["percentage"])

    return {
        "success": True, "marks": rows, "overall_pct": overall_pct, "overall_grade": grade_for(overall_pct),
        "best_subject": best["subject"], "best_pct": best["percentage"],
        "worst_subject": worst["subject"], "worst_pct": worst["percentage"],
    }


@router.get("/section/{section}")
def get_section_marks(section: str, db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.section == section).all()
    result = []
    for s in students:
        marks = db.query(Mark).filter(Mark.student_id == s.student_id).all()
        total_obtained = sum(m.obtained for m in marks)
        total_max = sum(m.max_marks for m in marks)
        pct = round((total_obtained / total_max) * 100, 1) if total_max else 0
        result.append({
            "student_name": s.name, "student_id": s.student_id,
            "obtained": total_obtained, "max_marks": total_max,
            "percentage": pct, "grade": grade_for(pct),
        })
    return {"success": True, "marks": result}
