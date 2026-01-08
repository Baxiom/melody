'''
This is more actually playing the music - or at least the melody component.
'''
import pygame as pg
import os
sounds = []
PATH_TO_SAMPLES = "samples/"
SAMPLE_PREFIX = "piano_"
SAMPLE_POSTFIX = ".mp3"

def init(notes):
    global sounds
    for note in notes:
        notefile = os.path.join(os.path.dirname(__file__), PATH_TO_SAMPLES, SAMPLE_PREFIX + note + SAMPLE_POSTFIX)
        print(f'Loading {note} from: {notefile}')
        sound = pg.mixer.Sound(notefile)
        sounds.append(sound)

def play(pressed, maxtime=2000):
    if pressed < len(sounds):
        print(f'Play {pressed} notes, maxtime: {maxtime}')
        sounds[pressed].play(maxtime=maxtime)


def play_sequence(stored):
    return None