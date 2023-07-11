import os
import pickle
import base64
import email
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Escopos necesarios para acceder a la bandeja de entrada de Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None

    # Si ya se ha autorizado, carga las credenciales del token almacenado en disco
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas disponibles, realiza el flujo de autenticación.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guarda las credenciales para el próximo inicio de sesión
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)

    return service

def get_emails(num_emails):
    service = get_gmail_service()

    # Llama al método de la API para obtener los mensajes de la bandeja de entrada
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    # Procesa los mensajes
    for i, message in enumerate(messages):
        if i >= num_emails:
            break
        
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_data = msg['payload']['headers']
        
        # Extrae el asunto y el remitente del mensaje
        for values in email_data:
            name = values['name']
            if name == 'Subject':
                subject = values['value']
            if name == 'From':
                sender = values['value']
        
        # Imprime el asunto y el remitente del mensaje
        print('Asunto:', subject)
        print('Remitente:', sender)
        print('---')
num_emails = int(input('Ingrese la cantidad de correos electrónicos a mostrar: '))
get_emails(num_emails)
