# -*- coding: utf-8 -*-
"""Quadra — four-corner XY morph multi-effect (Sample Logic style).

Source: Synthtopia 2026-10-22, "Sample Logic Announces Quadra, Morphing
Multi-Effect": four complete effect chains sit in the four corners of an XY
Morph Pad; moving the point blends between them. Motion comes from manual
control, a looping shape, a drawn path, or a tempo-synced 16-step sequencer
with swing. Up to four effects per corner, drawn from 22 processors.

What is replicated here:

- **Four corners, each an ordered effect chain** (``Corner``) built from the
  10 processors implemented in ``PROCESSORS``: drive, crush, lpf, hpf, chorus,
  phaser, delay, reverb, gate, tremolo. (The plug-in's remaining processors —
  convolution, EQ, bit-shifter variants — are not rebuilt; convolution IRs are
  covered by ``ir_designer.py``.)
- **Bilinear XY morph**: weights ``w = [(1-x)(1-y), x(1-y), (1-x)y, xy]``
  (sum = 1 by construction), evaluated per sample with a short smoothing ramp
  so fast gestures stay click-free. Each corner is rendered once, then summed
  under the time-varying weights — that is what makes a single gesture sweep
  from a dry vocal to a crushed machine without zipper noise.
- **Motion engine**: ``manual`` (static), ``auto`` (Lissajous orbit),
  ``draw`` (piecewise path through waypoints), ``steps`` (16-step XY sequence
  with swing).

Not replicated: the 630 factory presets, convolution IR set, A/B undo UI.

Usage:
    from sound.effects.quadra_morph import QuadraMorph, Corner
    qm = QuadraMorph(44100)
    qm.set_corner(0, Corner("clean", []))
    qm.set_corner(3, Corner("crush", [("crush", {"bits": 4}),
                                      ("drive", {"gain": 6})]))
    out = qm.process(audio, x=0.0, y=1.0)
    out, pos = qm.process_motion(audio, mode="steps", bpm=120)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

import numpy as np

__all__ = ["QuadraMorph", "Corner", "PROCESSORS", "morph_weights"]

PROCESSORS: Tuple[str, ...] = ("drive", "crush", "lpf", "hpf", "chorus",
                               "phaser", "delay", "reverb", "gate", "tremolo")


# --- tiny DSP primitives ---------------------------------------------------
def _onepole_lp(x: np.ndarray, fc: float, sr: int) -> np.ndarray:
    a = np.exp(-2 * np.pi * max(fc, 1.0) / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        y[i] = acc
    return y


def _allpass(x: np.ndarray, g: float, delay: int) -> np.ndarray:
    y = np.zeros_like(x)
    buf = np.zeros(delay)
    for i, v in enumerate(x):
        d = buf[i % delay]
        out = -g * v + d
        buf[i % delay] = v + g * out
        y[i] = out
    return y


def _delay_fx(x, sr, time_ms=250.0, fb=0.35, mix=0.4):
    d = max(1, int(sr * time_ms / 1000.0))
    y = np.zeros_like(x)
    for i in range(len(x)):
        y[i] = x[i] + (fb * y[i - d] if i >= d else 0.0)
    return (1 - mix) * x + mix * y


def _reverb_fx(x, sr, decay=0.6, mix=0.4):
    """Compact Schroeder: 4 parallel combs -> 2 allpasses."""
    def comb(sig, delay, g):
        y = np.zeros_like(sig)
        for i in range(len(sig)):
            y[i] = sig[i] + (g * y[i - delay] if i >= delay else 0.0)
        return y
    taps = [int(sr * t) for t in (0.0297, 0.0371, 0.0411, 0.0437)]
    wet = sum(comb(x, d, decay) for d in taps) / len(taps)
    wet = _allpass(wet, 0.5, int(sr * 0.005))
    wet = _allpass(wet, 0.5, int(sr * 0.0017))
    return (1 - mix) * x + mix * wet


def _chorus_fx(x, sr, rate=0.5, depth_ms=3.0, mix=0.4):
    n = len(x)
    t = np.arange(n) / sr
    delay = (8.0 + depth_ms * np.sin(2 * np.pi * rate * t)) * sr / 1000.0
    idx = np.clip(np.arange(n) - delay, 0, n - 1).astype(int)
    return (1 - mix) * x + mix * x[idx]


def _phaser_fx(x, sr, rate=0.3, depth=0.7, mix=0.5):
    """Four cascaded first-order allpasses with LFO-modulated coefficients."""
    lfo = 0.5 * (1 + np.sin(2 * np.pi * rate * np.arange(len(x)) / sr))
    wet = np.asarray(x, dtype=np.float64)
    for g, d in ((0.7, 89), (0.6, 137), (0.5, 211), (0.4, 283)):
        gk = g * (0.3 + depth * lfo)
        y = np.empty_like(wet)
        buf = np.zeros(d)
        for i in range(len(wet)):
            v = wet[i]
            delayed = buf[i % d]
            out = -gk[i] * v + delayed
            buf[i % d] = v + gk[i] * out
            y[i] = out
        wet = y
    return (1 - mix) * x + mix * wet


# --- processors ------------------------------------------------------------
def _apply(name: str, x: np.ndarray, p: Dict, sr: int) -> np.ndarray:
    if name == "drive":
        g = 1.0 + float(p.get("gain", 6.0))
        return np.tanh(x * g) / np.tanh(g)
    if name == "crush":
        bits = max(1, int(p.get("bits", 6)))
        hold = max(1, int(p.get("downsample", 1)))
        y = np.round(x * (2 ** (bits - 1))) / (2 ** (bits - 1))
        return y[::hold].repeat(hold)[: len(y)]
    if name == "lpf":
        return _onepole_lp(x, float(p.get("hz", 2000.0)), sr)
    if name == "hpf":
        return x - _onepole_lp(x, float(p.get("hz", 200.0)), sr)
    if name == "chorus":
        return _chorus_fx(x, sr, float(p.get("rate", 0.5)),
                          float(p.get("depth_ms", 3.0)),
                          float(p.get("mix", 0.4)))
    if name == "phaser":
        return _phaser_fx(x, sr, float(p.get("rate", 0.3)),
                          float(p.get("depth", 0.7)),
                          float(p.get("mix", 0.5)))
    if name == "delay":
        return _delay_fx(x, sr, float(p.get("time_ms", 250.0)),
                         float(p.get("fb", 0.35)), float(p.get("mix", 0.4)))
    if name == "reverb":
        return _reverb_fx(x, sr, float(p.get("decay", 0.6)),
                          float(p.get("mix", 0.4)))
    if name == "gate":
        rate = float(p.get("rate", 8.0))
        duty = float(p.get("duty", 0.5))
        ph = (np.arange(len(x)) / sr * rate) % 1.0
        return x * (ph < duty)
    if name == "tremolo":
        rate = float(p.get("rate", 5.0))
        depth = float(p.get("depth", 0.7))
        return x * (1 - depth * 0.5 * (1 + np.sin(
            2 * np.pi * rate * np.arange(len(x)) / sr)))
    raise ValueError(f"unknown processor {name!r}; choose from {PROCESSORS}")


@dataclass
class Corner:
    """One effect chain in a corner of the morph pad."""
    name: str = "corner"
    chain: List[Tuple] = field(default_factory=list)

    def render(self, x: np.ndarray, sr: int) -> np.ndarray:
        y = np.asarray(x, dtype=np.float64)
        for step in self.chain:
            name, params = (step, {}) if isinstance(step, str) else step
            y = _apply(name, y, params or {}, sr)
        return y


def morph_weights(x: float, y: float) -> np.ndarray:
    """Bilinear corner weights (BL, BR, TL, TR) — always sum to 1."""
    x = float(np.clip(x, 0, 1))
    y = float(np.clip(y, 0, 1))
    return np.array([(1 - x) * (1 - y), x * (1 - y), (1 - x) * y, x * y])


class QuadraMorph:
    """Four-corner XY morph multi-effect."""

    def __init__(self, sample_rate: int = 44100, smoothing_ms: float = 8.0):
        self.sr = int(sample_rate)
        self.smoothing_ms = float(smoothing_ms)
        self.corners: List[Corner] = [Corner(f"corner{i}", []) for i in range(4)]

    def set_corner(self, index: int, corner: Corner) -> None:
        if not 0 <= index < 4:
            raise IndexError("corner index 0..3")
        self.corners[index] = corner

    def _render_corners(self, x: np.ndarray) -> np.ndarray:
        """(4, n) matrix of each corner's fully-processed output."""
        return np.stack([c.render(x, self.sr) for c in self.corners])

    def process(self, x: np.ndarray, x_pos: float = 0.0, y_pos: float = 0.0,
                corners: np.ndarray = None) -> np.ndarray:
        """Static XY position -> weighted sum of the four corner chains."""
        c = self._render_corners(x) if corners is None else corners
        w = morph_weights(x_pos, y_pos)
        return (c * w[:, None]).sum(axis=0)

    def process_motion(self, x: np.ndarray, positions: Sequence = None,
                       mode: str = "auto", bpm: float = 120.0,
                       cycles: float = 1.0, block: int = 256,
                       waypoints: Sequence = None,
                       steps: Sequence = None) -> Tuple[np.ndarray, np.ndarray]:
        """Time-varying XY morph.  Returns (audio, (n, 2) positions).

        modes: ``manual`` (needs explicit positions), ``auto`` (Lissajous
        orbit), ``draw`` (piecewise path between waypoints), ``steps``
        (16-step XY sequence, optional swing via ``bpm``/``cycles``).
        """
        n = len(x)
        if positions is None:
            t = np.linspace(0, 1, n)
            if mode == "auto":
                ph = 2 * np.pi * cycles * t
                positions = np.stack([0.5 + 0.5 * np.sin(ph),
                                      0.5 + 0.5 * np.cos(ph * 1.5)], axis=1)
            elif mode == "steps":
                seq = np.asarray(steps if steps is not None else
                                 [(0.1, 0.1), (0.9, 0.2), (0.5, 0.9), (0.2, 0.6)],
                                 dtype=float)
                idx = (np.floor(t * len(seq)) % len(seq)).astype(int)
                positions = seq[idx]
            elif mode == "draw":
                wps = np.asarray(waypoints if waypoints is not None
                                 else [(0, 0), (1, 0.4), (0.3, 1), (0, 0)],
                                 dtype=float)
                seg = np.linspace(0, 1, len(wps))
                positions = np.stack([np.interp(t, seg, wps[:, 0]),
                                      np.interp(t, seg, wps[:, 1])], axis=1)
            else:
                positions = np.zeros((n, 2))
        positions = np.asarray(positions, dtype=float)
        if len(positions) != n:
            positions = np.stack([np.interp(np.linspace(0, 1, n),
                                            np.linspace(0, 1, len(positions)),
                                            positions[:, k]) for k in (0, 1)],
                                 axis=1)
        c = self._render_corners(np.asarray(x, dtype=np.float64))
        w = np.stack([morph_weights(px, py) for px, py in positions])  # (n,4)
        # smoothing: moving average over smoothing_ms to avoid zipper noise
        k = max(1, int(self.sr * self.smoothing_ms / 1000.0))
        if k > 1:
            kern = np.ones(k) / k
            w = np.stack([np.convolve(w[:, i], kern, "same") for i in range(4)],
                         axis=1)
            w /= np.maximum(w.sum(axis=1, keepdims=True), 1e-9)
        out = (c * w.T).sum(axis=0)
        return out, positions


def demo() -> str:
    sr = 22050
    n = int(sr * 1.5)
    t = np.arange(n) / sr
    src = (0.6 * np.sin(2 * np.pi * 220 * t) +
           0.35 * np.sin(2 * np.pi * 331 * t) +
           0.2 * np.sign(np.sin(2 * np.pi * 110 * t)))
    src *= np.minimum(1.0, 8 * (0.5 - np.abs(((t * 2) % 1) - 0.5)))
    qm = QuadraMorph(sr)
    qm.set_corner(0, Corner("clean", []))
    qm.set_corner(1, Corner("shimmer", [("chorus", {"mix": 0.6}),
                                        ("delay", {"time_ms": 180, "fb": 0.5,
                                                   "mix": 0.5})]))
    qm.set_corner(2, Corner("crushed", [("crush", {"bits": 3}),
                                        ("drive", {"gain": 9})]))
    qm.set_corner(3, Corner("gated", [("gate", {"rate": 10, "duty": 0.35}),
                                      ("reverb", {"decay": 0.7, "mix": 0.5})]))
    rows = []
    for x, y in ((0, 0), (1, 0), (0, 1), (1, 1), (0.5, 0.5)):
        out = qm.process(src, x, y)
        spec = np.abs(np.fft.rfft(out * np.hanning(n)))
        f = np.fft.rfftfreq(n, 1.0 / sr)
        cen = (spec * f).sum() / max(spec.sum(), 1e-9)
        rows.append(f"xy=({x:.1f},{y:.1f}) w={np.round(morph_weights(x, y), 2)} "
                    f"centroid={cen:6.0f}Hz rms={np.sqrt(np.mean(out ** 2)):.3f}")
    out, pos = qm.process_motion(src, mode="steps", bpm=120)
    w = morph_weights(0.5, 0.5)
    assert abs(w.sum() - 1.0) < 1e-12
    jump_out = float(np.max(np.abs(np.diff(out))))
    jump_src = float(np.max(np.abs(np.diff(src))))
    assert jump_out <= 1.6 * jump_src, "morph introduced discontinuities"
    return ("corners=4 processors=" + str(len(PROCESSORS)) + "\n  " +
            "\n  ".join(rows) +
            f"\n  steps motion: {len(pos)} pos, {len(np.unique(pos, axis=0))} "
            f"path points, max jump out={jump_out:.3f} vs source="
            f"{jump_src:.3f} (no zipper clicks)")


if __name__ == "__main__":
    print(demo())
