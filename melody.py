import math
import os
import sys
# from tkinter import filedialog
import tkinter as tk
# from encodings.punycode import selective_len
import bisect
from tkinter import filedialog
from colorsys import rgb_to_yiq

from pygame import freetype, SurfaceType
from pygame._sdl2.video import Window
import player
import io_interface

NOTE_HEIGHT = 10
STAVE_HEIGHT = 19 #This is the number of notes high
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
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
    MOUSEMOTION,
    K_UP,
    K_DOWN,
)
MLDY_EXT = '.mldy'
STEP_COLOUR = (200, 150, 120)
SCROLL_COLOUR = (0, 255, 240)
SCROLL_PLAYING = (255, 100, 0)
BLACKISH = (80, 90, 70)
SEL_STAVE_COLOUR = (160, 180, 200)
SEL_NOTE_COLOUR = (110, 130, 200)

file_list = []
pressed_list = []
stored = []

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
MAX_STORABLE = 12 + 4 #Notes in melody gamut


def reset_advance_timer(gap = 500):
    # print('Resetting advance timer')
    pg.time.set_timer(ADVANCE_EVENT, 0)
    pg.time.set_timer(ADVANCE_EVENT, gap)

def make_times(rhythm, stored):
    #Currently assuming rhythm is one screen width.
    x0 = 0
    x = x0
    line = [x0]
    lines = []
    for i in range(len(stored)):
        length = rhythm[i % len(rhythm)] * WIDTH // 8000
        if x + length > WIDTH:
            lines.append(line)
            x = x0
            line = [x0]
        x += length
        line.append(x)
    lines.append(line)
    return lines


def display(screen, rhythm, stored, index, stave):
    x0 = 0
    x = x0
    y = NOTE_HEIGHT * STAVE_HEIGHT
    i = 0
    index_test = (index - 1) if index > 0 else -3
    if stave is not None:
        stave_num = stave[0]
        stave_line = stave[1]
        note_index = stave[2]
        pg.draw.rect(screen, SEL_STAVE_COLOUR, (stave_line[0], y*stave_num + NOTE_HEIGHT, stave_line[len(stave_line)-1]-stave_line[0], y))
        pg.draw.rect(screen, SEL_NOTE_COLOUR, (stave_line[note_index-1], y*stave_num + NOTE_HEIGHT, stave_line[note_index]-stave_line[note_index-1], y))
    for note in stored:
        length = rhythm[i % len(rhythm)] * WIDTH // 8000
        if x + length > WIDTH:
            pg.draw.line(screen, SCROLL_COLOUR, (0,y + NOTE_HEIGHT), (x + WIDTH, y + NOTE_HEIGHT), 2)
            x = x0
            y += NOTE_HEIGHT * STAVE_HEIGHT
        pg.draw.rect(screen, SCROLL_PLAYING if i == index_test else SCROLL_COLOUR, (x, y - NOTE_HEIGHT * note, length, NOTE_HEIGHT))
        pg.draw.rect(screen, BLACKISH, (x, y - NOTE_HEIGHT * note, length, NOTE_HEIGHT), 1)
        i += 1
        x += length

def prep_for_tk_modal():
    pg.event.set_blocked(pg.KEYDOWN)
    # pg.event.set_blocked(KEYUP)

def finished_with_tk_modal():
    pg.event.set_allowed(pg.KEYDOWN)
    # pg.event.set_allowed(KEYUP)

def load_file(win, window):
    global rhythm
    global stored
    prep_for_tk_modal()
    filenames = filedialog.askopenfilenames(title="load melody file",
                                            filetypes=(("load melody file", "*.mldy"),
                                                       ("all files", "*.*")))
    if (filenames == None):
        finished_with_tk_modal()
        return
    if len(filenames) > 0:
        print(f'len(filenames) and os.path.splitext(filenames[0]) = {os.path.splitext(filenames[0])}')
    if len(filenames) == 1:
        print(f'filenames[0] is {filenames[0]}')
        if os.path.splitext(filenames[0])[1] == MLDY_EXT:
            rhythm, stored = io_interface.load(filenames[0], win, window)
            finished_with_tk_modal()
            return
    finished_with_tk_modal()

def main():
    win = tk.Tk()
    win.withdraw()
    pg.init()
    running = True
    paused = False
    clock = pg.time.Clock()
    old_index = None
    octave3_names = [(n + str(START_OCTAVE)) for n in NOTE_NAMES]
    octave4_names = [(n + str(START_OCTAVE+1)) for n in NOTE_NAMES[:5]]
    pitch_names = octave3_names + octave4_names
    player.init(pitch_names)
    lines = []
    play = False #Whether to play the clicked mouse note
    selected_stave = None
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
    sel_index = None
    global stored
    stored = []
    index = -1
    to_play = None
    step_input = False
    #TODO: eventually selectable/editable
    global rhythm
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
            elif event.type == MOUSEBUTTONUP:
                if event.touch:
                    continue
                pos = event.pos
                if pos[1] > 0:
                    # print(f'pos {pos}, pos[0] = {pos[0]}, pos[1] = {pos[1]}')
                    stave_number = pos[1] // (NOTE_HEIGHT * STAVE_HEIGHT)
                    if stave_number < len(lines):
                        selected_note_index = bisect.bisect_right(lines[stave_number], pos[0])
                        if selected_note_index < len(lines[stave_number]):
                            selected_stave = (stave_number, lines[stave_number], selected_note_index)
                            sel_index = max(0, selected_note_index - 1) + sum([len(l) for l in lines[0:stave_number]]) - stave_number
                            # print(f'selected_note_index = {selected_note_index}, lines[stave_number] = {lines[stave_number]}, sel_index = {sel_index}')
                            play = True
                        else:
                            selected_stave = None
                            sel_index = None
                    else:
                        selected_stave = None
                        sel_index = None
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
                        # print(f'Deleting, len(stored) = {len(stored)}')
                        stored.pop()
                        # index -= 1
                        # print(f'Deleted, len(stored) = {len(stored)}')
                elif event.key == K_UP:
                    if step_input and sel_index is not None:
                        stored[sel_index] = min(stored[sel_index] + 1, MAX_STORABLE)
                        play = True
                elif event.key == K_DOWN:
                    if step_input and sel_index is not None:
                        stored[sel_index] = max(stored[sel_index] - 1, 0)
                        play = True
                elif event.key == K_SPACE:
                    step_input = not step_input
                elif event.unicode == 'X':
                    io_interface.export(rhythm, stored)
                elif event.unicode == 'S':
                    io_interface.save(rhythm, stored)
                elif event.unicode == 'L':
                    load_file(window, win)
                    lines = make_times(rhythm, stored)
            elif event.type == ADVANCE_EVENT:
                if -1 < index < len(stored):
                    # print(f'In Advance: {stored[index]}, from index: {index}')
                    to_play = stored[index]
                    index += 1
                    if index >= len(stored):
                        index = -1
                        # print(f'Advance, index reset to -1')
                    else:
                        # print(f'Advance, with index = {index}, reset timer')
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
        if play:
            if sel_index is not None:
                player.play(stored[sel_index])
                play = False
        if (to_play is not None):
            player.play(to_play)
            to_play = None
        if len(pressed_list) > 0:
            for p in pressed_list:
                player.play(p)
            if step_input:
                if sel_index is not None:
                    stored[sel_index] = pressed_list[0]
                else:
                    stored.append(pressed_list[0])
                lines = make_times(rhythm, stored)
                # print(f'Pressed {pressed} with step input. stored is {stored}')
                pressed = None
            pressed_list.clear()
        display(screen, rhythm, stored, index, selected_stave)
        pg.display.flip()
        clock.tick(60)
    pg.quit()
    sys.exit()



if __name__ == '__main__':
    main()