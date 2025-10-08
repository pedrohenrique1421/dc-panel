import pygame

def init_audio(alarm_file):
    pygame.mixer.init()
    pygame.mixer.music.load(alarm_file)
    pygame.mixer.music.set_volume(0.02)

def play_alarm():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()
