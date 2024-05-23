import os
from twilio.rest import Client
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage




def send_sms():

    load_dotenv()

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body='Personas detectadas en la zona, revisa tu email para ver la imagen',
        from_='+14356592185',
        to='+51941768950'
    )

def send_email(filename):
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

    with open('templates/email.html', 'r') as file:
        html = file.read()

    # Adjuntar el mensaje al cuerpo del correo
    mensaje.attach(MIMEText(html, 'html'))

    # Adjuntar la imagen al correo
    with open(filename, 'rb') as file:
        img = MIMEImage(file.read())
    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
    mensaje.attach(img)

    # Crear la conexión con el servidor
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #conexion segura
    server.starttls()
    server.login(remitente, os.getenv("PASS"))

    # Enviar el mensaje
    server.sendmail(remitente, destinatario, mensaje.as_string())
    server.quit()


def send_whatsapp_zone(zone):

    load_dotenv()

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Alerta en la zona ' + zone + ', avisar al personal de seguridad',
        to='whatsapp:+51941768950'
    )
    #print(message.sid)



