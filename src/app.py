import threading
import tkinter as tk
import time
from tkinter import messagebox, simpledialog, Toplevel
from camera import Camera
from detection import ObjectDetection
from notifications import send_sms, send_email
from towfactor import generate_secret, generate_qr_code, verify_code, save_secret, load_secret
from PIL import Image, ImageTk

import os
from dotenv import load_dotenv
import telebot



class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.is_camera_on = False
        self.camera = Camera()
        self.object_detection = ObjectDetection()
        self.last_sms_time = 0
        self.sms_interval = 20  # Intervalo de tiempo mínimo entre mensajes SMS en segundos
        self.secret = load_secret()



        self.main_menu()

    def main_menu(self):
        # Limpiar la ventana
        for widget in self.window.winfo_children():
            widget.destroy()

        # Botón para vincular autenticador
        self.btn_link_authenticator = tk.Button(self.window, text="Vincular autenticador", width=50, command=self.link_authenticator)
        self.btn_link_authenticator.pack(anchor=tk.CENTER, expand=True)

        # Botón para sistema de alarma
        self.btn_alarm_system = tk.Button(self.window, text="Sistema Alarma", width=50, command=self.alarm_system)
        self.btn_alarm_system.pack(anchor=tk.CENTER, expand=True)

        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)

    def link_authenticator(self):
        self.secret = generate_secret()
        save_secret(self.secret)
        generate_qr_code(self.secret, "MyAppAccount")
        self.show_qr_code()

    def show_qr_code(self):
        qr_window = Toplevel(self.window)
        qr_window.title("Escanee este código QR con su autenticador")
        qr_image = Image.open("qrcode.png")
        qr_photo = ImageTk.PhotoImage(qr_image)
        qr_label = tk.Label(qr_window, image=qr_photo)
        qr_label.image = qr_photo
        qr_label.pack()

    def alarm_system(self):
        if not self.secret:
            messagebox.showerror("Error", "Debe vincular el autenticador antes de usar el sistema de alarma.")
            return

        # Limpiar la ventana
        for widget in self.window.winfo_children():
            widget.destroy()

        # Botón para encender la cámara
        self.btn_start = tk.Button(self.window, text="Encender Sistema", width=50, command=self.open_camera)
        self.btn_start.pack(anchor=tk.CENTER, expand=True)

        # Botón para apagar la cámara
        self.btn_stop = tk.Button(self.window, text="Apagar Sistema", width=50, command=self.authenticate_and_close)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)

        # Deshabilitar el botón de cerrar ventana (la 'X')
        self.window.protocol("WM_DELETE_WINDOW", self.disable_event)

    def disable_event(self):
        pass

    def open_camera(self):
        if not self.is_camera_on:
            if not self.camera.open():
                messagebox.showerror("Error", "No se pudo abrir la cámara.")
                return
            self.is_camera_on = True
            self.btn_start.config(text="Sistema encendido")
            threading.Thread(target=self.run_object_detection).start()

    def authenticate_and_close(self):
        code = simpledialog.askstring("Autenticación", "Ingrese el código del autenticador:")
        if code and verify_code(self.secret, code):
            self.close_camera()
            self.main_menu()
        else:
            messagebox.showerror("Error", "Código incorrecto. No se puede apagar el sistema.")

    def close_camera(self):
        if self.is_camera_on:
            self.is_camera_on = False
            self.camera.close()
            self.btn_start.config(text="Encender Sistema")

    def run_object_detection(self):
        while self.is_camera_on:
            frame = self.camera.get_frame()
            if frame is None:
                break

            # Realizar la detección de objetos
            detections = self.object_detection.detect(frame)
            for box, label in detections:
                if label == 'Persona':
                    print("¡Persona detectada!")
                    current_time = time.time()
                    if current_time - self.last_sms_time > self.sms_interval:
                        # Iniciar un nuevo hilo para guardar la imagen y enviar el correo
                        threading.Thread(target=self.save_image_and_send_notifications, args=(frame.copy(),)).start()
                        self.last_sms_time = current_time

        self.camera.close()

    def save_image_and_send_notifications(self, image):
        filename = self.object_detection.save_image(image)
        send_email(filename)
        send_sms()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, "Detección")
    root.mainloop()
