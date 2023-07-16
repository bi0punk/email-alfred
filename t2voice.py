import speech_recognition as sr

# Crea un objeto de reconocimiento de voz
r = sr.Recognizer()

# Utiliza el micrófono como fuente de audio
with sr.Microphone() as source:
    print("Di algo...")
    audio = r.listen(source)

    try:
        # Reconoce el audio utilizando Google Speech Recognition
        texto = r.recognize_google(audio, language="es")
        print("Texto reconocido: " + texto)
    except sr.UnknownValueError:
        print("No se pudo reconocer el audio.")
    except sr.RequestError as e:
        print("Error al solicitar los resultados al servicio de reconocimiento de voz: {0}".format(e))
