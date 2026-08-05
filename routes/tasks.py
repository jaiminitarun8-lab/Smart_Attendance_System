from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date as date_type

from database.connection import get_db
from database.models import Task, TaskCompletion, Student

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    subject: str
    due_date: date_type
    section: str
    assigned_by: str   # faculty_id


class TaskCompleteRequest(BaseModel):
    student_id: str


@router.get("/student/{student_id}")
def get_student_tasks(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return {"success": False, "message": "Student not found."}

    tasks = db.query(Task).filter(Task.section == student.section).order_by(Task.due_date).all()
    completed_ids = {
        tc.task_id for tc in db.query(TaskCompletion).filter(TaskCompletion.student_id == student_id).all()
    }

    result = [
        {
            "id": t.id,
            "title": t.title,
            "subject": t.subject,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "completed": t.id in completed_ids,
        }
        for t in tasks
    ]
    return {"success": True, "tasks": result}


@router.get("/faculty/{faculty_id}")
def get_faculty_tasks(faculty_id: str, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.assigned_by == faculty_id).order_by(Task.due_date).all()

    result = []
    for t in tasks:
        total_in_section = db.query(Student).filter(Student.section == t.section).count()
        completed_count = db.query(TaskCompletion).filter(TaskCompletion.task_id == t.id).count()
        result.append({
            "id": t.id,
            "title": t.title,
            "subject": t.subject,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "section": t.section,
            "completed_count": completed_count,
            "total_count": total_in_section,
        })
    return {"success": True, "tasks": result}


@router.post("")
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=data.title,
        subject=data.subject,
        due_date=data.due_date,
        section=data.section,
        assigned_by=data.assigned_by,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"success": True, "id": task.id}


@router.post("/{task_id}/complete")
def complete_task(task_id: int, data: TaskCompleteRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return {"success": False, "message": "Task not found."}

    already = db.query(TaskCompletion).filter(
        TaskCompletion.task_id == task_id, TaskCompletion.student_id == data.student_id
    ).first()
    if already:
        return {"success": True, "message": "Already marked complete."}

    db.add(TaskCompletion(task_id=task_id, student_id=data.student_id))
    db.commit()
    return {"success": True, "message": "Task marked complete."}
