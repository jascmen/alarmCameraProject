import bcrypt
import cv2
import numpy as np
from database import get_user, add_user

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def register_user(username, password, email,celular, role_id, face_data):
    hashed_password = hash_password(password)
    add_user(username, hashed_password, email, celular, role_id, face_data)

def authenticate_user(username, password):
    user = get_user(username)
    if user and verify_password(password, user[2]):
        return True, user
    return False, None

def save_face_data(image):
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()

def load_face_data(data):
    nparr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
