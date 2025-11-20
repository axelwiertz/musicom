from constants import TwelveTET, MIDIinstrument
from structures import MusicScale, MusicUnit, MusicVoice, MusicComposition, PitchRegister
from converters import score_to_midifile
from generators import ProgressionGenerator
from structures.composition import MusicTime, MusicSection
from structures.theory import Diatonic
from analysis.music21 import stream

def test_progression():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicScale(Diatonic.TRIA, Diatonic.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicScale(Diatonic.TETRA, Diatonic.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicScale(Diatonic.PENTA, Diatonic.SCALE)

    seed_unit = MusicUnit("Seed", MusicTime(4,4,4), PitchRegister())
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

    seed_unit2 = MusicUnit("Seed2", MusicTime(4,4,4), PitchRegister())
    scale2 = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, 60, Diatonic.mixolydian)

    gen = ProgressionGenerator(
        seed_unit=seed_unit2,
        time=seed_unit2.time,
        musicscale=scale2,
        chord_progression_degrees=[1, 4, 5, 6, 3, 2, 7]
    )

    section = MusicSection("Chord progression",
                           [gen.generate()])
    voice = MusicVoice('Piano voice',
                            [section],
                            MIDIinstrument.PIANO)
    comp = MusicComposition('Chord progressions and triads',
                            [voice])
    # Convert to music21 stream and save as MIDI file
    score = stream.Score()
    # TO DO: convert MusicComposition to music21 stream
    score_to_midifile(score,
                        'chordlibrary_in_key_' +
                        TwelveTET.PITCH_CLASS_NAMES_SHARP(scale1.tonic) +
                        '.mid')


def main():
    test_progression()

if __name__ == "__main__":
    main()