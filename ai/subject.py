import sqlite3

DB_PATH = "attendance.db"

def get_subject_attendance(user_id, subject):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE user_id=? AND subject=?
    """, (user_id, subject))

    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE user_id=? AND subject=? AND status='present'
    """, (user_id, subject))

    present = cursor.fetchone()[0]

    conn.close()

    if total == 0:
        return None

    percentage = round((present / total) * 100, 2)

    return {
        "subject": subject,
        "present": present,
        "total": total,
        "percentage": percentage
    }