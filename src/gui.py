import os
import time
import customtkinter as ctk
from tkinter import messagebox, simpledialog

from dotenv import load_dotenv

from auth import register_user, authenticate_user, save_face_data, load_face_data
from database import init_db, add_role, get_role, get_user, get_users, get_role_user, get_roles
from camera import Camera
from face_recognition import encode_face, compare_faces
from detection import MobileNetSSD
import cv2
from PIL import Image, ImageTk
import threading
import queue
import pygame

from notifications import send_whatsapp_zone, send_email, send_whatsapp_admin
from towfactor import generate_secret, save_secret, generate_qr_code, verify_code, load_secret


class App:
    def __init__(self, root):
        self.current_role = None
        self.password_entry = None
        self.username_entry = None
        self.root = root
        self.root.title("Sistema de Alarma con Webcam")
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        self.cameras = []
        self.zones = []
        self.camera = Camera(1)
        self.login_screen()
        self.detector = MobileNetSSD(confidence_threshold=0.9)
        self.running = False
        self.threads = []
        # self.last_save_image_time = 0
        # self.save_image_interval = 5
        self.whatsapp_alert_sent = False
        self.whatsapp_alert_interval = 20
        self.last_whatsapp_alert_time = 0
        self.secret = load_secret()






    def login_screen(self):
        self.clear_frame()

        logo_frame = ctk.CTkFrame(self.main_frame)
        logo_frame.grid(row=0, column=0, rowspan=5, padx=20, pady=20, sticky="ns")
        system_name_label = ctk.CTkLabel(logo_frame, text="ALERTSHIELD", font=("Cascadia Code Pl", 25, "bold"), text_color="red")
        system_name_label.pack(pady=(0, 10))
        logo_image = ctk.CTkImage(Image.open("img_sistema/LOGO ALERTSHIELD.jpg"), size=(200, 200))
        logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="")
        logo_label.pack(pady=10)

        ctk.CTkLabel(self.main_frame, text="Inicio de Sesión", font=("Cascadia Code Pl", 20)).grid(row=0, column=1, columnspan=2,
                                                                                                   pady=20)

        user_icon = ctk.CTkImage(Image.open("img_sistema/user-logo.png"), size=(20, 20))
        ctk.CTkLabel(self.main_frame, text="  Usuario", font=("Cascadia Code Pl", 15), image=user_icon, compound="left", anchor='w').grid(row=1,
                                                                                                                                          column=1,
                                                                                                                                          sticky="ew",
                                                                                                                                          padx=10,
                                                                                                                                          pady=(10, 5))
        self.username_entry = ctk.CTkEntry(self.main_frame)
        self.username_entry.grid(row=1, column=2, sticky="ew", padx=10, pady=(10, 5))

        pass_icon = ctk.CTkImage(Image.open("img_sistema/password-logo.png"), size=(20, 20))
        ctk.CTkLabel(self.main_frame, text="  Contraseña", font=("Cascadia Code Pl", 15), image=pass_icon, compound="left", anchor='w').grid(row=2,
                                                                                                                                             column=1,
                                                                                                                                             sticky="ew",
                                                                                                                                             padx=10,
                                                                                                                                             pady=(
                                                                                                                                                 5, 10))
        self.password_entry = ctk.CTkEntry(self.main_frame, show="*")
        self.password_entry.grid(row=2, column=2, sticky="ew", padx=10, pady=(5, 10))

        ctk.CTkButton(self.main_frame, text="Login", font=("Cascadia Code Pl", 13), command=self.login).grid(row=3, column=1, columnspan=2, pady=10)

        ctk.CTkButton(self.main_frame, text="Login con Rostro", font=("Cascadia Code Pl", 13), command=self.login_with_face).grid(row=4, column=1,
                                                                                                                                  columnspan=2,
                                                                                                                                  pady=10)

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        authenticated, user = authenticate_user(username, password)
        if authenticated:
            role_id = user[5]
            self.load_user_interface(username, role_id)

        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def login_with_face(self):
        username = self.username_entry.get()
        self.clear_frame()
        role = get_role_user(username)
        if not username:
            messagebox.showerror("Error", "Por favor, ingrese el nombre de usuario")
            return

        loading_label = ctk.CTkLabel(self.main_frame, text="Preparando captura de rostro...")
        loading_label.grid(row=2, columnspan=2, pady=10)
        self.root.update_idletasks()

        if not self.camera.open():
            loading_label.destroy()
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            return

        face_image = None
        cv2.namedWindow("Captura de Rostro, presione ESC para capturar")

        loading_label.destroy()

        while True:
            ret, frame = self.camera.get_frame()
            if ret:
                cv2.imshow("Captura de Rostro, presione ESC para capturar", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # Presiona ESC para capturar el rostro
                    face_image = frame
                    break

        cv2.destroyAllWindows()
        self.camera.close()

        if face_image is None:
            messagebox.showerror("Error", "No se pudo capturar la imagen")
            return

        face_encoding = encode_face(face_image)
        if face_encoding is None:
            messagebox.showerror("Error", "No se detectó ningún rostro")
            return

        user = get_user(username)
        if user is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        stored_face_data = load_face_data(user[6])
        stored_face_encoding = encode_face(stored_face_data)
        if stored_face_encoding is not None and compare_faces(stored_face_encoding, face_encoding):
            self.load_user_interface(user[1], user[5])
        else:
            messagebox.showerror("Error", "Rostro no reconocido")
            self.login_screen()

    def load_user_interface(self,username, role_id):
        self.clear_frame()
        role = get_role_user(role_id)
        name = get_user(username)
        self.current_role = role[0]
        if role[0] == 1:
            self.admin_menu()
        elif role[0] == 2:
            self.monitor_menu()
        else:
            ctk.CTkLabel(self.main_frame, text=f"Bienvenido, {name[1]}").pack()

    def admin_menu(self):
        self.clear_frame()

        ctk.CTkLabel(self.main_frame, text="Menú de Administrador", font=("Cascadia Code Pl", 25, "bold"),
                     text_color="#ffffff").pack(pady=20)

        menu_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        menu_frame.pack(padx=20, pady=20, fill='both', expand=True)

        button_config = {
            "width": 300,
            "height": 50,
            "corner_radius": 10,
            "font": ("Cascadia Code Pl", 15),
            "hover_color": "#ff6600",
            "compound": "left",
            "anchor": "w"
        }

        icon_size = (20, 20)
        user_icon = ctk.CTkImage(Image.open("img_sistema/add-user.png"), size=icon_size)
        camera_icon = ctk.CTkImage(Image.open("img_sistema/config_cam.png"), size=icon_size)
        notification_icon = ctk.CTkImage(Image.open("img_sistema/config_notificaciones.png"), size=icon_size)
        logs_icon = ctk.CTkImage(Image.open("img_sistema/registro_actv.png"), size=icon_size)
        monitor_icon = ctk.CTkImage(Image.open("img_sistema/sist_monitoreo.png"), size=icon_size)
        detection_icon = ctk.CTkImage(Image.open("img_sistema/deteccion_st.png"), size=icon_size)
        exit_icon = ctk.CTkImage(Image.open("img_sistema/salir.png"), size=icon_size)

        ctk.CTkButton(menu_frame, text="Registrar Usuario", image=user_icon, command=self.register_user,
                      **button_config).pack(pady=10, padx=10)
        #boton para vincular autenticador de google
        ctk.CTkButton(menu_frame, text="Vincular Autenticador de Google", image=user_icon, command=self.link_autenticator,**button_config).pack(pady=10, padx=10)
        ctk.CTkButton(menu_frame, text="Configurar Cámaras", image=camera_icon, command=self.configure_cameras,
                      **button_config).pack(pady=10, padx=10)
        # ctk.CTkButton(menu_frame, text="Configurar Notificaciones", image=notification_icon,
        #               command=self.configure_notifications, **button_config).pack(pady=10, padx=10)
        ctk.CTkButton(menu_frame, text="Visualizar Registros de Actividad", image=logs_icon,
                      command=self.view_activity_logs, **button_config).pack(pady=10, padx=10)
        ctk.CTkButton(menu_frame, text="Encender Sistema de Monitoreo", image=monitor_icon, command=self.show_cameras,
                      **button_config).pack(pady=10, padx=10)
        ctk.CTkButton(menu_frame, text="Encender Sistema de Detección", image=detection_icon,
                      command=self.start_system_alarm, **button_config).pack(pady=10, padx=10)
        ctk.CTkButton(menu_frame, text="Salir", image=exit_icon, command=self.root.quit,
                      **button_config).pack(pady=10, padx=10)

        self.main_frame.configure(fg_color="#333333")
        self.root.configure(bg="#333333")

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def monitor_menu(self):
        self.clear_frame()
        #ctk.CTkLabel(self.main_frame, text=f"Bienvenido, {name[1]}").pack()

        ctk.CTkButton(self.main_frame, text="Configurar Cámaras", command=self.configure_cameras).pack(fill='x')
        ctk.CTkButton(self.main_frame, text="Encender Sistema de monitoreo", command=self.show_cameras).pack(fill='x')
        #ctk.CTkButton(self.main_frame, text="Encender Sistema de Deteccion", command=self.start_system_alarm).pack(fill='x')
        ctk.CTkButton(self.main_frame, text="Salir", command=self.root.quit).pack(fill='x')

    def register_user(self):
        self.clear_frame()

        ctk.CTkLabel(self.main_frame, text="Registrar Usuario", font=("Cascadia Code Pl", 25, "bold"),
                     text_color="#ffffff").pack(pady=20)

        form_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        form_frame.pack(padx=20, pady=20, fill='both', expand=True)

        field_config = {
            "font": ("Cascadia Code Pl", 15),
            "text_color": "#ffffff",
            "corner_radius": 10,
            "padx": 10,
            "pady": 10
        }

        entry_config = {
            "width": 300,
            "height": 30,
            "corner_radius": 10,
            "font": ("Cascadia Code Pl", 15)
        }

        user_icon = ctk.CTkImage(Image.open("img_sistema/add-user.png"), size=(20, 20))
        ctk.CTkLabel(form_frame, text="Usuario", image=user_icon, compound="left", anchor='w', **field_config).pack()
        self.username_entry = ctk.CTkEntry(form_frame, **entry_config)
        self.username_entry.pack()

        pass_icon = ctk.CTkImage(Image.open("img_sistema/password-logo.png"), size=(20, 20))
        ctk.CTkLabel(form_frame, text="Contraseña", image=pass_icon, compound="left", anchor='w', **field_config).pack()
        self.password_entry = ctk.CTkEntry(form_frame, show="*", **entry_config)
        self.password_entry.pack()

        email_icon = ctk.CTkImage(Image.open("img_sistema/email.png"), size=(20, 20))
        ctk.CTkLabel(form_frame, text="Correo Electrónico", image=email_icon, compound="left", anchor='w',
                     **field_config).pack()
        self.email_entry = ctk.CTkEntry(form_frame, **entry_config)
        self.email_entry.pack()

        phone_icon = ctk.CTkImage(Image.open("img_sistema/phone.png"), size=(20, 20))
        ctk.CTkLabel(form_frame, text="Celular", image=phone_icon, compound="left", anchor='w', **field_config).pack()
        self.celular_entry = ctk.CTkEntry(form_frame, **entry_config)
        self.celular_entry.pack()

        roles = get_roles()
        role_names = [role[1] for role in roles]

        ctk.CTkLabel(form_frame, text="Rol", **field_config).pack()
        self.role_var = ctk.StringVar(form_frame)
        if role_names:
            self.role_var.set(role_names[0])

        self.role_option = ctk.CTkOptionMenu(
            form_frame,
            variable=self.role_var,
            values=role_names,
            font=("Cascadia Code Pl", 15),
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            text_color="#ffffff",
            dropdown_fg_color="#333333",
            dropdown_hover_color="#444444"
        )
        self.role_option.pack(pady=10)

        ctk.CTkButton(form_frame, text="Capturar Rostro", command=self.capture_face_for_registration,
                      width=300, height=50, corner_radius=10, font=("Cascadia Code Pl", 15),
                      hover_color="#ff6600").pack(pady=20)

        ctk.CTkButton(form_frame, text="Volver", command=self.load_interface_by_role,
                      width=300, height=50, corner_radius=10, font=("Cascadia Code Pl", 15),
                      hover_color="#ff6600").pack(pady=10)

        self.main_frame.configure(fg_color="#333333")
        self.root.configure(bg="#333333")

    def capture_face_for_registration(self):
        if not self.username_entry.get() or not self.password_entry.get() or not self.email_entry.get():
            messagebox.showerror("Error", "Por favor, complete todos los campos antes de capturar el rostro")
            return

        if not self.camera.open():
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            return

        cv2.namedWindow("Captura de Rostro")
        while True:
            ret, frame = self.camera.get_frame()
            if ret:
                cv2.imshow("Captura de Rostro", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # Presiona ESC para capturar el rostro
                    face_image = frame
                    break

        cv2.destroyAllWindows()
        self.camera.close()

        face_encoding = encode_face(face_image)
        if face_encoding is None:
            messagebox.showerror("Error", "No se detectó ningún rostro")
            return

        face_data = save_face_data(face_image)
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        celular = self.celular_entry.get()
        role_name = self.role_var.get()
        role = get_role(role_name)
        if role:
            register_user(username, password, email, celular, role[0], face_data)
            messagebox.showinfo("Éxito", "Usuario registrado con éxito")
            threading.Thread(target=self.send_email_user, args=(email,)).start()
            self.admin_menu()
        else:
            messagebox.showerror("Error", "Rol no válido")

    def configure_cameras(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Configurar Cámaras", font=("Cascadia Code Pl", 25, "bold"),
                     text_color="#ffffff").pack(pady=20)

        camera_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        camera_frame.pack(padx=20, pady=20, fill='both', expand=True)

        button_config = {
            "width": 300,
            "height": 50,
            "corner_radius": 10,
            "font": ("Cascadia Code Pl", 15),
            "hover_color": "#ff6600",
            "compound": "left",
            "anchor": "w"
        }

        add_camera_icon = ctk.CTkImage(Image.open("img_sistema/config_cam.png"), size=(20, 20))
        back_icon = ctk.CTkImage(Image.open("img_sistema/volver_icon.png"), size=(20, 20))

        ctk.CTkButton(camera_frame, text="Agregar Cámara", image=add_camera_icon, command=self.add_camera,
                      **button_config).pack(pady=10)
        ctk.CTkButton(camera_frame, text="Volver", image=back_icon, command=self.load_interface_by_role, **button_config).pack(
            pady=10)

    def add_camera(self):
        source = simpledialog.askstring("URL de Cámara IP",
                                        "Ingrese la URL de la cámara IP o el índice de la cámara web (e.g., 0 para la primera cámara web):")
        if not source:
            messagebox.showerror("Error", "URL de la cámara IP no válida")
            return

        try:
            source = int(source)
        except ValueError:
            pass

        for cam in self.cameras:
            if cam.source == source:
                messagebox.showinfo("Info", "La cámara ya está en la lista")
                return

        zone = simpledialog.askstring("Zona de la Cámara", "Ingrese la zona de la cámara (e.g., zona 1):")
        if not zone:
            messagebox.showerror("Error", "Zona no válida")
            return

        if zone in self.zones:
            messagebox.showinfo("Info", "La zona ya está en la lista")
            return

        new_camera = Camera(source, zone)
        if new_camera.open():
            while True:
                ret, frame = new_camera.cap.read()
                if not ret:
                    messagebox.showerror("Error", "No se pudo obtener la señal de la cámara")
                    new_camera.close()
                    return

                cv2.imshow('Vista previa: ESC para cancelar, Y para agregar', frame)
                key = cv2.waitKey(1)
                if key == ord('y') or key == ord('Y'):
                    new_camera.close()
                    self.cameras.append(new_camera)
                    self.zones.append(zone)
                    cv2.destroyAllWindows()
                    messagebox.showinfo("Éxito", f"Cámara agregada correctamente en {zone}")
                    break
                elif key == 27:  # ESC key
                    new_camera.close()
                    cv2.destroyAllWindows()
                    messagebox.showinfo("Cancelado", "Cámara no agregada")
                    break
        else:
            messagebox.showerror("Error", "No se pudo abrir la cámara")

    # def configure_notifications(self, button_config=None):
    #     self.clear_frame()
    #     ctk.CTkLabel(self.main_frame, text="Configurar Notificaciones", font=("Cascadia Code Pl", 25, "bold"),
    #                  text_color="#ffffff").pack(pady=20)
    #
    #     notification_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
    #     notification_frame.pack(padx=20, pady=20, fill='both', expand=True)
    #
    #     input_config = {
    #         "width": 300,
    #         "height": 40,
    #         "corner_radius": 10,
    #         "font": ("Cascadia Code Pl", 15)
    #     }
    #
    #     ctk.CTkLabel(notification_frame, text="Email de Notificación").pack(pady=10)
    #     self.notification_email_entry = ctk.CTkEntry(notification_frame, **input_config)
    #     self.notification_email_entry.pack(pady=10)
    #
    #     if button_config is None:
    #         button_config = {
    #             "width": 300,
    #             "height": 50,
    #             "corner_radius": 10,
    #             "font": ("Cascadia Code Pl", 15),
    #             "hover_color": "#ff6600"
    #         }
    #
    #     ctk.CTkButton(notification_frame, text="Guardar", command=self.save_notifications, **button_config).pack(
    #         pady=10)
    #     ctk.CTkButton(notification_frame, text="Volver", command=self.load_interface_by_role, **button_config).pack(pady=10)
    #
    #     notification_frame.grid_columnconfigure(0, weight=1)
    #     notification_frame.grid_columnconfigure(1, weight=1)

    def save_notifications(self):
        notification_email = self.notification_email_entry.get()
        messagebox.showinfo("Notificaciones", "Funcionalidad en desarrollo")

    def view_activity_logs(self):
        messagebox.showinfo("Registros de Actividad", "Funcionalidad en desarrollo")

    def show_cameras(self):
        self.clear_frame()
        self.loading_label = ctk.CTkLabel(self.main_frame, text="Cargando cámaras...", font=("Cascadia Code Pl", 15))
        self.loading_label.pack()
        self.root.update_idletasks()

        for camera in self.cameras:
            if not camera.open():
                messagebox.showerror("Error", f"No se pudo abrir la cámara con source {camera.source}")
                return

        self.loading_label.destroy()
        ctk.CTkLabel(self.main_frame, text="Visualización de Cámaras", font=("Cascadia Code Pl", 20, "bold")).pack()

        cameras_frame = ctk.CTkFrame(self.main_frame)
        cameras_frame.pack(fill=ctk.BOTH, expand=True)

        num_columns = 2
        num_cameras = len(self.cameras)
        num_rows = (num_cameras + num_columns - 1) // num_columns

        row_frames = [ctk.CTkFrame(cameras_frame) for _ in range(num_rows)]
        for rf in row_frames:
            rf.pack(fill=ctk.BOTH, expand=True)

        for i, camera in enumerate(self.cameras):
            row = i // num_columns
            col = i % num_columns

            frame = ctk.CTkFrame(row_frames[row])
            frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5, pady=5)

            label = ctk.CTkLabel(frame, text=f"Cámara {i + 1}, {camera.zone}", font=("Cascadia Code Pl", 15))
            label.pack()

            canvas = ctk.CTkCanvas(frame, width=320, height=240)
            canvas.pack(fill=ctk.BOTH, expand=True)

            self.update_camera_check(camera, canvas)
            ctk.CTkButton(frame, text="WhatsApp Zona", command=lambda zone=camera.zone: self.alert_zone(zone)).pack()

        ctk.CTkButton(self.main_frame, text="Sonar Alerta", command=self.sound_alert).pack()

        ctk.CTkButton(self.main_frame, text="Volver", command=self.close_cameras).pack()

    def update_camera_check(self, camera, canvas):
        def update():
            ret, frame = camera.get_frame()
            if ret and frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                canvas_width = canvas.winfo_width()
                canvas_height = canvas.winfo_height()
                if canvas_width != img.width or canvas_height != img.height:
                    img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

                imgtk = ImageTk.PhotoImage(image=img)
                canvas.create_image(0, 0, anchor=ctk.NW, image=imgtk)
                canvas.imgtk = imgtk

            canvas.after(30, update)

        update()

    def start_system_alarm(self):
        if not self.secret:
            messagebox.showerror("Error", "Debe vincular el autenticador antes de usar el sistema de alarma.")
            return
        self.clear_frame()
        self.loading_label = ctk.CTkLabel(self.main_frame, text="Cargando cámaras...", font=("Cascadia Code Pl", 15))
        self.loading_label.pack()
        self.root.update_idletasks()

        for camera in self.cameras:
            if not camera.open():
                messagebox.showerror("Error", f"No se pudo abrir la cámara con source {camera.source}")
                return

        self.loading_label.destroy()
        ctk.CTkLabel(self.main_frame, text="Sistema de Alarma - Detección de Personas",
                     font=("Cascadia Code Pl", 20, "bold")).pack()

        cameras_frame = ctk.CTkFrame(self.main_frame)
        cameras_frame.pack(fill=ctk.BOTH, expand=True)

        num_columns = 2
        num_cameras = len(self.cameras)
        num_rows = (num_cameras + num_columns - 1) // num_columns

        row_frames = [ctk.CTkFrame(cameras_frame) for _ in range(num_rows)]
        for rf in row_frames:
            rf.pack(fill=ctk.BOTH, expand=True)

        self.running = True

        for i, camera in enumerate(self.cameras):
            row = i // num_columns
            col = i % num_columns

            frame = ctk.CTkFrame(row_frames[row])
            frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5, pady=5)

            label = ctk.CTkLabel(frame, text=f"Cámara {i + 1}, Zone {camera.zone}", font=("Cascadia Code Pl", 15))
            label.pack()

            canvas = ctk.CTkCanvas(frame, width=320, height=240)
            canvas.pack(fill=ctk.BOTH, expand=True)

            q = queue.Queue()
            t = threading.Thread(target=self.update_camera_view, args=(camera, q, True))
            t.start()
            self.threads.append(t)

            self.root.after(100, self.update_canvas, canvas, q)


        ctk.CTkButton(self.main_frame, text="Volver", command=self.authenticate_and_close).pack()
        # Guardar el protocolo original para restaurarlo después si es necesario
        self.original_close_protocol = self.root.protocol("WM_DELETE_WINDOW")

        # Configurar el nuevo protocolo
        self.root.protocol("WM_DELETE_WINDOW", self.authenticate_and_close)


    def update_camera_view(self, camera, q, detect_person=False):
        while self.running:
            ret, frame = camera.get_frame()
            if ret and frame is not None:
                if detect_person:
                    frame, detections,save_image = self.detector.detect(frame)
                    if save_image:
                        current_time = time.time()
                        if current_time - self.last_whatsapp_alert_time > self.whatsapp_alert_interval:
                            threading.Thread(target=self.send_whatsapp_alert_detection).start()
                            self.whatsapp_alert_sent = True
                            self.last_whatsapp_alert_time = current_time
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                q.put(img)
                time.sleep(0.1)

    def update_canvas(self, canvas, q):
        if not canvas.winfo_exists():
            return

        try:
            img = q.get_nowait()
        except queue.Empty:
            pass
        else:
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            if canvas_width != img.width or canvas_height != img.height:
                img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

            imgtk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=ctk.NW, image=imgtk)
            canvas.imgtk = imgtk

        if self.running:
            self.root.after(100, self.update_canvas, canvas, q)

    def close_cameras(self):
        self.running = False
        for t in self.threads:
            t.join()

        for camera in self.cameras:
            camera.close()
        self.clear_frame()
        self.load_interface_by_role()
    def load_interface_by_role(self):
        if self.current_role == 1:
            self.admin_menu()
        elif self.current_role == 2:
            self.monitor_menu()
        else:
            self.admin_menu()
            ctk.CTkLabel(self.main_frame, text=f"Bienvenido, {self.current_role}").pack()
       
    def sound_alert(self):
        threading.Thread(target=self.play_sound).start()

    def play_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("../sounds/alarm.mp3")
        pygame.mixer.music.play(0)

        pygame.time.wait(3000)

        pygame.mixer.music.stop()
        pygame.mixer.quit()

    def alert_zone(self, zone):
        threading.Thread(target=self.send_whatsapp_alert, args=(zone,)).start()

    def send_whatsapp_alert(self, zone):
        send_whatsapp_zone(zone)

    def send_whatsapp_alert_detection(self):
        send_whatsapp_admin()
        threading.Thread(target=self.reset_whatsapp_alert).start()

    def reset_whatsapp_alert(self):
        time.sleep(self.whatsapp_alert_interval)
        self.whatsapp_alert_sent = False

    def send_email_user(self,correo):
        send_email(correo)

    def authenticate_and_close(self):
        code = simpledialog.askstring("Autenticación", "Ingrese el código del autenticador:")
        if code and verify_code(self.secret, code):
            # Restaurar el protocolo original antes de cerrar
            self.root.protocol("WM_DELETE_WINDOW", self.original_close_protocol)
            self.close_cameras()
        else:
            messagebox.showerror("Error", "Código incorrecto. No se puede apagar el sistema.")
    def link_autenticator(self):
        self.secret = generate_secret()
        save_secret(self.secret)
        generate_qr_code(self.secret, "AdminAccount")
        self.show_qr_code()

    def show_qr_code(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_frame, text="Escanea el código QR para vincular tu autenticador de Google",
                     font=("Cascadia Code Pl", 20, "bold")).pack()

        qr_code = ctk.CTkImage(Image.open("qrcode.png"), size=(200, 200))
        ctk.CTkLabel(self.main_frame, image=qr_code).pack()

        ctk.CTkButton(self.main_frame, text="Volver", command=self.load_interface_by_role).pack()




    # def save_image(self, image):
    #     local_path = self.detector.save_image(image)
    #
    #     # Sube el archivo a Google Drive en un hilo separado
    #     thread = threading.Thread(target=upload_to_drive, args=(self.service, local_path, self.folder_id))
    #     thread.start()
    #
    #     folder_url = f"https://drive.google.com/drive/folders/{self.folder_id}"
    #     #print(f'File uploaded. Folder URL: {folder_url}')
    #     send_email(folder_url)








if __name__ == "__main__":
    init_db()
    if not get_role('Admin'):
        add_role('Admin')
        add_role('Monitoreo')
        add_role('General')
        register_user('admin', 'admin', 'admin@example.com', '941768950', get_role('Admin')[0], None)

    root = ctk.CTk()
    app = App(root)
    root.mainloop()
