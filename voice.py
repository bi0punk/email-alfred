import pyttsx3

# Crear un objeto de la clase Text-to-Speech
engine = pyttsx3.init()

# Obtener una lista de voces disponibles
voices = engine.getProperty('voices')

# Imprimir las voces disponibles
for voice in voices:
    print("ID de la voz:", voice.id)
    print("Nombre de la voz:", voice.name)
    print("Idioma de la voz:", voice.languages)
    print("")

# Cambiar la voz
# Por ejemplo, puedes usar el índice 1 para seleccionar la segunda voz en la lista
engine.setProperty('voice', voices[2].id)

# Cambiar la velocidad de habla (valor predeterminado: 200)
engine.setProperty('rate', 150)

# Cambiar el volumen de la voz (valor predeterminado: 1.0)
engine.setProperty('volume', 0.8)

# Texto que deseas convertir a voz
texto = "Hola, este es un ejemplo de síntesis de voz en Python."

# Sintetizar y reproducir el texto
engine.say(texto)
engine.runAndWait()
