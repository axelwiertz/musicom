from structures import MusicPitchClass, MusicPitchClassSet, MusicUnit, MusicVoice, MusicProject, MusicSection, \
    MusicTimeGrid, UnitMatrix
from converters.midi_converter import score_to_midifile
from converters.musicpy_converter import chord_to_unit, pattern_to_mpscale
from structures import PatternType, PatternRotation
from rules import Scale7PitchDegree, Counterpoint, PatternMovementRules
from generators import StochasticGenerator, MarkovChainGenerator, ChordDegreeGenerator, HarmonicsGenerator, PatternGenerator
from music21 import stream, note, key, roman

def test_counterpoint():
    # Create a two-voice counterpoint composition
    unit1 = MusicUnit(pitches=[60, 61, 72, 74, 76, 77, 79, 81])
    gen = StochasticGenerator(length=len(unit1),
                              duration_set=[1],
                              pitch_set=[60, 62, 64, 65, 67, 69, 71])
    unit2 = gen.generate()

    cp = Counterpoint(unit1, unit2)
    # Keep generating until counterpoint reached
    while not cp.has_crossing_voices() or not cp.has_parallel_perfect_intervals():
        unit2 = gen.generate()
        cp.set_units(unit1, unit2)
    print("Counterpoint achieved between two units.")

def test_genetic():
    from generators.genetic import GeneticGenerator, GenomeType

    # Example fitness function: counts the number of 1s in the genome
    def fitness_func(genome_: GenomeType) -> int:
        return sum(genome_)

    gen = GeneticGenerator(fitness_func,100, 20, fitness_limit=100 )

    # Run the genetic algorithm
    units = gen.generate()
    print ("Generated musical unit : %s" % units[0])

def test_harmonics():
    # Generate harmonic series
    unit = MusicUnit(pitches=[64, 62, 59, 58, 63, 61, 60, 55, 57])

    gen = HarmonicsGenerator(fundamental_pitch = note.Pitch('A1').midi,
                            harmonic_numbers  = list(range(1,21))
    )

    unit.stream = gen.harmonic_series(note.Pitch('A1').midi,[5,6,7,9,12,15])

def test_markov_chain ():

    gen = MarkovChainGenerator(train=PatternMovementRules.movement_rules, start='1', length=16)
    units = gen.produce()
    print('Generated chords by Markov chain: ' + units[0])

    gen = MarkovChainGenerator(train=Scale7PitchDegree.movement_rules, start='1', length=16)
    units = gen.produce()
    print('Generated pitches by Markov chain: ' + units[0])


def test_progression():

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicPitchClassSet("Major triad",PatternType.MAJOR)
    print("Scale3:", scale3)
    # 4 Tetra patterns:
    scale4 = MusicPitchClassSet("Major seventh", PatternType.MAJOR7)
    print("Scale4:", scale4)
    # 5 Penta patterns:
    scale5 = MusicPitchClassSet("Pentatonic scale", PatternType.PENTATONIC)
    print("Scale5:", scale5)
    # 6 Hexa patterns:
    scale6 = MusicPitchClassSet("Whole tone scale", PatternType.HEXATONIC)
    print("Scale6:", scale6)
    # 7 Hepta patterns:
    scale7 = MusicPitchClassSet("Major scale", PatternType.HEPTATONIC)
    print("Scale7:", scale7)


    time = MusicTimeGrid(ticks_per_cycle=16, beats_per_cycle=4, beat_note=4)
    scale1 = MusicPitchClassSet(name="C4 major", definition=PatternType.HEPTATONIC,
                                rotation=PatternRotation.major, initial= 60)

    triads_in_scale =  chord_to_unit(pattern_to_mpscale(scale7) % (1234567, 1))
    print("Triads in C major scale:", triads_in_scale)
    gen = ChordDegreeGenerator(
        time,
        scale7,
    [1, 2, 3, 4, 5, 6, 7])
    unit1 = gen.generate()
    print("Triads in C major scale:", unit1)

    scale2 = MusicPitchClassSet(name="C mixolydian",
                          definition=PatternType.HEPTATONIC,
                          rotation=PatternRotation.mixolydian,
                          initial=MusicPitchClass.C
                          )

    gen = ChordDegreeGenerator(
        time,
        scale2,
        [1, 4, 5, 6, 3, 2, 7]
    )
    unit2 = gen.generate()

    section = MusicSection ("Chord progression")
    voice = MusicVoice('Piano voice')
    proj = MusicProject(name='Chord progressions and triads',
                        pitch_pattern=MusicPitchClassSet("Project pattern"),
                        sections=[section],
                        voices=[voice],
                        matrix=UnitMatrix(shape=(1,1))
                        )
    proj.matrix.set_unit(pos=(0, 0), unit=unit1)
    proj.matrix.set_unit(pos=(0, 1), unit=unit2)

    print(proj)
    # Convert to music21 stream and save as MIDI file
    score = stream.Score()
    score_to_midifile(score,
                        'test.mid')


    """Double code"""
    # Example: Get triads in C major
    gen = ChordDegreeGenerator(
        MusicTimeGrid(ticks_per_cycle=4,beats_per_cycle=4,beat_note=4),
        scale1,
        [1, 2, 3, 4, 5, 6, 7]
    )
    triads_c_major = gen.generate()
    print(triads_c_major)


def test_from_chords():
    # Create based on chord progression
    main_key = key.Key('C')
    # chord_degrees = [1, 4, 6, 2, 5, 1]
    chord_degrees = PatternMovementRules.movement_rules[0]

    main_chords = stream.Stream()
    for i in chord_degrees:
        main_chords.append(roman.RomanNumeral(i, main_key))

    pattern = MusicPitchClassSet("Major7", PatternType.MAJOR7)
    print("Pattern:", pattern)

    """ Generate a stream from chords """
    gen = PatternGenerator([pattern], [3], 4, 2)
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