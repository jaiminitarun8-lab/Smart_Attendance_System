import sqlite3

DB_PATH = "attendance.db"

def get_today_attendance(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, status, date
        FROM attendance
        WHERE user_id=?
        ORDER BY date DESC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return {
            "subject": row[0],
            "status": row[1],
            "date": row[2]
        }

    return None