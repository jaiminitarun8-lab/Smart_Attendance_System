import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:
    print(f"\nTable: {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]})")
    for column in cursor.fetchall():
        print(column)

conn.close()