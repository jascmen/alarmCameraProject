import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import time
import os

class ObjectDetection:
    def __init__(self):
        self.model = YOLO('yolov8s')

    def detect(self, frame):
        results = self.model.predict(frame, stream=True, verbose=False, conf=0.75, classes=[0])
        annotator = Annotator(frame)
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                r = box.xyxy[0]
                c = box.cls
                if int(c) == 0:
                    annotator.box_label(r, label='Persona', color=(0, 255, 0))
                    detections.append((r, 'Persona'))
        return detections

    def save_image(self, image):
        filename = '../images/detection_{}.png'.format(int(time.time()))
        if os.path.exists(filename):
            os.remove(filename)
        cv2.imwrite(filename, image)
        return filename
