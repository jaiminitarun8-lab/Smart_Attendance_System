import sqlite3
from datetime import date

DB_PATH = "attendance.db"


def mark_attendance(student_id, subject):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = str(date.today())

    # Check if attendance already marked
    cursor.execute("""
        SELECT id
        FROM attendance
        WHERE user_id=?
        AND date=?
        AND subject=?
    """, (student_id, today, subject))

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return False, "Attendance already marked."

    # Insert attendance
    cursor.execute("""
        INSERT INTO attendance
        (
            user_id,
            user_type,
            subject,
            date,
            status,
            marked_by
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?
        )
    """, (
        student_id,
        "student",
        subject,
        today,
        "Present",
        "Face Recognition AI"
    ))

    conn.commit()
    conn.close()

    return True, "Attendance marked successfully."