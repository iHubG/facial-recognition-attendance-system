import face_recognition
import cv2
from PIL import Image
import numpy as np

# Load a sample image and learn how to recognize it
try:
    # Load image using PIL to ensure consistent format handling
    known_image_pil = Image.open("ian.jpg")
    
    # Convert image to RGB mode if it's not already
    if known_image_pil.mode != 'RGB':
        known_image_pil = known_image_pil.convert('RGB')

    # Convert PIL image to numpy array
    known_image_np = np.array(known_image_pil)

except FileNotFoundError:
    print("Error: Image file 'ian.png' not found.")
    exit()

# Check image dimensions and channels
print(f"Image shape: {known_image_np.shape}")
print(f"Image dtype: {known_image_np.dtype}")

# Check if the image is already in RGB format
if known_image_np.shape[-1] == 3:
    print("Image is already in RGB format.")
elif known_image_np.shape[-1] == 4:
    print("Converting RGBA image to RGB.")
    known_image_np = known_image_np[:, :, :3]
else:
    print("Unsupported image format. Please use RGB or RGBA image.")
    exit()

# Get face encoding from the known image
try:
    known_encoding = face_recognition.face_encodings(known_image_np)[0]
except IndexError:
    print("No face found in the known image.")
    exit()

# Capture video from the default camera
video_capture = cv2.VideoCapture(0)

while True:
    # Capture a single frame of video
    ret, frame = video_capture.read()

    # Convert the frame from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all face locations and encodings in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        # Compare each face found in the frame with the known face
        match = face_recognition.compare_faces([known_encoding], face_encoding)
        name = "Unknown"

        if match[0]:
            name = "Known Person"

        # Draw a rectangle around the face
        top, right, bottom, left = face_locations[0]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with the name below the face
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
video_capture.release()
cv2.destroyAllWindows()
