"""
Seed script — database me sample/dummy data daalne ke liye.
Isse sirf ek baar chalana hai (testing data set karne ke liye).

Chalane ka tarika:
    python -m database.seed
"""

import hashlib
from datetime import date, timedelta

from database.connection import Base, engine, SessionLocal
from database.models import Student, Faculty, Attendance, Leave


def hash_password(password: str) -> str:
    """Simple SHA-256 hashing. auth.py me bhi yehi function use hoga verify karne ke liye."""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_data():
    # Pehle saari tables bana lo agar nahi bani hain
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Agar pehle se data hai to dobara mat daalo (duplicate avoid karne ke liye)
    if db.query(Student).first() or db.query(Faculty).first():
        print("⚠️  Database me pehle se data hai — seed skip kar raha hu.")
        print("    (Agar dobara daalna hai to pehle 'attendance.db' file delete kar do)")
        db.close()
        return

    # ---------------- Sample Students ----------------
    students = [
        Student(student_id="S2026-0001", name="Aarav Sharma", password_hash=hash_password("student123"),
                email="aarav.sharma@attendai.edu", phone="9876500001", department="Computer Science", section="B"),
        Student(student_id="S2026-0002", name="Meera Nair", password_hash=hash_password("student123"),
                email="meera.nair@attendai.edu", phone="9876500002", department="Computer Science", section="B"),
        Student(student_id="S2026-0003", name="Kabir Singh", password_hash=hash_password("student123"),
                email="kabir.singh@attendai.edu", phone="9876500003", department="Computer Science", section="B"),
        Student(student_id="S2026-0004", name="Ishita Rao", password_hash=hash_password("student123"),
                email="ishita.rao@attendai.edu", phone="9876500004", department="Computer Science", section="B"),
        Student(student_id="S2026-0005", name="Devansh Patel", password_hash=hash_password("student123"),
                email="devansh.patel@attendai.edu", phone="9876500005", department="Computer Science", section="B"),
    ]

    # ---------------- Sample Faculty ----------------
    faculty = [
        Faculty(faculty_id="F2026-0001", name="Dr. Ramesh Verma", password_hash=hash_password("faculty123"),
                email="ramesh.verma@attendai.edu", phone="9876511001", department="Computer Science"),
        Faculty(faculty_id="F2026-0002", name="Dr. Anjali Gupta", password_hash=hash_password("faculty123"),
                email="anjali.gupta@attendai.edu", phone="9876511002", department="Computer Science"),
    ]

    db.add_all(students)
    db.add_all(faculty)
    db.commit()

    # ---------------- Sample Attendance (last 5 days, sabhi students ke liye) ----------------
    today = date.today()
    statuses = ["present", "present", "absent", "present", "present"]

    attendance_records = []
    for student in students:
        for i in range(5):
            attendance_records.append(
                Attendance(
                    user_id=student.student_id,
                    user_type="student",
                    subject="Mathematics",
                    date=today - timedelta(days=i),
                    status=statuses[i % len(statuses)],
                    marked_by="manual",
                )
            )

    db.add_all(attendance_records)

    # ---------------- Sample Leave request ----------------
    leave = Leave(
        user_id="S2026-0003",
        user_type="student",
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=3),
        reason="Family function",
        status="pending",
    )
    db.add(leave)

    db.commit()
    db.close()

    print("✅ Sample data successfully add ho gaya:")
    print(f"   - {len(students)} students")
    print(f"   - {len(faculty)} faculty")
    print(f"   - {len(attendance_records)} attendance records")
    print("   - 1 leave request")
    print("\nLogin karne ke liye use karo:")
    print("   Student → ID: S2026-0001   Password: student123")
    print("   Faculty → ID: F2026-0001   Password: faculty123")


if __name__ == "__main__":
    seed_data()
