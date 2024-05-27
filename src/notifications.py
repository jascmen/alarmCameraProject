import os
from twilio.rest import Client
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText




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

def send_email(url):
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    remitente = os.getenv("USER")
    destinatario = "teamga94@gmail.com"
    asunto = 'Alerta de persona detectada'

    # Cuerpo del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    with open('templates/email.html', 'r') as file:
        html = file.read()

    # Reemplazar "url" en la plantilla HTML con la URL real
    html = html.replace("url", url)

    # Adjuntar el mensaje al cuerpo del correo
    mensaje.attach(MIMEText(html, 'html'))

    # Crear la conexión con el servidor
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # Conexion segura
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

def send_whatsapp_admin():

    load_dotenv()
    link_drive = os.getenv("LINK_DRIVE")

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Persona detectada en el loca, revise el enlace para ver los archivos:'+link_drive +' \nDe ser necesario avise a las autoridades.',
        to='whatsapp:+51941768950'
    )
    #print(message.sid)



