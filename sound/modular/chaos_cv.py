"""Digital chaos CV — EuroRack-style chaotic control voltage generator.

Replicable logic from digital-chaos hardware modules (Xaoc Sofia /
Sofia2 chaotic oscillators, Xaoc Leibniz complex systems): iterating
discrete chaotic maps to produce pseudo-random-but-structured CV.

Two maps:
- Logistic map:   x_{n+1} = r * x_n * (1 - x_n), r in [3.57, 4.0]
- Tent map:       x_{n+1} = r * min(x_n, 1 - x_n), r in [1.0, 2.0]

Usage:
    from sound.modular.chaos_cv import ChaosCV

    cv = ChaosCV(map_type="logistic", r=3.9, seed=0.5)
    values = cv.generate(n_samples=64, smooth=0.3)   # 0..1 CV stream
    midi = cv.to_midi_velocity(values)               # 0..127
"""

from typing import List, Optional


class ChaosCV:
    """Iterated-map chaotic control-voltage generator."""

    def __init__(self, map_type: str = "logistic", r: float = 3.9,
                 seed: float = 0.5):
        """Initialize.

        Args:
            map_type: 'logistic' or 'tent'.
            r: Map parameter. Logistic: 3.57-4.0 (4.0 = full chaos).
               Tent: 1.0-2.0 (2.0 = full chaos).
            seed: Initial state in (0, 1).
        """
        self.map_type = map_type
        self.r = r
        self.x = seed

    def _iterate(self) -> float:
        """One map iteration, returns next state in (0, 1)."""
        x = self.x
        if self.map_type == "logistic":
            x = self.r * x * (1.0 - x)
        elif self.map_type == "tent":
            x = self.r * min(x, 1.0 - x)
        else:
            raise ValueError("map_type must be 'logistic' or 'tent'")
        self.x = min(0.9999, max(0.0001, x))  # stay in domain
        return self.x

    def generate(self, n_samples: int = 64,
                 smooth: float = 0.0) -> List[float]:
        """Generate a CV stream of n_samples values in [0, 1].

        Args:
            n_samples: Number of output samples.
            smooth: One-pole smoothing factor 0..1 (0 = none, 1 = frozen).
        """
        out: List[float] = []
        prev = self.x
        for _ in range(n_samples):
            v = self._iterate()
            if smooth > 0:
                v = (1.0 - smooth) * v + smooth * prev
                prev = v
            out.append(v)
        return out

    @staticmethod
    def to_midi_velocity(values: List[float]) -> List[int]:
        """Map CV values to MIDI velocity 0..127."""
        return [int(round(v * 127)) for v in values]

    @staticmethod
    def to_midi_pitch(values: List[float], scale: List[int],
                      root: int = 60) -> List[int]:
        """Quantize CV values to a scale (list of semitone offsets)."""
        out = []
        for v in values:
            idx = int(round(v * (len(scale) - 1)))
            out.append(root + scale[idx])
        return out


def demo() -> str:
    """Render a demo CV stream to text (64 samples)."""
    cv = ChaosCV("logistic", 3.9, 0.5)
    vals = cv.generate(64)
    chars = [" .:-=+*#%@"]  # 10 levels
    return "".join(chars[0][min(9, int(v * 10))] for v in vals)


if __name__ == "__main__":
    print(demo())
