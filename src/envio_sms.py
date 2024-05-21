# envio_sms.py
import os
from twilio.rest import Client
from dotenv import load_dotenv

def enviar_sms():
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

    #print(message.sid)
