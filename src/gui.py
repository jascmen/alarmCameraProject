import tkinter as tk
from tkinter import messagebox, simpledialog
from auth import register_user, authenticate_user, save_face_data, load_face_data
from database import init_db, add_role, get_role, get_user
from camera import Camera
from face_recognition import encode_face, compare_faces
import sqlite3
import cv2
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Alarma con Webcam")
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.cameras = []
        self.camera = Camera(0)  # Inicializa la cámara web por defecto
        self.login_screen()

    def login_screen(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Usuario").grid(row=0, column=0)
        tk.Label(self.main_frame, text="Contraseña").grid(row=1, column=0)
        self.username_entry = tk.Entry(self.main_frame)
        self.password_entry = tk.Entry(self.main_frame, show="*")
        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        tk.Button(self.main_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2)
        tk.Button(self.main_frame, text="Login con Rostro", command=self.login_with_face).grid(row=3, column=0, columnspan=2)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        authenticated, user = authenticate_user(username, password)
        if authenticated:
            role_id = user[5]
            self.load_user_interface(role_id)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def login_with_face(self):
        if not self.camera.open():
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            return

        face_image = self.camera.get_frame()
        self.camera.close()

        if face_image is None:
            messagebox.showerror("Error", "No se pudo capturar la imagen")
            return

        face_encoding = encode_face(face_image)
        if face_encoding is None:
            messagebox.showerror("Error", "No se detectó ningún rostro")
            return

        users = get_all_users()
        known_face_encodings = []
        for user in users:
            stored_face_data = load_face_data(user[5])
            stored_face_encoding = encode_face(stored_face_data)
            if stored_face_encoding is not None:
                known_face_encodings.append(stored_face_encoding)

        if compare_faces(known_face_encodings, face_encoding):
            for user in users:
                stored_face_data = load_face_data(user[5])
                stored_face_encoding = encode_face(stored_face_data)
                if stored_face_encoding is not None and compare_faces([stored_face_encoding], face_encoding):
                    role_id = user[4]
                    self.load_user_interface(role_id)
                    return
        messagebox.showerror("Error", "Rostro no reconocido")

    def load_user_interface(self, role_id):
        self.clear_frame()
        role = get_role_by_id(role_id)
        if role[1] == 'Admin':
            self.admin_menu()
        else:
            tk.Label(self.main_frame, text=f"Bienvenido, {role[1]}").pack()

    def admin_menu(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Menú de Administrador").pack()

        tk.Button(self.main_frame, text="Registrar Usuario", command=self.register_user).pack(fill='x')
        tk.Button(self.main_frame, text="Configurar Cámaras", command=self.configure_cameras).pack(fill='x')
        tk.Button(self.main_frame, text="Configurar Notificaciones", command=self.configure_notifications).pack(fill='x')
        tk.Button(self.main_frame, text="Visualizar Registros de Actividad", command=self.view_activity_logs).pack(fill='x')
        tk.Button(self.main_frame, text="Mostrar Cámaras", command=self.show_cameras).pack(fill='x')
        tk.Button(self.main_frame, text="Salir", command=self.root.quit).pack(fill='x')

    def register_user(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Registrar Usuario").pack()

        tk.Label(self.main_frame, text="Usuario").pack()
        self.username_entry = tk.Entry(self.main_frame)
        self.username_entry.pack()

        tk.Label(self.main_frame, text="Contraseña").pack()
        self.password_entry = tk.Entry(self.main_frame, show="*")
        self.password_entry.pack()

        tk.Label(self.main_frame, text="Correo Electrónico").pack()
        self.email_entry = tk.Entry(self.main_frame)
        self.email_entry.pack()

        tk.Label(self.main_frame, text="Celular").pack()
        self.celular_entry = tk.Entry(self.main_frame)
        self.celular_entry.pack()

        tk.Label(self.main_frame, text="Rol").pack()
        self.role_var = tk.StringVar(self.main_frame)
        self.role_var.set("Standard User")
        self.role_option = tk.OptionMenu(self.main_frame, self.role_var, "Power User", "Standard User", "Guest")
        self.role_option.pack()

        tk.Button(self.main_frame, text="Capturar Rostro", command=self.capture_face_for_registration).pack()

        tk.Button(self.main_frame, text="Volver", command=self.admin_menu).pack()

    def capture_face_for_registration(self):
        if not self.username_entry.get() or not self.password_entry.get() or not self.email_entry.get():
            messagebox.showerror("Error", "Por favor, complete todos los campos antes de capturar el rostro")
            return

        if not self.camera.open():
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            return

        cv2.namedWindow("Captura de Rostro")
        while True:
            ret, frame = self.camera.get_frame()  # Asegurarse de capturar correctamente ret y frame
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
            self.admin_menu()
        else:
            messagebox.showerror("Error", "Rol no válido")


    def configure_cameras(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Configurar Cámaras").pack()

        tk.Button(self.main_frame, text="Agregar Cámara", command=self.add_camera).pack(fill='x')
        tk.Button(self.main_frame, text="Volver", command=self.admin_menu).pack()

    def add_camera(self):
        camera_type = simpledialog.askstring("Tipo de Cámara", "Ingrese 'webcam' para cámara web o 'ip' para cámara IP:")
        if camera_type == 'webcam':
            source = 0  # Valor predeterminado para la cámara web
        elif camera_type == 'ip':
            source = simpledialog.askstring("URL de Cámara IP", "Ingrese la URL de la cámara IP (e.g., http://192.168.18.4:4747/video):")
            if not source:
                messagebox.showerror("Error", "URL de la cámara IP no válida")
                return
        else:
            messagebox.showerror("Error", "Tipo de cámara no válido")
            return

        new_camera = Camera(source)
        if new_camera.open():
            self.cameras.append(new_camera)
            messagebox.showinfo("Éxito", "Cámara agregada correctamente")
        else:
            messagebox.showerror("Error", "No se pudo abrir la cámara")


    def configure_notifications(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Configurar Notificaciones").pack()

        tk.Label(self.main_frame, text="Email de Notificación").pack()
        self.notification_email_entry = tk.Entry(self.main_frame)
        self.notification_email_entry.pack()

        tk.Button(self.main_frame, text="Guardar", command=self.save_notifications).pack(fill='x')
        tk.Button(self.main_frame, text="Volver", command=self.admin_menu).pack()

    def save_notifications(self):
        notification_email = self.notification_email_entry.get()
        # Implementa el guardado de la dirección de correo electrónico para notificaciones aquí
        messagebox.showinfo("Notificaciones", "Funcionalidad en desarrollo")
    def view_activity_logs(self):
        # Implementa la visualización de registros de actividad aquí
        messagebox.showinfo("Registros de Actividad", "Funcionalidad en desarrollo")

    def show_cameras(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Visualización de Cámaras").pack()

        # Frame contenedor para las cámaras
        cameras_frame = tk.Frame(self.main_frame)
        cameras_frame.pack(fill=tk.BOTH, expand=True)

        # Determina el número de columnas
        num_columns = 2  # Puedes ajustar este valor según sea necesario
        num_cameras = len(self.cameras)
        num_rows = (num_cameras + num_columns - 1) // num_columns

        # Crear una lista de frames para cada fila
        row_frames = [tk.Frame(cameras_frame) for _ in range(num_rows)]
        for rf in row_frames:
            rf.pack(fill=tk.BOTH, expand=True)

        for i, camera in enumerate(self.cameras):
            row = i // num_columns
            col = i % num_columns

            frame = tk.Frame(row_frames[row])
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

            label = tk.Label(frame, text=f"Cámara {i+1}")
            label.pack()

            canvas = tk.Canvas(frame, width=320, height=240)  # Tamaño inicial más pequeño
            canvas.pack(fill=tk.BOTH, expand=True)  # Permitir que el canvas se expanda

            self.update_camera_view(camera, canvas)

        tk.Button(self.main_frame, text="Volver", command=self.close_cameras).pack()


    def update_camera_view(self, camera, canvas):
        def update():
            ret, frame = camera.get_frame()  # Modificado para capturar correctamente ret y frame
            if ret and frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                # Redimensionar la imagen para que se ajuste al canvas
                canvas_width = canvas.winfo_width()
                canvas_height = canvas.winfo_height()
                img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

                imgtk = ImageTk.PhotoImage(image=img)
                canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                canvas.imgtk = imgtk

            canvas.after(10, update)

        update()

    def close_cameras(self):
        self.admin_menu()
        for camera in self.cameras:
            camera.close()



def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return users

def get_role_by_id(role_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM roles WHERE id = ?', (role_id,))
    role = c.fetchone()
    conn.close()
    return role

if __name__ == "__main__":
    init_db()
    if not get_role('Admin'):
        add_role('Admin')
        add_role('Power User')
        add_role('Standard User')
        add_role('Guest')
        register_user('admin', 'admin', 'admin@example.com', '941768950', get_role('Admin')[0], None)

    root = tk.Tk()
    app = App(root)
    root.mainloop()
