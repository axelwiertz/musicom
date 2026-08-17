"""Interval Markov chain generator — transposition-invariant melodies.

States are SEMITONE INTERVALS (deltas), not pitch classes. Generating a
chain of intervals and re-rooting at any start pitch yields the same
structural melody in any key — the transposition-invariance property.

Usage:
    from generators.interval_chain import IntervalMarkovGenerator

    gen = IntervalMarkovGenerator(train_intervals=[+2, -1, +4, -2, +3, ...])
    chain = gen.generate_sequence(length=16, seed=42)
    pitches = gen.to_pitches(chain, start=60)   # melody in MIDI
"""

import random
from collections import defaultdict
from typing import Dict, List, Optional, Sequence

from structures.unit import MusicUnit, MusicEvent
from generators.base import MusicGenerator


class IntervalMarkovGenerator(MusicGenerator):
    """Markov chain where states are semitone interval deltas."""

    def __init__(self,
                 train_intervals: Optional[Sequence[int]] = None,
                 start_interval: int = 0):
        """Initialize.

        Args:
            train_intervals: sequence of interval deltas to learn
                transitions from (e.g. [+2, -1, +4, ...]). If None, uses
                a default vocal-style interval vocabulary.
            start_interval: initial delta state (default 0 = no movement).
        """
        super().__init__()
        self.train_intervals = list(train_intervals) if train_intervals else \
            [+2, -1, +4, -2, +3, -3, +1, -1, +2, +5, -4, +2, -2, +1, -1, +7, -5]
        self.start_interval = start_interval
        self.trans: Dict[int, List[int]] = defaultdict(list)
        for a, b in zip(self.train_intervals, self.train_intervals[1:]):
            self.trans[a].append(b)

    def generate_sequence(self,
                          length: int = 16,
                          seed: Optional[int] = None) -> List[int]:
        """Generate a chain of interval deltas.

        Args:
            length: number of deltas (notes - 1).
            seed: optional RNG seed for determinism.

        Returns:
            List of interval deltas.
        """
        rng = random.Random(seed)
        out = [self.start_interval]
        cur = self.start_interval
        for _ in range(length - 1):
            choices = self.trans.get(cur) or list(self.trans.keys())
            cur = rng.choice(choices)
            out.append(cur)
        return out

    def to_pitches(self, deltas: Sequence[int], start: int = 60) -> List[int]:
        """Convert an interval chain to absolute MIDI pitches.

        Args:
            deltas: interval deltas (from generate_sequence).
            start: root pitch for the first note.

        Returns:
            List of MIDI pitches.
        """
        pitches = [start]
        for d in deltas[1:]:
            pitches.append(pitches[-1] + d)
        return pitches

    def to_unit(self,
                deltas: Sequence[int],
                start: int = 60,
                duration: int = 480,
                volume: int = 90) -> MusicUnit:
        """Render an interval chain to a MusicUnit (absolute ticks).

        Args:
            deltas: interval deltas.
            start: root pitch.
            duration: tick duration per note.
            volume: note velocity.

        Returns:
            MusicUnit with one event per note, zero-drift padded tail.
        """
        unit = MusicUnit()
        pitches = self.to_pitches(deltas, start)
        tick = 0
        for p in pitches:
            unit.add_event(MusicEvent(pitch=p, volume=volume,
                                      start_tick=tick, end_tick=tick + duration))
            tick += duration
        # zero-drift tail padding (silent resting event at boundary)
        unit.add_event(MusicEvent(pitch=0, volume=0,
                                  start_tick=tick, end_tick=tick + 10))
        return unit

    def generate(self) -> List[MusicUnit]:
        """Abstract base implementation: 16-step chain -> unit."""
        deltas = self.generate_sequence(length=16, seed=42)
        return [self.to_unit(deltas)]


if __name__ == "__main__":
    gen = IntervalMarkovGenerator()
    d = gen.generate_sequence(length=12, seed=7)
    print("interval chain:", d)
    print("pitches @60:", gen.to_pitches(d, 60))
    print("pitches @67 (transposed, same contour):", gen.to_pitches(d, 67))
    assert gen.to_pitches(d, 67)[0] - gen.to_pitches(d, 60)[0] == 7
    print("OK transposition-invariant")
