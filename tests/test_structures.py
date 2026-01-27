from structures import MusicPitchClass, PatternGraph,  MusicPitchGrid, Direction
from structures import MusicTimeGrid, MusicLinearTime, MusicRhythmPattern
from structures import MusicPitchClassSet, PatternType, PatternRotation
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
    project.matrix.set_unit(pos=(0, 0), unit= unit_a1)
    project.matrix.set_unit(pos=(0, 1), unit= unit_a2)
    project.matrix.set_unit(pos=(1, 0), unit= unit_b1)
    project.matrix.set_unit(pos=(1, 1), unit= unit_b2)
    print(project.matrix)


    # Print the structure
    print(project)
    print(project.sections[0])
    print(project.voices)


def test_pitch():
    tet_pitch = MusicPitchClass.E
    print(tet_pitch)

    # Chromatic pitches and transposition
    pitches = MusicPitchGrid()
    pitches.show()

    pos = pitches.index_of(3, 7)  # octave 3, MusicPitchClass 7 -> index
    next_pos = pitches.transpose(pos, Direction.ASCENDING)  # next MusicPitchClass
    octave_pitch_class = pitches.get_at(next_pos)
    print(f'MusicPitchRange: pos {pos} -> next pos {next_pos} -> (octave, MusicPitchClass) {octave_pitch_class}')


def test_patterns():

    pitch_pattern = MusicPitchClassSet(name="C Minor",
                                      definition=PatternType.HEPTATONIC,
                                      rotation=PatternRotation.minor,
                                      initial=MusicPitchClass.C)
    pitch_classes = pitch_pattern.pitch_classes
    print (f'Pattern pitch classes: {pitch_classes}')
    m21scale = pattern_to_m21scale(pitch_pattern)
    print(m21scale)

    # Diatonic heptatonic scale patterns
    interval_pattern7 = MusicPitchClassSet("Heptatonic scale", PatternType.HEPTATONIC)
    print(f'Heptatonic major scale intervals: {interval_pattern7.pitch_class_intervals}')

    major_triad = MusicPitchClassSet("Major triad", PatternType.MAJOR)  # Major triad
    print("Major Triad Intervals:", major_triad.pitch_class_intervals, "Pitch classes: ", major_triad.pitch_classes)

    minor7_chord = MusicPitchClassSet("minor7 chord", PatternType.MINOR7)  # Minor7 chord
    print("Minor7 Chord Intervals:", minor7_chord.pitch_class_intervals, "Pitch classes: ", minor7_chord.pitch_classes)

    # Patterns: Diatonic scales
    scale5cmajor = MusicPitchClassSet("Pentatonic C major", PatternType.PENTATONIC, PatternRotation.major, MusicPitchClass.C)
    print(scale5cmajor.pitch_class_intervals, scale5cmajor.pitch_classes)
    scale7cmajor = MusicPitchClassSet("Heptatonic C major", PatternType.HEPTATONIC, PatternRotation.major, MusicPitchClass.C,)
    print(scale7cmajor.pitch_class_intervals, scale7cmajor.pitch_classes)

    # Create pitch class sets
    chromatic = MusicPitchClassSet("Chromatic", PatternType.CHROMATIC, initial=0)
    major_scale = MusicPitchClassSet("Major Scale", PatternType.HEPTATONIC, initial=0)
    pentatonic = MusicPitchClassSet("Pentatonic", PatternType.PENTATONIC, initial=0)
    major_triad = MusicPitchClassSet("Major Triad", PatternType.MAJOR, initial=0)
    major_seventh = MusicPitchClassSet("Major 7th", PatternType.MAJOR7, initial=0)

    # Create pattern graph
    graph = PatternGraph()

    # Add pitch class sets to graph
    graph.add_pitch_class_set(chromatic)
    graph.add_pitch_class_set(major_scale)
    graph.add_pitch_class_set(pentatonic)
    graph.add_pitch_class_set(major_triad)
    graph.add_pitch_class_set(major_seventh)

    # Build subset hierarchy
    graph.add_subset_relation(chromatic, major_scale)
    graph.add_subset_relation(major_scale, pentatonic)
    graph.add_subset_relation(major_scale, major_seventh)
    graph.add_subset_relation(major_seventh, major_triad)

    # Query the hierarchy
    print("Subsets of major scale:")
    for subset in graph.get_subsets(major_scale):
        print(f"  - {subset.name}")

    print("\nAll subsets of chromatic scale:")
    for subset in graph.get_all_subsets(chromatic):
        print(f"  - {subset.name}")

    print("\nSupersets of major triad:")
    for superset in graph.get_supersets(major_triad):
        print(f"  - {superset.name}")

    # Visualize the hierarchy
    print("\n" + graph.visualize())



def test_rhythm_time():
    # Example MusicUnit with Euclidian rhythm
    rhythm = MusicRhythmPattern(onset_intervals=[1,2,1,1,2])
    print(rhythm.pitch_class_intervals)

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
