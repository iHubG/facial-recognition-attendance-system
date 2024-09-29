from flask import Blueprint, render_template, Response, jsonify
import cv2
import face_recognition
import sqlite3
from datetime import datetime, timedelta
import threading

# Create a Blueprint for face recognition
faceRecognition_bp = Blueprint('faceRecognition', __name__)

# Initialize variables for last insertion time and interval
last_insert_time = datetime.min
insert_interval = timedelta(minutes=5)
detected_info = {"name": None, "datetime": None}  # Store both name and timestamp

def insert_data(name, entry_datetime, period):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, entry_datetime, period) VALUES (?, ?, ?)", (name, entry_datetime, period))
    conn.commit()
    conn.close()

def get_user_data(name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, entry_datetime FROM users WHERE name = ?", (name,))
    result = c.fetchone()
    conn.close()
    return result if result else (None, None)  # Return both name and datetime

# Load a sample image and learn how to recognize it
known_image = face_recognition.load_image_file("ian.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.process_frame_interval = 5  # Process every nth frame
        self.frame_count = 0

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update_frame)
            self.thread.start()

    def stop(self):
        self.running = False
        self.video.release()
        print("Camera turned off.")

    def update_frame(self):
        while self.running:
            success, frame = self.video.read()
            if success:
                with self.lock:
                    self.frame = frame
                    self.frame_count += 1
            else:
                print("Failed to capture frame")

    def get_frame(self):
        with self.lock:
            return self.frame

camera = VideoCamera()

@faceRecognition_bp.route('/faceRecognition')
def dashboard():
    camera.start()  # Automatically start the camera when visiting this page
    return render_template('views/faceRecognition.html')

def generate_frames():
    global last_insert_time, detected_info
    while camera.running:
        frame = camera.get_frame()
        if frame is None:
            continue

        camera.frame_count += 1
        if camera.frame_count % camera.process_frame_interval != 0:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            match = face_recognition.compare_faces([known_encoding], face_encoding)
            name = "Unknown"

            if match[0]:
                name = "Ian Macalinao"
                
                # Retrieve user data from the database
                retrieved_name, entry_datetime = get_user_data(name)
                if retrieved_name:
                    detected_info["name"] = retrieved_name  # Store detected name
                    detected_info["datetime"] = entry_datetime  # Retrieve datetime from DB

            else:
                # If unknown, clear the detected_info
                detected_info["name"] = "Unknown"
                detected_info["datetime"] = None  # Or you can set it to "Unknown" as well

            face_names.append(name)

            now = datetime.now()
            entry_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            period = now.strftime("%p")

            if (now - last_insert_time) > insert_interval:
                insert_data(name, entry_datetime, period)
                last_insert_time = now

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@faceRecognition_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@faceRecognition_bp.route('/get_detected_info')
def get_detected_info():
    return jsonify(detected_info)

# Function to listen for commands (not needed if the camera is automatically turned on)
def listen_for_commands():
    while True:
        command = input("Enter command ('on' to start, 'off' to stop camera): ")
        if command.lower() == "on":
            camera.start()
            print("Camera turned on.")
        elif command.lower() == "off":
            camera.stop()
        else:
            print("Unknown command.")

# Start listening for commands in a separate thread (optional)
# command_thread = threading.Thread(target=listen_for_commands)
# command_thread.start()
