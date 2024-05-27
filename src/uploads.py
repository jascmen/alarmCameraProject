import os.path
import pickle
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Si modificas estos alcances, elimina el archivo token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.pickle'):
        print("Cargando token de acceso desde token.pickle...")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        print("token.pickle no encontrado.")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("El token ha expirado, refrescando el token...")
            creds.refresh(Request())
        else:
            print("Autenticando con OAuth 2.0...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("Autenticación completada.")

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            print("Token de acceso guardado en token.pickle.")

    service = build('drive', 'v3', credentials=creds)
    print("Servicio de Google Drive autenticado correctamente.")
    return service


def upload_to_drive(service, filename, folder_id):
    file_metadata = {'name': os.path.basename(filename), 'parents': [folder_id]}
    media = MediaFileUpload(filename, mimetype='image/png')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return f"https://drive.google.com/file/d/{file['id']}/view"


# Ejecutar la función para probar la autenticación
authenticate_google_drive()
