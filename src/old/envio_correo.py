import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def enviar_correo(image_path):
    #cargar variables de entorno desde el archivo .env
    load_dotenv()

    remitente = os.getenv("USER")
    destinatario = "jascmen@gmail.com"
    asunto = 'Alerta de persona detectada'

    # Cuerpo del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    with open('../email.html', 'r') as file:
        html = file.read()

    # Adjuntar el mensaje al cuerpo del correo
    mensaje.attach(MIMEText(html, 'html'))

    # Adjuntar la imagen al correo
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read())
    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
    mensaje.attach(img)

    # Crear la conexión con el servidor
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #conexion segura
    server.starttls()
    server.login(remitente, os.getenv("PASS"))

    # Enviar el mensaje
    server.sendmail(remitente, destinatario, mensaje.as_string())
    server.quit()