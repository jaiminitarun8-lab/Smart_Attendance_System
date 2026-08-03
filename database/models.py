from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)   # e.g. S2026-0417
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    section = Column(String, nullable=True)
    face_encoding = Column(String, nullable=True)   # AI face recognition ke liye (baad me use hoga)
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
