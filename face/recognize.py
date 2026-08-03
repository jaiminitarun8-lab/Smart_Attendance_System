import sys
from attendance import mark_attendance
import cv2
import pickle
import numpy as np
from insightface.app import FaceAnalysis
from numpy.linalg import norm

# ======================================================
# Subject from Faculty Dashboard
# ======================================================
subject = "Artificial Intelligence"

if len(sys.argv) > 1:
    subject = sys.argv[1]

# ======================================================
# Load Face AI Model
# ======================================================
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0)

# ======================================================
# Load Saved Face Encodings
# ======================================================
with open("encodings/faces.pkl", "rb") as f:
    known_faces = pickle.load(f)

# ======================================================
# Cosine Similarity Function
# ======================================================
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# ======================================================
# Start Camera
# ======================================================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Camera not found.")
    exit()

print("===================================")
print(" Smart Attendance Face Recognition ")
print("===================================")
print(f"Subject : {subject}")
print("Press Q to Exit")
print()

# Attendance sirf ek baar mark karne ke liye
marked_students = set()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    faces = app.get(frame)

    for face in faces:

        embedding = face.embedding

        best_score = 0
        best_student = "Unknown"

        # Compare with saved faces
        for student_id, saved_embedding in known_faces.items():

            score = cosine_similarity(
                embedding,
                saved_embedding
            )

            if score > best_score:
                best_score = score
                best_student = student_id

        # Confidence Threshold
        if best_score < 0.55:
            best_student = "Unknown"

        else:

            # Attendance sirf ek baar
            if best_student not in marked_students:

                status, message = mark_attendance(
                    best_student,
                    subject
                )

                print("--------------------------------")
                print("Student :", best_student)
                print("Subject :", subject)
                print("Confidence :", round(best_score, 2))
                print(message)
                print("--------------------------------")

                marked_students.add(best_student)

        # Face Box
        box = face.bbox.astype(int)

        x1, y1, x2, y2 = box

        color = (0, 255, 0)

        if best_student == "Unknown":
            color = (0, 0, 255)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            f"{best_student} ({best_score:.2f})",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    cv2.imshow("Smart Attendance - Live Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("\nCamera Closed.")