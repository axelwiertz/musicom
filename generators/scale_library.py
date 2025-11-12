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

from generators import Generator

class ProgressionGenerator (Generator):
    """ ScaleLibrary generator"""
    def __init__(self, seed_unit: MusicUnit, time : MusicTime,
                 musicscale : MusicScale,
                 chord_progression_degrees : List[int]):
        super().__init__(seed_unit)
        self.time = time
        self.musicscale = musicscale
        self.chord_progression_degrees = chord_progression_degrees

    def generate(self) -> MusicUnit:
        """Generate a MusicUnit with the chord progression."""
        return self.progression()

    def progression(self) -> MusicUnit:
        # Chord progression patterns in a key
        # mp
        unit = chord_to_unit (self.musicscale.mpscale.chord_progression(
                self.chord_progression_degrees,
                durations=self.source_unit.time.beat_duration,
                intervals=0,
                volumes=None,
                chords_interval=None))
        # m21
        stream1 = stream.Stream()
        for i in range (len(self.chord_progression_degrees)):
            # m21 Create chord from Roman numeral
            chord01 = roman.RomanNumeral (self.chord_progression_degrees[i], keyOrScale=self.musicscale.m21scale)
            chord01.duration.quarterLength = self.source_unit.time.beat_duration
            stream1.append(chord01)

        unit = stream_to_unit(stream1)

        return unit



def main():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicScale(Diatonic.TRIA, Diatonic.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicScale(Diatonic.TETRA, Diatonic.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicScale(Diatonic.PENTA, Diatonic.SCALE)

    seed_unit = MusicUnit(MusicTime(4,4,4), PitchRegister())
    scale1 = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, 60, Diatonic.major_mode)

    gen = ProgressionGenerator(
        seed_unit=seed_unit,
        time=seed_unit.time,
        musicscale=scale1,
        chord_progression_degrees=[1,2,3,4,5,6,7]
    )

    def triads_in_scale7 (self) -> MusicUnit:
        # triads_in_scale =  chord_to_unit(self.seed_unit.musicscale.mpscale % (1234567, 1))
        return self.progression([1,2,3,4,5,6,7])

    seed_unit2 = MusicUnit(MusicTime(4,4,4), PitchRegister())
    scale2 = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, 60, Diatonic.mixolydian)

    gen = ProgressionGenerator(
        seed_unit=seed_unit2,
        time=seed_unit2.time,
        musicscale=scale2,
        chord_progression_degrees=[1, 4, 5, 6, 3, 2, 7]
    )

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