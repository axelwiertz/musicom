"""
Schillinger System of Musical Design Generator (Method 018)

Generates rhythmic resultants and coordinates based on algebraic
interference patterns between two generators (periodicities a and b).
"""

from typing import List, Tuple
from structures.matrix import MusicUnit
from structures.unit import MusicEvent
import math

class SchillingerGenerator:
    """
    Implements Joseph Schillinger's system of musical design for RHYTHM
    and PITCH axis projections.
    """
    def __init__(self, generator_a: int = 3, generator_b: int = 2):
        self.a = generator_a
        self.b = generator_b

    def generate_resultant(self) -> List[int]:
        """
        Generates the binary interference pattern (resultant r_ab)
        of two periodic generators a and b.
        Returns a list of durations (ticks/pulses).
        """
        total_span = self.a * self.b
        pattern_a = [0] * total_span
        pattern_b = [0] * total_span

        for i in range(total_span):
            if i % self.a == 0:
                pattern_a[i] = 1
            if i % self.b == 0:
                pattern_b[i] = 1

        # Combine arrays
        combined = [0] * total_span
        for i in range(total_span):
            if pattern_a[i] == 1 or pattern_b[i] == 1:
                combined[i] = 1

        # Extract durations
        durations = []
        current_dur = 0
        for i in range(total_span):
            if combined[i] == 1 and i > 0:
                durations.append(current_dur)
                current_dur = 1
            else:
                current_dur += 1
        durations.append(current_dur)
        return durations

    def generate_unit(self, base_tick_dur: int = 120, key_scale: List[int] = None) -> MusicUnit:
        """
        Converts Schillinger durations and axis projection to a MusicUnit.
        """
        if key_scale is None:
            key_scale = [60, 62, 64, 65, 67, 69, 71, 72] # C Major

        durations = self.generate_resultant()
        unit = MusicUnit()
        current_time = 0

        for i, dur in enumerate(durations):
            # Map index/time to a coordinate axis projection for PITCH
            # Coordinate tracking along a diagonal/sine curve trajectory
            pitch_idx = int(4 + 3 * math.sin(i * 0.8))
            pitch = key_scale[pitch_idx % len(key_scale)]
            
            event = MusicEvent(
                pitch=pitch,
                volume=100,
                start_tick=current_time,
                end_tick=current_time + (dur * base_tick_dur)
            )
            unit.add_event(event)
            current_time += dur * base_tick_dur

        return unit
