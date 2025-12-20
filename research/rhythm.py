""" Rhythm and Meter Data Structures"""
from music21 import meter

# Rhythm: sequential pattern of events at timesteps
# A rhythm sequence is defined by
#  - a sequence of timestep intervals between events
#  - a tempo (BPM) defining real-time mapping of timesteps to seconds
#  - a number of timesteps per measure (defining the meter)

# Meter: hierarchical structure of time signatures
"""
Aspects of TimeSignatures are controlled by the music21.meter.TimeSignature.
    beatSequence   : where the beats in the measure are and how many there are
    beamSequence   : How the notes should be beamed
    accentSequence : How much accent or weight each note gets
All sequences are of class MeterSequence
"""
term = meter.MeterTerminal()
seq = meter.MeterSequence(term)
# [1, 0, 1, 0]  # e.g., 4/4 time with accents on beats 1 and 3
ts = meter.TimeSignature('4/4')
ts.beatSequence = seq

# Data structures for rhythm representation

# Quantized grid (ticks per beat)
# quantized_grid.py
# quant_events -> use in MIDI-like grid processing
from dataclasses import dataclass



@dataclass
class QuantizedEvent:
    tick: int          # integer tick index
    ticks_per_beat: int
    duration_ticks: int

def seconds_to_ticks(time_s: float, bpm: float, ticks_per_beat: int) -> int:
    beats = time_s * (bpm / 60.0)
    return int(round(beats * ticks_per_beat))


# Hierarchical tree (metrical levels)
# hierarchical_tree.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MetricalNode:
    level_name: str                # e.g., 'beat', 'measure', 'subdivision'
    period: float                  # seconds between ticks at this level
    phase_offset: float = 0.0      # seconds offset relative to global t=0
    children: List['MetricalNode'] = field(default_factory=list)

@dataclass
class HierarchicalEvent:
    time: float
    node: MetricalNode
    label: Optional[str] = None


def build_sample_metrical_tree() -> MetricalNode:
    measure_node = MetricalNode(level_name='measure', period=4.0)
    beat_node = MetricalNode(level_name='beat', period=1.0)
    subdivision_node = MetricalNode(level_name='subdivision', period=0.5)

    beat_node.children.append(subdivision_node)
    measure_node.children.append(beat_node)

    return measure_node

def test_rhythm_structures():
    # Test QuantizedEvent
    quant_event = QuantizedEvent(tick=120, ticks_per_beat=480, duration_ticks=240)
    print(f'Quantized Event: {quant_event}')

    # Test seconds to ticks conversion
    ticks = seconds_to_ticks(2.0, bpm=120, ticks_per_beat=480)
    print(f'Seconds to Ticks: 2.0s at 120 BPM -> {ticks} ticks')

    # Test MetricalNode tree
    metrical_tree = build_sample_metrical_tree()
    print(f'Metrical Tree Root: {metrical_tree.level_name} with period {metrical_tree.period}s')

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
    test_rhythm_structures()

if __name__ == '__main__':
    main()