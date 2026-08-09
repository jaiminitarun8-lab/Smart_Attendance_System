import sqlite3
import os
import random
from datetime import date, timedelta

# IMPORTANT: Change this path to where YOUR attendance.db file is saved
DB_PATH = os.path.join(os.path.dirname(__file__), "attendance.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_attendance_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            record_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    INTEGER NOT NULL,
            date          TEXT NOT NULL,
            status        TEXT NOT NULL,  -- 'Present' or 'Absent'
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
    """)
    conn.commit()


def create_risk_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_prediction (
            student_id       INTEGER PRIMARY KEY,
            total_days        INTEGER,
            present_days       INTEGER,
            attendance_percent REAL,
            risk_level         TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
    """)
    conn.commit()


def generate_attendance(conn, num_days=30):
    cursor = conn.cursor()
    students = cursor.execute("SELECT student_id FROM students").fetchall()

    if not students:
        print("No students found! Please run the students seeding script first.")
        return

    today = date.today()
    records = []

    for (student_id,) in students:
        # Give each student a random "attendance tendency" so results vary
        # nicely across Green / Yellow / Red
        tendency = random.choice([0.95, 0.85, 0.75, 0.55, 0.40])
        for i in range(num_days):
            day = today - timedelta(days=i)
            status = "Present" if random.random() < tendency else "Absent"
            records.append((student_id, day.isoformat(), status))

    cursor.executemany("""
        INSERT INTO attendance_records (student_id, date, status)
        VALUES (?, ?, ?);
    """, records)
    conn.commit()
    print(f"{len(records)} attendance records inserted for {len(students)} students.")


def calculate_risk(conn):
    cursor = conn.cursor()
    students = cursor.execute("SELECT student_id FROM students").fetchall()

    for (student_id,) in students:
        total = cursor.execute(
            "SELECT COUNT(*) FROM attendance_records WHERE student_id = ?",
            (student_id,)
        ).fetchone()[0]

        present = cursor.execute(
            "SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND status = 'Present'",
            (student_id,)
        ).fetchone()[0]

        percent = round((present / total) * 100, 2) if total > 0 else 0

        if percent >= 85:
            risk = "Green"
        elif percent >= 60:
            risk = "Yellow"
        else:
            risk = "Red"

        cursor.execute("""
            INSERT INTO risk_prediction (student_id, total_days, present_days, attendance_percent, risk_level)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                total_days = excluded.total_days,
                present_days = excluded.present_days,
                attendance_percent = excluded.attendance_percent,
                risk_level = excluded.risk_level;
        """, (student_id, total, present, percent, risk))

    conn.commit()
    print("Risk prediction calculated for all students.")

    # Print a quick summary
    summary = cursor.execute("""
        SELECT risk_level, COUNT(*) FROM risk_prediction GROUP BY risk_level;
    """).fetchall()
    print("\nSummary:")
    for level, count in summary:
        print(f"  {level}: {count} students")


if __name__ == "__main__":
    conn = get_connection()
    create_attendance_table(conn)
    create_risk_table(conn)
    generate_attendance(conn, num_days=30)
    calculate_risk(conn)
    conn.close()
    print("\nDone! Two new tables created: attendance_records, risk_prediction")
