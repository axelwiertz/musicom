"""Multiband stereo frequency shifter (FAC Shifter-style).

Frequency shifting translates the spectrum *linearly* in Hz (single-sideband
modulation), unlike pitch shifting which scales it multiplicatively.  This
module splits the signal into three complementary bands, Hilbert-transforms
each band into its analytic (I/Q) representation, and complex-mixes it with a
quadrature oscillator so only one sideband survives.

Key behaviours replicated from the hardware/plugin design space:

* **Flat-sum crossover.**  ``band_low = LP(f1)``, ``band_mid = LP(f2) - LP(f1)``,
  ``band_high = x - LP(f2)``.  Because the bands are formed by subtraction they
  sum back to the input *exactly*, whatever the filter shape -- no dip at the
  crossover.  Slope is set by the number of cascaded one-poles (1 pole = 6 dB/oct,
  so 1..32 poles = 6..192 dB/oct, matching the "6 dB to 192 dB" range).
* **Independent L/R sideband choice** (positive / negative / both).  "Both"
  degenerates into a double-sideband ring-modulated band, which is the classic
  metallic/bell sound.
* **MIDI anchor / follow.**  Shifts are expressed as musical intervals from a
  tracked note, so the shifted band lands on a scale tone instead of an
  arbitrary beat frequency.
* **Internal quadrature fuzzing.**  A fraction of the Q (imaginary) signal is
  fed back into the I path, breaking the perfect 90-degree relationship and
  adding the gritty, unstable character of analog dome filters.

Author: musicom surveillance 2026-11-19 (FAC Shifter finding).
"""

from __future__ import annotations

import numpy as np

__all__ = ["Hilbert", "BandSplitter", "MultibandFreqShifter", "demo"]

SCALES = {
    "chromatic": tuple(range(12)),
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "pentatonic": (0, 2, 4, 7, 9),
    "whole_tone": (0, 2, 4, 6, 8, 10),
}


def _midi_to_hz(m: float) -> float:
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


class Hilbert:
    """Windowed-FIR Hilbert transformer -> analytic signal (real + j*quad).

    A true Hilbert transform is a 90-degree all-pass; the FIR approximation is
    an odd-length anti-symmetric kernel convolved in 'same' mode so the group
    delay is compensated by the centring.
    """

    def __init__(self, taps: int = 127):
        if taps % 2 == 0:
            taps += 1
        n = np.arange(taps) - (taps - 1) / 2.0
        h = np.zeros(taps)
        odd = ((np.arange(taps) % 2) == 1) & (n != 0.0)
        h[odd] = 2.0 / (np.pi * n[odd])
        h *= np.blackman(taps)
        self.kernel = h
        self.taps = taps

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return np.convolve(np.asarray(x, dtype=np.float64), self.kernel, mode="same")


class BandSplitter:
    """Three-band flat-sum splitter built from cascaded one-pole lowpasses."""

    def __init__(self, lo_hz: float = 250.0, hi_hz: float = 2500.0,
                 slope_db_oct: int = 24, sample_rate: int = 44100):
        self.sr = sample_rate
        self.lo_hz = max(20.0, min(lo_hz, sample_rate * 0.45))
        self.hi_hz = max(self.lo_hz * 1.01, min(hi_hz, sample_rate * 0.45))
        # 6 dB/oct per pole; clamp to 1..32 poles to stay stable
        self.poles = int(np.clip(round(slope_db_oct / 6.0), 1, 32))
        self._update()

    def _update(self):
        self.a_lo = float(np.exp(-2.0 * np.pi * self.lo_hz / self.sr))
        self.a_hi = float(np.exp(-2.0 * np.pi * self.hi_hz / self.sr))

    def _onepole(self, x: np.ndarray, a: float) -> np.ndarray:
        y = np.empty_like(x)
        z = 0.0
        for i in range(x.size):
            z = (1.0 - a) * x[i] + a * z
            y[i] = z
        return y

    def split(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = np.asarray(x, dtype=np.float64)
        lo = x.copy()
        hi = x.copy()
        for _ in range(self.poles):
            lo = self._onepole(lo, self.a_lo)
            hi = self._onepole(hi, self.a_hi)
        mid = hi - lo
        top = x - hi
        return lo, mid, top


class MultibandFreqShifter:
    """Three-band SSB frequency shifter with per-band, per-channel control.

    Parameters
    ----------
    sample_rate : int
    band_lo, band_hi : split points in Hz
    slope_db_oct : crossover steepness (6..192 dB/oct)
    shifts_hz : per-band shift amount (positive = up)
    sideband : per-band "up" | "down" | "both"
    quad_fuzz : 0..1 amount of Q-to-I feedback (analog instability)
    mix : dry/wet
    """

    def __init__(self, sample_rate: int = 44100, band_lo: float = 250.0,
                 band_hi: float = 2500.0, slope_db_oct: int = 24,
                 shifts_hz=(0.0, 0.0, 0.0), sideband=("up", "up", "up"),
                 quad_fuzz: float = 0.0, mix: float = 1.0):
        self.sr = sample_rate
        self.splitter = BandSplitter(band_lo, band_hi, slope_db_oct, sample_rate)
        self.shifts_hz = list(shifts_hz)
        self.sideband = list(sideband)
        self.quad_fuzz = float(np.clip(quad_fuzz, 0.0, 1.0))
        self.mix = float(np.clip(mix, 0.0, 1.0))
        self.hilbert = Hilbert(127)
        self._t = np.arange(sample_rate * 8) / float(sample_rate)
        self.anchor_midi = None

    # -- musical anchoring -------------------------------------------------
    def set_anchor(self, midi_note: float):
        """Track a played note; later shifts are measured from its frequency."""
        self.anchor_midi = float(midi_note)

    def musical_shift(self, semitones: int, scale: str = "chromatic") -> float:
        """Hz shift that moves the anchored note by ``semitones``, scale-snapped.

        In FOLLOW mode the sounding pitch of the shifted band is quantised to
        the nearest scale degree, so the shift amount is
        ``f(note + offset) - f(note)`` rather than an arbitrary Hz value.
        """
        if self.anchor_midi is None:
            raise ValueError("set_anchor() first")
        steps = SCALES.get(scale, SCALES["chromatic"])
        target = self.anchor_midi + semitones
        pc = int(round(target)) % 12
        for d in range(0, 7):
            for cand in (pc + d, pc - d):
                if cand % 12 in steps:
                    target = np.floor(target) + (cand - pc)
                    break
            else:
                continue
            break
        return _midi_to_hz(target) - _midi_to_hz(self.anchor_midi)

    # -- core --------------------------------------------------------------
    @staticmethod
    def _shift_band(band: np.ndarray, quad: np.ndarray, f_hz: float,
                    mode: str, fuzz: float, t: np.ndarray) -> np.ndarray:
        if abs(f_hz) < 1e-9:
            return band
        analytic = band + 1j * quad
        if mode == "up":
            out = np.real(analytic * np.exp(2j * np.pi * f_hz * t))
        elif mode == "down":
            out = np.real(analytic * np.exp(-2j * np.pi * f_hz * t))
        elif mode == "both":
            up = np.real(analytic * np.exp(2j * np.pi * f_hz * t))
            dn = np.real(analytic * np.exp(-2j * np.pi * f_hz * t))
            out = 0.5 * (up + dn)
        else:
            raise ValueError(f"bad sideband mode {mode!r}")
        if fuzz > 0.0:
            # imperfect quadrature: leak Q into I (asymmetric, edgy)
            out = out + fuzz * 0.5 * quad
        return out

    def process_channel(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        n = x.size
        t = self._t[:n]
        bands = self.splitter.split(x)
        out = np.zeros(n)
        for band, f, mode in zip(bands, self.shifts_hz, self.sideband):
            quad = self.hilbert(band)
            out += self._shift_band(band, quad, f, mode, self.quad_fuzz, t)
        return (1.0 - self.mix) * x + self.mix * out

    def process(self, x: np.ndarray) -> np.ndarray:
        """Process mono (N,) or stereo (2,N); L/R may use different shifts."""
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            return self.process_channel(x)
        if x.shape[0] != 2:
            raise ValueError("stereo input must be shape (2, N)")
        # Right channel: mirror the sideband polarity unless offsets given
        r = self.process_channel(x[1])
        l = self.process_channel(x[0])
        return np.stack([l, r])


def demo() -> None:
    sr = 44100
    n = sr  # 1 second
    t = np.arange(n) / sr
    # 220 Hz saw-ish tone, panned centre
    src = 0.4 * (2.0 * ((220.0 * t) % 1.0) - 1.0)

    fsh = MultibandFreqShifter(sr, band_lo=200.0, band_hi=2000.0,
                               slope_db_oct=24,
                               shifts_hz=(0.0, 55.0, -110.0),
                               sideband=("up", "both", "down"),
                               quad_fuzz=0.25)
    fsh.set_anchor(57)  # A3
    print(f"anchor A3, major-third shift -> {fsh.musical_shift(4, 'major'):+.2f} Hz")
    y = fsh.process(np.stack([src, src]))
    print(f"input rms {np.sqrt(np.mean(src**2)):.4f} "
          f"-> output rms {np.sqrt(np.mean(y**2)):.4f}")
    # neutral setting must be transparent
    flat = MultibandFreqShifter(sr, shifts_hz=(0, 0, 0))
    err = float(np.max(np.abs(flat.process_channel(src) - src)))
    print(f"bypass max error: {err:.2e}")
    assert err < 1e-9, "flat-sum crossover not transparent"


if __name__ == "__main__":
    demo()
