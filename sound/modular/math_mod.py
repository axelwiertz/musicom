"""Math modulators + 24-step sequencer — Altitude-style.

Arbitrary math functions evaluated as modulation sources (vectorized),
plus a 24-step sequencer and a patch combining both.

Usage:
    mod = MathModulator("sin(2*pi*rate*t)", rate=0.5)
    signal = mod.process(44100)          # 1s of LFO

    seq = StepSequencer24()
    seq.set_pattern([1, 0, 0.5, ...])
    v = seq.get_step(3)
"""

import numpy as np
from typing import Dict, List, Optional, Union

__all__ = ["MathModulator", "StepSequencer24", "MathPatch"]


class MathModulator:
    """Evaluate a math expression as a control signal.

    The expression is evaluated with numpy functions available and can
    reference `t` (time in seconds) and `n` (sample index).
    """

    def __init__(self, expr: str, sample_rate: int = 44100, **params):
        self.expr = expr
        self.sample_rate = sample_rate
        self.params: Dict[str, float] = dict(params)

    def set_params(self, **kwargs):
        """Bind extra names used in the expression."""
        self.params.update(kwargs)

    def process(self, n_samples: int, t_start: float = 0.0) -> np.ndarray:
        """Evaluate the expression over n_samples.

        Returns:
            Float array; zeros if the expression is invalid.
        """
        t = t_start + np.arange(n_samples) / self.sample_rate
        n = np.arange(n_samples)
        env = {
            "t": t,
            "n": n,
            "np": np,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log,
            "abs": np.abs,
            "sqrt": np.sqrt,
            "pi": np.pi,
        }
        env.update(self.params)
        try:
            out = eval(self.expr, {"__builtins__": {}}, env)
            out = np.asarray(out, dtype=float)
            if out.ndim == 0:
                out = np.full(n_samples, float(out))
            if len(out) != n_samples:
                out = np.resize(out, n_samples)
            return out
        except Exception:
            return np.zeros(n_samples)


class StepSequencer24:
    """24-step pattern sequencer (Altitude dual 24-step)."""

    def __init__(self, steps: int = 24):
        self.steps = max(1, steps)
        self._pattern: List[float] = [0.0] * self.steps
        self._index = 0

    def set_pattern(self, values: List[Union[float, int]]):
        """Set step values (length clipped/padded to self.steps)."""
        vals = [float(v) for v in values]
        self._pattern = (vals[:self.steps] +
                         [0.0] * max(0, self.steps - len(vals)))

    def get_step(self, step_index: int) -> float:
        """Value at absolute step index (wraps around)."""
        return self._pattern[step_index % self.steps]

    def advance(self) -> float:
        """Return current value, advance to next step."""
        value = self._pattern[self._index]
        self._index = (self._index + 1) % self.steps
        return value

    def reset(self):
        self._index = 0

    def sequence(self, n_steps: int) -> List[float]:
        """Read n_steps values sequentially (wrapping)."""
        return [self.get_step(self._index + i) for i in range(n_steps)]


class MathPatch:
    """Combine MathModulators + StepSequencer24 into a modulation patch.

    Routes sources to targets with per-route amounts, producing control
    signals (numpy arrays).
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._sources: Dict[str, object] = {}
        self._routes: List[tuple] = []  # (target, source, amount)

    def add_source(self, name: str, modulator_or_sequencer):
        """Register a modulation source."""
        self._sources[name] = modulator_or_sequencer

    def modulate(self, target_name: str, source_name: str, amount: float = 1.0):
        """Route source -> target with gain."""
        if source_name not in self._sources:
            raise KeyError(f"Unknown source: {source_name}")
        self._routes.append((target_name, source_name, amount))

    def _source_signal(self, name: str, n_samples: int) -> np.ndarray:
        src = self._sources[name]
        if isinstance(src, MathModulator):
            return src.process(n_samples)
        if isinstance(src, StepSequencer24):
            return np.asarray(src.sequence(n_samples), dtype=float)
        # Plain callable
        return np.asarray(src(n_samples), dtype=float)  # type: ignore[operator]

    def render(self, duration: float) -> Dict[str, np.ndarray]:
        """Render control signals for all routed targets.

        Returns:
            {target_name: summed control signal (len = int(duration*sr))}
        """
        n_samples = int(duration * self.sample_rate)
        sums: Dict[str, np.ndarray] = {}
        for target, source, amount in self._routes:
            sig = self._source_signal(source, n_samples) * amount
            sums[target] = sums.get(target, np.zeros(n_samples)) + sig
        return sums
