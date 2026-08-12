import cv2
import os

student_id = input("Enter Student ID: ")

folder = f"faces/{student_id}"
os.makedirs(folder, exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

count = 0

print("Look at the camera...")
print("Press ESC to stop")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100,100)
    )

    for (x,y,w,h) in faces:

        face = frame[y:y+h, x:x+w]

        count += 1

        cv2.imwrite(
            os.path.join(folder,f"{count}.jpg"),
            face
        )

        cv2.rectangle(
            frame,
            (x,y),
            (x+w,y+h),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Images : {count}",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    cv2.imshow("Face Registration",frame)

    key=cv2.waitKey(1)

    if key==27:
        break

    if count>=50:
        break

cap.release()
cv2.destroyAllWindows()

print("Registration Completed")