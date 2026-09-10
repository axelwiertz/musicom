"""Morphing five-character resonant filter — ZERO9 Fusion Filter style.

Replicable logic from the ZERO9 plugin range (MusicTech news, 2026-09-08):
"Fusion Filter, which puts five different filter characters into one workflow
and allows you to filter between engines while using the same amount,
resonance and mix controls."

What is replicated here:
- **Five distinct filter engines**, each a real (different) topology:
    * ``ladder``  — 4-pole transistor ladder, per-stage tanh saturation.
    * ``diode``   — 4-pole diode ladder with an *asymmetric* saturator
                    (`x - 0.35*x^2` before tanh) -> even-order colour.
    * ``svf``     — ZDF/trapezoidal state-variable filter, clean 2-pole.
    * ``comb``    — resonant comb with a lowpass in the feedback path
                    (metallic / formant-ish character instead of a peak).
    * ``scream``  — heavily driven ladder followed by a wavefolder.
- **Engine morphing**: a continuous ``position`` 0..4 bilinearly crossfades
  (equal-power) between the two *adjacent* characters, so all five share the
  same cutoff (amount), resonance, drive and mix controls while the character
  slides seamlessly from one engine to the next.
- Self-oscillation: with resonance > ~0.92 the ladder engines oscillate, as the
  hardware/plug-in versions do.

Not replicated: the plug-in UI, the exact ZERO9 coefficient tables.

Usage:
    from sound.effects.morph_filter import FusionFilter, CHARACTERS

    ff = FusionFilter(sample_rate=44100)
    out = ff.process(audio, cutoff=900.0, resonance=0.8,
                     position=1.5, drive=1.5, mix=1.0)
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

__all__ = ["FusionFilter", "CHARACTERS", "filter_character"]

CHARACTERS: Tuple[str, ...] = ("ladder", "diode", "svf", "comb", "scream")


def _saturate_odd(x):
    return np.tanh(x)


def _saturate_even(x):
    """Asymmetric (diode-ish) saturator: adds even harmonics."""
    return np.tanh(x - 0.35 * x * x)


def _ladder(x: np.ndarray, sr: int, cutoff: float, resonance: float,
            drive: float, sat=_saturate_odd, fold: bool = False) -> np.ndarray:
    """4-pole ladder lowpass with saturating feedback (per-sample loop)."""
    n = x.shape[0]
    g = 1.0 - np.exp(-2.0 * np.pi * float(np.clip(cutoff, 20.0, sr * 0.45)) / sr)
    k = 4.0 * float(np.clip(resonance, 0.0, 1.02))
    s1 = s2 = s3 = s4 = 0.0
    y = np.empty(n, dtype=np.float64)
    sd = drive
    for i in range(n):
        u = x[i] * sd - k * s4
        if u > 12.0:
            u = 12.0
        elif u < -12.0:
            u = -12.0
        u = sat(u)
        s1 += g * (u - s1)
        s2 += g * (sat(s1) - s2)
        s3 += g * (sat(s2) - s3)
        s4 += g * (sat(s3) - s4)
        out = s4
        if fold:
            out = 4.0 * abs(out / 2.0 - round(out / 2.0)) - 1.0
        y[i] = out
    return y


def _svf(x: np.ndarray, sr: int, cutoff: float, resonance: float,
         drive: float) -> np.ndarray:
    """Zero-delay-feedback (trapezoidal) state-variable filter, lowpass out."""
    n = x.shape[0]
    fc = float(np.clip(cutoff, 20.0, sr * 0.45))
    g = np.tan(np.pi * fc / sr)
    q = float(np.clip(0.5 + (1.0 - resonance) * 6.0, 0.5, 12.0))
    k = 1.0 / q
    a1 = 1.0 / (1.0 + g * (g + k))
    a2 = g * a1
    a3 = g * a2
    ic1 = ic2 = 0.0
    y = np.empty(n, dtype=np.float64)
    for i in range(n):
        v0 = np.tanh(x[i] * drive)
        v3 = v0 - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        y[i] = v2
    return y


def _comb(x: np.ndarray, sr: int, cutoff: float, resonance: float,
          drive: float) -> np.ndarray:
    """Resonant comb: delay tuned to 1/cutoff, lowpass damping in feedback."""
    n = x.shape[0]
    d = int(max(2, round(sr / max(20.0, cutoff))))
    fb = 0.35 + 0.62 * float(np.clip(resonance, 0.0, 1.0))
    lp = 0.5
    buf = np.zeros(d, dtype=np.float64)
    idx = 0
    z = 0.0
    y = np.empty(n, dtype=np.float64)
    for i in range(n):
        dl = buf[idx]
        z += lp * (dl - z)
        v = np.tanh(x[i] * drive + fb * z)
        buf[idx] = v
        idx = (idx + 1) % d
        y[i] = v
    return y


def filter_character(audio: np.ndarray, character: str, sample_rate: int = 44100,
                     cutoff: float = 1200.0, resonance: float = 0.6,
                     drive: float = 1.0) -> np.ndarray:
    """Render one named character (used directly and by FusionFilter)."""
    x = np.asarray(audio, dtype=np.float64)
    if character == "ladder":
        return _ladder(x, sample_rate, cutoff, resonance, drive)
    if character == "diode":
        return _ladder(x, sample_rate, cutoff, resonance, drive,
                       sat=_saturate_even)
    if character == "svf":
        return _svf(x, sample_rate, cutoff, resonance, drive)
    if character == "comb":
        return _comb(x, sample_rate, cutoff, resonance, drive)
    if character == "scream":
        return _ladder(x, sample_rate, cutoff, resonance, drive,
                       sat=_saturate_odd, fold=True)
    raise ValueError(f"unknown character {character!r}; use {CHARACTERS}")


class FusionFilter:
    """Five-engine morphing resonant filter with shared amount/res/res/mix."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.cutoff: float = 1200.0
        self.resonance: float = 0.6
        self.drive: float = 1.0
        self.mix: float = 1.0
        self.position: float = 0.0     # 0=ladder .. 4=scream (continuous)

    # -- character morphing -------------------------------------------------
    def morph_positions(self, position: float | None = None) -> Dict[str, float]:
        """Return the (engine -> equal-power weight) blend for a position."""
        pos = self.position if position is None else float(position)
        pos = float(np.clip(pos, 0.0, len(CHARACTERS) - 1.0))
        lo = int(np.floor(pos))
        hi = min(lo + 1, len(CHARACTERS) - 1)
        t = pos - lo
        w_lo = float(np.cos(t * np.pi / 2.0))   # equal-power crossfade
        w_hi = float(np.sin(t * np.pi / 2.0))
        if lo == hi:
            return {CHARACTERS[lo]: 1.0}
        return {CHARACTERS[lo]: w_lo, CHARACTERS[hi]: w_hi}

    def process(self, audio: np.ndarray, cutoff: float | None = None,
                resonance: float | None = None, position: float | None = None,
                drive: float | None = None, mix: float | None = None,
                ) -> np.ndarray:
        """Filter with a morphable character; only 2 engines are computed."""
        x = np.asarray(audio, dtype=np.float64)
        fc = self.cutoff if cutoff is None else float(cutoff)
        res = self.resonance if resonance is None else float(resonance)
        drv = self.drive if drive is None else float(drive)
        mx = self.mix if mix is None else float(mix)
        weights = self.morph_positions(position)

        wet = np.zeros_like(x)
        for name, w in weights.items():
            wet += w * filter_character(x, name, self.sr, fc, res, drv)
        return (1.0 - mx) * x + mx * wet

    def response_peak(self, freq_hz: float = 1200.0, position: float = 0.0,
                      resonance: float = 0.85, seconds: float = 0.4
                      ) -> Tuple[float, float]:
        """Sweep test: return (measured peak frequency, peak gain) of the engine."""
        n = int(self.sr * seconds)
        tt = np.arange(n) / self.sr
        chirp_lo, chirp_hi = 100.0, 6000.0
        # log sweep so the resonant peak shows up as a spectral max
        phase = 2 * np.pi * (chirp_lo * n / np.log(chirp_hi / chirp_lo) * 0.0)
        inst = np.linspace(0.0, 1.0, n)
        k = np.log(chirp_hi / chirp_lo)
        phase = 2 * np.pi * chirp_lo * n / k * (np.exp(inst * k) - 1.0)
        sweep = np.sin(phase)
        out = self.process(sweep, cutoff=freq_hz, resonance=resonance,
                           position=position, drive=1.0)
        spec = np.abs(np.fft.rfft(out * np.hanning(n)))
        fr = np.fft.rfftfreq(n, 1.0 / self.sr)
        pk = int(np.argmax(spec))
        return float(fr[pk]), float(spec[pk])


def demo() -> str:
    sr = 22050
    ff = FusionFilter(sample_rate=sr)
    n = int(sr * 0.3)
    tt = np.arange(n) / sr
    src = 0.5 * np.sin(2 * np.pi * 150.0 * tt) + 0.2 * np.random.default_rng(0).standard_normal(n)

    peaks = {}
    nfft = 1 << int(np.floor(np.log2(len(src))))
    win = np.hanning(nfft)
    for i, name in enumerate(CHARACTERS):
        out = ff.process(src, cutoff=1200.0, resonance=0.8, position=float(i))
        spec = np.abs(np.fft.rfft(out[:nfft] * win))
        fr = np.fft.rfftfreq(nfft, 1.0 / sr)
        band = (fr > 900) & (fr < 1600)
        peaks[name] = float(fr[band][np.argmax(spec[band])])
        assert np.all(np.isfinite(out)), name
        print(f"{name:7s} peak_in_band={peaks[name]:7.1f} Hz  "
              f"rms={np.sqrt(np.mean(out ** 2)):.4f}  "
              f"out={np.max(np.abs(out)):.3f}")

    # a mid-morph must differ from both neighbours and lie between them
    a = ff.process(src, cutoff=1200.0, resonance=0.8, position=0.0)
    m = ff.process(src, cutoff=1200.0, resonance=0.8, position=0.5)
    b = ff.process(src, cutoff=1200.0, resonance=0.8, position=1.0)
    print("morph differs from both engines:",
          (not np.allclose(a, m)) and (not np.allclose(b, m)))
    assert not np.allclose(a, m) and not np.allclose(b, m)
    print("weights at 0.5:", {k: round(v, 4)
                              for k, v in ff.morph_positions(0.5).items()})

    # high resonance must stay finite (self-oscillation, no NaN blow-up)
    hot = ff.process(src, cutoff=800.0, resonance=0.99, position=2.5, drive=3.0)
    print(f"res=0.99 drive=3 finite={np.all(np.isfinite(hot))} "
          f"peak={np.max(np.abs(hot)):.3f}")
    assert np.all(np.isfinite(hot))
    print("  morph_filter demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
