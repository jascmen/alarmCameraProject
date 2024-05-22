import cv2

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.source)
        return self.cap.isOpened()

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        ret, frame = self.cap.read()
        return ret, frame

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
