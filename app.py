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
import speech_recognition as sr

# Escopos necesarios para acceder a la bandeja de entrada de Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.pickle'
TIMER_DELAY = 300  # Tiempo de espera en segundos

def get_gmail_service():
    creds = None
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

def get_new_emails():
    service = get_gmail_service()
    # Llama al método de la API para obtener los mensajes de la bandeja de entrada
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])
    email_dict_unread = {
        i+1: process_message(service.users().messages().get(userId='me', id=message['id']).execute())
        for i, message in enumerate(messages)
    }
    return email_dict_unread



#Funcion para reproducir txto a voz
def play_notification_message(message):
    tts = gTTS(message, lang='es')
    speed = 1.5
    filename = "output.mp3"
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    # Esperar unos segundos para asegurar la reproducción completa del archivo
    time.sleep(1)

    # Mantener el programa en ejecución para permitir la reproducción completa
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(5)





#Funcion que reconoce de voz a texto, utilizando microfono
def recognize_speech():
    r = sr.Recognizer()

    # Utiliza el micrófono como fuente de audio
    with sr.Microphone() as source:
        print("Di algo...")
        audio = r.listen(source)

        try:
            # Reconoce el audio utilizando Google Speech Recognition
            texto = r.recognize_google(audio, language="es")
            print("Texto reconocido: " + texto)
            return texto
        except sr.UnknownValueError:
            print("No se pudo reconocer el audio.")
            return None
        except sr.RequestError as e:
            print("Error al solicitar los resultados al servicio de reconocimiento de voz: {0}".format(e))
            return None





#Funcion que pregunta si desea leer remitente, si es True, muestra por consola los emails nuevos y por voz
def leer_remitentes():
    notification_message = random.choice([
        '¿Quiere que verifique los remitentes, jefe?',
        '¿Le gustaría que lea los emisores, jefe?',
        'Jefe, ¿desea que revise los remitentes disponibles?',
        '¿Le interesa conocer los emisores, jefe?',
        'Jefe, ¿debo examinar los emisores relacionados?',
        'Jefe, ¿quiere que me encargue de revisar los remitentes?'
    ])
    play_notification_message(notification_message)

    texto = recognize_speech()
    if texto and 's' in texto:
        print('Mostrando remitente y asunto de mensajes nuevos')
        new_emails = get_new_emails()
        for email_num, email_info in new_emails.items():
            print(f'Correo #{email_num}')
            print("-----------------------------------------------")
            for key, value in email_info.items():
                print(f'{key}: {value}')
            print('-----------------------------------------------')

        # Leer remitentes y asuntos utilizando la función play_notification_message()
        for email_num, email_info in new_emails.items():
            remitente = email_info['Remitente']
            asunto = email_info['Asunto']
            play_notification_message(f"Remitente: {remitente}")
            play_notification_message(f"Asunto: {asunto}")




#funcion apara comprar si existen mensajes nuevos
def check_email_notifications():
    while True:
        new_emails = get_new_emails()
        if len(new_emails) > 0:
            print("Señor, tiene nuevos mensajes")
            play_notification_message(random.choice([
                'Señor, tiene nuevos mensajes',
                'Señor, ha recibido nuevos mensajes',
                'Jefe, hay mensajes frescos para revisar.',
                'Señor, le esperan mensajes novedosos.',
                'Jefe, tiene mensajes recientes.',
                'Señor, le han llegado mensajes actualizados.',
                'Jefe, hay mensajes nuevos en su bandeja.',
                'Señor, ha recibido mensajes frescos.',
                'Tiene mensajes sin leer jefe'
            ]))
            leer_remitentes()
        else:
            print("Sin mensajes nuevos")
            play_notification_message(random.choice([
                'Sin novedades, jefe',
                'No hay novedades, jefe.',
                'No hay mensajes nuevos, jefe.',
                'Nada relevante que reportar, jefe.',
                'Jefe, no ha llegado nada nuevo',
                'Todo en calma, jefe.',
                'Bandeja de entrada sin novedades',
                'No hay correos nuevos, señor.'
            ]))
        # Espera el tiempo de retardo antes de verificar nuevamente
        time.sleep(TIMER_DELAY)

# Inicia el hilo en segundo plano para verificar las notificaciones de correo electrónico
email_thread = threading.Thread(target=check_email_notifications)
email_thread.start()
