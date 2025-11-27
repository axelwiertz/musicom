from typing import List
import pandas as pd
import numpy as np
from utilities import Config
from constants import TwelveTET
from structures.composition import PitchRegister
from structures.unit import MusicUnit
from structures.time import MusicTime
from structures.pattern import MusicPattern
from regularity.diatonic import Diatonic
from structures.time import Circle
from structures.helix import Helix
from structures.rhythm import QuantizedEvent, seconds_to_ticks, MetricalNode, HierarchicalEvent
from generators.rhythm import euclidian
from music21 import interval

from structures.unit import MusicUnit
from structures.composition import MusicVoice
from structures.matrix import MusicMatrix
from structures.project import Project, Section

def test_project():
    ### Usage Example
    # Here is how you can combine these classes to build a project structure.

    # 2. Create units with voices
    voice1 = MusicVoice(0, name="Melody")
    unit_a1 = MusicUnit(1)
    unit_a2 = MusicUnit(2)
    voice2 = MusicVoice(1, name="Bass")
    unit_b1 = MusicUnit(3)
    unit_b2 = MusicUnit(4)
    proj = Project(1, name="My First Song", sections=[])

    # 3. Create a matrix and populate it with units
    section1 = Section(1, name="Intro", matrix=MusicMatrix(2,2))
    main_matrix.set_unit(0, 0, unit_a1)
    main_matrix.set_unit(0, 1, unit_a2)
    main_matrix.set_unit(1, 0, unit_b1)
    main_matrix.set_unit(1, 1, unit_b2)

    # 4. Create a section with the matrix
    intro_section = Section(name="Intro", matrix=main_matrix)

    # 5. Create a project and add the section
    my_project = Project(name="My First Song")
    my_project.add_section(intro_section)

    # Print the structure
    print(my_project)
    print(my_project.sections[0])
    print(my_project.sections[0].matrix.grid)


def test_structures():
    # Piano register from A0 to C8
    reg = PitchRegister(TwelveTET.A, 0, TwelveTET.C, 8)
    reg.show()

    pos = reg.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = reg.transpose(pos,reg.ASCENDING)  # next pitchclass
    octave_pitchclass = reg.get_at(next_pos)
    print (f'PitchRegister: pos {pos} -> next pos {next_pos} -> (octave, pitchclass) {octave_pitchclass}')

    scale5cmajor = MusicPattern(Diatonic.PENTA, Diatonic.SCALE,
                              tonic=TwelveTET.C, mode=Diatonic.major_mode)
    scale7cmajor = MusicPattern(Diatonic.HEPTA, Diatonic.SCALE,
                              tonic=TwelveTET.C, mode=Diatonic.major_mode)

    m21intervals = list(interval.ChromaticInterval(n) for n in TwelveTET.PITCH_CLASS_NUMBERS)

    # Table of all absolute chromatic data along pitch number set
    interval_pattern7 = MusicPattern(Diatonic.HEPTA, Diatonic.SCALE)
    scale7 = MusicPattern(Diatonic.HEPTA, Diatonic.SCALE, tonic=TwelveTET.C, mode=Diatonic.major_mode)

    # Pitch helixes for heptatonic modes
    # Major
    majormodehelix = TwelveTET.OCTAVES * interval_pattern7.modeshelix[Diatonic.major_mode]
    # Minor
    minormodehelix = TwelveTET.OCTAVES * interval_pattern7.modeshelix[Diatonic.minor_mode]

    # Major mode pitch helixes for all tonics (C, C#, D, ..., B)
    majorscales = [majormodehelix[-x:] + majormodehelix[:-x] for x in range(TwelveTET.TWELVE)]
    minorscales = [minormodehelix[-x:] + minormodehelix[:-x] for x in range(TwelveTET.TWELVE)]

    chromatic_data = pd.DataFrame(majorscales)
    chromatic_data.to_excel(Config.DEFAULT_PATH + 'ChromaticLayer.xlsx', index=True, sheet_name='Pitch')

    chromatic_table = chromatic_data.transpose()
    #chromatic_table.columns = ['Nr', 'ClassNr', 'ClassChr', 'Freq'] + list(TwelveTET.PITCH_CLASS_NAMES_SHARP)
    chromatic_table.to_excel(Config.DEFAULT_PATH + 'ChromaticTable.xlsx', index=True, sheet_name='Pitch')

    hepta_major_arr = np.array(majorscales)

    pc_circle = Circle(TwelveTET.TWELVE, TwelveTET.PITCH_CLASS_NAMES_SHARP)
    pc_circle.show()

#    pc_circle.show(pcp7.majormodeschromatic, TwelveTET.PITCH_CLASS_NAMES_SHARP, 'Major circle')

    h = Helix()
    h.show()
    # Test functions
    # Show rhythm in circle
    rc = Circle(4, ['Down', 'Up','Down', 'Up'])
    rc.show()

def test_rhythm_time():
    # Example MusicUnit with Euclidian rhythm
    unit = MusicUnit()
    unit.onset_intervals = euclidian (3, 8)

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
    test_structures()
    test_rhythm_time()

if __name__ == '__main__':
    main()
