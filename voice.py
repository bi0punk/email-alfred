from gtts import gTTS
import pygame
import time

text = "Hola hola"
tts = gTTS(text, lang='es')
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
