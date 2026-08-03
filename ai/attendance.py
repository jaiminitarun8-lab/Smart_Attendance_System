import sqlite3

DB_PATH = "attendance.db"


def get_attendance(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE user_id=?",
        (user_id,)
    )
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE user_id=? AND status='present'",
        (user_id,)
    )
    present = cursor.fetchone()[0]

    conn.close()

    if total == 0:
        return {
            "total": 0,
            "present": 0,
            "percentage": 0
        }

    percentage = round((present / total) * 100, 2)

    return {
        "total": total,
        "present": present,
        "percentage": percentage
    }