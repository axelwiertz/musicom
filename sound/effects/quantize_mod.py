"""Quantize modulators + routing — Radical1 Solo style.

QuantizeModulator snaps continuous modulation values to discrete steps
('Quantize' modulator). ModRouter is a signal routing matrix. QuantizeChain
applies quantized modulators as gain envelopes to audio.

Usage:
    qm = QuantizeModulator(steps=12)
    snapped = qm.process(0.37)   # -> 0.333...

    mr = ModRouter()
    mr.set_route("lfo1", "filter")
    out = mr.process({"lfo1": 0.5}, {"filter": 0.1})
"""

import numpy as np
from typing import Dict, Any, Optional

__all__ = ["QuantizeModulator", "ModRouter", "QuantizeChain"]


class QuantizeModulator:
    """Snap continuous values to the nearest of N steps in [0, 1]."""

    def __init__(self, steps: int = 12, bipolar: bool = False):
        self.steps = max(2, steps)
        self.bipolar = bipolar

    def process(self, value: float) -> float:
        """Snap a value in [0,1] (or [-1,1] if bipolar) to a step."""
        lo, hi = (-1.0, 1.0) if self.bipolar else (0.0, 1.0)
        clamped = max(lo, min(hi, value))
        steps = self.steps - 1
        snapped = round(clamped * steps) / steps
        return max(lo, min(hi, snapped))

    def process_array(self, values: np.ndarray) -> np.ndarray:
        """Vectorized snap."""
        lo, hi = (-1.0, 1.0) if self.bipolar else (0.0, 1.0)
        clamped = np.clip(values, lo, hi)
        steps = self.steps - 1
        snapped = np.round(clamped * steps) / steps
        return np.clip(snapped, lo, hi)


class ModRouter:
    """Signal routing matrix: route modulation sources to destinations."""

    def __init__(self):
        self._routes: Dict[str, str] = {}  # src -> dest

    def set_route(self, src: str, dest: str):
        """Route a source to a destination (one dest per src)."""
        self._routes[src] = dest

    def clear_route(self, src: str):
        self._routes.pop(src, None)

    def routes(self) -> Dict[str, str]:
        return dict(self._routes)

    def process(self, sources: Dict[str, float],
                destinations: Dict[str, float]) -> Dict[str, float]:
        """Apply routed source values onto destination values."""
        result = dict(destinations)
        for src, dest in self._routes.items():
            result[dest] = result.get(dest, 0.0) + sources.get(src, 0.0)
        return result


class QuantizeChain:
    """Apply quantized modulation as gain envelopes to audio."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.router = ModRouter()
        self.quantizers: Dict[str, QuantizeModulator] = {}

    def add_quantizer(self, name: str, steps: int = 12):
        self.quantizers[name] = QuantizeModulator(steps=steps)

    def process(self, audio: np.ndarray, source_values: Dict[str, float],
                destination_targets: Dict[str, float]) -> np.ndarray:
        """Apply quantized modulation to audio.

        Args:
            audio: Input signal.
            source_values: {source_name: current_value}.
            destination_targets: {dest_name: base_gain} — routed values
                become per-sample gain multipliers.
        """
        routed = self.router.process(source_values, destination_targets)
        n = len(audio)
        gain = np.ones(n, dtype=np.float64)
        for name, base in routed.items():
            if name in self.quantizers:
                base = self.quantizers[name].process(base)
            gain *= (1.0 + base)
        return (np.asarray(audio, dtype=np.float64) * gain).astype(audio.dtype)
