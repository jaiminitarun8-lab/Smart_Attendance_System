import sqlite3
import os
import time
from winotify import Notification

# IMPORTANT: This should point to the SAME attendance.db that Power BI is using
DB_PATH = os.path.join(os.path.dirname(__file__), "attendance.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def get_red_students(conn):
    """Fetch all students who are in the Red (high risk) zone, joined with their details."""
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT s.name, s.roll_no, s.class, s.section,
               r.attendance_percent
        FROM risk_prediction r
        JOIN students s ON s.student_id = r.student_id
        WHERE r.risk_level = 'Red'
        ORDER BY r.attendance_percent ASC;
    """).fetchall()
    return rows


def send_toast(title, message):
    toast = Notification(
        app_id="Smart Attendance System",
        title=title,
        msg=message,
        duration="long"
    )
    toast.show()


def show_notifications():
    conn = get_connection()
    red_students = get_red_students(conn)
    conn.close()

    if not red_students:
        send_toast("Attendance Risk Alert", "No students in Red zone. All good!")
        print("No red-zone students. Notification sent.")
        return

    # First, a summary popup
    send_toast(
        "Attendance Risk Alert",
        f"{len(red_students)} student(s) in RED zone. Sending individual alerts..."
    )
    time.sleep(3)

    # Then one popup per student
    for name, roll_no, cls, section, pct in red_students:
        message = f"{name} (Roll {roll_no}, Class {cls}-{section}) - Attendance: {pct}% - Contact urgently!"
        send_toast("RED ALERT: Low Attendance", message)
        print(f"Notification sent for {name}")
        time.sleep(3)

    print("\nAll notifications sent successfully!")


if __name__ == "__main__":
    show_notifications()
