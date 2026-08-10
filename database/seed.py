"""
Seed script — database me sample/dummy data daalne ke liye.
Isse sirf ek baar chalana hai (testing data set karne ke liye).

Chalane ka tarika:
    python -m database.seed
"""

from datetime import date, timedelta

from database.connection import Base, engine, SessionLocal
from database.models import Student, Faculty, Attendance, Leave, Task, TaskCompletion, Mark, Activity, TimetableEntry
from utils.security import hash_password


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

    # ---------------- Sample Tasks (faculty ne assign kiye) ----------------
    tasks = [
        Task(title="Submit lab report", subject="Physics", due_date=today + timedelta(days=3),
             section="B", assigned_by="F2026-0001"),
        Task(title="Solve worksheet Ch. 4", subject="Mathematics", due_date=today + timedelta(days=1),
             section="B", assigned_by="F2026-0001"),
        Task(title="Read Chapter 7 & summarize", subject="English", due_date=today - timedelta(days=1),
             section="B", assigned_by="F2026-0002"),
    ]
    db.add_all(tasks)
    db.commit()

    # Kuch students ne pehla task complete kar diya (testing ke liye)
    db.add(TaskCompletion(task_id=tasks[0].id, student_id="S2026-0001"))
    db.add(TaskCompletion(task_id=tasks[0].id, student_id="S2026-0002"))
    db.commit()

    # ---------------- Sample Marks (subject-wise, sabhi students ke liye) ----------------
    subjects_marks = [
        ("Mathematics", 88, 100), ("Physics", 76, 100), ("Chemistry", 82, 100),
        ("English", 91, 100), ("Computer Science", 95, 100),
    ]
    marks_records = []
    for student in students:
        for subject, obtained, maxm in subjects_marks:
            marks_records.append(
                Mark(student_id=student.student_id, subject=subject, obtained=obtained, max_marks=maxm)
            )
    db.add_all(marks_records)

    # ---------------- Sample Activities ----------------
    activities = [
        Activity(title="Annual Sports Day", description="Athletics ground, all sections invited",
                  type="announcement", event_date=today + timedelta(days=10)),
        Activity(title="Mid-term results declared", description="Check the Reports section",
                  type="announcement", event_date=today - timedelta(days=2)),
        Activity(title="Chess Club", description="Meets every Friday, 4 PM, Room 201",
                  type="extracurricular", event_date=None),
        Activity(title="Basketball practice", description="Mon/Wed/Fri, 6 AM, Sports complex",
                  type="extracurricular", event_date=None),
    ]
    db.add_all(activities)
    db.commit()

    # ---------------- Sample Timetable (Section B) ----------------
    timetable_rows = [
        ("9:00 AM", ["Mathematics", "Physics", "Mathematics", "Chemistry", "English"]),
        ("10:30 AM", ["Physics", "Chemistry", "English", "Mathematics", "Physics"]),
        ("1:30 PM", ["Chemistry", "Computer Sci.", "Physics", "English", "Computer Sci."]),
        ("3:00 PM", ["English", "Free period", "Computer Sci.", "Free period", "Free period"]),
    ]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    timetable_entries = []
    for time_slot, subjects in timetable_rows:
        for day, subject in zip(days, subjects):
            timetable_entries.append(TimetableEntry(section="B", day=day, time_slot=time_slot, subject=subject))
    db.add_all(timetable_entries)

    db.commit()
    db.close()

    print("✅ Sample data successfully add ho gaya:")
    print(f"   - {len(students)} students")
    print(f"   - {len(faculty)} faculty")
    print(f"   - {len(attendance_records)} attendance records")
    print("   - 1 leave request")
    print(f"   - {len(tasks)} tasks")
    print(f"   - {len(marks_records)} marks records")
    print(f"   - {len(activities)} activities")
    print(f"   - {len(timetable_entries)} timetable entries")
    print("\nLogin karne ke liye use karo:")
    print("   Student → ID: S2026-0001   Password: student123")
    print("   Faculty → ID: F2026-0001   Password: faculty123")


if __name__ == "__main__":
    seed_data()
