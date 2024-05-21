import cv2

class Camera:
    def __init__(self):
        self.vid = None

    def open(self):
        self.vid = cv2.VideoCapture(0)
        return self.vid.isOpened()

    def get_frame(self):
        if self.vid:
            ret, frame = self.vid.read()
            if ret:
                return frame
        return None

    def close(self):
        if self.vid:
            self.vid.release()
