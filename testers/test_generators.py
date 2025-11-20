from constants import TwelveTET, MIDIinstrument
from structures import MusicScale, MusicUnit, MusicVoice, MusicComposition
from converters import score_to_midifile
from generators import ProgressionGenerator, HarmonicFunction, GeneticGenerator
from structures.composition import MusicTime, MusicSection
from structures.theory import Diatonic
from music21 import stream, note


def test_genetic():
    # Example fitness function: counts the number of 1s in the genome
    gen = GeneticGenerator(MusicUnit("Seed"))
    def fitness_func(genome: gen.Genome) -> int:
        return sum(genome)

    # Run the genetic algorithm
    final_population, generations = gen.run_evolution(
        populate_func=lambda: gen.generate_population(10, 20),
        fitness_func=fitness_func,
        fitness_limit=20,
        generation_limit=50,
        printer=gen.print_stats
    )

    print("Final Population after %d generations:" % generations)
    for genome in final_population:
        print("%s (Fitness: %d)" % (gen.genome_to_string(genome), fitness_func(genome)))


def test_harmonics():

    tt = TwelveTET()
    unit = MusicUnit("Harmonics",
                     MusicTime(8,4,4),
                    tt.name_to_midi(name=['E4', 'D4', 'B3', 'Bb3', 'Eb4', 'Db4', 'C4', 'G3', 'A3'])
                     )

    gen = HarmonicFunction(unit,
                            fundamental_pitch = note.Pitch('A1').midi,
                            harmonic_numbers  = list(range(1,21))
                           )

    unit.stream = gen.harmonic_series(note.Pitch('A1').midi,[5,6,7,9,12,15])


def test_progression():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicScale(Diatonic.TRIA, Diatonic.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicScale(Diatonic.TETRA, Diatonic.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicScale(Diatonic.PENTA, Diatonic.SCALE)

    seed_unit = MusicUnit("Seed", MusicTime(4,4,4))
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

    seed_unit2 = MusicUnit("Seed2", MusicTime(4,4,4))
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