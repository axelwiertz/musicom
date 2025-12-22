from structures import MusicPitchClass, MusicPitch, Direction
from structures import MusicTime, MusicPattern, Cardinality, PatternType, PatternMode
from structures import MusicProject, MusicUnit, MusicVoice, MusicMatrix, MusicSection
from converters.music21_pattern import pattern_to_m21scale


def test_project():
    # Project
    my_project = MusicProject("My First Song")

    # Create voices
    voices = [MusicVoice("Melody"), MusicVoice("Bass")]
    print(voices)

    # Units
    unit_a1 = MusicUnit()
    unit_a2 = MusicUnit()
    unit_b1 = MusicUnit()
    unit_b2 = MusicUnit()

    # Section with matrix
    intro_section = MusicSection(name="Intro",
                                 time=MusicTime(4,4,4))
    matrix = MusicMatrix(2, 2)
    .matrix.set_unit(0, 0, unit_a1)
    intro_section.matrix.set_unit(0, 1, unit_a2)
    intro_section.matrix.set_unit(1, 0, unit_b1)
    intro_section.matrix.set_unit(1, 1, unit_b2)
    print(intro_section.matrix)

    my_project.sections = [intro_section]

    # Print the structure
    print(my_project)
    print(my_project.sections[0])
    print(my_project.sections[0].matrix)


def test_pitch():
    tet_pitch = MusicPitchClass.E
    print(tet_pitch)

    # Chromatic pitches and transposition
    pitches = MusicPitch()
    pitches.show()

    pos = pitches.index_of(3, 7)  # octave 3, MusicPitchClass 7 -> index
    next_pos = pitches.transpose(pos, Direction.ASCENDING)  # next MusicPitchClass
    octave_pitch_class = pitches.get_at(next_pos)
    print(f'PitchRange: pos {pos} -> next pos {next_pos} -> (octave, MusicPitchClass) {octave_pitch_class}')


def test_patterns():
    # New composition
    project = MusicProject('Test Patterns',
                           MusicPattern("C Major", Cardinality.HEPTA, PatternType.SCALE, PatternMode.major, MusicPitchClass.C)
                           )
    pitch_classes = project.pattern.pitch_classes
    print (f'Pattern pitch classes: {pitch_classes}')
    m21scale = pattern_to_m21scale(project.pattern)
    print(m21scale)

    # Diatonic heptatonic scale patterns
    interval_pattern7 = MusicPattern("Heptatonic scale", Cardinality.HEPTA, PatternType.SCALE)
    print(f'Heptatonic major scale intervals: {interval_pattern7.pitch_class_intervals}')

    major_triad = MusicPattern("Major triad", Cardinality.TRIA, PatternType.MAJOR)  # Major triad
    print("Major Triad Intervals:", major_triad.pitch_class_intervals, "Pitch classes: ", major_triad.pitch_classes)

    minor7_chord = MusicPattern("minor7 chord", Cardinality.TETRA, PatternType.MINOR7)  # Minor7 chord
    print("Minor7 Chord Intervals:", minor7_chord.pitch_class_intervals, "Pitch classes: ", minor7_chord.pitch_classes)

    # Patterns: Diatonic scales
    scale5cmajor = MusicPattern("Pentatonic C major", Cardinality.PENTA, PatternType.SCALE, PatternMode.major, MusicPitchClass.C)
    print(scale5cmajor.pitch_class_intervals, scale5cmajor.pitch_classes)
    scale7cmajor = MusicPattern("Heptatonic C major", Cardinality.HEPTA, PatternType.SCALE, PatternMode.major, MusicPitchClass.C,)
    print(scale7cmajor.pitch_class_intervals, scale7cmajor.pitch_classes)


def test_rhythm_time():
    # Example MusicUnit with Euclidian rhythm
    unit = MusicUnit()
    unit.onset_intervals = [1,2,1,1,2]

    # Music time and meter
    time = MusicTime(16, 4, 4, 120)
    time.show()


def main():
    test_project()
    test_pitch()
    test_patterns()
    test_rhythm_time()

if __name__ == '__main__':
    main()
