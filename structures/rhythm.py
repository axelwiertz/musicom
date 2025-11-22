"""
Musicom - rhythm
hythmic data structures
"""
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
seq = meter.MeterSequence()
seq.type = 'beat'
seq.sequence = [1, 0, 1, 0]  # e.g., 4/4 time with accents on beats 1 and 3
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
    track: int = 0
    velocity: float = 1.0
    duration_ticks: int = 1

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

