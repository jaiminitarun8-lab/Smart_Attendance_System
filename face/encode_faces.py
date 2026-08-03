from insightface.app import FaceAnalysis
import cv2
import os
import pickle
import numpy as np

# Load AI Face Model
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0)

faces_folder = "faces"
encodings = {}

for student_id in os.listdir(faces_folder):

    student_path = os.path.join(faces_folder, student_id)

    if not os.path.isdir(student_path):
        continue

    student_embeddings = []

    for img_name in os.listdir(student_path):

        img_path = os.path.join(student_path, img_name)

        img = cv2.imread(img_path)

        if img is None:
            continue

        faces = app.get(img)

        if len(faces) > 0:
            student_embeddings.append(faces[0].embedding)

    if len(student_embeddings) > 0:
        encodings[student_id] = np.mean(student_embeddings, axis=0)

os.makedirs("encodings", exist_ok=True)

with open("encodings/faces.pkl", "wb") as f:
    pickle.dump(encodings, f)

print("✅ Face Encodings Saved Successfully")