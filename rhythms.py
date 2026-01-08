'''
A class to hold a rhythm, that may be repeated, or re-occur in a melody.
Its most basic aspect is a list of durations, that give when the current note finishes, and the next begins.
It is elaborated to cover rests, and could also have stacatto, dynamic markers (or even things like mordents.)
'''
# from music21.note import Note


def make_sounding_notes(starts, durations:dict):
    sounds = []
    i = 0
    for start in starts: #he list of times until the next note starts
        duration = durations.get(i, start) #How long the current note lasts - default is until the next one
        if duration > 0:
            sounds.append(RhythmNote(start, sounding=duration))
    return sounds


class Rhythm:
    def __init__(self, starts, durations={}):
        self.starts = starts.copy()
        self.durations = durations.copy()
        self.sounding_notes = make_sounding_notes(starts, durations)

    def notes_length(self):
        '''
        How many notes does this rhythm have, not including rests.
        :return: the int that is the number of sounding notes (if there is a chord, each pitch counts)
        '''
        return len(self.sounding_notes)

    def get_duration(self, i):
        index = i % self.notes_length()
        return int(self.sounding_notes[index].duration)

    def get_sounding(self, i):
        index = i % self.notes_length()
        return int(self.sounding_notes[index].sounding)

    def split(self, index, ratio=(1,1)):
        length1 = RhythmNote(duration=self.get_duration(index) * (ratio[0]/(ratio[0]+ratio[1])))
        length2 = RhythmNote(duration=self.get_duration(index) * (ratio[1] / (ratio[0] + ratio[1])))
        self.sounding_notes = self.sounding_notes[:index] + [length1, length2] + self.sounding_notes[index+1:]

class RhythmNote:
    def __init__(self, duration, sounding=None):
        self.duration = duration
        self.sounding = duration if sounding is None else sounding

