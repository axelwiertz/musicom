from base import TwelveTET
from base.diatonic import Cardinality, PatternType, Mode
from converters.pitch import name_to_midi
from structures import MusicPattern, MusicUnit, MusicVoice, MusicProject
from converters import score_to_midifile
from generators.stochastic import StochasticGenerator
from generators.chain import MarkovChainGenerator
from regularity import Scale7PitchDegree
from generators.counterpoint import stream_is_counterpoint
from generators import ProgressionGenerator, HarmonicsGenerator
from structures.time import MusicTime
from structures.project import MusicSection
from regularity.progression import Scale7ChordHarmony
from music21 import stream, note, key, roman

def test_counterpoint():
    # Create a two-voice counterpoint composition
    unit1 = MusicUnit(pitch_nodes=name_to_midi(['A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5']))
    length = len(unit1)
    gen = StochasticGenerator(length=length, duration_set=[1], pitch_set=name_to_midi(['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']))
    unit2 = gen.generate()

    # Keep generating until counterpoint reached
    while not stream_is_counterpoint(unit1, unit2):
        unit2 = gen.generate()
    print("Counterpoint achieved between two streams.")

def test_genetic():
    from generators.genetic import GeneticGenerator, GenomeType

    # Example fitness function: counts the number of 1s in the genome
    def fitness_func(genome: GenomeType) -> int:
        return sum(genome)

    gen = GeneticGenerator(MusicUnit(0, "Seed"), fitness_func,100, 20, fitness_limit=100 )
    gen = gen.generate()


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
    from converters.pitch import name_to_midi
    time = MusicTime(8,4,4)
    unit = MusicUnit(0, "Harmonics",
                    name_to_midi(name=['E4', 'D4', 'B3', 'Bb3', 'Eb4', 'Db4', 'C4', 'G3', 'A3'])
                     )

    gen = HarmonicsGenerator(unit,
                            fundamental_pitch = note.Pitch('A1').midi,
                            harmonic_numbers  = list(range(1,21))
                           )

    unit.stream = gen.harmonic_series(note.Pitch('A1').midi,[5,6,7,9,12,15])

def test_markov_chain ():

    gen = MarkovChainGenerator(train=Scale7ChordHarmony.movement_rules, start='1', length=16)
    units = gen.generate()
    print('Generated chords by Markov chain: ' + units[0])

    gen = MarkovChainGenerator(train=Scale7PitchDegree.movement_rules, start='1', length=16)
    units = gen.generate()
    print('Generated pitches by Markov chain: ' + units[0])


def test_progression():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicPattern(Cardinality.TRIA, PatternType.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicPattern(Cardinality.TETRA, PatternType.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicPattern(Cardinality.PENTA, PatternType.SCALE)

    seed_unit = MusicUnit("Seed", MusicTime(4,4,4))
    scale1 = MusicPattern(Cardinality.HEPTA, PatternType.SCALE, 60, Mode.major_mode)

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
    scale2 = MusicPattern(Cardinality.HEPTA, PatternType.SCALE, 60, Mode.mixolydian)

    gen = ProgressionGenerator(
        seed_unit=seed_unit2,
        time=seed_unit2.time,
        musicscale=scale2,
        chord_progression_degrees=[1, 4, 5, 6, 3, 2, 7]
    )

    unit = gen.generate()
    section = MusicSection (1,"Chord progression")
    section.matrix.set_unit(0,0,unit)
    voice = MusicVoice(1,'Piano voice')
    comp = MusicProject(1,'Chord progressions and triads')
    # Convert to music21 stream and save as MIDI file
    score = stream.Score()
    # TO DO: convert MusicComposition to music21 stream
    score_to_midifile(score,
                        'chordlibrary_in_key_' +
                        TwelveTET.PITCH_CLASS_NAMES_SHARP(scale1.tonic) +
                        '.mid')


    """Double code"""
    # Example: Get triads in C major
    gen = ProgressionGenerator()
    triads_c_major = gen.generate_triads_in_key(TwelveTET.C, Mode.MAJOR)
    for chord in triads_c_major:
        print(chord)


def test_from_chords():
    from generators.from_chord import FromChordGenerator
    unit = MusicUnit()
    # Create based on chord progression
    main_key = key.Key('C')
    # chord_degrees = [1, 4, 6, 2, 5, 1]
    chord_degrees = Scale7ChordHarmony.PROGRESSIONS[0]

    main_chords = stream.Stream()
    for i in chord_degrees:
        main_chords.append(roman.RomanNumeral(i, main_key))


    """ Generate a stream from chords """
    gen = FromChordGenerator(main_chords, 3, 4, 2)
    voices_stream = gen.generate()


def main():
    test_counterpoint()
    test_genetic()
    test_harmonics()
    test_progression()
    test_from_chords()
    test_markov_chain()

if __name__ == "__main__":
    main()