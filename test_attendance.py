from face.attendance import mark_attendance

status, message = mark_attendance(
    "S2026-0001",
    "Artificial Intelligence"
)

print(status)
print(message)