from structures import MusicPitchClass, MusicPattern, MusicUnit, MusicVoice, MusicProject, MusicSection, MusicTime
from converters import score_to_midifile, chord_to_unit, pattern_to_mpscale
from rules import Cardinality, PatternType, PatternMode, Scale7PitchDegree, is_counterpoint, Scale7ChordHarmony
from generators import StochasticGenerator, MarkovChainGenerator, ChordDegreeGenerator, HarmonicsGenerator
from music21 import stream, note, key, roman

def test_counterpoint():
    # Create a two-voice counterpoint composition
    unit1 = MusicUnit("Test",
                      [60, 61, 72, 74, 76, 77, 79, 81]
                      )
    gen = StochasticGenerator(length=len(unit1),
                              duration_set=[1],
                              pitch_set=[60, 62, 64, 65, 67, 69, 71])
    unit2 = gen.generate()

    # Keep generating until counterpoint reached
    while not is_counterpoint(unit1, unit2):
        unit2 = gen.generate()
    print("Counterpoint achieved between two streams.")

def test_genetic():
    from generators.genetic import GeneticGenerator, GenomeType

    # Example fitness function: counts the number of 1s in the genome
    def fitness_func(genome_: GenomeType) -> int:
        return sum(genome_)

    gen = GeneticGenerator(fitness_func,100, 20, fitness_limit=100 )
    gen = gen.produce()

    # Run the genetic algorithm
    final_population, generations = gen.run_evolution(
        populate_func=lambda: gen.generate_population(),
        fitness_func=fitness_func,
        fitness_limit=20,
        generation_limit=50,
        printer=gen.print_stats
    )

    print("Final Population after %d generations:" % generations)
    for genome in final_population:
        print("%s (Fitness: %d)" % (gen.genome_to_string(genome), fitness_func(genome)))

    # Use a genetic algorithm to create a population of musical units
    gen = GeneticGenerator(fitness_func=fitness_func, size=10, genome_length=20, fitness_limit=20,
        generation_limit=50)

    # Run the genetic algorithm
    units = gen.generate()
    print ("Generated musical unit : %s" % units[0])

def test_harmonics():
    # Generate harmonic series
    unit = MusicUnit("Harmonics",
                    [64, 62, 59, 58, 63, 61, 60, 55, 57]
                     )

    gen = HarmonicsGenerator(unit,
                            fundamental_pitch = note.Pitch('A1').midi,
                            harmonic_numbers  = list(range(1,21))
    )

    unit.stream = gen.harmonic_series(note.Pitch('A1').midi,[5,6,7,9,12,15])

def test_markov_chain ():

    gen = MarkovChainGenerator(train=Scale7ChordHarmony.movement_rules, start='1', length=16)
    units = gen.produce()
    print('Generated chords by Markov chain: ' + units[0])

    gen = MarkovChainGenerator(train=Scale7PitchDegree.movement_rules, start='1', length=16)
    units = gen.produce()
    print('Generated pitches by Markov chain: ' + units[0])


def test_progression():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicPattern("Major triad",Cardinality.TRIA, PatternType.MAJOR)
    print("Scale3:", scale3)
    # 4 Tetra patterns:
    scale4 = MusicPattern("Major seventh", PatternType.MAJOR7)
    print("Scale4:", scale4)
    # 5 Penta patterns:
    scale5 = MusicPattern("Pentatonic scale", Cardinality.PENTA, PatternType.SCALE)
    print("Scale5:", scale5)
    # 6 Hexa patterns:
    scale6 = MusicPattern("Whole tone scale", Cardinality.HEXA, PatternType.SCALE)
    print("Scale6:", scale6)
    # 7 Hepta patterns:
    scale7 = MusicPattern("Major scale", Cardinality.HEPTA, PatternType.SCALE)
    print("Scale7:", scale7)


    time = MusicTime(4,4,4)
    scale1 = MusicPattern("C4 major", Cardinality.HEPTA, PatternType.SCALE, 60, PatternMode.major_mode)

    triads_in_scale =  chord_to_unit(pattern_to_mpscale(scale7) % (1234567, 1))
    print("Triads in C major scale:", triads_in_scale)
    gen = ChordDegreeGenerator(
        time,
        scale7,
    [1, 2, 3, 4, 5, 6, 7])
    unit = gen.generate()
    print("Triads in C major scale:", unit)

    scale2 = MusicPattern("C4 mixolydian",
                          Cardinality.HEPTA,
                          PatternType.SCALE,
                          60,
                          PatternMode.mixolydian)

    gen = ChordDegreeGenerator(
        time,
        scale2,
        [1, 4, 5, 6, 3, 2, 7]
    )

    unit = gen.generate()
    section = MusicSection ("Chord progression")
    section.matrix.set_unit(0,0,unit)
    voice = MusicVoice('Piano voice')
    proj = MusicProject('Chord progressions and triads',
                        MusicPattern("Project pattern"),
                        [section],
                        [voice],
                        )
    print(proj)
    # Convert to music21 stream and save as MIDI file
    score = stream.Score()
    # TO DO: convert MusicComposition to music21 stream
    score_to_midifile(score,
                        'chord_library_in_key_' +
                        MusicPitchClass.NAMES_SHARP(scale1.tonic_pitch_class) +
                        '.mid')


    """Double code"""
    # Example: Get triads in C major
    gen = ChordDegreeGenerator(
        MusicTime(4,4,4),
        scale1,
        [1, 2, 3, 4, 5, 6, 7]
    )
    triads_c_major = gen.generate()
    print(triads_c_major)


def test_from_chords():
    from generators import ParallelPatternChordGenerator
    # Create based on chord progression
    main_key = key.Key('C')
    # chord_degrees = [1, 4, 6, 2, 5, 1]
    chord_degrees = Scale7ChordHarmony.movement_rules[0]

    main_chords = stream.Stream()
    for i in chord_degrees:
        main_chords.append(roman.RomanNumeral(i, main_key))


    """ Generate a stream from chords """
    gen = ParallelPatternChordGenerator(main_chords, 3, 4, 2)
    units = gen.generate()
    print(units)

def main():
    test_counterpoint()
    test_genetic()
    test_harmonics()
    test_progression()
    test_from_chords()
    test_markov_chain()

if __name__ == "__main__":
    main()