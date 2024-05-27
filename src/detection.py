import threading

import cv2
import numpy as np
import time
import os

from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload

from uploads import authenticate_google_drive,upload_to_drive
from datetime import datetime


class MobileNetSSD:
    def __init__(self, confidence_threshold=0.9,save_interval=15):
        # Cargar el modelo preentrenado MobileNet-SSD
        self.net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'mobilenet_iter_73000.caffemodel')
        self.confidence_threshold = confidence_threshold
        self.last_saved_time = 0  # Tiempo de la última imagen guardada
        self.save_interval = save_interval  # Intervalo de tiempo en segundos entre guardados
        self.service = authenticate_google_drive()
        load_dotenv()


        self.folder_id = os.getenv('FOLDER_ID')


    def detect(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        person_detections = []
        current_time = time.time()
        save_image = False

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence_threshold:
                idx = int(detections[0, 0, i, 1])
                if idx == 15:  # Índice de clase 15 corresponde a 'person'
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    box = np.clip(box, 0, [w, h, w, h])  # Asegúrate de que los valores estén dentro del rango
                    (startX, startY, endX, endY) = box.astype("int")

                    if np.isnan(startX) or np.isnan(startY) or np.isnan(endX) or np.isnan(endY):
                        continue  # Ignorar detecciones con valores inválidos

                    startX, startY = max(0, startX), max(0, startY)
                    endX, endY = min(w, endX), min(h, endX)

                    label = "Persona: {:.2f}%".format(confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    person_detections.append((box, label))

                    # Guardar la imagen si ha pasado el intervalo de tiempo

                    if current_time - self.last_saved_time > self.save_interval:
                        save_image = True
                        self.last_saved_time = current_time
                        self.save_image(frame)

        return frame, person_detections,save_image

    # def save_image(self, image):
    #     filename = '../images/detection_{}.png'.format(int(time.time()))
    #     if os.path.exists(filename):
    #         os.remove(filename)
    #     cv2.imwrite(filename, image)
    #     return filename

    # def save_image(self, image):
    #     filename = f'detection_{int(time.time())}.png'
    #     local_path = f'../images/{filename}'
    #     if os.path.exists(local_path):
    #         os.remove(local_path)
    #     cv2.imwrite(local_path, cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))
    #     return local_path
    def save_image(self, image):
        # Obtener la fecha y hora actual
        now = datetime.now()

        # Formatear la fecha y hora en el formato deseado
        formatted_date = now.strftime('%Y-%m-%d-%H-%M-%S-%f')

        # Usar la fecha y hora formateada en el nombre del archivo
        filename = f'detection_{formatted_date}.png'
        #filename = f'detection_{int(time.time())}.png'
        local_path = f'../images/{filename}'

        # Asegurarse de que el directorio existe
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Convertir la imagen de PIL a OpenCV formato (RGB a BGR)
        image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Guardar la imagen
        cv2.imwrite(local_path, image_bgr)

        #print(f'Imagen guardada en: {local_path}')
        threading.Thread(target=upload_to_drive, args=(self.service, local_path, self.folder_id)).start()


