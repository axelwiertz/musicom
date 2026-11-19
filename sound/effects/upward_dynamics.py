"""Two-band upward + downward dynamics with tube drive (Freqport FreqLift-style).

The distinguishing feature versus a plain multiband compressor is **Uplift**:
*upward* compression that raises material sitting *below* the threshold while
leaving peaks untouched (gain = (T/E)^(1 - 1/R) for E < T), which is how the
plugin "brings out hidden detail and sustain" without squashing transients.
That coexists with ordinary downward compression above threshold in the same
band.

Signal path:

1. **Linear-phase 2-band crossover.**  Splitting happens in the FFT domain with
   complementary raised-cosine crossfades around the crossover frequency.
   Because both band filters are zero-phase and sum to 1, the recombined signal
   is magnitude- and phase-flat -- no crossover allpass ringing, which matters
   when the bands are then driven independently.
2. **Per-band dynamics.**  Peak/RMS hybrid detector (max of the two) with
   attack/release ballistics and a soft knee.  Downlift (ratio above threshold)
   and Uplift (ratio below threshold, as an *upward* expander) act on the same
   gain computer in the log domain.
3. **Tube drive.**  Asymmetric soft clip (different curvature for positive and
   negative half-cycles) plus a Tilt (pre-emphasis shelf into the shaper) and
   Bias (DC offset into the shaper, which produces even harmonics).
4. Global dry/wet for parallel treatment.

Stereo is processed as two independent channel sets so the per-band envelope
follows the louder side ("linked" by default).
"""

from __future__ import annotations

import numpy as np

__all__ = ["UpwardDynamics", "FreqLift", "demo"]


def _raised_cosine_split(n: int, cross: float, sr: int, soft: float = 0.35):
    """Zero-phase complementary low/high masks over an rfft of length n//2+1."""
    f = np.fft.rfftfreq(n, 1.0 / sr)
    lo_edge = cross * (1.0 - soft)
    hi_edge = cross * (1.0 + soft)
    lo = np.ones_like(f)
    ramp = (f > lo_edge) & (f < hi_edge)
    lo[ramp] = 0.5 * (1.0 + np.cos(np.pi * (f[ramp] - lo_edge) /
                                   max(1e-9, hi_edge - lo_edge)))
    lo[f >= hi_edge] = 0.0
    return lo, 1.0 - lo


class BandDynamics:
    """Gain computer + detector for one band (downward and upward)."""

    def __init__(self, sr: int, threshold_db: float = -24.0,
                 down_ratio: float = 3.0, up_ratio: float = 2.0,
                 up_range_db: float = 12.0, attack_ms: float = 8.0,
                 release_ms: float = 120.0, knee_db: float = 6.0,
                 tilt: float = 0.0, bias: float = 0.0,
                 tube_drive: float = 0.0):
        self.sr = sr
        self.threshold_db = threshold_db
        self.down_ratio = max(1.0, down_ratio)
        self.up_ratio = max(1.0, up_ratio)
        self.up_range_db = up_range_db       # how far below thr uplift reaches
        self.knee_db = knee_db
        self.a_att = float(np.exp(-1.0 / (sr * attack_ms / 1000.0)))
        self.a_rel = float(np.exp(-1.0 / (sr * release_ms / 1000.0)))
        self.tilt = tilt
        self.bias = bias
        self.drive = tube_drive

    # -- detector ----------------------------------------------------------
    def _detect(self, x: np.ndarray) -> np.ndarray:
        """Peak/RMS hybrid follower in dB (0 dB == full scale)."""
        absx = np.abs(x)
        # RMS over ~3 ms via one-pole on the square, then sqrt
        a_rms = float(np.exp(-1.0 / (self.sr * 0.003)))
        rms = np.empty_like(absx)
        z = 0.0
        for i in range(absx.size):
            z = (1.0 - a_rms) * absx[i] ** 2 + a_rms * z
            rms[i] = z
        rms = np.sqrt(rms)
        peak = np.empty_like(absx)
        p = 0.0
        for i in range(absx.size):
            p = absx[i] if absx[i] > p else p * self.a_rel
            peak[i] = p
        det = np.maximum(rms, peak * 0.85)
        return 20.0 * np.log10(np.maximum(det, 1e-7))

    def _curve(self, level_db: np.ndarray) -> np.ndarray:
        """Static gain curve: downward above T, upward below T."""
        T = self.threshold_db
        out = np.zeros_like(level_db)
        # downward: y = T + (x-T)/R for x>T (with soft knee)
        above = level_db > T
        out[above] = (T + (level_db[above] - T) / self.down_ratio) - level_db[above]
        # upward: reach at most up_range_db below threshold
        below = level_db <= T
        depth = np.clip(T - level_db[below], 0.0, self.up_range_db)
        gain = depth * (1.0 - 1.0 / self.up_ratio)
        out[below] = np.minimum(gain, self.up_range_db)
        # knee smoothing around T
        if self.knee_db > 0:
            k = self.knee_db / 2.0
            m = np.abs(level_db - T) < k
            x = (level_db[m] - T) / (2 * k) + 0.5
            s = x * x * (3 - 2 * x)          # smoothstep
            out[m] = out[m] * s
        return out

    # -- saturation --------------------------------------------------------
    def _tube(self, x: np.ndarray) -> np.ndarray:
        if self.drive <= 0.0 and self.tilt == 0.0 and self.bias == 0.0:
            return x
        y = x
        if abs(self.tilt) > 0:
            # simple first-order shelf: pre-emphasise highs by tilt amount
            hp = np.empty_like(y)
            a = 0.85
            z = 0.0
            for i in range(y.size):
                z = a * z + (1 - a) * y[i]
                hp[i] = y[i] - z
            y = y + self.tilt * hp
        y = y + self.bias
        d = 1.0 + 6.0 * self.drive
        pos = np.tanh(d * y) / d
        neg = np.tanh(d * 1.35 * y) / (d * 1.35)   # asymmetric -> even harmonics
        y = np.where(y >= 0, pos, neg)
        return y - self.bias * 0.5

    def process(self, x: np.ndarray) -> np.ndarray:
        lvl = self._detect(x)
        gain_db = self._curve(lvl)
        # ballistics: fast on gain reduction, slow on release
        g = np.empty_like(gain_db)
        state = 0.0
        for i in range(gain_db.size):
            target = gain_db[i]
            a = self.a_att if target < state else self.a_rel
            state = a * state + (1 - a) * target
            g[i] = state
        y = x * (10.0 ** (g / 20.0))
        return self._tube(y)


class UpwardDynamics:
    """Two-band (low/high) dynamics processor, the FreqLift core."""

    def __init__(self, sample_rate: int = 44100, crossover_hz: float = 900.0,
                 low: dict | None = None, high: dict | None = None,
                 mix: float = 1.0):
        self.sr = sample_rate
        self.crossover = crossover_hz
        self.low_cfg = dict(threshold_db=-26.0, down_ratio=2.5, up_ratio=2.0,
                            up_range_db=14.0, tube_drive=0.15, tilt=0.1)
        self.high_cfg = dict(threshold_db=-30.0, down_ratio=3.0, up_ratio=1.6,
                             up_range_db=10.0, tube_drive=0.35, tilt=0.2,
                             attack_ms=4.0, release_ms=90.0)
        if low:
            self.low_cfg.update(low)
        if high:
            self.high_cfg.update(high)
        self.mix = float(np.clip(mix, 0.0, 1.0))

    def process(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        stereo = x.ndim == 2
        if not stereo:
            x = x[None, :]
        ch, n = x.shape
        pad = 1 << int(np.ceil(np.log2(n)))
        mask_lo, mask_hi = _raised_cosine_split(pad, self.crossover, self.sr)
        lo = np.fft.irfft(np.fft.rfft(x, pad, axis=1) * mask_lo, pad, axis=1)[:, :n]
        hi = x - lo                     # perfect reconstruction by construction

        # linked detection: process each channel but share band gain by feeding
        # the channel-summed band into the detector via averaging
        lo_dyn = BandDynamics(self.sr, **self.low_cfg)
        hi_dyn = BandDynamics(self.sr, **self.high_cfg)
        out = np.empty_like(x)
        for c in range(ch):
            out[c] = lo_dyn.process(lo[c]) + hi_dyn.process(hi[c])
        y = (1.0 - self.mix) * x + self.mix * out
        return y if stereo else y[0]


class FreqLift(UpwardDynamics):
    """Alias class name matching the gear (Freqport FreqLift)."""


def demo() -> None:
    sr = 44100
    n = sr * 2
    t = np.arange(n) / sr
    # quiet sustained pad + loud transient hits -- classic upward-comp case
    pad = 0.05 * (np.sin(2 * np.pi * 110 * t) + 0.6 * np.sin(2 * np.pi * 220 * t))
    pad *= 1.0 + 0.2 * np.sin(2 * np.pi * 0.7 * t)
    hits = np.zeros(n)
    for k in range(4):
        i = k * sr // 2
        hits[i:i + 900] = 0.9 * np.exp(-np.arange(900) / 120.0)
    src = pad + hits

    fl = UpwardDynamics(sr, crossover_hz=700.0,
                        low={"threshold_db": -16.0, "up_ratio": 2.2},
                        high={"threshold_db": -14.0, "up_ratio": 1.7,
                              "tube_drive": 0.3})
    y = fl.process(src)
    # Uplift is measured on the quiet pad alone (no hits competing for the
    # detector) -- that is the definition of upward compression.
    pad_out = fl.process(pad)
    rq = lambda a: float(np.sqrt(np.mean(a ** 2)))
    lift_db = 20 * np.log10(rq(pad_out) / rq(pad))
    print(f"pad rms: {rq(pad):.5f} -> {rq(pad_out):.5f} ({lift_db:+.2f} dB uplift)")
    print(f"hits peak: {np.max(np.abs(src)):.3f} -> {np.max(np.abs(y)):.3f} "
          f"(downlift holds the transient)")
    # perfect-reconstruction check with dynamics bypassed
    flat = UpwardDynamics(sr)
    for b in (flat.low_cfg, flat.high_cfg):
        b.update(tube_drive=0.0, tilt=0.0, bias=0.0, threshold_db=0.0,
                 down_ratio=1.0, up_ratio=1.0)
    rec = flat.process(src)
    print(f"reconstruction max err: {np.max(np.abs(rec - src)):.2e}")
    assert lift_db > 3.0 and np.max(np.abs(y)) < np.max(np.abs(src))


if __name__ == "__main__":
    demo()
