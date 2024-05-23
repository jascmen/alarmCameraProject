import cv2

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        return self.cap.isOpened()

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return ret, frame
        return False, None

    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None
