from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date as date_type

from database.connection import get_db
from database.models import Task, TaskCompletion, Student, Notification


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# =========================================================
# REQUEST MODELS
# =========================================================

class TaskCreate(BaseModel):
    title: str
    subject: str
    due_date: date_type
    section: str
    assigned_by: str   # faculty_id


class TaskCompleteRequest(BaseModel):
    student_id: str


# =========================================================
# STUDENT - GET TASKS
# =========================================================

@router.get("/student/{student_id}")
def get_student_tasks(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = (
        db.query(Student)
        .filter(Student.student_id == student_id)
        .first()
    )

    if not student:
        return {
            "success": False,
            "message": "Student not found."
        }

    # Student ke section ke tasks
    tasks = (
        db.query(Task)
        .filter(Task.section == student.section)
        .order_by(Task.due_date)
        .all()
    )

    # Student ne kaunse tasks complete kiye
    completed_ids = {
        tc.task_id
        for tc in db.query(TaskCompletion)
        .filter(TaskCompletion.student_id == student_id)
        .all()
    }

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "subject": task.subject,
            "due_date": (
                task.due_date.isoformat()
                if task.due_date
                else None
            ),
            "section": task.section,
            "completed": task.id in completed_ids
        })

    return {
        "success": True,
        "tasks": result
    }


# =========================================================
# FACULTY - GET TASKS + COMPLETED STUDENTS
# =========================================================

@router.get("/faculty/{faculty_id}")
def get_faculty_tasks(
    faculty_id: str,
    db: Session = Depends(get_db)
):
    tasks = (
        db.query(Task)
        .filter(Task.assigned_by == faculty_id)
        .order_by(Task.due_date)
        .all()
    )

    result = []

    for task in tasks:

        # -----------------------------------------
        # Section ke total students
        # -----------------------------------------

        students = (
            db.query(Student)
            .filter(Student.section == task.section)
            .all()
        )

        total_in_section = len(students)

        # -----------------------------------------
        # Task complete karne wale students
        # -----------------------------------------

        completions = (
            db.query(TaskCompletion)
            .filter(TaskCompletion.task_id == task.id)
            .all()
        )

        completed_students = []

        for completion in completions:

            student = (
                db.query(Student)
                .filter(
                    Student.student_id == completion.student_id
                )
                .first()
            )

            if student:

                completed_students.append({
                    "student_id": student.student_id,
                    "name": student.name,
                    "roll_no": student.roll_no,
                    "email": student.email,
                    "completed_at": (
                        completion.completed_at.isoformat()
                        if completion.completed_at
                        else None
                    )
                })

        # -----------------------------------------
        # Pending students
        # -----------------------------------------

        completed_ids = {
            student["student_id"]
            for student in completed_students
        }

        pending_students = []

        for student in students:

            if student.student_id not in completed_ids:

                pending_students.append({
                    "student_id": student.student_id,
                    "name": student.name,
                    "roll_no": student.roll_no,
                    "email": student.email
                })

        # -----------------------------------------
        # Final task information
        # -----------------------------------------

        result.append({
            "id": task.id,
            "title": task.title,
            "subject": task.subject,
            "due_date": (
                task.due_date.isoformat()
                if task.due_date
                else None
            ),
            "section": task.section,

            "completed_count": len(completed_students),
            "total_count": total_in_section,

            "completed_students": completed_students,
            "pending_students": pending_students
        })

    return {
        "success": True,
        "tasks": result
    }


# =========================================================
# FACULTY - CREATE NEW TASK
# =========================================================

@router.post("")
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db)
):

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

    # -----------------------------------------
    # Section ke students ko notification
    # -----------------------------------------

    students = (
        db.query(Student)
        .filter(Student.section == data.section)
        .all()
    )

    for student in students:

        db.add(
            Notification(
                user_id=student.student_id,
                user_type="student",
                title=(
                    f"New task assigned: "
                    f"{data.title} ({data.subject}) "
                    f"— due {data.due_date}"
                )
            )
        )

    db.commit()

    return {
        "success": True,
        "id": task.id,
        "message": "Task created successfully."
    }


# =========================================================
# STUDENT - COMPLETE TASK
# =========================================================

@router.post("/{task_id}/complete")
def complete_task(
    task_id: int,
    data: TaskCompleteRequest,
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # Task check
    # -----------------------------------------

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        return {
            "success": False,
            "message": "Task not found."
        }

    # -----------------------------------------
    # Student check
    # -----------------------------------------

    student = (
        db.query(Student)
        .filter(Student.student_id == data.student_id)
        .first()
    )

    if not student:
        return {
            "success": False,
            "message": "Student not found."
        }

    # -----------------------------------------
    # Check student section
    # -----------------------------------------

    if student.section != task.section:
        return {
            "success": False,
            "message": "This task is not assigned to your section."
        }

    # -----------------------------------------
    # Already completed?
    # -----------------------------------------

    already = (
        db.query(TaskCompletion)
        .filter(
            TaskCompletion.task_id == task_id,
            TaskCompletion.student_id == data.student_id
        )
        .first()
    )

    if already:

        return {
            "success": True,
            "message": "Already marked complete.",
            "completed": True
        }

    # -----------------------------------------
    # Save completion
    # -----------------------------------------

    completion = TaskCompletion(
        task_id=task_id,
        student_id=data.student_id
    )

    db.add(completion)
    db.commit()
    db.refresh(completion)

    return {
        "success": True,
        "message": "Task marked complete.",
        "completed": True,
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "roll_no": student.roll_no,
            "completed_at": (
                completion.completed_at.isoformat()
                if completion.completed_at
                else None
            )
        }
    }