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
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guarda las credenciales para el próximo inicio de sesión
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Crea un objeto de servicio de la API de Gmail
    service = build('gmail', 'v1', credentials=creds)

    return service

def get_emails(num_emails):
    # Obtiene el servicio de la API de Gmail
    service = get_gmail_service()

    # Llama al método de la API para obtener los mensajes de la bandeja de entrada
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    # Diccionario para almacenar los mensajes
    email_dict = {}

    # Procesa los mensajes
    for i, message in enumerate(messages):
        if i == num_emails:
            break

        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_data = msg['payload']['headers']
        is_read = 'UNREAD' if 'UNREAD' in msg['labelIds'] else 'READ'
        received_time = msg['internalDate']
        
        # Extrae el asunto y el remitente del mensaje
        for values in email_data:
            name = values['name']
            if name == 'Subject':
                subject = values['value']
            if name == 'From':
                sender = values['value']
        
        # Almacena el mensaje en el diccionario
        email_dict[i+1] = {
            'Asunto': subject,
            'Remitente': sender,
            'Estado de lectura': is_read,
            'Hora de recepción': received_time
        }
    print("-------------------------------")
    print(email_dict[1]['Estado de lectura'])
    ultimo_email = email_dict[1]['Estado de lectura']
    if ultimo_email == 'READ':
        print("Sin mensajes nuevos")
    else:
        print("Nuevos mensajes")
    print("-------------------------------")
    return email_dict

    

    

# Solicita al usuario el número de correos a mostrar
num_emails = int(input('Ingrese el número de correos a mostrar: '))

# Obtiene el diccionario de correos electrónicos

emails_dict = get_emails(num_emails)



# Imprime los correos electrónicos almacenados en el diccionario
""" for email_num, email_info in emails_dict.items():
    print(f'Correo #{email_num}')
    print("-----------------------------------------------")
    for key, value in email_info.items():
        print(f'{key}: {value}')
    print('-----------------------------------------------')
"""