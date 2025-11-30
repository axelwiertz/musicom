from typing import List
from base.tuning import TwelveTET
from base.chromatic import Helix, ChromaticPitches
from base.diatonic import Cardinality, PatternType, Mode
from structures.time import MusicTime, Circle
from structures.pattern import MusicPattern
from structures.rhythm import QuantizedEvent, seconds_to_ticks, MetricalNode, HierarchicalEvent
from generators.rhythm import euclidian

from structures.unit import MusicUnit
from structures.project import MusicVoice
from structures.matrix import MusicMatrix
from structures.project import MusicProject, MusicSection


def test_project():
    # Project
    my_project = MusicProject(1, "My First Song")

    # Create voices
    voice1 = MusicVoice(0, "Melody")
    voice2 = MusicVoice(1, "Bass")
    print(voice1)
    print(voice2)

    # Units
    unit_a1 = MusicUnit(1)
    unit_a2 = MusicUnit(2)
    unit_b1 = MusicUnit(3)
    unit_b2 = MusicUnit(4)

    # Section with matrix
    intro_section = MusicSection(1, "Intro", MusicMatrix(2, 2))
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


def test_chromatic():
    # Chromatic pitches and transposition
    chromatic_pitches = ChromaticPitches()
    chromatic_pitches.show()

    pos = chromatic_pitches.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = chromatic_pitches.transpose(pos, chromatic_pitches.ASCENDING)  # next pitchclass
    octave_pitch_class = chromatic_pitches.get_at(next_pos)
    print(f'PitchRange: pos {pos} -> next pos {next_pos} -> (octave, pitchclass) {octave_pitch_class}')


def test_patterns():
    # Diatonic heptatonic scale patterns
    interval_pattern7 = MusicPattern(Cardinality.HEPTA, PatternType.SCALE)
    print(f'Heptatonic major scale intervals: {interval_pattern7.pitch_intervals}')

    major_triad = MusicPattern(3, 3)  # Major triad
    minor7_chord = MusicPattern(4, 1)  # Minor7 chord

    print("Major Triad Intervals:", major_triad.pitch_intervals)
    print("Minor7 Chord Intervals:", minor7_chord.pitch_intervals)


    # Show pitch class circle
    pc_circle = Circle(TwelveTET.TWELVE, TwelveTET.PITCH_CLASS_NAMES_SHARP)
    pc_circle.show()

    # Patterns: Diatonic scales
    scale5cmajor = MusicPattern(Cardinality.PENTA, PatternType.SCALE,
                              tonic=TwelveTET.C, mode=Mode.major_mode)
    print(scale5cmajor.pitch_intervals)
    scale7cmajor = MusicPattern(Cardinality.HEPTA, PatternType.SCALE,
                              tonic=TwelveTET.C, mode=Mode.major_mode)
    print(scale7cmajor.pitch_intervals)

    #    pc_circle.show(pcp7.majormodeschromatic, TwelveTET.PITCH_CLASS_NAMES_SHARP, 'Major circle')

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
    unit.onset_intervals = euclidian(3, 8)

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
    test_project()
    test_chromatic()
    test_patterns()
    test_rhythm_time()


if __name__ == '__main__':
    main()
