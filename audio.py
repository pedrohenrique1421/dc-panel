import pygame # type: ignore
from config import VOLUME

def init_audio(alarm_file, standby_file=None, standon_file=None):
    pygame.mixer.init()
    global alarm_sound, standby_sound, standon_sound

    standby_sound = None
    standon_sound = None

    alarm_sound = pygame.mixer.Sound(alarm_file)
    alarm_sound.set_volume(calcVolume(30, 10)) # valor geral menos 30%, volume minimo 10%

    if standby_file:
        standby_sound = pygame.mixer.Sound(standby_file)
        standby_sound.set_volume(calcVolume(0, 10))
    
    if standon_file:
        standon_sound = pygame.mixer.Sound(standon_file)
        standon_sound.set_volume(calcVolume(0, 10))

# Calcula o volume resultante com base na subtração, volume geral e volume minimo para o audio
def calcVolume(sub, min_vol):
    return (VOLUME/100 - (sub/100)) if VOLUME/100 - (sub/100) >= (min_vol/100) else (min_vol/100)

def play_alarm():
    if not pygame.mixer.get_busy():
        alarm_sound.play()


def play_standby():
    if standby_sound and not pygame.mixer.get_busy():
        standby_sound.play()

def play_standon():
    if standon_sound and not pygame.mixer.get_busy():
        standon_sound.play()