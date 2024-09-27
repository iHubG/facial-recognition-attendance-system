import cv2
import face_recognition
import sqlite3
from datetime import datetime, timedelta

# Initialize variables for last insertion time and interval
last_insert_time = datetime.min
insert_interval = timedelta(minutes=5)  # 5-minute interval

# Function to insert data into SQLite database
def insert_data(name, entry_datetime, period):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, entry_datetime, period) VALUES (?, ?, ?)", (name, entry_datetime, period))
    conn.commit()
    conn.close()

# Initialize variables
face_locations = []
face_encodings = []
face_names = []

# Load a sample image and learn how to recognize it (for demonstration purposes)
known_image = face_recognition.load_image_file("ian.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Initialize the webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Convert the frame from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all the faces in the current frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # Compare each face found in the frame with the known face
        match = face_recognition.compare_faces([known_encoding], face_encoding)
        name = "Unknown"

        if match[0]:
            name = "Ian Macalinao"

        face_names.append(name)

        # Get current date and time
        now = datetime.now()
        entry_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        period = now.strftime("%p")

        # Check if 5 minutes have passed since last insertion
        if (now - last_insert_time) > insert_interval:
            # Insert data into SQLite database
            insert_data(name, entry_datetime, period)
            last_insert_time = now  # Update last insertion time

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
    # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)  # Green rectangle

        # Draw a label with the name below the face
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 255, 0), cv2.FILLED)  # Green filled rectangle
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (0, 0, 0), 1)  # Black text


    # Display the resulting image
    cv2.imshow('Video', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
video_capture.release()
cv2.destroyAllWindows()
