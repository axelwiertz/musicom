""" Module to create from chords """
from typing import List
from structures import MusicGenerator, MusicUnit, MusicPattern
from converters import pattern_to_pitches
from music21 import stream, note


class SequentialPatternGenerator(MusicGenerator):
    """ Arpeggio generator class """

    def __init__(self,
                 patterns: List[MusicPattern],
                 octave_in: int = 4,
                 timesteps_in: int = 1,
                 duration_in: int = 1,
                 volume_in: int = 80
                 ):
        super().__init__()
        self.patterns = patterns
        self.octave_in = octave_in
        self.timesteps_in = timesteps_in
        self.duration_in = duration_in
        self.volume_in = volume_in

    def produce(self) -> List[MusicUnit]:
        """ Generate a stream of arpeggios from the chord progression """
        units = []
        for pattern in self.patterns:
            # Convert pattern to pitches
            pitch_nodes_ = pattern_to_pitches(pattern, self.octave_in)
            unit = MusicUnit("Arpeggio of "+pattern.name,
                             [pitch_nodes_],
                           [self.timesteps_in]*len(pitch_nodes_),
                               [self.duration_in]*len(pitch_nodes_),
                                [self.volume_in]*len(pitch_nodes_)
                             )

        return units

class ParallelPatternChordGenerator(MusicGenerator):
    """ Chord generator class """

    def __init__(self,
                 chord_progression: stream.Stream,
                 number_of_voices : int = 3,
                 octave_in: int = 4,
                 quarterLength_in = 2
                 ):
        super().__init__()
        self.chord_progression = chord_progression
        self.number_of_voices = number_of_voices
        self.octave_in = octave_in
        self.quarterLength_in = quarterLength_in

    def produce(self) -> stream.Stream:
        """ Generate a stream of voices from the chord progression """
        return create_stream_from_chords(self.chord_progression,
                                         self.number_of_voices,
                                         self.octave_in,
                                         self.quarterLength_in
                                         )

# TODO: improve function to handle chords with different number of notes

def create_stream_from_chords (stream_chords: stream.Stream,
                               number_of_voices : int = 3,
                               octave_in: int = 4,
                               quarterlength_in = 2) -> stream.Stream:
    # given chords, return a stream of voices,
    # starting in octave octave_in, and ascending
    # prepare some streams: one per voice
    # all bass notes of each chord form one voice
    # all 2nd notes of each chord form a second voice

    stream_out = stream.Stream()

    # create voice streams to hold chords
    for i in range(number_of_voices):
        stream_out.append(stream.Stream())

    for i, chord_in in enumerate(stream_chords):

        octave_correction = octave_in - chord_in.notes[0].octave
        for n in chord_in.notes:
            n.octave += octave_correction

        # split each chord into separate voices
        for j in range(number_of_voices):
            stream_out[j].append()
            stream_out.append(note.Note(chord_in.notes[j].pitch, quarterlength_in))

    return stream_out

