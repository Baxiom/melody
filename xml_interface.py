from music21 import stream, note, pitch, instrument
QUARTER = 500
BAR = 2000
C_MIDI_OFFSET = 60

def group_to_measures(rhythm, bar_length):
    measures = []
    acc = 0
    in_bar = 0
    for note_length in rhythm:
        in_bar += note_length
        if in_bar >= bar_length:
            measures.append(acc)
            in_bar = 0
        acc += 1
    return measures



def to_score(rhythm, stored):
    s = stream.Score()
    part = stream.Part()
    part.instrument = instrument.Piano()
    rhythm_measures = group_to_measures(rhythm, BAR)
    print(f'rhythm_measures: {rhythm_measures}')
    measure_index = 0
    m = stream.Measure(number=1)
    for i in range(len(stored)):
        rhythm_index = i % len(rhythm)
        p = pitch.Pitch(stored[i] + C_MIDI_OFFSET).nameWithOctave
        duration = rhythm[rhythm_index] / QUARTER
        m.append(note.Note(p, quarterLength=duration))
        if rhythm_measures[measure_index % len(rhythm_measures)] % len(rhythm) == rhythm_index:
            part.append(m)
            measure_index += 1
            m = stream.Measure(number=measure_index+1)
    s.append(part)
    return s


def save(rhythm, stored):
    the_score = to_score(rhythm, stored)
    the_score.write('musicxml', fp='stored_notes.musicxml')
