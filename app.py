from flask import Flask, request, jsonify
import cv2
import dlib
from scipy.spatial import distance as dist
import numpy as np
import base64

app = Flask(__name__)

# Thresholds
EYE_AR_THRESH = 0.25
CONSEC_FRAMES = 3
BLINK_ALERT_LOW = 5
BLINK_ALERT_HIGH = 30

# Load dlib's face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Indices for eyes in the facial landmark model
(lStart, lEnd) = (42, 48)  # Left eye
(rStart, rEnd) = (36, 42)  # Right eye

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

@app.route('/detect', methods=['POST'])
def detect():
    data = request.get_json()
    if 'frame' not in data:
        return jsonify({"error": "No frame provided"}), 400

    # Decode the base64-encoded frame
    frame_data = base64.b64decode(data['frame'].split(',')[1])
    np_frame = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blink detection
    faces = detector(gray)
    blink_count = 0
    for face in faces:
        landmarks = predictor(gray, face)
        points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]

        left_eye = points[lStart:lEnd]
        right_eye = points[rStart:rEnd]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        if ear < EYE_AR_THRESH:
            blink_count += 1

    blink_rate = blink_count * 6  # Approximation to blinks per minute
    alert = None

    if blink_rate < BLINK_ALERT_LOW:
        alert = "Low blink rate detected! Blink more consciously or take a break."
    elif blink_rate > BLINK_ALERT_HIGH:
        alert = "High blink rate detected! Possible eye strain."

    return jsonify({"blink_rate": blink_rate, "alert": alert or "No issues detected."})

if __name__ == '__main__':
    app.run(debug=True)
