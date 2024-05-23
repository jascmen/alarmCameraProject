import cv2
import numpy as np

def encode_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    (x, y, w, h) = faces[0]
    face = gray[y:y + h, x:x + w]
    return face

def compare_faces(known_face_encoding, face_encoding_to_check):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train([known_face_encoding], np.array([0]))
    label, confidence = recognizer.predict(face_encoding_to_check)
    return confidence < 50  # Ajusta el umbral de confianza según tus necesidadesn tus necesidades