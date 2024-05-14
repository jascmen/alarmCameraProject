import cv2
import os
import threading
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
from envio_sms import enviar_sms
from envio_correo import enviar_correo
import time

def save_image_and_send_email(image):

    # def save_image_and_send_email(image):
    #     filename = 'detection_{}.png'.format(int(time.time()))
    # # Guardar la imagen en un archivo
    # cv2.imwrite(filename, image)
    # # Enviar la imagen por correo
    # enviar_correo(filename)
    # # Enviar un mensaje SMS
    # enviar_sms()

    if os.path.exists('detection.png'):
        os.remove('detection.png')
    # Guardar la imagen en un archivo
    cv2.imwrite('detection.png', image)
    # Enviar la imagen por correo
    enviar_correo('detection.png')
    # Enviar un mensaje SMS
    enviar_sms()

cap = cv2.VideoCapture(0)
model = YOLO('yolov8s')

last_sms_time = 0
sms_interval = 20  # Intervalo de tiempo mínimo entre mensajes SMS en segundos

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(frame,stream=True,verbose=False,conf = 0.75,classes=[0])
    annotator = Annotator(frame)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            r = box.xyxy[0]
            c = box.cls
            if int(c) == 0:
                print("¡Persona detectada!")
                current_time = time.time()
                if current_time - last_sms_time > sms_interval:
                    # Iniciar un nuevo hilo para guardar la imagen y enviar el correo
                    threading.Thread(target=save_image_and_send_email, args=(frame.copy(),)).start()
                    last_sms_time = current_time
            annotator.box_label(r, label='Persona', color=(0, 255, 0))

    cv2.imshow('Image', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()