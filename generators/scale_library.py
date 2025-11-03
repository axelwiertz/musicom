"""
Musicom generators module - scale library
Module for generating musical scales and chords.
"""
from constants import TwelveTET, MIDIinstrument
from structures import MusicScale, MusicUnit, MusicVoice, MusicComposition, PitchRegister
from converters import comp_to_file
from rhythm import MusicTime
from theory import Diatonic
from music21 import roman
from harmony import Scale7ChordHarmony


def progression_in_scale (chord_progression: list[int],
                            music_scale : MusicScale):
    # Chord progression patterns in a key
    time = MusicTime(4,4,4)
    reg = PitchRegister()
    unit_prog = MusicUnit(time, reg)
    voice_prog = MusicVoice('Chord progression voice',
                            [unit_prog],
                            MIDIinstrument.PIANO)
    comp = MusicComposition('Chord progressions',
                       music_scale,
                       [voice_prog],
                       chord_progression,
                       [0]
                       )
    # mp
    unit_prog.chord = music_scale.mpscale.chord_progression(
            chord_progression,
            durations=1 / 2,
            intervals=0,
            volumes=None,
            chords_interval=None)
    # m21
    for i in range (len(chord_progression)):
        # m21 Create chord from Roman numeral
        chord01 = roman.RomanNumeral (chord_progression[i], keyOrScale=music_scale.m21scale)
        chord01.duration.quarterLength = 4
        unit_prog.stream.append(chord01)


def triads_in_scale7 (scale7 : MusicScale):
    progression_in_scale([1,2,3,4,5,6,7],
                         scale7)


def library (musicscale: MusicScale) -> MusicComposition:
    # Create a score with library elements
    reg = PitchRegister()
    time = MusicTime(4, 4, 4)
    # Common chord progressions
    #
    triads_in_scale = MusicUnit(time, reg)
    triads_in_scale.chord = musicscale.mpscale % (1234567, 1)

    prog_in_scale = MusicUnit(time, reg)
    progression_in_scale(Scale7ChordHarmony.common_progressions, musicscale)

    voice = MusicVoice('Chord progression voice', [triads_in_scale, prog_in_scale], MIDIinstrument.PIANO)
    comp = MusicComposition('Chord progressions and triads',
                            musicscale,
                            [voice],
                            [1,2,3,4,5,6,7],
                            [0,1])
    return comp

def main():
    comp = library(MusicScale(Diatonic.HEPTA, Diatonic.SCALE, 60, Diatonic.mixolydian))
    # Save score
    comp_to_file(comp, 'chordlibrary_in_key_' + TwelveTET.PITCH_CLASS_NAMES_SHARP(comp.main_scale.tonic) + '.mid')


if __name__ == '__main__':
    main()