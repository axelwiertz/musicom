"""Dual complex-oscillator voice with comparator waveshaping and Mid/Side matrix
— Larix Elektro "Origami Duo" style.

Replicable logic from Synthtopia 2026-11-13 ("Larix Elektro Origami Duo
Combines Dual Complex Oscillators With Mid-Side Processing"). The module is a
complete analogue voice built from:

  * two **AS3340** saw-core oscillators (the CEM3340 clone), each with a
    sawtooth and a variable-width pulse output;
  * a **multi-stage wavefolder** per oscillator;
  * a **comparator** stage that pushes the triangle toward a square — the
    pulse width of the resulting square is set by the comparator threshold,
    and the blend amount decides how much of the squared signal is mixed in;
  * two **VCAs** that can run unipolar (amplitude) or bipolar (ring
    modulation);
  * a configurable **Mid/Side matrix** so the two channels can be recombined
    as L/R → M/S or M/S → L/R;
  * a four-output LFO with fixed phase offsets, and an AD/AR envelope.

DSP notes that matter for the sound:

  * AS3340 saw is a **capacitor-reset ramp**: phase accumulator → 2φ−1. The
    reset discontinuity is what gives the buzzy, slightly "hollow" character
    versus a mathematically ideal saw; we keep it (no band-limiting), which is
    the point of a VA model of this chip in this repo.
  * The comparator is implemented as tanh(k·(tri − threshold)) so its
    transition has finite slope (a real comparator has slew); k controls edge
    sharpness and therefore HF content. Threshold offset = pulse width.
  * The wavefolder is the Sine folder family: gain → asin(sin(·)) per stage.
    For |x| ≤ 1 the shaper is the identity, so small signals pass clean and
    only large signals fold — the defining behaviour of a West-Coast folder.
    Cascading stages folds the already-folded signal again.
  * Bipolar VCA = four-quadrant multiplication, i.e. ring modulation; the
    modulator is the channel's own oscillator or the LFO.

All rendering is offline numpy at a fixed sample rate.
"""

from __future__ import annotations

import numpy as np

TAU = 2.0 * np.pi


# --------------------------------------------------------------------- pieces
def as3340_saw(phase: np.ndarray) -> np.ndarray:
    """Saw core: reset ramp in [-1, 1]."""
    return 2.0 * (phase % 1.0) - 1.0


def as3340_pulse(phase: np.ndarray, width: float = 0.5) -> np.ndarray:
    """Pulse output of the same core; width clamped away from 0/1."""
    w = float(np.clip(width, 0.02, 0.98))
    return np.where((phase % 1.0) < w, 1.0, -1.0)


def triangle(phase: np.ndarray) -> np.ndarray:
    """Triangle from the same phase accumulator, [-1, 1]."""
    p = phase % 1.0
    return 4.0 * np.abs(p - 0.5) - 1.0


def comparator(tri: np.ndarray, threshold: float = 0.0, sharpness: float = 12.0) -> np.ndarray:
    """Soft comparator: tanh(k*(tri - threshold)) -> square with finite slew."""
    return np.tanh(sharpness * (tri - threshold))


def comparator_morph(tri: np.ndarray, amount: float = 0.0, threshold: float = 0.0,
                     sharpness: float = 12.0) -> np.ndarray:
    """Blend triangle -> comparator square. amount=0 tri, 1 square."""
    a = float(np.clip(amount, 0.0, 1.0))
    return (1.0 - a) * tri + a * comparator(tri, threshold, sharpness)


def sine_fold(x: np.ndarray, drive: float = 1.0, stages: int = 1) -> np.ndarray:
    """Multi-stage sine wavefolder. Linear for |drive*x| <= 1, folds above."""
    y = np.asarray(x, dtype=float) * float(drive)
    for _ in range(max(1, int(stages))):
        y = np.arcsin(np.sin(0.5 * np.pi * np.clip(y, -4.0, 4.0))) / (0.5 * np.pi)
    return np.clip(y, -1.0, 1.0)


def vca(x: np.ndarray, gain: np.ndarray | float, bipolar: bool = False) -> np.ndarray:
    """Unipolar VCA (gain >= 0) or bipolar four-quadrant multiplier (ring mod)."""
    g = np.asarray(gain, dtype=float)
    if not bipolar:
        g = np.clip(g, 0.0, None)
    return x * g


def mid_side(a: np.ndarray, b: np.ndarray, mid_gain: float = 1.0,
             side_gain: float = 1.0, to_ms: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """L/R <-> M/S matrix. to_ms=True encodes (L,R)->(M,S), False decodes.

    Encoding is the standard sum/difference pair; decoding is its exact
    inverse scaled by mid_gain/side_gain (width control).
    """
    if to_ms:
        return 0.5 * (a + b) * mid_gain, 0.5 * (a - b) * side_gain
    L2 = a * mid_gain + b * side_gain
    R2 = a * mid_gain - b * side_gain
    return L2, R2


# ---------------------------------------------------------------------- voice
class OrigamiDuo:
    """Two AS3340 complex oscillators, comparator + folder, VCA, M/S out."""

    def __init__(self, sr: int = 44100):
        self.sr = int(sr)
        # per-channel configuration (sensible "complete voice" defaults)
        self.pw = [0.5, 0.5]
        self.comp_amount = [0.0, 0.0]
        self.comp_threshold = [0.0, 0.0]
        self.fold_drive = [1.0, 1.0]
        self.fold_stages = [1, 1]
        self.level = [0.8, 0.5]
        self.bipolar = [False, False]
        self.detune_cents = [-7.0, 7.0]
        self.mid_gain = 1.0
        self.side_gain = 1.0

    # ------------------------------------------------------------------ utils
    def _osc(self, freq: float, n: int, ch: int, phase0: float = 0.0) -> np.ndarray:
        f = freq * 2.0 ** (self.detune_cents[ch] / 1200.0)
        ph = phase0 + np.arange(n) * (f / self.sr)
        tri = triangle(ph)
        shaped = comparator_morph(tri, self.comp_amount[ch],
                                  self.comp_threshold[ch])
        return sine_fold(shaped, self.fold_drive[ch], self.fold_stages[ch])

    def lfo(self, rate: float, n: int, phases=(0.0, 0.25, 0.5, 0.75)) -> np.ndarray:
        """Four phase-offset LFO outputs, shape (4, n)."""
        t = np.arange(n) / self.sr
        return np.stack([np.sin(TAU * rate * t + TAU * p) for p in phases])

    def envelope(self, n: int, attack: float = 0.01, decay: float = 0.3,
                 sustain: float = 0.6, release: float = 0.2,
                 hold_s: float | None = None) -> np.ndarray:
        """Linear AD/AR segment envelope (sustain=0 gives a pure AD)."""
        a = max(1, int(attack * self.sr))
        d = max(1, int(decay * self.sr))
        r = max(1, int(release * self.sr))
        env = np.zeros(n)
        i = 0
        seg = min(a, n)
        env[i:seg] = np.linspace(0.0, 1.0, seg, endpoint=False)
        i = seg
        hi = min(i + d, n)
        if hi > i:
            env[i:hi] = np.linspace(1.0, sustain, hi - i, endpoint=False)
        i = hi
        sus_end = n if hold_s is None else min(n, i + int(hold_s * self.sr))
        env[i:sus_end] = sustain
        i = sus_end
        if i < n:
            env[i:] = np.linspace(env[i - 1] if i else sustain, 0.0, n - i)
        return env

    # ----------------------------------------------------------------- render
    def render(self, freq: float, seconds: float = 1.0, ring_amount: float = 0.0,
               width: float | None = None) -> np.ndarray:
        """Render a stereo note. `ring_amount` mixes ch0×ch1 (ring) into ch0."""
        n = max(1, int(seconds * self.sr))
        a = self._osc(freq, n, 0)
        b = self._osc(freq, n, 1, phase0=0.17)
        if ring_amount > 0.0:
            a = (1.0 - ring_amount) * a + ring_amount * a * b
        env = self.envelope(n)
        L = vca(a, env * self.level[0], self.bipolar[0])
        R = vca(b, env * self.level[1], self.bipolar[1])
        if width is not None:
            self.side_gain = float(width)
        M, S = mid_side(L, R, self.mid_gain, self.side_gain, to_ms=True)
        L2, R2 = mid_side(M, S, 1.0, 1.0, to_ms=False)
        out = np.stack([L2, R2], axis=1)
        peak = np.max(np.abs(out)) + 1e-12
        return out * (0.89 / peak) if peak > 1.0 else out

    def render_note(self, freq: float, seconds: float = 1.0) -> np.ndarray:
        """Convenience alias used by the production pipeline."""
        return self.render(freq, seconds)


def demo() -> None:
    sr = 44100
    n = 8192
    t = np.arange(n) / sr
    f0 = 220.0

    def harm(y, k, f=f0):
        spec = np.abs(np.fft.rfft(y * np.hanning(len(y))))
        fr = np.fft.rfftfreq(len(y), 1 / sr)
        def at(hz):
            return float(spec[np.argmin(np.abs(fr - hz))])
        return at(k * f) / (at(f) + 1e-12)

    # ---- 1. AS3340 saw: 1/n harmonic series
    saw = as3340_saw(f0 * t)
    h2, h3 = harm(saw, 2), harm(saw, 3)
    print(f"saw-core harmonics: 2nd={h2:.3f} (ideal 0.50), 3rd={h3:.3f} (ideal 0.33), peak={np.abs(saw).max():.2f}")
    assert 0.35 < h2 < 0.65 and 0.2 < h3 < 0.45

    # ---- 2. comparator morph turns triangle into a square: odd harmonics rise
    tri = triangle(f0 * t)
    sq = comparator_morph(tri, amount=1.0, threshold=0.0)
    print(f"tri 3rd={harm(tri,3):.3f} -> comparator 3rd={harm(sq,3):.3f}, "
          f"tri peak={np.abs(tri).max():.2f} comp rms={sq.std():.3f}")
    assert harm(sq, 3) > harm(tri, 3) * 2.0
    assert abs(tri).max() <= 1.001

    # ---- 3. pulse width via comparator threshold: duty cycle moves
    for th, want in ((-0.5, 0.75), (0.0, 0.5), (0.5, 0.25)):
        p = comparator(tri, th, sharpness=40.0)
        duty = float((p > 0).mean())
        print(f"threshold {th:+.1f} -> duty {duty:.3f} (expect {want:.2f})")
        assert abs(duty - want) < 0.03

    # ---- 4. wavefolder: bounded output, harmonic growth, odd-dominant
    clean = np.sin(TAU * f0 * t)
    folded = sine_fold(clean, drive=3.0, stages=3)
    print(f"fold: peak clean={np.abs(clean).max():.2f} folded={np.abs(folded).max():.2f} "
          f"3rd={harm(folded,3):.3f} 2nd={harm(folded,2):.4f}")
    assert np.abs(folded).max() <= 1.0
    assert harm(folded, 3) > 0.05
    assert harm(folded, 2) < harm(folded, 3)

    # ---- 5. bipolar VCA = ring modulation -> sum/difference sidebands
    car = np.sin(TAU * 440 * t)
    mod = np.sin(TAU * 110 * t)
    ring = vca(car, mod, bipolar=True)
    spec = np.abs(np.fft.rfft(ring * np.hanning(n)))
    fr = np.fft.rfftfreq(n, 1 / sr)
    def band_energy(hz, bw=6.0):
        m = (fr >= hz - bw) & (fr <= hz + bw)
        return float(spec[m].sum())
    side = band_energy(330) + band_energy(550)
    carrier = band_energy(440)
    print(f"ring mod: sideband energy={side:.1f}, carrier energy={carrier:.4f} "
          f"(suppressed), unipolar rms={vca(car, mod).std():.3f}")
    assert side > 10.0 * carrier

    # ---- 6. Mid/Side: width 0 = mono, width 2 = wide
    v = OrigamiDuo(sr)
    v.comp_amount = [0.8, 0.4]
    v.fold_drive = [2.2, 1.6]
    stereo0 = v.render(f0, 0.5, width=0.0)
    stereow = v.render(f0, 0.5, width=2.0)

    def lr_corr(x):
        return float(np.corrcoef(x[:, 0], x[:, 1])[0, 1])

    print(f"mid/side: corr width0={lr_corr(stereo0):.4f} width2={lr_corr(stereow):.4f}, "
          f"peak={np.abs(stereow).max():.3f}")
    assert abs(lr_corr(stereo0) - 1.0) < 1e-6
    assert lr_corr(stereow) < 0.99

    # ---- 7. four-output LFO is phase-spread, not four copies
    lfo = v.lfo(2.0, 2 * sr)
    c01 = float(np.corrcoef(lfo[0], lfo[1])[0, 1])
    c02 = float(np.corrcoef(lfo[0], lfo[2])[0, 1])
    print(f"LFO outs corr: 0/1={c01:.3f} 0/2={c02:.3f}")
    assert abs(c01) < 0.05 and abs(c02 + 1.0) < 0.05

    # ---- 8. envelope shape (AD, sustain 0)
    env = v.envelope(int(0.5 * sr), attack=0.01, decay=0.2, sustain=0.0)
    print(f"AD env: early={env[100]:.3f} mid={env[int(0.18*sr)]:.3f} tail={env[-1]:.3f}")
    assert env[100] > env[int(0.18 * sr)] > env[-1]

    # ---- 9. full voice renders finite, bounded audio
    out = v.render(110.0, 0.5)
    print(f"voice: {out.shape} rms={out.std():.4f} peak={np.abs(out).max():.3f} "
          f"finite={bool(np.isfinite(out).all())}")
    assert np.isfinite(out).all() and out.shape == (int(0.5 * sr), 2)
    print("demo OK")


if __name__ == "__main__":
    demo()
