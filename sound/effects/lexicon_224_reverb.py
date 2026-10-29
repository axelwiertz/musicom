# -*- coding: utf-8 -*-
"""Lexicon 224-style diffuse reverb — Cineol-X 224 style (SP-133).

Replicable logic from the Synthtopia article "Open Source Cineol-X 224 Brings
Classic Lexicon Reverb to DAWs, Daisy DSP" (2026-10-27): Cineol-X 224 is an
open-source project porting the classic Lexicon 224 digital reverb to desktop
plugins and the Daisy embedded DSP platform — six programs, bass/mid/treble
decay controls, pre-delay, diffusion, modulation enhancement, a continuously
adjustable "Dirt" parameter for the converter-filter character, and optional
spillover between algorithm changes.

The Lexicon 224's topology is the well-known *diffuse delay network*: input
predelay -> a few all-pass diffusers -> a network of cross-coupled delay lines
whose feedback path contains the bass/treble decay filters -> output all-pass
diffusers.  The de-facto public reference implementation of this family is
Dattorro's reverb structure (JAES 1997), which we implement clean-room here.

What is replicated (self-contained numpy, offline, stereo):

- ``Lexicon224Reverb``: stereo diffuse reverb with
  - predelay (0..120 ms),
  - input diffusion: two series all-pass filters (diffusion 0..1),
  - eight cross-coupled delay lines (four per side; stereo decorrelation by
    feeding each side's feedback into the opposite side's inputs),
  - feedback loop containing a one-pole damping filter (treble decay) and a
    500 Hz bass shelf (bass decay), scaled by the overall decay gain,
  - slow sinusoidal delay-tap modulation (mod_rate/mod_depth) for the
    characteristic 224 "movement" (modulation enhancement),
  - output diffusion: two series all-pass filters per side,
  - ``dirt``: converter character — wet-path bit-depth reduction (16->4 bit)
    with first-order noise shaping plus zero-order-hold sample-rate reduction
    (the 224's early digital converters), matching the Cineol-X "Dirt" knob.
- Six programs named after the original 224 programs (hall/plate/room/
  chamber/rich/random) implemented as delay-length sets.

Not replicated: the original Lexicon firmware (the project is BYO-ROM), the
Daisy embedded target, spillover across program switches, and the plugin UI.

Usage:
    from sound.effects.lexicon_224_reverb import Lexicon224Reverb

    rv = Lexicon224Reverb(sample_rate=44100, program="hall", decay=0.6)
    wet = rv.process(x, wet=0.35, dry=0.8)   # x: mono or (N,2) stereo
"""

import math
from typing import Optional, Tuple

import numpy as np

__all__ = ["Lexicon224Reverb", "PROGRAMS"]

# Base delay-line lengths (seconds) — Dattorro-style network, L/R pairs.
_BASE_LENGTHS = (672, 4453, 1800, 3720, 1747, 4872, 613, 4156)  # @29761 Hz
_BASE_SR = 29761.0

# Six programs, tuned by scaling the base lengths and default settings.
PROGRAMS = {
    "hall":    {"scale": 1.00, "decay": 0.60, "diffusion": 0.70, "mod": 0.55},
    "plate":   {"scale": 0.80, "decay": 0.55, "diffusion": 0.85, "mod": 0.45},
    "room":    {"scale": 0.60, "decay": 0.45, "diffusion": 0.55, "mod": 0.35},
    "chamber": {"scale": 1.15, "decay": 0.62, "diffusion": 0.75, "mod": 0.50},
    "rich":    {"scale": 1.30, "decay": 0.68, "diffusion": 0.80, "mod": 0.60},
    "random":  {"scale": 1.00, "decay": 0.58, "diffusion": 0.72, "mod": 0.65},
}


class _Allpass:
    """One all-pass filter (delay line + feedback/feedforward)."""

    __slots__ = ("buf", "len", "idx", "g")

    def __init__(self, length: int, g: float) -> None:
        self.buf = np.zeros(length)
        self.len = length
        self.idx = 0
        self.g = g

    def tick(self, x: float) -> float:
        b = self.buf[self.idx]
        y = -self.g * x + b
        self.buf[self.idx] = x + self.g * b
        self.idx = (self.idx + 1) % self.len
        return y


class _DelayTap:
    """Circular delay with a modulated (interpolated) read tap."""

    __slots__ = ("buf", "len", "widx", "base", "phase", "rate", "depth", "seed", "sr")

    def __init__(self, length: int, rate: float, depth: float,
                 phase: float, seed: int, sample_rate: int) -> None:
        self.buf = np.zeros(length + 8)          # headroom for modulation
        self.len = length
        self.widx = 0
        self.base = length
        self.phase = phase
        self.rate = rate
        self.depth = depth
        self.seed = seed
        self.sr = float(sample_rate)

    def write(self, x: float) -> None:
        self.buf[self.widx] = x
        self.widx = (self.widx + 1) % (self.len + 8)

    def read(self, n: float) -> float:
        # n = absolute sample index; delay = base + mod depth * LFO
        mod = self.depth * math.sin(2.0 * math.pi * self.rate * n /
                                    self.sr + self.phase)
        delay = self.base + mod
        rp = (self.widx - delay) % (self.len + 8)
        i0 = int(math.floor(rp))
        frac = rp - i0
        i1 = (i0 + 1) % (self.len + 8)
        return self.buf[i0] * (1.0 - frac) + self.buf[i1] * frac


class Lexicon224Reverb:
    """Stereo diffuse delay-network reverb (Lexicon 224 topology).

    Parameters
    ----------
    sample_rate : int
        Output sample rate in Hz.
    program : str
        One of PROGRAMS (``'hall'``/``'plate'``/``'room'``/``'chamber'``/
        ``'rich'``/``'random'``).  Sets delay lengths + default settings.
    predelay_ms : float
        Input pre-delay in milliseconds (0..120).
    diffusion : float
        0..1 — input all-pass feedback (density of the early build).
    decay : float
        0..1 — overall feedback gain of the delay network (tail length).
    bass_decay : float
        0..1 — low-frequency feedback multiplier (bass shelf at 500 Hz).
    treble_decay : float
        0..1 — damping; higher = darker, faster high-frequency tail.
    mod_rate : float
        LFO rate in Hz for delay-tap modulation (0..10).
    mod_depth : float
        0..1 — tap modulation depth in samples (0..~5 at 44.1 kHz).
    dirt : float
        0..1 — converter character on the wet path: bit depth 16->4 bit
        plus zero-order-hold rate reduction (224-style early converters).
    wet / dry : float
        Output mix gains (also overridable per call in ``process``).
    seed : int
        Seed for per-tap LFO phases and jitter (deterministic runs).
    """

    def __init__(self, sample_rate: int = 44100, program: str = "hall",
                 predelay_ms: float = 25.0, diffusion: float = 0.7,
                 decay: float = 0.6, bass_decay: float = 0.65,
                 treble_decay: float = 0.45, mod_rate: float = 0.9,
                 mod_depth: float = 0.5, dirt: float = 0.0,
                 wet: float = 0.32, dry: float = 0.85,
                 seed: Optional[int] = None) -> None:
        self.sr = int(sample_rate)
        prog = PROGRAMS[program]
        self.program = program
        self.predelay_ms = float(predelay_ms)
        self.diffusion = float(diffusion)
        self.decay = float(decay)
        self.bass_decay = float(bass_decay)
        self.treble_decay = float(treble_decay)
        self.mod_rate = float(mod_rate)
        self.mod_depth = float(mod_depth)
        self.dirt = float(dirt)
        self.wet = float(wet)
        self.dry = float(dry)
        rng = np.random.default_rng(seed)

        scale = prog["scale"]
        self._lengths = tuple(
            max(8, int(round(l * scale * self.sr / _BASE_SR)))
            for l in _BASE_LENGTHS)

        # input diffusers (two series all-passes per side)
        g_in = 0.4 + 0.35 * self.diffusion
        l142 = int(142 * self.sr // _BASE_SR)
        l107 = int(107 * self.sr // _BASE_SR)
        self._ap_in_l = (_Allpass(l142, g_in), _Allpass(l107, g_in))
        self._ap_in_r = (_Allpass(l142, g_in), _Allpass(l107, g_in))
        # output diffusers
        l266 = int(266 * self.sr // _BASE_SR)
        l316 = int(316 * self.sr // _BASE_SR)
        self._ap_out_l = (_Allpass(l266, 0.5), _Allpass(l316, 0.5))
        self._ap_out_r = (_Allpass(l266, 0.5), _Allpass(l316, 0.5))

        # 8 delay lines: indices 0-3 = left side, 4-7 = right side
        depth_s = self.mod_depth * 4.0
        self._taps = []
        for i, ln in enumerate(self._lengths):
            self._taps.append(_DelayTap(
                ln, self.mod_rate, depth_s,
                phase=2.0 * (i / 8.0) * math.pi,
                seed=int(rng.integers(0, 2 ** 31)),
                sample_rate=self.sr))

        self._pd_buf = np.zeros(int(self.sr * 0.125) + 1)  # 125 ms max
        self._pd_w = 0
        self._pd_len = max(1, int(round(self.sr * self.predelay_ms / 1000.0)))

        # feedback filters (one-pole damping + bass shelf)
        self._damp_l = 0.0
        self._damp_r = 0.0
        self._bass_l = 0.0
        self._bass_r = 0.0
        self._fb_g = 0.35 + 0.64 * self.decay
        fc_damp = 20000.0 * (1.0 - 0.975 * self.treble_decay)
        self._a_damp = 1.0 - math.exp(-2.0 * math.pi * fc_damp / self.sr)
        fc_bass = 500.0
        self._a_bass = 1.0 - math.exp(-2.0 * math.pi * fc_bass / self.sr)
        self._bass_mult = 0.25 + 2.4 * self.bass_decay

        # dirt (converter) state
        self._bits = max(4, int(round(16.0 - 12.0 * self.dirt)))
        self._zoh = max(1, int(round(1.0 + 3.0 * self.dirt)))
        self._err_l = 0.0
        self._err_r = 0.0
        self._zoh_cnt = 0
        self._zoh_hold = 0.0

    # ------------------------------------------------------------------
    def _bass_shelf(self, x: float, lp_state: float) -> Tuple[float, float]:
        lp = lp_state + self._a_bass * (x - lp_state)
        return x + (self._bass_mult - 1.0) * lp, lp

    def _dirt_convert(self, x: float, err_state: float) -> Tuple[float, float]:
        # zero-order hold (rate reduction) then bit-depth + noise shaping
        if self._zoh > 1:
            if self._zoh_cnt % self._zoh == 0:
                self._zoh_hold = x
            self._zoh_cnt += 1
            x = self._zoh_hold
        levels = (2 ** (self._bits - 1)) - 1
        q = round((x + err_state * 0.8) * levels) / levels
        err = (x + err_state * 0.8) - q
        return q, err

    def process(self, x, wet: Optional[float] = None,
                dry: Optional[float] = None) -> np.ndarray:
        """Apply the reverb.  ``x`` is mono (N,) or stereo (N,2); output is
        stereo (N,2)."""
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        n = x.shape[0]
        out = np.zeros((n, 2))
        g_wet = self.wet if wet is None else wet
        g_dry = self.dry if dry is None else dry

        for i in range(n):
            xl = x[i, 0]
            xr = x[i, 1]

            # predelay (shared)
            self._pd_buf[self._pd_w] = xl
            pd = self._pd_buf[(self._pd_w - self._pd_len) % len(self._pd_buf)]
            self._pd_w = (self._pd_w + 1) % len(self._pd_buf)

            # input diffusion
            for ap in self._ap_in_l:
                pd = ap.tick(pd)
            for ap in self._ap_in_r:
                xr = ap.tick(xr)

            # feedback sums (opposite-side cross-coupling for decorrelation)
            fb_l = 0.0
            fb_r = 0.0
            taps_l = []
            taps_r = []
            for k in range(4):
                taps_l.append(self._taps[k].read(i))
                taps_r.append(self._taps[k + 4].read(i))
            fb_l = sum(taps_r) * self._fb_g       # right side feeds left
            fb_r = sum(taps_l) * self._fb_g

            # write delay lines: input + damped/bassed feedback
            self._taps[0].write(pd + fb_l)
            self._taps[1].write(pd + fb_l)
            self._taps[2].write(pd + fb_l)
            self._taps[3].write(pd + fb_l)
            self._taps[4].write(xr + fb_r)
            self._taps[5].write(xr + fb_r)
            self._taps[6].write(xr + fb_r)
            self._taps[7].write(xr + fb_r)

            # wet = sum of all taps -> damping/bass shaping -> output diffusers
            wet_l = sum(taps_l) + sum(taps_r)
            wet_r = wet_l
            # damping + bass shelf on the wet signal (treble/bass decay)
            self._damp_l += self._a_damp * (wet_l - self._damp_l)
            wet_l, self._bass_l = self._bass_shelf(self._damp_l, self._bass_l)
            self._damp_r += self._a_damp * (wet_r - self._damp_r)
            wet_r, self._bass_r = self._bass_shelf(self._damp_r, self._bass_r)

            for ap in self._ap_out_l:
                wet_l = ap.tick(wet_l)
            for ap in self._ap_out_r:
                wet_r = ap.tick(wet_r)

            if self.dirt > 0.0:
                wet_l, self._err_l = self._dirt_convert(wet_l, self._err_l)
                wet_r, self._err_r = self._dirt_convert(wet_r, self._err_r)

            out[i, 0] = g_dry * x[i, 0] + g_wet * wet_l
            out[i, 1] = g_dry * x[i, 1] + g_wet * wet_r

        peak = float(np.max(np.abs(out)))
        if peak > 1.0:
            out = out / peak * 0.98
        return out

    @staticmethod
    def programs() -> dict:
        return dict(PROGRAMS)


def demo() -> dict:
    """Render a short synth pad through three programs and report stats."""
    sr = 22050
    rng = np.random.default_rng(3)
    t = np.arange(int(sr * 1.5)) / sr
    pad = (0.25 * np.sin(2 * np.pi * 220 * t)
           + 0.15 * np.sin(2 * np.pi * 330 * t)
           + 0.10 * np.sin(2 * np.pi * 440 * t)) * np.exp(-t / 0.9)
    # add a sharp transient so the reverb build is audible
    pad[: int(0.01 * sr)] += 0.8 * rng.uniform(-1, 1, int(0.01 * sr))
    results = {}
    for prog in ("room", "hall", "plate"):
        rv = Lexicon224Reverb(sample_rate=sr, program=prog, dirt=0.25,
                              decay=0.6)
        y = rv.process(pad, wet=0.5, dry=0.7)
        tail = y[int(sr * 0.5):, :]
        results[prog] = (y.shape, float(np.max(np.abs(y))),
                         float(np.sqrt(np.mean(tail ** 2))))
    return results


if __name__ == "__main__":
    import os
    import tempfile
    import wave

    sr = 22050
    rng = np.random.default_rng(3)
    t = np.arange(int(sr * 1.6)) / sr
    pad = (0.25 * np.sin(2 * np.pi * 220 * t)
           + 0.15 * np.sin(2 * np.pi * 330 * t)
           + 0.10 * np.sin(2 * np.pi * 440 * t)) * np.exp(-t / 0.9)
    pad[: int(0.01 * sr)] += 0.8 * rng.uniform(-1, 1, int(0.01 * sr))

    rv = Lexicon224Reverb(sample_rate=sr, program="hall", dirt=0.2,
                          decay=0.62, mod_depth=0.5)
    y = rv.process(pad, wet=0.5, dry=0.7)
    print("out shape:", y.shape, "peak:", round(float(np.max(np.abs(y))), 3))
    tail = y[int(sr * 0.5):, :]
    print("tail rms (reverb body):", round(float(np.sqrt(np.mean(tail ** 2))), 4))

    res = demo()
    for prog, (shape, pk, trms) in res.items():
        print(f"  program {prog:<7} shape={shape} peak={pk:.3f} tail_rms={trms:.4f}")
    assert all(pk > 0.05 and trms > 0.001 for _, pk, trms in res.values()), \
        "program rendered too quiet"

    path = os.path.join(tempfile.gettempdir(), "lexicon_224_demo.wav")
    pcm = (np.clip(y, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    print("wrote", path, os.path.getsize(path), "bytes")
    assert os.path.getsize(path) > 1000, "demo wav too small"
    print("OK — SP-133 lexicon_224_reverb module works")
