# -*- coding: utf-8 -*-
"""OP-XY "drumline" — ten-model drum synthesizer + dynamic filter.

Source: Synthtopia 2026-10-23, "OP-XY Update Adds A New Drum Synth,
Multichannel Audio & More" (Teenage Engineering OP-XY OS 1.2.0):

  "drumline is a new drum synthesizer featuring ten different drum models,
   covering everything from kicks, snares, and hi-hats to congas, shakers, and
   claps. each drum model comes with four dedicated parameters ... a new
   envelope ... introduce rhythmic variations with the funk parameter, or add
   randomization to every sound on every hit."

  "The new dynamic filter combines a high-pass and low-pass filter with
   compression and drive."

What is replicated here:

- **10 synthesis models**, each a real generator (not samples):
  ``kick``, ``snare``, ``rim``, ``hat_closed``, ``hat_open``, ``conga_low``,
  ``conga_high``, ``shaker``, ``clap``, ``tom``.
  Each exposes four parameters: ``tone``, ``decay``, ``pitch``, ``snap``.
- **Envelope**: per-hit attack + decay(length) with an optional exponential
  "funk" shape (fast double-trigger on the body).
- **funk** (0..1) = seeded per-hit timing push/drag, pitch drift and level
  variation. **randomize** adds extra pitch/decay jitter on every hit.
- **DynamicFilter**: 2-pole high-pass + 2-pole low-pass (RBJ biquads) in
  series followed by a feed-forward compressor (peak detector, ratio,
  attack/release) and a tanh drive stage.

Not replicated: the OP-XY hardware, its preset set, multichannel USB audio.

Usage:
    from sound.generators.drumline import Drumline, DynamicFilter
    dl = Drumline(sample_rate=44100, seed=3)
    audio = dl.render("kick", steps=[1,0,0,0,0,0,1,0], bpm=120,
                      params={"tone": 0.5, "decay": 0.45, "pitch": 0.3,
                              "snap": 0.6}, funk=0.4)
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

__all__ = ["Drumline", "DynamicFilter", "MODELS"]

MODELS = ("kick", "snare", "rim", "hat_closed", "hat_open",
          "conga_low", "conga_high", "shaker", "clap", "tom")

A440 = 440.0


def _hz(midi: float) -> float:
    return A440 * 2.0 ** ((midi - 69.0) / 12.0)


def _biquad(x: np.ndarray, b: Sequence[float], a: Sequence[float]) -> np.ndarray:
    """Direct-form-I IIR (short buffers: plain loop is fast enough)."""
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = b
    _, a1, a2 = a
    for i, xi in enumerate(x):
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, xi
        y2, y1 = y1, yi
        y[i] = yi
    return y


def _coeffs(kind: str, f0: float, sr: int, q: float = 0.707) -> tuple:
    """RBJ cookbook biquad coefficients (lowpass/highpass/bandpass)."""
    f0 = float(np.clip(f0, 10.0, sr * 0.45))
    w0 = 2 * np.pi * f0 / sr
    cw, sw = np.cos(w0), np.sin(w0)
    alpha = sw / (2 * q)
    if kind == "lp":
        b = ((1 - cw) / 2, 1 - cw, (1 - cw) / 2)
    elif kind == "hp":
        b = ((1 + cw) / 2, -(1 + cw), (1 + cw) / 2)
    elif kind == "bp":
        b = (alpha, 0.0, -alpha)
    else:
        raise ValueError(kind)
    a = (1 + alpha, -2 * cw, 1 - alpha)
    return tuple(v / a[0] for v in b), tuple(v / a[0] for v in a)


def _hp(x, f0, sr, q=0.707):
    b, a = _coeffs("hp", f0, sr, q)
    return _biquad(x, b, a)


def _lp(x, f0, sr, q=0.707):
    b, a = _coeffs("lp", f0, sr, q)
    return _biquad(x, b, a)


def _bp(x, f0, sr, q=0.9):
    b, a = _coeffs("bp", f0, sr, q)
    return _biquad(x, b, a)


def _decay_env(n: int, sr: int, decay: float, attack: float = 0.002):
    t = np.arange(n) / sr
    a = max(1, int(attack * sr))
    env = np.exp(-t / max(decay, 1e-3))
    if a > 1:
        env[:a] *= np.linspace(0.0, 1.0, a)
    return env


def _metal(n: int, sr: int, base: float = 320.0, seed: int = 0):
    """Six inharmonic square oscillators — the classic 808/909 hat source."""
    t = np.arange(n) / sr
    ratios = (1.0, 1.34, 1.62, 1.87, 2.11, 2.47)
    out = np.zeros(n)
    for r in ratios:
        out += np.sign(np.sin(2 * np.pi * base * r * t))
    return out / len(ratios)


class DynamicFilter:
    """HPF + LPF + compressor + drive (OP-XY "dynamic filter")."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)

    def process(self, x: np.ndarray, hp: float = 25.0, lp: float = 14000.0,
                drive: float = 0.0, comp: float = 0.0,
                ratio: float = 4.0, attack: float = 0.005,
                release: float = 0.08) -> np.ndarray:
        y = _hp(x, hp, self.sr) if hp > 20 else x
        y = _lp(y, lp, self.sr) if lp < self.sr * 0.49 else y
        if drive > 0:
            y = np.tanh(y * (1.0 + 4.0 * drive)) / np.tanh(1.0 + 4.0 * drive)
        if comp > 0:
            env = np.zeros_like(y)
            a_att = np.exp(-1.0 / (attack * self.sr))
            a_rel = np.exp(-1.0 / (release * self.sr))
            e = 0.0
            for i, v in enumerate(np.abs(y)):
                coef = a_att if v > e else a_rel
                e = coef * e + (1 - coef) * v
                env[i] = e
            thr = 0.25
            over = np.maximum(env / thr, 1.0)
            gain = over ** (1.0 / ratio - 1.0)
            y = y * (1.0 - comp + comp * gain)
        return y


class Drumline:
    """Ten-model drum synthesizer with funk/randomize humanisation."""

    def __init__(self, sample_rate: int = 44100, seed: int = 0):
        self.sr = int(sample_rate)
        self.rng = np.random.default_rng(seed)
        self.filter = DynamicFilter(self.sr)

    # -- individual models -------------------------------------------------
    def hit(self, model: str, velocity: float = 1.0,
            params: Dict[str, float] = None) -> np.ndarray:
        if model not in MODELS:
            raise ValueError(f"unknown model {model!r}; choose from {MODELS}")
        p = {"tone": 0.5, "decay": 0.5, "pitch": 0.5, "snap": 0.5}
        p.update(params or {})
        sr = self.sr
        tone = float(np.clip(p["tone"], 0, 1))
        decay_s = 0.03 + float(np.clip(p["decay"], 0, 1)) ** 2 * 1.2
        pitch = float(np.clip(p["pitch"], 0, 1))
        snap = float(np.clip(p["snap"], 0, 1))
        n = int(sr * (decay_s * 1.6 + 0.02))
        t = np.arange(n) / sr
        rng = self.rng
        noise = rng.uniform(-1, 1, n)

        if model == "kick":
            f_start = 90.0 + 160.0 * pitch
            f_end = 38.0 + 30.0 * pitch
            f = f_end + (f_start - f_end) * np.exp(-t / (0.02 + 0.05 * (1 - tone)))
            body = np.sin(2 * np.pi * np.cumsum(f) / sr)
            body = np.tanh(body * (1.0 + 3.0 * tone)) * _decay_env(
                n, sr, decay_s, 0.001)
            click = _hp(noise, 2000, sr) * np.exp(-t / 0.0025) * snap * 0.6
            out = body + click
        elif model == "snare":
            f0 = 160.0 + 140.0 * pitch
            body = (np.sin(2 * np.pi * f0 * t) +
                    0.6 * np.sin(2 * np.pi * f0 * 1.83 * t)) * \
                _decay_env(n, sr, decay_s * 0.6, 0.001)
            rattle = _bp(noise, 1200 + 2500 * tone, sr, 0.7) * \
                _decay_env(n, sr, decay_s, 0.001)
            out = 0.7 * body + (0.5 + 0.5 * snap) * rattle
        elif model == "rim":
            f0 = 300 + 900 * pitch
            click = _bp(noise, f0 * 4, sr, 2.0) * np.exp(-t / 0.006)
            tone_part = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.012)
            out = 0.8 * click * (0.5 + snap) + 0.5 * tone_part
        elif model in ("hat_closed", "hat_open"):
            base = 260.0 + 320.0 * pitch
            metal = _metal(n, sr, base)
            metal = _hp(metal, 6500 + 3000 * tone, sr)
            d = (0.03 + 0.06 * decay_s) if model == "hat_closed" else decay_s
            out = metal * _decay_env(n, sr, d, 0.0005) * (0.6 + 0.4 * snap)
        elif model in ("conga_low", "conga_high"):
            base = (_hz(50) if model == "conga_low" else _hz(57)) * \
                (0.8 + 0.6 * pitch)
            sweep = base * (1.0 + 0.25 * np.exp(-t / 0.01))
            body = np.sin(2 * np.pi * np.cumsum(sweep) / sr) + \
                0.35 * np.sin(2 * np.pi * 1.59 * np.cumsum(sweep) / sr)
            out = body * _decay_env(n, sr, decay_s * 0.5, 0.001)
            out += _hp(noise, 2500, sr) * np.exp(-t / 0.004) * 0.4 * snap
        elif model == "shaker":
            # three AM grain bursts -> "chk-chk" texture
            am = np.zeros(n)
            for k, off in enumerate((0.0, 0.012, 0.026)):
                i0 = int(off * sr)
                seg = np.exp(-np.arange(n - i0) / (0.008 * sr)) if i0 < n else 0
                if i0 < n:
                    am[i0:] += (0.8 - 0.2 * k) * seg
            out = _hp(noise, 3500 + 3000 * tone, sr) * am * (0.4 + 0.6 * decay_s)
        elif model == "clap":
            bp = _bp(noise, 900 + 1800 * tone, sr, 1.4)
            env = np.zeros(n)
            for k, off in enumerate((0.0, 0.008, 0.017, 0.026)):
                i0 = int(off * sr)
                if i0 < n:
                    seg = np.exp(-np.arange(n - i0) / (0.004 * sr))
                    env[i0:] += (1.0 - 0.15 * k) * seg
            tail = 0.45 * np.exp(-t / max(0.03, decay_s * 0.4))
            out = bp * (env + tail) * (0.6 + 0.4 * snap)
        else:  # tom
            f0 = 110.0 * (0.7 + 0.9 * pitch)
            f = f0 * (1.0 + 0.6 * np.exp(-t / 0.03))
            body = np.sin(2 * np.pi * np.cumsum(f) / sr) * \
                _decay_env(n, sr, decay_s * 0.7, 0.001)
            out = body + _bp(noise, f0 * 8, sr, 1.0) * np.exp(-t / 0.01) * 0.3 * snap

        out = out * float(np.clip(velocity, 0, 2))
        # trim trailing silence so model length reflects its real decay
        audible = np.where(np.abs(out) > 1e-2 * max(np.max(np.abs(out)), 1e-9))[0]
        if len(audible):
            out = out[:min(len(out), audible[-1] + int(0.01 * sr))]
        peak = np.max(np.abs(out))
        return (out / peak * 0.9).astype(np.float32) if peak > 1e-9 else out

    # -- sequencer ---------------------------------------------------------
    def render(self, model: str, steps: Sequence[float], bpm: float = 120.0,
               params: Dict[str, float] = None, funk: float = 0.0,
               randomize: float = 0.0, step_division: int = 4,
               dynamic: Dict[str, float] = None,
               seed: int = None) -> np.ndarray:
        """Render a one-bar (len(steps)) pattern.  steps: 0..1 velocities.

        ``funk`` pushes/drags each hit in time and drifts pitch/level;
        ``randomize`` jitters decay and pitch per hit.  ``dynamic`` is forwarded
        to :class:`DynamicFilter` ({hp, lp, drive, comp}).
        """
        rng = np.random.default_rng(self.rng.integers(1 << 31) if seed is None
                                    else seed)
        step_s = 60.0 / bpm / step_division
        total = int(step_s * len(steps) * self.sr) + self.sr
        out = np.zeros(total, dtype=np.float64)
        self.last_events: List[Dict[str, float]] = []
        for i, vel in enumerate(steps):
            if vel <= 0:
                continue
            p = dict(params or {})
            drift_cents = (rng.uniform(-1, 1) * funk * 40.0 +
                           rng.uniform(-1, 1) * randomize * 120.0)
            p["pitch"] = float(np.clip(p.get("pitch", 0.5) + drift_cents / 120.0,
                                       0.0, 1.0))
            p["decay"] = float(np.clip(p.get("decay", 0.5) +
                                       rng.uniform(-1, 1) * randomize * 0.3,
                                       0.0, 1.0))
            hit = self.hit(model, velocity=vel * (1.0 - 0.25 * funk *
                                                  rng.uniform(0, 1)), params=p)
            push = rng.uniform(-1, 1) * funk * 0.018  # ±18 ms
            start = int((i * step_s + push) * self.sr)
            start = max(0, start)
            self.last_events.append({
                "step": i, "expected": i * step_s, "time": start / self.sr,
                "push_ms": push * 1000.0, "velocity": float(vel),
                "pitch_cents": drift_cents})
            end = min(total, start + len(hit))
            out[start:end] += hit[:end - start]
        if dynamic:
            out = self.filter.process(out, **dynamic)
        peak = np.max(np.abs(out))
        if peak > 1e-9:
            out = out / peak * 0.9
        return out.astype(np.float32)


def demo() -> str:
    sr = 22050
    dl = Drumline(sample_rate=sr, seed=11)
    rows = []
    for m in MODELS:
        h = dl.hit(m, params={"tone": 0.5, "decay": 0.4, "pitch": 0.5,
                              "snap": 0.6})
        spec = np.abs(np.fft.rfft(h * np.hanning(len(h))))
        f = np.fft.rfftfreq(len(h), 1.0 / sr)
        centroid = (spec * f).sum() / max(spec.sum(), 1e-9)
        rows.append(f"{m:11s} {len(h)/sr*1000:6.0f}ms centroid={centroid:7.0f}Hz")
    pat = [1, 0, 0, 0, 0.7, 0, 0, 0.9, 0, 0, 0.8, 0, 0, 0.6, 0, 0]
    tight = dl.render("kick", pat, funk=0.0, seed=1)
    tight_ev = list(dl.last_events)
    loose = dl.render("kick", pat, funk=0.8, seed=1)
    loose_ev = list(dl.last_events)
    dyn = dl.render("hat_closed", pat, params={"decay": 0.2},
                    dynamic={"hp": 300, "lp": 4000, "drive": 0.5, "comp": 0.7})

    def push_stats(events):
        p = np.array([e["push_ms"] for e in events])
        c = np.array([e["pitch_cents"] for e in events])
        return (f"n={len(p)} push sd={p.std():.1f}ms "
                f"pitch sd={c.std():.1f}c")

    t_sd = push_stats(tight_ev).split("push sd=")[1].split("ms")[0]
    l_sd = push_stats(loose_ev).split("push sd=")[1].split("ms")[0]
    assert float(l_sd) > float(t_sd), "funk must add timing variation"
    assert len({m: len(dl.hit(m)) for m in MODELS}.values()) > 1, \
        "models must differ in length"
    return ("models=10\n  " + "\n  ".join(rows) +
            f"\n  funk=0.0: {push_stats(tight_ev)}"
            f"\n  funk=0.8: {push_stats(loose_ev)}"
            f"\n  lengths: " + ", ".join(
                f"{m}={len(dl.hit(m)) / sr * 1000:.0f}ms" for m in MODELS[:5]) +
            f"\n  dynamic filter rms={np.sqrt(np.mean(dyn ** 2)):.3f} "
            f"peak={np.max(np.abs(dyn)):.3f}")


if __name__ == "__main__":
    print(demo())
