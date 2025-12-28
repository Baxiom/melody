import math
import os
import sys
# from tkinter import filedialog
import tkinter as tk
from colorsys import rgb_to_yiq

from pygame import freetype, SurfaceType
from pygame._sdl2.video import Window
import player
import xml_interface
from pathlib import Path

# from geopy.geocoders import Nominatim
# from PIL.ExifTags import GPSTAGS

win = tk.Tk()
win.withdraw()
import pygame as pg
pg.mixer.init()
pg.font.init()
pg.freetype.init()

from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_BACKSPACE,
)
STEP_COLOUR = (200, 150, 120)
SCROLL_COLOUR = (0, 255, 240)
SCROLL_PLAYING = (255, 100, 0)
BLACKISH = (80, 90, 70)

file_list = []

PRIV = 20. # Fraction of a degree lat/long we will obscure, for privacy. 20 gives ~5km lat
WIDTH, HEIGHT = 1200, 900
SMALL_WIDTH, SMALL_HEIGHT = (WIDTH - 200), (HEIGHT - 40)
screen = pg.display.set_mode((WIDTH, HEIGHT))#, pg.FULLSCREEN | pg.SCALED)
pg.display.set_caption("Melody Patterns")
ADVANCE_EVENT = pg.USEREVENT + 1
DUMMY_DATE = '1900:01:01 23:30:00'
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
START_OCTAVE = 3

PIANO_SAMPLE_DIR = "~/Downloads/Steinway Grand  (DS)/Samples/"
NAME_START = "Steinway_"
NAME_END = "_Dyn4_RR1.wav"


def reset_advance_timer(gap = 500):
    print('Resetting advance timer')
    pg.time.set_timer(ADVANCE_EVENT, 0)
    pg.time.set_timer(ADVANCE_EVENT, gap)


def display(screen, rhythm, stored, index):
    x = 0
    y = 10 * 17
    i = 0
    index_test = (index - 1) if index > 0 else -3
    for note in stored:
        length = rhythm[i % len(rhythm)] * WIDTH // 8000
        if x + length > WIDTH:
            pg.draw.line(screen, SCROLL_COLOUR, (0,y+20), (x + WIDTH, y+20), 2)
            x = 0
            y += 10 * 19
        pg.draw.rect(screen, SCROLL_PLAYING if i == index_test else SCROLL_COLOUR, (x, y - 10*note, length, 10))
        pg.draw.rect(screen, BLACKISH, (x, y - 10 * note, length, 10), 1)
        i += 1
        x += length



def main():
    pg.init()
    running = True
    paused = False
    clock = pg.time.Clock()
    old_index = None
    octave3_names = [(n + str(START_OCTAVE)) for n in NOTE_NAMES]
    octave4_names = [(n + str(START_OCTAVE+1)) for n in NOTE_NAMES[:5]]
    pitch_names = octave3_names + octave4_names
    player.init(pitch_names)
    #get the sounds:
    # PATH_TO_A1 = os.path.join(os.path.expanduser(PIANO_SAMPLE_DIR), NAME_START + "A1" + NAME_END)
    # print(f'PATH_TO_A1 = {PATH_TO_A1}, existS? : {os.path.exists(PATH_TO_A1)}')
    # a4 = pg.mixer.Sound(PATH_TO_A1)
    # PATH_TO_B1 = os.path.join(os.path.expanduser(PIANO_SAMPLE_DIR), NAME_START + "B2" + NAME_END)
    # b4 = pg.mixer.Sound(PATH_TO_B1)
    # PATH_TO_C1 = os.path.join(os.path.expanduser(PIANO_SAMPLE_DIR), NAME_START + "C0" + NAME_END)
    # c4 = pg.mixer.Sound(PATH_TO_C1)
    pressed = None
    pressed_list = []
    stored = []
    index = -1
    to_play = None
    step_input = False
    #TODO: eventually selectable/editable
    rhythm = [1000, 500, 500,
              1000, 500, 500,
              750, 250, 500, 500,
              1000, 1000
              ]
    while running:
        window = Window.from_display_module()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.unicode == 'a':
                    pressed = 0
                elif event.unicode == 's':
                    pressed = 2
                elif event.unicode == 'd':
                    pressed = 4
                elif event.unicode == 'f':
                    pressed = 5
                elif event.unicode == 'g':
                    pressed = 7
                elif event.unicode == 'h':
                    pressed = 9
                elif event.unicode == 'j':
                    pressed = 11
                elif event.unicode == 'k':
                    pressed = 12
                elif event.unicode == 'l':
                    pressed = 14
                elif event.unicode == ';':
                    pressed = 16
                elif event.unicode == 'w': #Now the accidentals
                    pressed = 1
                elif event.unicode == 'e':
                    pressed = 3
                elif event.unicode == 't':
                    pressed = 6
                elif event.unicode == 'y':
                    pressed = 8
                elif event.unicode == 'u':
                    pressed = 10
                elif event.unicode == 'o':
                    pressed = 13
                elif event.unicode == 'p':
                    pressed = 15
                elif event.key == K_LEFT:
                    stored.clear()
                elif event.key == K_RIGHT: #PLAY!
                    pg.time.set_timer(ADVANCE_EVENT, 20)
                    index = 0
                    # step_input = False
                elif event.key == K_BACKSPACE:
                    if step_input and len(stored) > 0:
                        print(f'Deleting, len(stored) = {len(stored)}')
                        stored.pop()
                        # index -= 1
                        print(f'Deleted, len(stored) = {len(stored)}')
                elif event.key == K_SPACE:
                    step_input = not step_input
                elif event.unicode == 'X':
                    xml_interface.export(rhythm, stored)
                elif event.unicode == 'S':
                    xml_interface.save(rhythm, stored)
                elif event.unicode == 'L':
                    rhythm, stored = xml_interface.load()
            elif event.type == ADVANCE_EVENT:
                if -1 < index < len(stored):
                    print(f'In Advance: {stored[index]}, from index: {index}')
                    to_play = stored[index]
                    index += 1
                    if index >= len(stored):
                        index = -1
                        print(f'Advance, index reset to -1')
                    else:
                        print(f'Advance, with index = {index}, reset timer')
                        reset_advance_timer(rhythm[(index-1) % len(rhythm)])
                else:
                    to_play = None
            else:
                to_play = None
                pressed = None
            if pressed is not None:
                pressed_list.append(pressed)
                pressed = None

        # if (old_index != index):
        #     old_index = index

        screen.fill(STEP_COLOUR if step_input else (30, 120, 70))
        if (to_play is not None):
            player.play(to_play)
            to_play = None
        if len(pressed_list) > 0:
            for p in pressed_list:
                player.play(p)
            if step_input:
                stored.append(pressed_list[0])
                print(f'Pressed {pressed} with step input. stored is {stored}')
                pressed = None
            pressed_list.clear()
        display(screen, rhythm, stored, index)
        pg.display.flip()
        clock.tick(60)
    pg.quit()
    sys.exit()



if __name__ == '__main__':
    main()