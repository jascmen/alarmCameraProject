import cv2
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
from envio_sms import enviar_sms
from envio_correo import enviar_correo
import time
import os
import numpy as np

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.is_camera_on = False
        self.vid = None
        self.model = YOLO('yolov8s')
        self.last_sms_time = 0
        self.sms_interval = 20  # Intervalo de tiempo mínimo entre mensajes SMS en segundos

        # Crear un label para mostrar la imagen de la cámara
        self.image_label = tk.Label(window)
        self.image_label.pack(padx=10, pady=10)

        # Botón para encender la cámara
        self.btn_start = tk.Button(window, text="Encender Sistema", width=50, command=self.open_camera)
        self.btn_start.pack(anchor=tk.CENTER, expand=True)

        # Botón para apagar la cámara
        self.btn_stop = tk.Button(window, text="Apagar Sistema", width=50, command=self.close_camera)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)

        # Mostrar una imagen gris cuando la cámara no está encendida
        self.gray_image = ImageTk.PhotoImage(Image.fromarray(np.zeros((500, 500, 3), dtype=np.uint8)))
        self.image_label.config(image=self.gray_image)

        # Iniciar el bucle principal de la interfaz
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
            self.image_label.config(image=self.gray_image)
            self.image_label.update()

    def run_object_detection(self):
        while self.is_camera_on:
            ret, frame = self.vid.read()
            if not ret:
                break

            results = self.model.predict(frame,stream=True,verbose=False,conf = 0.75,classes=[0])
            annotator = Annotator(frame)

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    r = box.xyxy[0]
                    c = box.cls
                    if int(c) == 0:
                        print("¡Persona detectada!")
                        current_time = time.time()
                        if current_time - self.last_sms_time > self.sms_interval:
                            # Iniciar un nuevo hilo para guardar la imagen y enviar el correo
                            threading.Thread(target=self.save_image_and_send_email, args=(frame.copy(),)).start()
                            self.last_sms_time = current_time
                    annotator.box_label(r, label='Persona', color=(0, 255, 0))

            # Convertir la imagen de OpenCV a una imagen de Tkinter y mostrarla
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.image_label.config(image=imgtk)
            self.image_label.image = imgtk

        self.vid.release()

    def save_image_and_send_email(self, image):
        filename = 'detection_{}.png'.format(int(time.time()))
        if os.path.exists(filename):
            os.remove(filename)
        # Guardar la imagen en un archivo
        cv2.imwrite(filename, image)
        # Enviar la imagen por correo
        enviar_correo(filename)
        # Enviar un mensaje SMS
        enviar_sms()

App(tk.Tk(), "Detección de objetos")