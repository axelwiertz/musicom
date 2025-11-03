"""
Musicom generators module
harmonic functions
"""

from music21 import chord, note, stream, interval
from structures import MusicUnit, PitchRegister

def harmonic_series (fundamental_pitch  : int,
                           harmonic_numbers: list[int] = range(1,17)) -> chord.Chord:
    # The harmonic series of a fundamental pitch

    harmonic_chord = chord.Chord()
    stream_out = stream.Stream()
    for harmonic in harmonic_numbers:
        new_pitch = note.Pitch(fundamental_pitch).getHarmonic(harmonic)
        harmonic_chord.add (note.Note(new_pitch.midi))
        stream_out.append (note.Note(new_pitch))

    return harmonic_chord


def main():

    t = TwelveTET()
    ph = PitchRegister()

    time = MusicTime(8,4,4)
    unit = MusicUnit(time, reg,
                   t.name_to_midi( ['E4', 'D4', 'B3', 'Bb3', 'Eb4', 'Db4', 'C4', 'G3', 'A3']))

    for bass_pitch in unit.pitch_nodes:
        random_harmonics = random.sample(range(4,21), random.randrange(3, 6))
        new_chord = harmonic_series(bass_pitch, random_harmonics)
        new_chord.transpose(interval.Interval(new_chord[0],
                                              note.Pitch(bass_pitch),
                            inPlace=True))

        new_chord.duration = note.Duration(random.choice([time.M21_QUARTER/2, time.M21_QUARTER/1]))

    unit.stream = harmonic_series(note.Pitch('A1').midi,[5,6,7,9,12,15])

if __name__ == '__main__':
    main()