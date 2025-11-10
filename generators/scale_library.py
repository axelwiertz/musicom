"""
Musicom generators module - scale library
Module for generating musical scales and chords.
"""
from typing import List
from constants import TwelveTET, MIDIinstrument
from structures import MusicScale, MusicUnit, MusicVoice, MusicComposition, PitchRegister
from converters import score_to_midifile, chord_to_unit, comp_to_score, stream_to_unit
from rhythm import MusicTime
from theory import Diatonic
from music21 import roman, stream
from harmony import Scale7ChordHarmony

from generators.generator import Generator


class ScaleLibrary (Generator):
    """ ScaleLibrary generator"""
    def __init__(self, source_unit : MusicUnit,
                 musicscale : MusicScale):
        super().__init__(source_unit)
        self.musicscale = musicscale

    def generate(self) -> List[MusicUnit]:
        # Create a unit with library elements
        # Common chord progressions

        self.target_units.append(self.triads_in_scale7())

        self.target_units.append(self.progression(Scale7ChordHarmony.common_progressions))

        return self.target_units

    def progression(self, chord_progression: list[int]) -> MusicUnit:
        # Chord progression patterns in a key
        # mp
        unit = chord_to_unit (self.musicscale.mpscale.chord_progression(
                chord_progression,
                durations=self.source_unit.time.beat_duration,
                intervals=0,
                volumes=None,
                chords_interval=None))
        # m21
        stream1 = stream.Stream()
        for i in range (len(chord_progression)):
            # m21 Create chord from Roman numeral
            chord01 = roman.RomanNumeral (chord_progression[i], keyOrScale=self.musicscale.m21scale)
            chord01.duration.quarterLength = self.source_unit.time.beat_duration
            stream1.append(chord01)

        unit = stream_to_unit(stream1)

        return unit

    def triads_in_scale7 (self) -> MusicUnit:
        # triads_in_scale =  chord_to_unit(self.seed_unit.musicscale.mpscale % (1234567, 1))
        return self.progression([1,2,3,4,5,6,7])


def main():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicScale(Diatonic.TRIA, Diatonic.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicScale(Diatonic.TETRA, Diatonic.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicScale(Diatonic.PENTA, Diatonic.SCALE)

    gen = ScaleLibrary(MusicUnit(MusicTime(4,4,4),
                                 PitchRegister()),
                        MusicScale(Diatonic.HEPTA, Diatonic.SCALE, 60, Diatonic.mixolydian))

    voice = MusicVoice('Chord progression voice',
                            gen.generate(),
                            MIDIinstrument.PIANO)

    comp = MusicComposition('Chord progressions and triads',
                            gen.musicscale,
                            [voice],
                            [1, 2, 3, 4, 5, 6, 7],
                            [0, 1])
    score_to_midifile(comp_to_score(comp),
                        'chordlibrary_in_key_' +
                        TwelveTET.PITCH_CLASS_NAMES_SHARP(comp.main_scale.tonic) +
                        '.mid')


if __name__ == '__main__':
    main()