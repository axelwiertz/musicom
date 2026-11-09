# -*- coding: utf-8 -*-
"""Oberheim Matrix-12 style modulation function generators.

Replicable logic from the Sound On Sound item "GForce launch Oberheim
Matrix-12" (2026-11-06).  Per voice the Matrix-12 has five envelopes, five
LFOs, **four ramps, three trackers and a lag processor**, and any source can
be routed to any destination.  GForce added tempo-synchronised ramps with
linear-to-exponential curves, smoothing on every LFO shape, and a *stepped
tracker* mode that turns any LFO into a 4-step sequence.

What is replicated here (pure control-signal DSP, numpy only):

* ``Ramp`` — multi-segment ramp generator.  Every segment has a duration
  (beats when ``sync=True``, seconds otherwise), a target level and a
  ``curve`` in [-1, +1] where -1 = logarithmic, 0 = linear, +1 = exponential
  (the Matrix-12's "linear-to-exponential" ramp shape).  Loops or one-shots.
* ``Tracker`` — breakpoint map from an input signal to an output value, with
  linear or smooth interpolation and a ``stepped`` mode (4 steps) so an LFO
  becomes a stepped sequence, matching the hardware's tracker behaviour.
* ``LagProcessor`` — one-pole slew limiter with *independent rise and fall*
  times (the classic Oberheim lag), used to smooth stepped modulation.
* ``ModFunctionBank`` — 4 ramps + 3 trackers + 1 lag, evaluated together over
  a block of time and routed to named destinations.

Not replicated: the 12-voice VCO/15-mode filter audio path (proprietary
modelling), MPE, and the drag-and-drop host UI.

Usage:
    from sound.modular.mod_functions import ModFunctionBank

    bank = ModFunctionBank(bpm=120)
    bank.ramp(0).set_segments([(1.0, 0.0, -0.3), (2.0, 1.0, 0.6)])
    bank.tracker(0).set_points([(0.0, 0.0), (0.6, 1.0), (1.0, 0.0)])
    streams = bank.evaluate(duration=2.0, src="ramp1", dest="filter_cutoff")
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# shaping helpers
# ---------------------------------------------------------------------------
def shape_curve(x: np.ndarray, curve: float) -> np.ndarray:
    """Map 0..1 -> 0..1 with a linear/exponential/logarithmic curve.

    Args:
        x: input in [0, 1].
        curve: -1 (logarithmic) .. 0 (linear) .. +1 (exponential).
    """
    x = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
    c = float(np.clip(curve, -1.0, 1.0))
    if abs(c) < 1e-6:
        return x
    k = 4.0 * abs(c)
    if c > 0:                                  # slow start, fast finish
        return (np.exp(k * x) - 1.0) / (np.exp(k) - 1.0)
    return np.log1p(k * x) / np.log1p(k)       # fast start, slow finish


# ---------------------------------------------------------------------------
# ramp generator
# ---------------------------------------------------------------------------
class Ramp:
    """Multi-segment ramp with per-segment curve, loop and tempo sync.

    A ramp is the Matrix-12's slow modulation source: a sequence of
    (duration, target level, curve) segments that can loop, retrigger on a
    key press, or free-run.
    """

    def __init__(self, segments: Optional[Sequence[Tuple[float, float, float]]] = None,
                 loop: bool = True, sync: bool = True, bpm: float = 120.0):
        self.segments: List[Tuple[float, float, float]] = list(
            segments or [(1.0, 1.0, 0.0), (1.0, 0.0, 0.0)])
        self.loop = bool(loop)
        self.sync = bool(sync)
        self.bpm = float(bpm)

    def set_segments(self, segments: Sequence[Tuple[float, float, float]]) -> "Ramp":
        """Set (duration, target_level, curve) segments."""
        self.segments = [(float(d), float(l), float(c)) for d, l, c in segments]
        return self

    def _seg_seconds(self, dur: float) -> float:
        return dur * 60.0 / self.bpm if self.sync else dur

    def total_seconds(self) -> float:
        return float(sum(self._seg_seconds(d) for d, _, _ in self.segments))

    def render(self, n: int, sr: int = 44100, trigger_time: float = 0.0,
               start_level: float = 0.0) -> np.ndarray:
        """Render ``n`` samples of the ramp starting at ``trigger_time`` s."""
        t = trigger_time + np.arange(n) / sr
        total = self.total_seconds()
        if total <= 0:
            return np.full(n, float(self.segments[-1][1]))

        durs = np.array([self._seg_seconds(d) for d, _, _ in self.segments])
        bounds = np.concatenate([[0.0], np.cumsum(durs)])   # len = n_seg + 1
        tt = np.mod(t, total) if self.loop else np.minimum(t, total - 1e-9)

        out = np.empty(n, dtype=np.float64)
        seg = np.clip(np.searchsorted(bounds[1:], tt, side="right"), 0, len(durs) - 1)
        for s, (_, target, curve) in enumerate(self.segments):
            m = seg == s
            if not np.any(m):
                continue
            d = durs[s]
            frac = np.zeros(m.sum()) if d <= 0 else (tt[m] - bounds[s]) / d
            lvl_from = start_level if s == 0 else float(self.segments[s - 1][1])
            out[m] = lvl_from + (float(target) - lvl_from) * shape_curve(frac, curve)
        if not self.loop:
            out[t >= total] = float(self.segments[-1][1])
        return out


# ---------------------------------------------------------------------------
# tracker
# ---------------------------------------------------------------------------
class Tracker:
    """Breakpoint map: input signal (0..1) -> output value.

    ``stepped=True`` quantises the input into ``steps`` bands before mapping,
    which is how the Matrix-12's stepped tracker turns a continuous LFO into
    a short stepped sequence.
    """

    def __init__(self, points: Optional[Sequence[Tuple[float, float]]] = None,
                 stepped: bool = False, steps: int = 4, smooth: bool = False):
        self.points = list(points or [(0.0, 0.0), (1.0, 1.0)])
        self.stepped = bool(stepped)
        self.steps = int(max(2, steps))
        self.smooth = bool(smooth)

    def set_points(self, points: Sequence[Tuple[float, float]]) -> "Tracker":
        self.points = sorted((float(x), float(y)) for x, y in points)
        return self

    def __call__(self, x: np.ndarray) -> np.ndarray:
        x = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
        if self.stepped:
            # quantise into N bands, evaluated at band centres
            x = np.clip((np.floor(x * self.steps) + 0.5) / self.steps, 0.0, 1.0)
        xs = np.array([p[0] for p in self.points], dtype=np.float64)
        ys = np.array([p[1] for p in self.points], dtype=np.float64)
        if self.smooth:
            y = np.interp(x, xs, ys)
            # one-pole smoothing of the mapped result
            a = 0.15
            out = np.empty_like(y)
            acc = y[0]
            for i, v in enumerate(y):
                acc += a * (v - acc)
                out[i] = acc
            return out
        return np.interp(x, xs, ys)


# ---------------------------------------------------------------------------
# lag processor
# ---------------------------------------------------------------------------
class LagProcessor:
    """One-pole slew with independent rise and fall time constants."""

    def __init__(self, rise: float = 0.05, fall: float = 0.20):
        self.rise = float(max(1e-5, rise))
        self.fall = float(max(1e-5, fall))

    def __call__(self, x: np.ndarray, sr: int = 44100) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        out = np.empty_like(x)
        y = x[0] if len(x) else 0.0
        for i, v in enumerate(x):
            tau = self.rise if v > y else self.fall
            b = 1.0 - np.exp(-1.0 / (tau * sr))
            y += b * (v - y)
            out[i] = y
        return out


# ---------------------------------------------------------------------------
# bank
# ---------------------------------------------------------------------------
class ModFunctionBank:
    """4 ramps + 3 trackers + 1 lag, with named routing.

    Args:
        bpm: tempo used by tempo-synchronised ramps.
        sr: sample rate for evaluation.
    """

    def __init__(self, bpm: float = 120.0, sr: int = 44100):
        self.bpm = float(bpm)
        self.sr = int(sr)
        self.ramps: List[Ramp] = [Ramp(bpm=bpm) for _ in range(4)]
        self.trackers: List[Tracker] = [Tracker() for _ in range(3)]
        self.lag = LagProcessor()
        self.routes: List[Tuple[str, str, float]] = []

    def ramp(self, i: int) -> Ramp:
        return self.ramps[i % 4]

    def tracker(self, i: int) -> Tracker:
        return self.trackers[i % 3]

    def route(self, source: str, dest: str, amount: float) -> "ModFunctionBank":
        self.routes.append((source, dest, float(amount)))
        return self

    def evaluate(self, duration: float, src: str = "ramp1",
                 dest: str = "filter_cutoff", amount: float = 1.0,
                 lag: bool = True) -> Dict[str, np.ndarray]:
        """Evaluate one source through optional lag into one destination."""
        n = int(duration * self.sr)
        if src.startswith("ramp"):
            idx = int(src[4:]) - 1
            sig = self.ramp(max(0, idx)).render(n, self.sr)
        elif src.startswith("tracker"):
            idx = int(src[7:]) - 1
            base = self.ramp(0).render(n, self.sr)
            sig = self.tracker(max(0, idx))(base)
        elif src == "lfo":
            t = np.arange(n) / self.sr
            sig = 0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t)
        elif src == "velocity":
            sig = np.full(n, amount)
        else:
            raise ValueError(f"unknown source {src!r}")
        if lag:
            sig = self.lag(sig, self.sr)
        return {dest: sig * float(amount), "src": sig}


# ---------------------------------------------------------------------------
# demo
# ---------------------------------------------------------------------------
def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Drive a resonant SVF filter with ramp -> tracker -> lag."""
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = 44100
    dur = 4.0
    n = int(dur * sr)
    t = np.arange(n) / sr

    bank = ModFunctionBank(bpm=120, sr=sr)
    bank.ramp(0).set_segments([(0.5, 0.05, -0.6), (1.5, 0.95, 0.7), (1.0, 0.4, 0.0)])
    bank.ramp(1).set_segments([(2.0, 1.0, 0.9), (2.0, 0.0, -0.9)])
    bank.tracker(0).set_points([(0.0, 0.05), (0.35, 0.55), (0.7, 0.95), (1.0, 0.2)])
    bank.trackers[1] = Tracker(points=[(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)],
                               stepped=True, steps=4)

    ramp = bank.evaluate(dur, src="ramp1", dest="filter_cutoff")["filter_cutoff"]
    stepped = bank.tracker(1)(bank.ramp(1).render(n, sr))
    lagged = bank.lag(stepped, sr)

    print("=== Oberheim Matrix-12 modulation functions ===")
    print(f"ramp1 : {n} samples, range {ramp.min():.3f}..{ramp.max():.3f}")
    print(f"tracker (stepped 4): unique {len(np.unique(np.round(stepped, 4)))} levels")
    print(f"lag rise/fall {bank.lag.rise:.3f}s/{bank.lag.fall:.3f}s, "
          f"max slew {np.max(np.abs(np.diff(lagged))) * sr:.2f} /s")

    # audio: saw -> resonant SVF, cutoff driven by ramp (log-mapped 200..6000 Hz)
    saw = 2.0 * (t * 55.0 % 1.0) - 1.0
    cutoff = 200.0 * (6000.0 / 200.0) ** np.clip(ramp, 0, 1)
    res = 0.92
    f = 2.0 * np.sin(np.pi * np.clip(cutoff, 20, sr * 0.45) / sr)
    low = band = 0.0
    out = np.empty(n)
    for i in range(n):
        high = saw[i] - low - res * band
        band += f[i] * high
        low += f[i] * band
        out[i] = low
    out = np.tanh(out * 1.5)
    out /= np.max(np.abs(out)) + 1e-9

    path = os.path.join(out_dir, "matrix12_mod_functions.wav")
    write_wav(path, out.astype(np.float32), sr)
    print(f"audio  : {path} ({os.path.getsize(path)} B)")

    # show the curve family
    x = np.linspace(0, 1, 9)
    for c in (-1.0, -0.5, 0.0, 0.5, 1.0):
        print(f"curve {c:+.1f}: " + " ".join(f"{v:.2f}" for v in shape_curve(x, c)))

    assert os.path.getsize(path) > 1000 and np.max(np.abs(out)) > 0.5
    print("demo OK")
    return {"path": path, "samples": n}


if __name__ == "__main__":
    demo()
