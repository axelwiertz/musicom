""" Module to create streams of chords and split them into voices """
from generators.base import Generator
from music21 import stream, note

# TODO: improve function to handle chords with different number of notes

class FromChordGenerator(Generator):
    """ Chord generator class """

    def __init__(self,
                 chord_progression: stream.Stream,
                 number_of_voices : int = 3,
                 octave_in: int = 4,
                 quarterLength_in = 2
                 ):
        super().__init__(chord_progression)
        self.chord_progression = chord_progression
        self.number_of_voices = number_of_voices
        self.octave_in = octave_in
        self.quarterLength_in = quarterLength_in

    def generate(self) -> stream.Stream:
        """ Generate a stream of voices from the chord progression """
        return create_stream_from_chords(self.chord_progression,
                                         self.number_of_voices,
                                         self.octave_in,
                                         self.quarterLength_in
                                         )


def create_stream_from_chords (stream_chords: stream.Stream,
                               number_of_voices : int = 3,
                               octave_in: int = 4,
                               quarterLength_in = 2) -> stream.Stream:
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
            stream_out.append(note.Note(chord_in.notes[j].pitch, quarterLength_in))

    return stream_out

