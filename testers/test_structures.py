from typing import List
from structures import Constants, PitchClass, MusicPitches
from structures import Helix, Circle, Direction
from structures import MusicTime, MusicPattern, MusicUnit, MusicVoice, MusicMatrix, MusicProject, MusicSection
from structures.rhythm import QuantizedEvent,seconds_to_ticks, MetricalNode, HierarchicalEvent
from rules import Cardinality, PatternType, PatternMode
from converters import pattern_to_m21scale



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
    intro_section = MusicSection("Intro", MusicTime(4,4,4) , MusicMatrix(2, 2))
    intro_section.matrix.set_unit(0, 0, unit_a1)
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
    tet = Constants.OCTAVES
    print(f"TwelveTET Octaves: {tet}")
    tet_pitch = PitchClass.E
    print(tet_pitch)

    # Chromatic pitches and transposition
    pitches = MusicPitches()
    pitches.show()

    pos = pitches.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = pitches.transpose(pos, Direction.ASCENDING)  # next pitchclass
    octave_pitch_class = pitches.get_at(next_pos)
    print(f'PitchRange: pos {pos} -> next pos {next_pos} -> (octave, pitchclass) {octave_pitch_class}')


def test_patterns():
    # New composition
    project = MusicProject('Test Patterns',
                           MusicPattern("C Major", Cardinality.HEPTA, PatternType.SCALE, PatternMode.major_mode, PitchClass.C)
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

    # Show pitch class circle
    pc_circle = Circle(Constants.TWELVE, PitchClass.NAMES_SHARP)
    pc_circle.show()

    # Patterns: Diatonic scales
    scale5cmajor = MusicPattern("Pentatonic C major", Cardinality.PENTA, PatternType.SCALE, PatternMode.major_mode, PitchClass.C)
    print(scale5cmajor.pitch_class_intervals, scale5cmajor.pitch_classes)
    scale7cmajor = MusicPattern("Heptatonic C major", Cardinality.HEPTA, PatternType.SCALE, PatternMode.major_mode, PitchClass.C,)
    print(scale7cmajor.pitch_class_intervals, scale7cmajor.pitch_classes)

    #    pc_circle.show(pcp7.majormodeschromatic, PitchClass.NAMES_SHARP, 'Major circle')

def test_helix():
    # Show helix
    h = Helix()
    h.show()
    # Test functions
    # Show rhythm in circle
    rc = Circle(4, ['Down', 'Up', 'Down', 'Up'])
    rc.show()


def test_rhythm_time():
    # Example MusicUnit with Euclidian rhythm
    unit = MusicUnit()
    unit.onset_intervals = [1,2,1,1,2]

    # Music time and meter
    time = MusicTime(16, 4, 4, 120)
    time.show('16 timesteps circle')

    # Example quantized events
    bpm = 120.0
    tpb = 96  # high-resolution
    times = [0.0, 0.5, 0.75]

    quant_events: List[QuantizedEvent] = [
        QuantizedEvent(tick=seconds_to_ticks(t, bpm, tpb),
                       ticks_per_beat=tpb,
                       duration_ticks=max(1, seconds_to_ticks(0.1, bpm, tpb)))
        for t in times
    ]
    print("Quantized Events:")
    for qe in quant_events:
        print(qe)

    # Build a simple hierarchy for 120 BPM (0.5s per beat), 4/4 measure
    beat = MetricalNode('beat', period=0.5, phase_offset=0.0)
    measure = MetricalNode('measure', period=2.0, phase_offset=0.0, children=[beat])
    print(measure)
    sub = MetricalNode('eighth', period=0.25, phase_offset=0.0, children=[])
    beat.children.append(sub)

    # Map onsets into hierarchy (choose nearest level/phase)
    times = [0.0, 0.5, 0.75]
    hier_events = []
    for t in times:
        # find closest metrical level and its phase
        # naive: pick beat-level for demonstration
        hier_events.append(HierarchicalEvent(time=t, node=beat, label='onset'))
    print(hier_events)

def main():
    test_helix()
    test_project()
    test_pitch()
    test_patterns()
    test_rhythm_time()

if __name__ == '__main__':
    main()
