"""
Rhythm - Data structures for each representation
(event-list, quantised grid, hierarchical tree, phase-based)

(dataclasses + simple constructors) for four rhythm representations:
event-list, quantized grid, hierarchical tree, and phase-based.
Example (three onsets at 0.0s, 0.5s, 0.75s; tempo 120 BPM) into that format.

- Use event-list for flexible, continuous-time processing (onset detection, ML datasets).
- Use quantized grid for symbolic editing, MIDI export, and DAW workflows.
- Use hierarchical tree for metrical analyses, score rendering, and meter-aware algorithms.
- Use phase-based states for oscillator models, entrainment simulations, and beat-prediction.

"""

# Event-list (timestamped events)
# event_list.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Event:
    time: float            # seconds (continuous)
    duration: Optional[float] = None  # seconds or None
    track: Optional[int] = 0
    velocity: Optional[float] = 1.0
    label: Optional[str] = None

# Example rhythm (seconds)
events: List[Event] = [
    Event(time=0.0, duration=0.1, track=0, velocity=1.0),
    Event(time=0.5, duration=0.1, track=0, velocity=0.9),
    Event(time=0.75, duration=0.1, track=0, velocity=0.95),
]
```

# Quantized grid (ticks per beat)
# quantized_grid.py
# quant_events -> use in MIDI-like grid processing
from dataclasses import dataclass
from typing import List
import math

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

# Example params
bpm = 120.0
tpb = 96  # high-resolution
times = [0.0, 0.5, 0.75]

quant_events: List[QuantizedEvent] = [
    QuantizedEvent(tick=seconds_to_ticks(t, bpm, tpb),
                   ticks_per_beat=tpb,
                   duration_ticks=max(1, seconds_to_ticks(0.1, bpm, tpb)))
    for t in times
]

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


# Phase-based representation (continuous phase per metrical level)
# phase_based.py
from dataclasses import dataclass
from typing import Dict, List
import math

@dataclass
class PhaseState:
    level: str           # e.g., 'beat', 'bar'
    phase: float         # radians in [0, 2*pi)
    frequency: float     # Hz

@dataclass
class PhaseEvent:
    time: float
    phases: Dict[str, float]   # mapping level -> phase (radians)

def time_to_phase(time_s: float, bpm: float, level_div: float = 1.0) -> float:
    hz = bpm / 60.0 / level_div
    return (2 * math.pi * (time_s * hz)) % (2*math.pi)

# Example: compute phase states for times at beat and bar levels
bpm = 120.0
times = [0.0, 0.5, 0.75]
phase_events: List[PhaseEvent] = []
for t in times:
    phases = {
        'beat': time_to_phase(t, bpm, level_div=1.0),
        'bar' : time_to_phase(t, bpm, level_div=4.0),
        'eighth': time_to_phase(t, bpm, level_div=0.5),
    }
    phase_events.append(PhaseEvent(time=t, phases=phases))
