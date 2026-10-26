# -*- coding: utf-8 -*-
"""Sample flipper — Knobula Drum Farm "Player" style 16-slot resampler.

Source: Sound On Sound, Oct 2026 review of the Knobula Drum Farm (Eurorack):
the Player section holds 16 grabbed slots; "using Shift you can use the slot
knob to choose from 16 different ways the samples are flipped in real time",
and slots can be flipped by modulating the slot selector. Player 1 samples a
synth model or a played sample ("Get"), Player 2 resamples whatever is
playing, and the module can re-sample its own output through its effects.

What is replicated here — the flip engine, which is pure sequencing logic:

- A **16-slot bank** of audio buffers with a ``grab()`` resample step (capture
  the current tail of a source, optionally through an effect callback — that
  is the "sample through the FX then flip it" workflow).
- **16 flip modes** (``FLIP_MODES``) deciding, per step, which slot plays and
  how: forward, reverse, alternate, random, pingpong, ratchet ×2/3/4,
  gate-half, gate-quarter, odd-only, skip-2, pitch-up, pitch-down,
  stutter-last, chop-ladder.
- ``plan()`` produces a deterministic playback plan (slot, rate, reverse,
  gate, repeats) — inspectable and reproducible per seed; ``render()``
  renders it onto a step grid.

Not replicated: the hardware module, its 16 effects, ROM sample banks.

Usage:
    from sound.generators.sample_flipper import SampleFlipper
    sf = SampleFlipper(sample_rate=44100)
    for i, buf in enumerate(hits):
        sf.set_slot(i, buf)
    audio, plan = sf.render(slot_map=[0, 3, 7, 12], mode="pingpong",
                            steps=16, bpm=128, seed=4)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["SampleFlipper", "Flip", "FLIP_MODES"]

FLIP_MODES: Tuple[str, ...] = (
    "forward", "reverse", "alternate", "random", "pingpong",
    "ratchet2", "ratchet3", "ratchet4", "gate_half", "gate_quarter",
    "odd_only", "skip2", "pitch_up", "pitch_down", "stutter_last",
    "chop_ladder",
)


@dataclass
class Flip:
    """One playback instruction produced by the flipper."""
    slot: int
    rate: float = 1.0          # playback rate (1.0 = original pitch)
    reverse: bool = False
    gate: float = 1.0          # fraction of the step that sounds
    repeats: int = 1           # ratchets inside the step
    offset: float = 0.0        # read start, as a fraction of the buffer


class SampleFlipper:
    """16-slot bank + 16 flip modes (Drum Farm Player-style)."""

    def __init__(self, sample_rate: int = 44100, n_slots: int = 16,
                 seed: int = 0):
        self.sr = int(sample_rate)
        self.n_slots = int(n_slots)
        self.slots: List[np.ndarray] = [np.zeros(0)] * self.n_slots
        self.rng = np.random.default_rng(seed)

    # -- bank --------------------------------------------------------------
    def set_slot(self, index: int, audio: np.ndarray) -> None:
        if not 0 <= index < self.n_slots:
            raise IndexError(f"slot {index} out of range 0..{self.n_slots - 1}")
        a = np.asarray(audio, dtype=np.float64)
        self.slots[index] = a.mean(axis=1) if a.ndim > 1 else a

    def grab(self, index: int, source: np.ndarray, length: float = 0.25,
             fx: Optional[Callable[[np.ndarray], np.ndarray]] = None,
             start: float = 0.0) -> np.ndarray:
        """Sample a slice of ``source`` into a slot ("Get" on the Player)."""
        n = int(self.sr * length)
        i0 = int(start * self.sr)
        chunk = np.asarray(source, dtype=np.float64)[i0:i0 + n]
        if len(chunk) < n:
            chunk = np.pad(chunk, (0, n - len(chunk)))
        if fx is not None:
            chunk = np.asarray(fx(chunk), dtype=np.float64)
        peak = np.max(np.abs(chunk))
        if peak > 1e-9:
            chunk = chunk / peak * 0.9
        self.set_slot(index, chunk)
        return self.slots[index]

    def _buf(self, slot: int) -> np.ndarray:
        a = self.slots[slot % self.n_slots]
        return a if len(a) else np.zeros(64)

    # -- flip logic --------------------------------------------------------
    def plan(self, slot_map: Sequence[int], mode: str = "forward",
             steps: int = None, seed: int = None,
             rng: np.random.Generator = None) -> List[Flip]:
        """Return the per-step playback plan for a flip mode."""
        if mode not in FLIP_MODES:
            raise ValueError(f"unknown flip mode {mode!r}; "
                             f"choose from {FLIP_MODES}")
        rng = rng or np.random.default_rng(
            self.rng.integers(1 << 31) if seed is None else seed)
        steps = int(steps or len(slot_map))
        base = [int(s) % self.n_slots for s in slot_map]
        if not base:
            base = [0]
        out: List[Flip] = []
        for i in range(steps):
            slot = base[i % len(base)]
            f = Flip(slot=slot)
            if mode == "reverse":
                f.reverse = True
            elif mode == "alternate":
                f.reverse = (i % 2 == 1)
            elif mode == "random":
                f.slot = int(rng.integers(0, len(base)))
                f.slot = base[f.slot]
                f.reverse = bool(rng.integers(0, 2))
            elif mode == "pingpong":
                cycle = 2 * len(base)
                k = i % cycle
                f.slot = base[k] if k < len(base) else base[cycle - 1 - k]
            elif mode.startswith("ratchet"):
                f.repeats = int(mode[-1])
                f.gate = 1.0 / f.repeats
            elif mode == "gate_half":
                f.gate = 0.5
            elif mode == "gate_quarter":
                f.gate = 0.25
            elif mode == "odd_only":
                f.gate = 1.0 if (i % 2 == 0) else 0.0
            elif mode == "skip2":
                f.gate = 0.0 if (i % 3 == 1) else 1.0
            elif mode == "pitch_up":
                f.rate = 1.5
            elif mode == "pitch_down":
                f.rate = 2.0 / 3.0
            elif mode == "stutter_last":
                # re-fire the previous musical step's slot, half-gated
                f.slot = base[(i - 1) % len(base)] if i else base[0]
                f.gate = 0.5
            elif mode == "chop_ladder":
                f.repeats = 1 + (i % 4)
                f.gate = 1.0 / f.repeats
                f.offset = ((i % 4) * 0.25)
            out.append(f)
        return out

    def render(self, slot_map: Sequence[int], mode: str = "forward",
               steps: int = 16, bpm: float = 120.0, step_division: int = 4,
               seed: int = None, tail_pad: float = 0.3) -> Tuple[np.ndarray, List[Flip]]:
        """Render a flip pattern to audio.  Returns (audio, plan)."""
        plan = self.plan(slot_map, mode, steps, seed)
        step_s = 60.0 / bpm / step_division
        step_n = int(step_s * self.sr)
        total = int(steps * step_n + self.sr * tail_pad)
        out = np.zeros(total)
        for i, f in enumerate(plan):
            if f.gate <= 0:
                continue
            buf = self._buf(f.slot)
            if f.reverse:
                buf = buf[::-1]
            if f.offset > 0:
                o = int(f.offset * len(buf))
                buf = np.roll(buf, -o)
            # resample by rate (linear interp)
            if abs(f.rate - 1.0) > 1e-9:
                idx = np.arange(0, len(buf), f.rate)
                buf = np.interp(idx, np.arange(len(buf)), buf)
            seg_n = int(step_n * f.gate)
            for r in range(max(1, f.repeats)):
                start = i * step_n + int(r * step_n * f.gate)
                chunk = buf[:seg_n]
                if len(chunk) == 0:
                    continue
                # short fade-out per slice -> no clicks on chop/ratchet
                fade = min(len(chunk), max(8, int(0.004 * self.sr)))
                chunk = chunk.copy()
                chunk[-fade:] *= np.linspace(1.0, 0.0, fade)
                end = min(total, start + len(chunk))
                out[start:end] += chunk[:end - start]
        peak = np.max(np.abs(out))
        if peak > 1e-9:
            out = out / peak * 0.9
        return out.astype(np.float32), plan


def _hit(sr: int, freq: float, decay: float, seed: int) -> np.ndarray:
    n = int(sr * decay * 4)
    t = np.arange(n) / sr
    rng = np.random.default_rng(seed)
    y = np.sin(2 * np.pi * freq * t) * np.exp(-t / decay)
    y += 0.4 * rng.uniform(-1, 1, n) * np.exp(-t / (decay * 0.3))
    return (y / max(np.max(np.abs(y)), 1e-9) * 0.9).astype(np.float32)


def demo() -> str:
    sr = 22050
    sf = SampleFlipper(sample_rate=sr, seed=9)
    freqs = (60, 180, 320, 900, 240, 700, 120, 1400)
    for i, f in enumerate(freqs):
        sf.set_slot(i, _hit(sr, f, 0.05 + 0.01 * i, seed=i))
    # "Get" workflow: resample the current bank output through an FX callback
    src = np.concatenate([sf._buf(i) for i in range(4)])
    sf.grab(15, src, length=0.35,
            fx=lambda b: np.tanh(b * 3.0) * 0.8)
    lines = []
    for mode in ("forward", "reverse", "pingpong", "ratchet3",
                 "pitch_up", "chop_ladder", "stutter_last"):
        audio, plan = sf.render([0, 2, 5, 15], mode=mode, steps=8, bpm=120,
                                seed=3)
        desc = " ".join(
            f"{f.slot}{'R' if f.reverse else ''}"
            f"{'x%d' % f.repeats if f.repeats > 1 else ''}"
            f"{'@%.2f' % f.rate if f.rate != 1.0 else ''}"
            f"{'g%.2f' % f.gate if f.gate != 1.0 else ''}"
            for f in plan)
        lines.append(f"{mode:12s} {desc}  rms={np.sqrt(np.mean(audio ** 2)):.3f}")
    a1, _ = sf.render([0, 2, 5], "random", steps=8, seed=42)
    a2, _ = sf.render([0, 2, 5], "random", steps=8, seed=42)
    assert np.array_equal(a1, a2), "flip must be deterministic per seed"
    a3, _ = sf.render([0, 2, 5], "random", steps=8, seed=43)
    assert not np.array_equal(a1, a3), "different seeds must differ"
    return ("slots=16 modes=" + str(len(FLIP_MODES)) + "\n  " +
            "\n  ".join(lines) + "\n  deterministic per seed: OK")


if __name__ == "__main__":
    print(demo())
