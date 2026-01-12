from structures import MusicPitchClass, MusicPitches, Direction
from structures import MusicTimeGrid, MusicLinearTime, MusicPitchClassPattern, Cardinality, PatternType, PatternRotation
from structures import MusicProject, MusicUnit, MusicVoice, UnitMatrix, MusicSection
from converters.music21_pattern import pattern_to_m21scale


def test_project():
    # Project
    project = MusicProject(
        name="My First Song",
        time_grid = MusicTimeGrid(ticks_per_cycle=4, beats_per_cycle=4),
        sections=[MusicSection(name="Intro")],
        voices=[MusicVoice("Melody"), MusicVoice("Bass")],
        matrix=UnitMatrix(shape=(2, 2)),
    )
    print(project.voices)

    # Units
    unit_a1 = MusicUnit()
    unit_a2 = MusicUnit()
    unit_b1 = MusicUnit()
    unit_b2 = MusicUnit()

    # Section with matrix
    project.matrix.set_unit(0, 0, unit_a1)
    project.matrix.set_unit(0, 1, unit_a2)
    project.matrix.set_unit(1, 0, unit_b1)
    project.matrix.set_unit(1, 1, unit_b2)
    print(project.matrix)


    # Print the structure
    print(project)
    print(project.sections[0])
    print(project.voices)


def test_pitch():
    tet_pitch = MusicPitchClass.E
    print(tet_pitch)

    # Chromatic pitches and transposition
    pitches = MusicPitches()
    pitches.show()

    pos = pitches.index_of(3, 7)  # octave 3, MusicPitchClass 7 -> index
    next_pos = pitches.transpose(pos, Direction.ASCENDING)  # next MusicPitchClass
    octave_pitch_class = pitches.get_at(next_pos)
    print(f'PitchRange: pos {pos} -> next pos {next_pos} -> (octave, MusicPitchClass) {octave_pitch_class}')


def test_patterns():

    pitch_pattern = MusicPitchClassPattern(name="C Minor",
                                      cardinality=Cardinality.HEPTA,
                                      definition=PatternType.SCALE,
                                      rotation=PatternRotation.minor,
                                      tonic=MusicPitchClass.C)
    pitch_classes = pitch_pattern.pitch_classes
    print (f'Pattern pitch classes: {pitch_classes}')
    m21scale = pattern_to_m21scale(pitch_pattern)
    print(m21scale)

    # Diatonic heptatonic scale patterns
    interval_pattern7 = MusicPitchClassPattern("Heptatonic scale", Cardinality.HEPTA, PatternType.SCALE)
    print(f'Heptatonic major scale intervals: {interval_pattern7.pitch_class_intervals}')

    major_triad = MusicPitchClassPattern("Major triad", Cardinality.TRIA, PatternType.MAJOR)  # Major triad
    print("Major Triad Intervals:", major_triad.pitch_class_intervals, "Pitch classes: ", major_triad.pitch_classes)

    minor7_chord = MusicPitchClassPattern("minor7 chord", Cardinality.TETRA, PatternType.MINOR7)  # Minor7 chord
    print("Minor7 Chord Intervals:", minor7_chord.pitch_class_intervals, "Pitch classes: ", minor7_chord.pitch_classes)

    # Patterns: Diatonic scales
    scale5cmajor = MusicPitchClassPattern("Pentatonic C major", Cardinality.PENTA, PatternType.SCALE, PatternRotation.major, MusicPitchClass.C)
    print(scale5cmajor.pitch_class_intervals, scale5cmajor.pitch_classes)
    scale7cmajor = MusicPitchClassPattern("Heptatonic C major", Cardinality.HEPTA, PatternType.SCALE, PatternRotation.major, MusicPitchClass.C,)
    print(scale7cmajor.pitch_class_intervals, scale7cmajor.pitch_classes)


def test_rhythm_time():
    # Example MusicUnit with Euclidian rhythm
    unit = MusicUnit()
    unit.onset_intervals = [1,2,1,1,2]

    # Music time and meter
    time_grid = MusicTimeGrid(ticks_per_cycle=16, beats_per_cycle=4, beat_note=4)
    time_grid.show()
    time = MusicLinearTime (time_grid=time_grid, bpm=120)
    print(f'Seconds per beat: {time.seconds_per_beat}, Seconds per cycle: {time.seconds_per_cycle()}')

def main():
    test_project()
    test_pitch()
    test_patterns()
    test_rhythm_time()

if __name__ == '__main__':
    main()
