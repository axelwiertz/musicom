"""L-System with interval semantics — fractal melodies via rewrite rules.

Symbols map to SEMITONE INTERVALS: '+' = +n, '-' = -n, '=' = unison.
Iterating the grammar yields self-similar interval structures that scale
across melody (horizontal) and harmony (vertical when layered).

Usage:
    from generators.interval_lsystem import IntervalLSystem

    ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                         symbols={"+": 2, "-": 1})
    deltas = ls.generate_deltas(iterations=4)
    pitches = ls.to_pitches(deltas, start=60)
"""

from typing import Dict, List, Optional, Sequence

from structures.unit import MusicUnit, MusicEvent
from generators.base import MusicGenerator


class IntervalLSystem(MusicGenerator):
    """Lindenmayer system where terminal symbols are semitone intervals."""

    def __init__(self,
                 axiom: str = "A",
                 rules: Optional[Dict[str, str]] = None,
                 symbols: Optional[Dict[str, int]] = None,
                 name: str = "interval-lsystem"):
        """Initialize.

        Args:
            axiom: starting string (e.g. "A").
            rules: rewrite rules {symbol: expansion}, e.g. {"A": "A+B", "B": "A-B"}.
            symbols: terminal -> semitone interval mapping,
                e.g. {"+": 2, "-": 1} means '+' = +2 semitones, '-' = -1.
                Non-terminals (rule heads) are skipped during pitch mapping.
            name: generator name.
        """
        super().__init__()
        self.axiom = axiom
        self.rules = rules or {"A": "A+B", "B": "A-B"}
        self.symbols = symbols or {"+": 2, "-": 1}
        self.name = name

    def _iterate(self, iterations: int) -> str:
        current = self.axiom
        for _ in range(iterations):
            current = "".join(self.rules.get(c, c) for c in current)
        return current

    def generate_deltas(self, iterations: int = 3) -> List[int]:
        """Iterate the grammar and map terminal symbols to interval deltas."""
        string = self._iterate(iterations)
        return [self.symbols[c] for c in string if c in self.symbols]

    def generate_string(self, iterations: int = 3) -> str:
        """Return the raw L-System string (for inspection)."""
        return self._iterate(iterations)

    def to_pitches(self, deltas: Sequence[int], start: int = 60) -> List[int]:
        pitches = [start]
        for d in deltas:
            pitches.append(pitches[-1] + d)
        return pitches

    def to_unit(self,
                deltas: Sequence[int],
                start: int = 60,
                duration: int = 480,
                volume: int = 90,
                section_ticks: Optional[int] = None) -> MusicUnit:
        """Render interval deltas to a MusicUnit (absolute ticks).

        Args:
            deltas: interval deltas from generate_deltas.
            start: root pitch.
            duration: ticks per note.
            volume: velocity.
            section_ticks: hard section boundary for zero-drift padding.
                If None, uses len(deltas)*duration.

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
        boundary = section_ticks if section_ticks is not None else tick
        if tick < boundary:
            unit.add_event(MusicEvent(pitch=0, volume=0,
                                      start_tick=tick, end_tick=boundary))
        return unit

    def generate(self) -> List[MusicUnit]:
        """Abstract base implementation: 3-iteration chain -> unit."""
        deltas = self.generate_deltas(iterations=3)
        return [self.to_unit(deltas)]


if __name__ == "__main__":
    ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                         symbols={"+": 2, "-": 1})
    print("string (3 iters):", ls.generate_string(3))
    d = ls.generate_deltas(3)
    print("deltas:", d)
    print("pitches @60:", ls.to_pitches(d, 60))
    assert len(d) > 0
    print("OK")
