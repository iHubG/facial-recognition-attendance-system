from flask import Blueprint, render_template, redirect, url_for, session
import cv2
from flask import Flask, Response

faceRecognition_bp = Blueprint('faceRecognition', __name__)

@faceRecognition_bp.route('faceRecognition')
def dashboard():
    return render_template('views/faceRecognition.html')

def generate_frames():
    camera = cv2.VideoCapture(0)  # For Raspberry Pi, this can be set to Pi Camera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame as part of an HTTP response with the appropriate headers
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to provide the video feed
@faceRecognition_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')