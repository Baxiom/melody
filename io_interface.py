import tkinter
from music21 import stream, note, pitch, instrument
import json
import os

import rhythms

# import sys
# import tkinter as tk

QUARTER = 500
BAR = 2000
C_MIDI_OFFSET = 60

def group_to_measures(rhythm:rhythms.Rhythm, bar_length):
    measures = []
    starts = rhythm.starts
    acc = 0
    in_bar = 0
    for note_length in starts:
        in_bar += note_length
        if in_bar >= bar_length:
            measures.append(acc)
            in_bar = 0
        acc += 1
    return measures

def to_score(rhythm:rhythms.Rhythm, stored):
    s = stream.Score()
    part = stream.Part()
    part.instrument = instrument.Piano()
    rhythm_measures = group_to_measures(rhythm, BAR)
    print(f'rhythm_measures: {rhythm_measures}')
    measure_index = 0
    m = stream.Measure(number=1)
    for i in range(len(stored)):
        rhythm_index = i % len(rhythm.starts)
        p = pitch.Pitch(stored[i] + C_MIDI_OFFSET).nameWithOctave
        duration = rhythm.get_sounding(i)#rhythm[rhythm_index] / QUARTER
        m.append(note.Note(p, quarterLength=duration))
        if rhythm_measures[measure_index % len(rhythm_measures)] % len(rhythm.starts) == rhythm_index:
            part.append(m)
            measure_index += 1
            m = stream.Measure(number=measure_index+1)
    s.append(part)
    return s

def export(rhythm, stored):
    the_score = to_score(rhythm, stored)
    print(f'the_score:, {the_score}')
    if (the_score.isWellFormedNotation()):
        the_score.write('musicxml', fp='stored_notes.musicxml')
    else:
        print(f'Issue with the_score.isWellFormedNotation() = {the_score.isWellFormedNotation()}')


def save(rhythm:rhythms.Rhythm, stored):
    save_dict = {'rhythm': {'starts':rhythm.starts, 'durations':rhythm.durations}, 'stored': stored}
    # filename = 'save.mldy'
    # file_path = os.path.join(os.path.dirname(__file__), filename)
    file_path = tkinter.filedialog.asksaveasfile(title="save melody", defaultextension="mldy")
    with (open(file_path.name, "w") as file):
        to_save = json.dumps(save_dict, indent=4)
        file.write(to_save)
        file.close()
    return None

def load(file_name, win, window):
    global rhythm, stored
    # filename = 'save.mldy'
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    load_dict = json.load(open(file_path))
    rhythm_load = load_dict.get('rhythm', {})
    rhythm = rhythms.Rhythm(rhythm_load.get('starts', []), rhythm_load.get('durations', []))
    stored = load_dict.get('stored', [])
    print(f'interface load:- rhythm: {rhythm}, stored: {stored}')
    return rhythm, stored