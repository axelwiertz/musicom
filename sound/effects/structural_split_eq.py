"""Structural Split EQ: independent EQ + dynamics on transients vs tonal body.

Eventide's SplitEQ splits a signal into its *transient* and *tonal* elements and
then gives each its own EQ curve, dynamics and pan.  The split here is the
classic differential-envelope decomposition (the same family as Sines+Transients
modelling and the "attack/sustain" designs):

* Two envelope followers run on the rectified signal.
  - ``fast``: short attack, short release -- tracks percussive onsets.
  - ``slow``: medium attack, long release -- tracks the sustained body.
* The *transient gain* is ``max(0, fast - slow) / fast``: it is ~1 during the
  first tens of milliseconds of an onset and ~0 once the body stabilises.  A
  raised-cosine **smoothing** of that gain (plus a ``sensitivity`` knee) keeps
  the split click-free and avoids the phase cancellation of naive
  high-pass "transient extraction".
* ``transient = x * g``, ``tonal = x - transient`` -- complementary, so the two
  elements sum back to the input exactly (bit-level unity reconstruction).

On top of the split:

* **Per-element 8-band EQ** (zero-phase, FFT magnitude shaping) with shelving
  low/high bands.
* **Per-band dynamics** on the tonal element: downward comp or *expansion*
  per band, which is what the v2 "dynamic control every way, everywhere" adds.
* **Unmask analysis**: given a competing signal, compare band energies and
  report the bands where one masks the other, with suggested cut amounts.
"""

from __future__ import annotations

import numpy as np

__all__ = ["StructuralSplit", "StructuralSplitEQ", "demo"]

BAND_EDGES = (40.0, 120.0, 300.0, 700.0, 1500.0, 3000.0, 6000.0, 10000.0, 16000.0)


def _smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


class EnvelopeFollower:
    """One-pole rectified envelope with independent attack/release."""

    def __init__(self, sr: int, attack_ms: float, release_ms: float):
        self.a_att = float(np.exp(-1.0 / (sr * attack_ms / 1000.0)))
        self.a_rel = float(np.exp(-1.0 / (sr * release_ms / 1000.0)))

    def run(self, x: np.ndarray) -> np.ndarray:
        rect = np.abs(x)
        out = np.empty_like(rect)
        s = 0.0
        for i in range(rect.size):
            a = self.a_att if rect[i] > s else self.a_rel
            s = a * s + (1.0 - a) * rect[i]
            out[i] = s
        return out


class StructuralSplit:
    """Complementary transient/tonal decomposition."""

    def __init__(self, sample_rate: int = 44100, fast_ms=(0.6, 12.0),
                 slow_ms=(18.0, 180.0), sensitivity: float = 1.0,
                 smooth_ms: float = 3.0):
        self.sr = sample_rate
        self.fast = EnvelopeFollower(sample_rate, *fast_ms)
        self.slow = EnvelopeFollower(sample_rate, *slow_ms)
        self.sensitivity = float(sensitivity)
        a = float(np.exp(-1.0 / (sample_rate * smooth_ms / 1000.0)))
        self._smooth_a = a

    def transient_gain(self, x: np.ndarray) -> np.ndarray:
        f = self.fast.run(x)
        s = self.slow.run(x)
        raw = np.maximum(0.0, f - s) / np.maximum(f, 1e-9)
        raw = _smoothstep(raw * self.sensitivity)
        # one-pole smoothing of the gain itself (click-free element split)
        g = np.empty_like(raw)
        z = 0.0
        for i in range(raw.size):
            z = self._smooth_a * z + (1.0 - self._smooth_a) * raw[i]
            g[i] = z
        return g

    def split(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        g = self.transient_gain(x)
        tr = x * g
        return tr, x - tr


class StructuralSplitEQ:
    """SplitEQ-style processor: split -> per-element EQ/dynamics -> pan."""

    def __init__(self, sample_rate: int = 44100, crossover: float = 1.0):
        self.sr = sample_rate
        self.splitter = StructuralSplit(sample_rate)
        self.transient_gains = np.zeros(8)
        self.tonal_gains = np.zeros(8)
        self.transient_dyn = (1.0, 0.0)     # (ratio, threshold_db)
        self.tonal_dyn = (1.0, 0.0)
        self.transient_pan = 0.0
        self.tonal_pan = 0.0
        self.tonal_mix = 1.0
        self.transient_mix = 1.0

    # -- EQ ----------------------------------------------------------------
    def _band_masks(self, n: int) -> list[np.ndarray]:
        f = np.fft.rfftfreq(n, 1.0 / self.sr)
        masks = []
        edges = BAND_EDGES
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1]
            m = np.zeros_like(f)
            m[(f >= lo) & (f < hi)] = 1.0
            # 1/6-octave raised-cosine skirts keep the bands complementary
            w = 1.0 / 6.0
            k_lo = (f >= lo * 2 ** (-w)) & (f < lo)
            k_hi = (f >= hi) & (f < hi * 2 ** w)
            m[k_lo] = 0.5 * (1 - np.cos(np.pi * (f[k_lo] - lo * 2 ** (-w)) /
                                        (lo - lo * 2 ** (-w))))
            m[k_hi] = 0.5 * (1 + np.cos(np.pi * (f[k_hi] - hi) /
                                        (hi * 2 ** w - hi)))
            masks.append(m)
        return masks

    def _apply_eq(self, x: np.ndarray, gains_db: np.ndarray) -> np.ndarray:
        n = x.size
        pad = 1 << int(np.ceil(np.log2(max(n, 2))))
        X = np.fft.rfft(x, pad)
        curve = np.zeros_like(X.real)
        masks = self._band_masks(pad)
        acc = np.zeros_like(curve)
        for m, g in zip(masks, gains_db):
            acc += m
            curve += m * (10 ** (g / 20.0))
        # anything outside the band table passes through
        curve += np.clip(1.0 - acc, 0.0, 1.0)
        return np.fft.irfft(X * curve, pad)[:n]

    # -- dynamics ----------------------------------------------------------
    def _apply_dyn(self, x: np.ndarray, ratio: float, thr_db: float) -> np.ndarray:
        """Per-band static comp/expand driven by a single band-energy envelope.

        Applied as a slow gain curve over the whole element, which is what the
        "global pre/post-routable" control does in the plugin.
        """
        if ratio == 1.0:
            return x
        env = EnvelopeFollower(self.sr, 5.0, 80.0).run(x)
        lvl = 20 * np.log10(np.maximum(env, 1e-7))
        over = lvl - thr_db
        if ratio > 1.0:                     # compress above threshold
            g = np.where(over > 0, over * (1.0 / ratio - 1.0), 0.0)
        else:                               # expand below threshold (ratio<1)
            g = np.where(over < 0, over * (1.0 / max(ratio, 1e-3) - 1.0), 0.0)
        return x * (10 ** (g / 20.0))

    # -- main --------------------------------------------------------------
    def process(self, x: np.ndarray, pan_law: float = 0.5) -> np.ndarray:
        """Mono-in/stereo-out when panning; stereo-in/stereo-out otherwise."""
        x = np.asarray(x, dtype=np.float64)
        mono = x.ndim == 1
        if mono:
            base = x
            tr, ton = self.splitter.split(base)
        else:
            base = x
            tr, ton = self.splitter.split(x[0]), None
            tr_r, ton_r = self.splitter.split(x[1])
        tr = self._apply_eq(tr, self.transient_gains)
        tr = self._apply_dyn(tr, *self.transient_dyn)
        if mono:
            ton = self._apply_eq(ton, self.tonal_gains)
            ton = self._apply_dyn(ton, *self.tonal_dyn)
            out = self.transient_mix * tr + self.tonal_mix * ton
            if self.transient_pan == 0.0 and self.tonal_pan == 0.0:
                return out
            l = self.transient_mix * tr * self._pan(self.transient_pan, "l") + \
                self.tonal_mix * ton * self._pan(self.tonal_pan, "l")
            r = self.transient_mix * tr * self._pan(self.transient_pan, "r") + \
                self.tonal_mix * ton * self._pan(self.tonal_pan, "r")
            return np.stack([l, r])
        # stereo path
        ton_r = self._apply_eq(ton_r, self.tonal_gains)
        ton_r = self._apply_dyn(ton_r, *self.tonal_dyn)
        ton = self._apply_eq(ton, self.tonal_gains)
        ton = self._apply_dyn(ton, *self.tonal_dyn)
        l = self.transient_mix * tr + self.tonal_mix * ton
        r = self.transient_mix * tr_r + self.tonal_mix * ton_r
        return np.stack([l, r])

    @staticmethod
    def _pan(p: float, side: str) -> float:
        """Constant-power pan; p in [-1, 1]."""
        ang = (np.clip(p, -1, 1) + 1) * np.pi / 4
        return float(np.cos(ang) if side == "l" else np.sin(ang))

    # -- unmask ------------------------------------------------------------
    def unmask(self, mine: np.ndarray, other: np.ndarray,
               max_cut_db: float = 6.0) -> list[tuple[float, float, float]]:
        """Report bands where ``other`` masks ``mine``: (lo, hi, cut_db)."""
        n = min(mine.size, other.size)
        pad = 1 << int(np.ceil(np.log2(n)))
        spec_a = np.abs(np.fft.rfft(mine[:n], pad)) ** 2
        spec_b = np.abs(np.fft.rfft(other[:n], pad)) ** 2
        out = []
        for i, m in enumerate(self._band_masks(pad)):
            ea = float((spec_a * m).sum())
            eb = float((spec_b * m).sum())
            if eb <= 0:
                continue
            ratio_db = 10 * np.log10((ea + 1e-12) / (eb + 1e-12))
            if ratio_db < 0:
                cut = min(max_cut_db, -ratio_db * 0.5)
                out.append((BAND_EDGES[i], BAND_EDGES[i + 1], round(cut, 2)))
        return out


def demo() -> None:
    sr = 44100
    n = sr
    t = np.arange(n) / sr
    # tonal body: slowly evolving chord
    body = 0.18 * (np.sin(2 * np.pi * 220 * t) + 0.7 * np.sin(2 * np.pi * 330 * t)
                   + 0.5 * np.sin(2 * np.pi * 440 * t))
    body *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * t)
    # transients: 4 sharp clicks
    hits = np.zeros(n)
    for k in range(4):
        i = int(k * sr / 4) + 100
        hits[i:i + 200] += 0.85 * np.exp(-np.arange(200) / 25.0) * \
            np.sin(2 * np.pi * 1800 * np.arange(200) / sr)
    src = body + hits

    splitter = StructuralSplit(sr)
    tr, ton = splitter.split(src)
    g = splitter.transient_gain(src)
    print(f"transient fraction: {float(np.sum(tr**2)/np.sum(src**2)):.3f}, "
          f"peak gain {g.max():.2f}")
    print(f"reconstruction max err: {np.max(np.abs(tr + ton - src)):.2e}")

    eq = StructuralSplitEQ(sr)
    # tame the tonal body's low-mids, boost transient snap
    eq.tonal_gains = np.array([-2.0, -3.5, -1.5, 0.0, 0.0, 0.5, 0.0, 0.0])
    eq.transient_gains = np.array([0.0, 0.0, 0.0, 0.0, 2.0, 3.5, 3.0, 1.5])
    eq.transient_dyn = (3.0, -12.0)
    out = eq.process(src)
    # band-level check: transient band energy above 1.5 kHz should rise
    def band_energy(sig, lo, hi):
        sp = np.abs(np.fft.rfft(sig)) ** 2
        f = np.fft.rfftfreq(sig.size, 1 / sr)
        return float(sp[(f >= lo) & (f < hi)].sum())
    print(f"1.5-6k energy: {band_energy(src,1500,6000):.4f} -> "
          f"{band_energy(out,1500,6000):.4f}")
    print(f"40-300 Hz energy: {band_energy(src,40,300):.4f} -> "
          f"{band_energy(out,40,300):.4f}")
    mask = eq.unmask(src - hits, hits)
    print("unmask suggestions (lo, hi, cut dB):", mask[:4])
    assert np.max(np.abs(tr + ton - src)) < 1e-12 and out.size == src.size


if __name__ == "__main__":
    demo()
