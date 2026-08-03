import sqlite3

DB_PATH = "attendance.db"


def get_leave(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reason, status
        FROM leaves
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return {
            "reason": row[0],
            "status": row[1]
        }

    return {
        "reason": "No Leave Found",
        "status": "None"
    }