"""Wavetable scan + nonlinear wave-shaper voice — Roland n/vision style.

Replicable logic from the Synthtopia item "Roland n/vision Synthesizer
Expands Boutique Line Into Wavetable Synthesis" (2026-10-20): a compact
wavetable synthesizer combining digital waveform scanning (sequences of
single-cycle waveforms) with Roland's wave-shaper technology — nonlinear
processing that generates additional harmonics and alters waveform
character — plus analog-modeling filters, step LFOs, motion recording and
a stereo spread control for expanding the image.

What is replicated here (offline numpy synthesis):
- ``WaveShaperVoice``: phase-accumulator wavetable scanning with
  frame interpolation (``position`` morphs through the table).
- Nonlinear wave-shapers: ``tanh``, ``soft_clip``, ``asym`` (asymmetric
  sigmoid — adds even harmonics), and Chebyshev polynomials ``cheby2``
  .. ``cheby6`` (T_n(x) adds the n-th harmonic — the textbook harmonic
  generator behind "wave-shaping" synthesis).
- ``drive`` before the shaper + output trim (harmonic content grows with
  drive; Chebyshev of order n generates up to harmonic n).
- Step LFO: a 16-step pattern modulates drive / wavetable position /
  pitch with per-target depth and smoothness (step-LFO interpolation),
  the n/vision step-LFO behaviour.
- Stereo spread: right channel detuned (cents) + phase offset.
- Two-layer blend (the n/vision's two adjustable wavetable layers).

Not replicated: the hardware, analog-model filter bank, MFX engine,
JUNO-style chorus, motion recording UI, and the exact proprietary
wave-shaper curves (replaced by the standard waveshaping families).

Usage:
    from sound.synthesis.waveshaper_voice import WaveShaperVoice, WAVESHAPERS

    v = WaveShaperVoice(sample_rate=44100)
    wt = v.build_wavetable(n_frames=16, wave_len=512, kind="saw")
    out = v.process(wt, freq=220.0, dur_sec=2.0, drive=2.0, shaper="cheby4")
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

__all__ = ["WaveShaperVoice", "WAVESHAPERS", "chebyshev"]

DEFAULT_SR = 44100


def chebyshev(x: np.ndarray, n: int) -> np.ndarray:
    """Chebyshev polynomial T_n(x) by recurrence (stable for |x|<=1)."""
    x = np.clip(x, -1.0, 1.0)
    if n == 0:
        return np.ones_like(x)
    if n == 1:
        return x
    t0, t1 = np.ones_like(x), x
    for _ in range(2, n + 1):
        t0, t1 = t1, 2.0 * x * t1 - t0
    return t1


WAVESHAPERS: Dict[str, str] = {
    "tanh": "soft symmetric saturation (odd harmonics)",
    "soft_clip": "x/(1+|x|) gentle symmetric clip",
    "asym": "asymmetric sigmoid — adds even harmonics (wave-shaper character)",
    "cheby2": "T2(x) — second-harmonic generator",
    "cheby3": "T3(x) — third-harmonic generator",
    "cheby4": "T4(x) — fourth-harmonic generator",
    "cheby6": "T6(x) — sixth-harmonic generator",
}


class WaveShaperVoice:
    """Wavetable-scan voice with nonlinear wave-shaping and a step LFO.

    Args:
        sample_rate: audio sample rate in Hz.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sample_rate = int(sample_rate)

    # ------------------------------------------------------------------
    def build_wavetable(self, n_frames: int = 16, wave_len: int = 512,
                        kind: str = "saw", seed: int = 0) -> np.ndarray:
        """Synthesize a ``(n_frames, wave_len)`` wavetable.

        ``kind``: saw (band-limited harmonic ramp, frame k has k+1
        harmonics), sine, square, or noise (seeded). Frame index = the
        "wavetable position" that scanning morphs through.
        """
        n_frames = max(2, int(n_frames))
        wave_len = max(64, int(wave_len))
        t = np.arange(wave_len) / wave_len
        frames = []
        for k in range(n_frames):
            if kind == "noise":
                rng = np.random.RandomState(seed + k)
                f = rng.randn(wave_len)
            elif kind == "square":
                f = np.sign(np.sin(2 * np.pi * t * (k + 1) + 1e-9))
            elif kind == "sine":
                f = np.sin(2 * np.pi * t * (k + 1))
            else:  # saw: k+1 harmonics, band-limited
                f = np.zeros(wave_len)
                for h in range(1, k + 2):
                    f += np.sin(2 * np.pi * t * h) / h
            f = f - f.mean()
            peak = np.max(np.abs(f)) + 1e-9
            frames.append(f / peak * 0.8)
        return np.array(frames)

    # ------------------------------------------------------------------
    def _shape(self, x: np.ndarray, shaper: str, drive: float) -> np.ndarray:
        """Apply the nonlinear transfer function."""
        u = x * drive
        if shaper == "tanh":
            return np.tanh(u)
        if shaper == "soft_clip":
            return u / (1.0 + np.abs(u))
        if shaper == "asym":
            return np.tanh(1.2 * u) + 0.25 * u   # asymmetric: even harmonics
        if shaper.startswith("cheby"):
            order = int(shaper[5:])
            return chebyshev(u, order)
        raise ValueError(f"unknown shaper {shaper!r}")

    # ------------------------------------------------------------------
    def _scan(self, wt: np.ndarray, freq: float, dur_sec: float,
              position: float, pos_mod: Optional[np.ndarray]) -> np.ndarray:
        """Phase-accumulator scan with frame interpolation."""
        n_frames, wave_len = wt.shape
        m = int(self.sample_rate * dur_sec)
        phase = np.cumsum(2.0 * np.pi * freq / self.sample_rate * np.ones(m))
        idx = (phase / (2.0 * np.pi) * wave_len).astype(np.int64) % wave_len
        if pos_mod is not None and len(pos_mod) == m:
            frame_pos = np.clip(position + pos_mod, 0.0, n_frames - 1)
        else:
            frame_pos = np.full(m, float(np.clip(position, 0.0, n_frames - 1)))
        f0 = np.floor(frame_pos).astype(np.int64)
        f1 = np.minimum(f0 + 1, n_frames - 1)
        frac = frame_pos - f0
        a = wt[f0, idx]
        b = wt[f1, idx]
        return a * (1 - frac) + b * frac

    # ------------------------------------------------------------------
    def process(self, wavetable: np.ndarray, freq: float = 220.0,
                dur_sec: float = 2.0, drive: float = 1.5,
                shaper: str = "tanh", position: float = 0.0,
                pos_mod: Optional[np.ndarray] = None,
                step_lfo: Optional[Dict[str, list]] = None,
                lfo_steps: int = 16, blend: float = 0.5,
                spread_cents: float = 6.0, gain: float = 0.5) -> np.ndarray:
        """Render a two-layer wavetable voice with wave-shaping.

        Args:
            wavetable: ``(n_frames, wave_len)`` float matrix.
            freq: fundamental frequency (layer A).
            dur_sec: output duration.
            drive: wave-shaper input gain (harmonic content grows with it).
            shaper: one of ``WAVESHAPERS``.
            position: base wavetable position (frame index).
            pos_mod: optional per-sample position modulation (array len
                ``dur_sec * sr``), e.g. an envelope or LFO sweep.
            step_lfo: dict mapping target -> 16 values, e.g.
                ``{"drive": [...], "position": [...], "pitch": [...]}``.
                Values are held per step with optional smoothing (the
                n/vision step LFO). Targets: drive, position, pitch.
            lfo_steps: number of steps in the step LFO.
            blend: layer B mix (0 = layer A only, 1 = layer B only).
            spread_cents: layer B detune in cents (stereo spread).
            gain: output trim.

        Returns:
            Stereo ``(m, 2)`` float array.
        """
        wt = np.asarray(wavetable, dtype=np.float64)
        if wt.ndim != 2:
            raise ValueError("wavetable must be (n_frames, wave_len)")
        n_frames, wave_len = wt.shape
        m = int(self.sample_rate * dur_sec)

        # step LFO -> per-sample modulation signals
        step_mod: Dict[str, np.ndarray] = {}
        if step_lfo:
            for target, values in step_lfo.items():
                vals = np.asarray(values, dtype=np.float64).reshape(-1)
                if len(vals) < 2:
                    step_mod[target] = np.full(m, float(vals[0]))
                    continue
                seg = m / lfo_steps
                sig = np.zeros(m)
                for i in range(lfo_steps):
                    i0 = int(round(i * seg))
                    i1 = int(round((i + 1) * seg))
                    i1 = min(i1, m)
                    if i1 <= i0:
                        continue
                    a = vals[i % len(vals)]
                    b = vals[(i + 1) % len(vals)]
                    sig[i0:i1] = np.linspace(a, b, i1 - i0, endpoint=False)
                step_mod[target] = sig

        # layer A
        drive_a = drive * (1.0 + step_mod["drive"]) if "drive" in step_mod else drive
        freq_a = freq * (2.0 ** (step_mod["pitch"] / 12.0)) if "pitch" in step_mod \
            else np.full(m, freq)
        pos_a = position + (step_mod["position"] if "position" in step_mod
                            else np.zeros(m))
        la = np.zeros(m)
        phase = 0.0
        for i in range(m):
            f = float(freq_a[i])
            phase = (phase + 2.0 * np.pi * f / self.sample_rate) % (2 * np.pi)
            fi = min(n_frames - 1, float(pos_a[i]))
            f0 = int(fi)
            f1 = min(f0 + 1, n_frames - 1)
            frac = fi - f0
            idx = int(phase / (2 * np.pi) * wave_len) % wave_len
            la[i] = wt[f0, idx] * (1 - frac) + wt[f1, idx] * frac
        la = self._shape(la, shaper, drive_a)

        # layer B: detuned + phase-offset scan, blended
        detune = 2.0 ** (spread_cents / 1200.0)
        lb = self._scan(wt, freq * detune, dur_sec, position, pos_mod)
        lb = self._shape(lb, shaper, drive)

        mono = la * (1 - blend) + lb * blend
        mono = mono * gain
        # stereo: layer A hard-left-ish, layer B right with detune -> spread
        left = la * (1 - blend) + lb * blend * 0.5
        right = la * (1 - blend) * 0.5 + lb * blend
        out = np.stack([left, right], axis=1) * gain
        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: Chebyshev drive adds harmonics; step LFO sweeps position."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    v = WaveShaperVoice(sample_rate=sr)
    wt = v.build_wavetable(n_frames=16, wave_len=512, kind="saw")

    def _harm_ratio(sig, f0, h):
        Y = np.abs(np.fft.rfft(sig))
        freqs = np.fft.rfftfreq(len(sig), 1 / sr)
        at = lambda f: float(Y[np.argmin(np.abs(freqs - f))])
        return at(f0 * h) / (at(f0) + 1e-12)

    # cheby4 with drive=0: nearly no 4th harmonic; drive=3: strong 4th
    y0 = v.process(wt, freq=220.0, dur_sec=1.0, drive=0.0, shaper="cheby4",
                   gain=0.8)[:, 0]
    y1 = v.process(wt, freq=220.0, dur_sec=1.0, drive=3.0, shaper="cheby4",
                   gain=0.4)[:, 0]
    r0 = _harm_ratio(y0, 220.0, 4)
    r1 = _harm_ratio(y1, 220.0, 4)
    assert r1 > r0 * 3 + 0.02, f"cheby4 harmonic growth failed {r0:.3f} -> {r1:.3f}"

    # step LFO on position (16 steps sweeping the wavetable) + tanh drive
    y2 = v.process(wt, freq=220.0, dur_sec=2.0, drive=2.0, shaper="tanh",
                   position=0.0, step_lfo={"position": list(range(16))},
                   blend=0.5, spread_cents=8.0)
    p2 = os.path.join(out_dir, "nvision_waveshaper.wav")
    write_wav(p2, y2, sr)
    assert os.path.getsize(p2) > 40
    assert y2.shape[1] == 2 and float(np.max(np.abs(y2))) > 1e-3

    return {
        "cheby4_harmonic_ratio_drive0": round(r0, 4),
        "cheby4_harmonic_ratio_drive3": round(r1, 4),
        "step_lfo_stereo": {"samples": int(y2.shape[0]), "channels": 2,
                            "peak": round(float(np.max(np.abs(y2))), 4)},
        "shapers": sorted(WAVESHAPERS),
        "wav_bytes": os.path.getsize(p2),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
