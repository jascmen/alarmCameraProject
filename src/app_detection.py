import cv2
import threading
import tkinter as tk
from tkinter import messagebox
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
from envio_sms import enviar_sms
from envio_correo import enviar_correo
import time
import os

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.is_camera_on = False
        self.vid = None
        self.model = YOLO('yolov8s')
        self.last_sms_time = 0
        self.sms_interval = 20  # Intervalo de tiempo mínimo entre mensajes SMS en segundos

        # Botón para encender la cámara
        self.btn_start = tk.Button(window, text="Encender Sistema", width=50, command=self.open_camera)
        self.btn_start.pack(anchor=tk.CENTER, expand=True)

        # Botón para apagar la cámara
        self.btn_stop = tk.Button(window, text="Apagar Sistema", width=50, command=self.close_camera)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)

        self.window.mainloop()

    def open_camera(self):
        if not self.is_camera_on:
            self.vid = cv2.VideoCapture(0)
            if not self.vid.isOpened():
                messagebox.showerror("Error", "No se pudo abrir la cámara.")
                return
            self.is_camera_on = True
            self.btn_start.config(text="Sistema encendido")
            threading.Thread(target=self.run_object_detection).start()

    def close_camera(self):
        if self.is_camera_on:
            self.is_camera_on = False
            self.vid.release()
            self.btn_start.config(text="Encender Sistema")

    def run_object_detection(self):
        while self.is_camera_on:
            ret, frame = self.vid.read()
            if not ret:
                break

            # Realizar la detección de objetos, se configura los parámetros de confianza y las clases a detectar
            results = self.model.predict(frame,stream=True,verbose=False,conf = 0.75,classes=[0])
            annotator = Annotator(frame)

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Dibujar un rectángulo alrededor de la persona detectada
                    r = box.xyxy[0]
                    # Obtener la clase del objeto detectado
                    c = box.cls
                    if int(c) == 0:
                        print("¡Persona detectada!")
                        current_time = time.time()
                        if current_time - self.last_sms_time > self.sms_interval:
                            # Iniciar un nuevo hilo para guardar la imagen y enviar el correo
                            threading.Thread(target=self.save_image_and_send_email, args=(frame.copy(),)).start()
                            self.last_sms_time = current_time
                    annotator.box_label(r, label='Persona', color=(0, 255, 0))

        self.vid.release()

    def save_image_and_send_email(self, image):
        filename = '../images/detection_{}.png'.format(int(time.time()))
        if os.path.exists(filename):
            os.remove(filename)
        # Guardar la imagen en un archivo
        cv2.imwrite(filename, image)
        # Enviar la imagen por correo
        enviar_correo(filename)
        # Enviar un mensaje SMS
        enviar_sms()

App(tk.Tk(), "Detección")