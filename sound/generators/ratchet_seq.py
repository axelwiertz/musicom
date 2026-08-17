"""Ratchet step sequencer — TR-808 SuperOS-808 firmware-style logic.

Replicable logic from the SuperOS-808 open-source firmware (Synthtopia
2026-08-13): a step sequencer with ratcheting (sub-division bursts) per
step, probability per step, and accent per step. Modeled on the 808
CPU-board sequencer behavior (AT90USB1286 / Teensy++ 2.0 in a uPD650C
socket).

Usage:
    from sound.generators.ratchet_seq import RatchetSequencer

    seq = RatchetSequencer(steps=16, subdivisions=4)
    seq.set_ratchet(step=3, count=2)      # double-hit on step 3
    seq.set_ratchet(step=11, count=4)     # 32nd-note burst on step 11
    seq.set_probability(step=7, prob=0.5) # 50% chance step 7 fires
    seq.set_accent(step=0, accent=127)    # hard hit on step 0
    events = seq.generate(seed=42)        # list of (step_frac, velocity)
"""

from typing import Dict, List, Optional, Tuple


class RatchetSequencer:
    """Step sequencer with per-step ratchet, probability, and accent."""

    def __init__(self, steps: int = 16, subdivisions: int = 4):
        """Initialize.

        Args:
            steps: Number of steps in the pattern (e.g. 16 sixteenths).
            subdivisions: Number of sub-divisions per step (4 = 64ths max).
        """
        self.steps = steps
        self.subdivisions = subdivisions
        self.ratchets: Dict[int, int] = {}       # step -> hit count
        self.probabilities: Dict[int, float] = {}  # step -> 0..1
        self.accents: Dict[int, int] = {}        # step -> 0..127

    def set_ratchet(self, step: int, count: int) -> None:
        """Set ratchet (sub-division burst count) for a step.

        count=1 → single hit; count=2 → double-time; count=4 → 32nd burst.
        """
        if not 1 <= count <= self.subdivisions:
            raise ValueError(f"ratchet count must be 1..{self.subdivisions}")
        if count > 1:
            self.ratchets[step % self.steps] = count

    def set_probability(self, step: int, prob: float) -> None:
        """Set probability (0..1) that a step fires."""
        self.probabilities[step % self.steps] = max(0.0, min(1.0, prob))

    def set_accent(self, step: int, accent: int) -> None:
        """Set velocity accent (0..127) for a step."""
        self.accents[step % self.steps] = max(0, min(127, accent))

    def generate(self, seed: Optional[int] = None) -> List[Tuple[int, int]]:
        """Generate the pattern.

        Returns:
            List of (step_fraction, velocity) where step_fraction is a
            float in [0, steps) — sub-divisions land between integers.
        """
        import random
        rng = random.Random(seed)
        out: List[Tuple[int, int]] = []
        for step in range(self.steps):
            prob = self.probabilities.get(step, 1.0)
            if prob < 1.0 and rng.random() > prob:
                continue  # step skipped
            base_vel = self.accents.get(step, 100)
            count = self.ratchets.get(step, 1)
            for i in range(count):
                frac = step + (i / count)
                vel = base_vel if i == 0 else max(40, base_vel - 20)
                out.append((frac, vel))
        return out


def demo() -> str:
    """Render a demo pattern to text."""
    seq = RatchetSequencer(steps=16, subdivisions=4)
    seq.set_ratchet(3, 2)
    seq.set_ratchet(11, 4)
    seq.set_probability(7, 0.5)
    seq.set_accent(0, 127)
    events = seq.generate(seed=42)
    cells = ["."] * 16
    for frac, vel in events:
        s = int(frac)
        cells[s] = "#" if vel > 90 else "+"
    return "".join(cells)


if __name__ == "__main__":
    print(demo())
