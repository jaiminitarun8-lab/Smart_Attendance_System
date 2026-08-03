import sqlite3

DB_PATH = "attendance.db"


def predict_attendance(user_id, target=75):

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
        return None

    current = round((present / total) * 100, 2)

    needed = 0

    while True:

        new_present = present + needed
        new_total = total + needed

        percent = (new_present / new_total) * 100

        if percent >= target:
            break

        needed += 1

    return {
        "current": current,
        "needed": needed,
        "target": target
    }