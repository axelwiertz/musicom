"""
Musicom generators - rhythm
Generating rhythmic patterns
"""

# Rhythm: sequential pattern of onsets at timesteps
# A rhythm sequence is defined by
#  - a sequence of timestep intervals between onsets

# Meter: hierarchical structure of time signatures
"""
Aspects of TimeSignatures are controlled by the music21.meter.TimeSignature.
    beatSequence   : where the beats in the measure are and how many there are
    beamSequence   : How the notes should be beamed
    accentSequence : How much accent or weight each note gets
All sequences are of class MeterSequence
"""



# Quantized grid (ticks per beat)
# quantized_grid.py
# quant_events -> use in MIDI-like grid processing
from dataclasses import dataclass

from structures import MusicUnit, Circle


class MusicTime (Circle):
    # Rhythm and meter
    def __init__(self,
                 timesteps: int = 8, # Number of timesteps (ticks) per cycle
                 beats_in_measure: int = 4,
                 beat_note: int = 4,
                 bpm: int = 100):
        # Timestep is the smallest rhythm relative unit, represented as integer
        self.timesteps = timesteps
        super().__init__(timesteps, labels=[str(i+1) for i in range(timesteps)])
        # Meter: measure cycle of beats
        self.beats_in_measure = beats_in_measure
        self.beat_note = beat_note
        self.bpm = bpm


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


def euclidian (onsets: int = 4,
                      timesteps: int = 4 ) -> list[int] :
    # Divide number of onsets evenly over number of timesteps, reduced if duplicate

    # Onsets gets an equal timestep interval
    base_timestep_interval = timesteps // onsets
    # And the remaining timesteps are a separate time step interval
    remaining_timesteps = timesteps % onsets

    rhythm = []
    for i in range(onsets):
        rhythm_timestep_interval = base_timestep_interval
        if i < remaining_timesteps:
            rhythm_timestep_interval += 1
        rhythm.append (rhythm_timestep_interval)

    # Reduce
    while rhythm[0] != rhythm[-1]:
        for group in rhythm:
            if group != rhythm[-1]:
                    group += rhythm.pop(-1)

    last_interval = timesteps - sum(rhythm)
    if last_interval > 0:
        rhythm.append(last_interval)

    return rhythm


def main():
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

if __name__ == "__main__":
    main()