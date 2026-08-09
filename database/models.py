from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)   # e.g. S2026-0417 (used by face recognition)
    roll_no = Column(String, nullable=True)          # original school roll number, e.g. R001
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    section = Column(String, nullable=True)
    class_name = Column(String, nullable=True)         # e.g. "7", "10"
    dob = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    address = Column(String, nullable=True)
    admission_date = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    mother_name = Column(String, nullable=True)
    face_encoding = Column(String, nullable=True)   # AI face recognition ke liye
    joined_date = Column(DateTime(timezone=True), server_default=func.now())


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(String, unique=True, index=True, nullable=False)   # e.g. F2026-0417
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    face_encoding = Column(String, nullable=True)
    joined_date = Column(DateTime(timezone=True), server_default=func.now())


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)          # student_id ya faculty_id
    user_type = Column(String, nullable=False)         # "student" ya "faculty"
    subject = Column(String, nullable=True)             # jaise "Mathematics" ya "Section B"
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)             # "present" / "absent" / "pending"
    marked_by = Column(String, default="manual")         # "manual" ya "ai_face_recognition"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    user_type = Column(String, nullable=False)          # "student" ya "faculty"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending")            # "pending" / "approved" / "rejected"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    section = Column(String, nullable=True)          # kis section ko assign hua (e.g. "B")
    assigned_by = Column(String, nullable=False)       # faculty_id
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_id = Column(String, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    obtained = Column(Integer, nullable=False)
    max_marks = Column(Integer, nullable=False)
    term = Column(String, default="Current term")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)          # "announcement" ya "extracurricular"
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)          # student_id ya faculty_id
    user_type = Column(String, nullable=False)         # "student" ya "faculty"
    title = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    section = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)      # e.g. "9:00 AM"
    monday = Column(String, nullable=True)
    tuesday = Column(String, nullable=True)
    wednesday = Column(String, nullable=True)
    thursday = Column(String, nullable=True)
    friday = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)          # row display order
