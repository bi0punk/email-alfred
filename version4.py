import os
import pickle
import base64
import email
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from gtts import gTTS
import pygame
import time
import random
import threading

# Escopos necesarios para acceder a la bandeja de entrada de Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.pickle'
NUM_EMAILS = 1
TIMER_DELAY = 450  # Tiempo de espera en segundos

def get_gmail_service():
    creds = None

    # Si ya se ha autorizado, carga las credenciales del token almacenado en disco
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Si no hay credenciales válidas disponibles, realiza el flujo de autenticación.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Guarda las credenciales para el próximo inicio de sesión
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    # Crea un objeto de servicio de la API de Gmail
    service = build('gmail', 'v1', credentials=creds)
    return service

def process_message(message):
    email_data = message['payload']['headers']
    is_read = 'UNREAD' if 'UNREAD' in message['labelIds'] else 'READ'
    received_time = message['internalDate']
    subject = None
    sender = None

    for values in email_data:
        name = values['name']
        if name == 'Subject':
            subject = values['value']
        if name == 'From':
            sender = values['value']

    return {
        'Asunto': subject,
        'Remitente': sender,
        'Estado de lectura': is_read,
        'Hora de recepción': received_time
    }

def get_emails(num_emails):
    service = get_gmail_service()
    # Llama al método de la API para obtener los mensajes de la bandeja de entrada
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=num_emails).execute()
    messages = results.get('messages', [])
    email_dict_unread = {i+1: process_message(service.users().messages().get(userId='me', id=message['id']).execute()) for i, message in enumerate(messages)}

    return email_dict_unread

def play_notification_message(message):
    tts = gTTS(message, lang='es')
    filename = "output.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Esperar unos segundos para asegurar la reproducción completa del archivo
    time.sleep(2)

    # Mantener el programa en ejecución para permitir la reproducción completa
    while pygame.mixer.music.get_busy():
        pass

def leer_remitentes():
    play_notification_message(random.choice(['¿Quiere que verifique los remitentes, jefe?',
                                            '¿Le gustaría que lea los emisores, jefe?',
                                            'Jefe, ¿desea que revise los remisores disponibles?',
                                            '¿Le interesa conocer los emisores, jefe?',
                                            'Jefe, ¿debo examinar los emisores relacionados?',
                                            'Jefe, ¿quiere que me encargue de revisar los remitentes?']))

def check_email_notifications():
    while True:
        # Definir el número de correos a mostrar
        num_emails = NUM_EMAILS

        # Obtiene el diccionario de correos electrónicos
        emails_dict = get_emails(num_emails)

        # Imprime los correos electrónicos almacenados en el diccionario
        for email_num, email_info in emails_dict.items():
            print(f'Correo #{email_num}')
            print("-----------------------------------------------")
            for key, value in email_info.items():
                print(f'{key}: {value}')
            print('-----------------------------------------------')

        # Verifica si hay mensajes nuevos y reproduce una notificación
        ultimo_email = emails_dict[1]['Estado de lectura']
        if ultimo_email == 'UNREAD':
            print("Señor, tiene nuevos mensajes")
            play_notification_message(random.choice(['Señor, tiene nuevos mensajes', 'Señor, ha recibido nuevos mensajes',
                'Jefe, hay mensajes frescos para revisar.',
                'Señor, le esperan mensajes novedosos.',
                'Jefe, tiene mensajes recientes.',
                'Señor, le han llegado mensajes actualizados.',
                'Jefe, hay mensajes nuevos en su bandeja.',
                'Señor, ha recibido mensajes frescos.',
                'Tiene mensajes sin leer jefe']))
            leer_remitentes()
            print("Leyendo...")
        else:
            print("Sin mensajes nuevos")
            play_notification_message(random.choice([
                'Sin novedades, jefe', 'No hay novedades, jefe.',
                'No hay mensajes nuevos, jefe.',
                'Nada relevante que reportar, jefe.',
                'jefe, No ha llegado nada nuevo',
                'Todo en calma, jefe.',
                'Bandeja de entrada sin novedades',
                'No hay correos nuevos, señor.'
            ]))

        # Espera el tiempo de retardo antes de verificar nuevamente
        time.sleep(TIMER_DELAY)

# Inicia el hilo en segundo plano para verificar las notificaciones de correo electrónico
email_thread = threading.Thread(target=check_email_notifications)
email_thread.start()
