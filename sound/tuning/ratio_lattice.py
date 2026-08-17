"""Just-intonation ratio lattice — compose with pure frequency ratios.

Nodes are rational frequency ratios (e.g. 3:2, 5:4); edges are comma
steps (P5 = 3:2, M3 = 5:4, harmonic 7th = 7:4). Walking the lattice
builds interval networks (Ben Johnston / Harry Partch style) rather
than 12-TET note sequences.

Usage:
    from sound.tuning.ratio_lattice import RatioLattice

    lat = RatioLattice(base_freq=220.0)
    path = lat.walk([(3, 2), (5, 4), (3, 2), (5, 4)])   # ratio sequence
    freqs = lat.path_freqs(path)                          # absolute Hz
    notes = lat.freqs_to_midi(freqs)                      # nearest 12-TET
"""

from typing import List, Sequence, Tuple

from sound.tuning.just_intonation import JustIntonation


class RatioLattice:
    """Just-intonation lattice: ratios as nodes, comma steps as edges."""

    # Fundamental comma steps (interval ratios)
    STEPS = {
        "P5": (3, 2),     # perfect fifth
        "P4": (4, 3),     # perfect fourth
        "M3": (5, 4),     # major third (5-limit)
        "m3": (6, 5),     # minor third
        "h7": (7, 4),     # harmonic seventh (7-limit)
        "M2": (9, 8),     # major second (Pythagorean whole tone)
        "m7": (7, 4) / 2 if False else (16, 9),  # minor seventh
    }

    def __init__(self, base_freq: float = 220.0):
        """Initialize.

        Args:
            base_freq: Hz of the lattice origin (ratio 1:1).
        """
        self.base_freq = base_freq
        self.ji = JustIntonation(root_freq=base_freq)

    # -- ratio math ----------------------------------------------------

    def multiply(self, a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
        """Multiply two ratios (numerator/denominator product, simplified)."""
        num = a[0] * b[0]
        den = a[1] * b[1]
        return self.ji.simplify_ratio(num, den)

    def invert(self, r: Tuple[int, int]) -> Tuple[int, int]:
        return (r[1], r[0])

    # -- lattice walking ------------------------------------------------

    def walk(self, steps: Sequence[Tuple[int, int]],
             start: Tuple[int, int] = (1, 1)) -> List[Tuple[int, int]]:
        """Walk the lattice: accumulate ratios from a step sequence.

        Args:
            steps: list of interval ratios, e.g. [(3,2), (5,4), (7,4)].
            start: starting node ratio.

        Returns:
            List of node ratios visited (including start).
        """
        nodes = [start]
        cur = start
        for s in steps:
            cur = self.multiply(cur, s)
            nodes.append(cur)
        return nodes

    def path_freqs(self, nodes: Sequence[Tuple[int, int]]) -> List[float]:
        """Absolute frequencies (Hz) for lattice node ratios."""
        return [self.base_freq * n[0] / n[1] for n in nodes]

    def freqs_to_midi(self, freqs: Sequence[float]) -> List[int]:
        """Nearest 12-TET MIDI note for each frequency."""
        import math
        return [int(round(69 + 12 * math.log2(f / 440.0))) for f in freqs]

    def path_to_pitches(self, steps: Sequence[Tuple[int, int]],
                        base_midi: int = 57,  # A3
                        start: Tuple[int, int] = (1, 1)) -> List[int]:
        """Walk the lattice and map to nearest MIDI pitches (for UnitMatrix)."""
        nodes = self.walk(steps, start)
        freqs = self.path_freqs(nodes)
        midi = self.freqs_to_midi(freqs)
        # normalize around base_midi (keep octave placement sane)
        offset = midi[0] - base_midi
        return [m - offset for m in midi]


if __name__ == "__main__":
    lat = RatioLattice(base_freq=220.0)
    # Circle of fifths fragment: A3 -> E4 -> B4 -> F#4 (3:2 steps)
    path = lat.walk([(3, 2), (3, 2), (3, 2)])
    print("nodes:", path)
    freqs = lat.path_freqs(path)
    print("freqs:", [round(f, 2) for f in freqs])
    print("midi:", lat.freqs_to_midi(freqs))
    # Harmonic seventh: A3 + 7:4 = ~G4 (harmonic minor 7th)
    h7 = lat.walk([(7, 4)])
    print("h7 node:", h7[-1], "freq:", round(lat.path_freqs(h7)[-1], 2))
    print("OK")
