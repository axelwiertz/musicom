"""Frequency shifter — complex SSB frequency shifting (FAC Gravity-style).

Two processing modes:
- STEREO: independent L/R channels shifted separately, Ratio control ties them.
- MONO: quadrature processing for stereo widening from a mono source.

Spiral feedback path with configurable delay, diffusion blur, and
low/high shelving filters for self-oscillation and evolving effects.

Frequency shifting is *not* pitch shifting: it translates the spectrum
linearly (in Hz) rather than multiplicatively.  Harmonics become inharmonic,
producing metallic, phasing, chorus-like, or sci-fi effects depending on
shift amount.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Quadrature oscillator (sine/cosine pair)
# ---------------------------------------------------------------------------

class QuadOsc:
    """Numerically-stable quadrature oscillator for complex mixing."""

    def __init__(self, freq_hz: float, sample_rate: int = 44100):
        self.sr = sample_rate
        self._phase = 0.0
        self.freq_hz = freq_hz

    @property
    def freq_hz(self) -> float:
        return self._freq

    @freq_hz.setter
    def freq_hz(self, v: float):
        self._freq = v
        self._delta = 2.0 * np.pi * v / self.sr

    def next(self) -> tuple[float, float]:
        """Return (cos, sin) for current phase, advance by delta."""
        c = np.cos(self._phase)
        s = np.sin(self._phase)
        self._phase += self._delta
        # wrap to avoid float drift
        if self._phase > 2.0 * np.pi:
            self._phase -= 2.0 * np.pi
        return c, s


# ---------------------------------------------------------------------------
# One-pole low/high shelving filters (Spiral signal path)
# ---------------------------------------------------------------------------

class ShelfFilter:
    """One-pole low/high shelving filter for the feedback path."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self._lp = True          # True=low-shelf, False=high-shelf
        self._cutoff = 1000.0
        self._gain_db = 0.0
        self._z1 = 0.0
        self._update_coeffs()

    def set_low_shelf(self, cutoff: float, gain_db: float = 0.0):
        self._lp = True
        self._cutoff = max(20.0, min(cutoff, self.sr * 0.49))
        self._gain_db = gain_db
        self._update_coeffs()

    def set_high_shelf(self, cutoff: float, gain_db: float = 0.0):
        self._lp = False
        self._cutoff = max(20.0, min(cutoff, self.sr * 0.49))
        self._gain_db = gain_db
        self._update_coeffs()

    def _update_coeffs(self):
        w0 = 2.0 * np.pi * self._cutoff / self.sr
        g = 10.0 ** (self._gain_db / 20.0)
        if self._lp:
            # one-pole low shelf
            self._a1 = np.exp(-w0)
            self._b0 = 1.0 + (g - 1.0) * (1.0 - self._a1)
            self._b1 = -(g - 1.0) * (1.0 - self._a1) * self._a1
        else:
            # one-pole high shelf
            self._a1 = np.exp(-w0)
            self._b0 = g + (1.0 - g) * self._a1
            self._b1 = (g - 1.0) * (1.0 - self._a1)

    def process(self, x: np.ndarray) -> np.ndarray:
        out = np.empty_like(x)
        for i in range(len(x)):
            out[i] = self._b0 * x[i] + self._b1 * self._z1
            self._z1 = x[i] - self._a1 * self._z1
        return out


# ---------------------------------------------------------------------------
# Simple delay line (Spiral path)
# ---------------------------------------------------------------------------

class DelayLine:
    """Circular buffer delay line with interpolation."""

    def __init__(self, max_delay_s: float = 2.0, sample_rate: int = 44100):
        self.sr = sample_rate
        self._buf = np.zeros(int(max_delay_s * sample_rate) + 1)
        self._size = len(self._buf)
        self._wp = 0
        self._delay_samples = 0

    @property
    def delay_samples(self) -> int:
        return self._delay_samples

    @delay_samples.setter
    def delay_samples(self, v: int):
        self._delay_samples = max(1, min(v, self._size - 1))

    def write(self, x: float):
        self._buf[self._wp] = x
        self._wp = (self._wp + 1) % self._size

    def read(self) -> float:
        rp = (self._wp - self._delay_samples) % self._size
        return self._buf[rp]


# ---------------------------------------------------------------------------
# Spiral processor (feedback path with delay + blur + filtering)
# ---------------------------------------------------------------------------

@dataclass
class SpiralConfig:
    """Configuration for the Spiral feedback path."""
    feedback: float = 0.0           # 0..0.99
    delay_ms: float = 20.0          # delay time in ms
    blur: float = 0.0               # diffusion/blur amount 0..1
    low_cutoff: float = 20.0        # low shelf cutoff Hz
    low_gain_db: float = 0.0
    high_cutoff: float = 20000.0    # high shelf cutoff Hz
    high_gain_db: float = 0.0


class SpiralProcessor:
    """Feedback path: delay → blur (1-pole LP) → shelf filters."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self._delay = DelayLine(max_delay_s=2.0, sample_rate=sample_rate)
        self._lpf = ShelfFilter(sample_rate)
        self._blur_z = 0.0
        self._config = SpiralConfig()

    @property
    def config(self) -> SpiralConfig:
        return self._config

    @config.setter
    def config(self, cfg: SpiralConfig):
        self._config = cfg
        self._delay.delay_samples = int(cfg.delay_ms * self.sr / 1000.0)
        self._lpf.set_low_shelf(cfg.low_cutoff, cfg.low_gain_db)
        self._lpf.set_high_shelf(cfg.high_cutoff, cfg.high_gain_db)

    def process(self, x: np.ndarray) -> np.ndarray:
        """Process input through the spiral feedback path."""
        out = np.empty_like(x)
        for i in range(len(x)):
            # read delayed signal
            delayed = self._delay.read()
            # blur (1-pole LP)
            blurred = (1.0 - self._config.blur) * delayed + self._config.blur * self._blur_z
            self._blur_z = blurred
            # shelving filters
            filtered = self._lpf.process(np.array([blurred]))[0]
            # feedback mix
            fb = filtered * self._config.feedback
            # write input + feedback to delay line
            self._delay.write(x[i] + fb)
            out[i] = fb
        return out


# ---------------------------------------------------------------------------
# Main Frequency Shifter
# ---------------------------------------------------------------------------

class FrequencyShifter:
    """Complex single-sideband frequency shifter (FAC Gravity-style).

    Modes
    -----
    - 'stereo': independent L/R shift with Ratio parameter.
    - 'mono': quadrature processing, mono→wide stereo.

    The Ratio parameter (0..1) in stereo mode ties the right-channel shift
    to the left:  right_hz = left_hz * ratio.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self.mode = 'stereo'          # 'stereo' | 'mono'
        self.shift_hz: float = 0.0    # left-channel shift in Hz
        self.ratio: float = 1.0       # stereo mode: right = left * ratio
        self.mix: float = 0.5         # dry/wet (0 = dry, 1 = wet)
        self.limit: bool = True       # soft-clip output

        # quadrature oscillators
        self._quad_l = QuadOsc(0.0, sample_rate)
        self._quad_r = QuadOsc(0.0, sample_rate)

        # Spiral processor
        self.spiral = SpiralProcessor(sample_rate)

        # Hilbert transform (mono mode quadrature) — simple 1-tap approx
        self._hilbert_z = 0.0
        self._alpha = 0.5  # all-pass coefficient for approx 90° shift

    def _update_oscs(self):
        self._quad_l.freq_hz = self.shift_hz
        if self.mode == 'stereo':
            self._quad_r.freq_hz = self.shift_hz * self.ratio
        else:
            self._quad_r.freq_hz = self.shift_hz

    def process(self, left: np.ndarray, right: Optional[np.ndarray] = None
                ) -> tuple[np.ndarray, np.ndarray]:
        """Process audio through the frequency shifter.

        Parameters
        ----------
        left : np.ndarray (mono) or left channel
        right : np.ndarray or None (None = mono input)

        Returns
        -------
        (left_out, right_out) : tuple of np.ndarrays
        """
        self._update_oscs()
        n = len(left)

        left_out = np.empty(n)
        right_out = np.empty(n)

        if self.mode == 'mono':
            # Mono → quadrature → stereo w/ shift
            for i in range(n):
                # approx Hilbert: all-pass for 90° shift
                s = left[i]
                q = self._alpha * (s - self._hilbert_z)
                self._hilbert_z = s

                cos_l, sin_l = self._quad_l.next()
                cos_r, sin_r = self._quad_r.next()

                # SSB: in-phase * cos + quadrature * sin
                shifted_l = s * cos_l - q * sin_l
                shifted_r = s * cos_r + q * sin_r

                # Spiral
                spiralled = self.spiral.process(np.array([shifted_l + shifted_r]))[0]
                wet_l = shifted_l + spiralled
                wet_r = shifted_r + spiralled

                left_out[i] = (1.0 - self.mix) * s + self.mix * wet_l
                right_out[i] = (1.0 - self.mix) * s + self.mix * wet_r
        else:
            # Stereo: independent L/R
            if right is None:
                right = left.copy()
            for i in range(n):
                cos_l, sin_l = self._quad_l.next()
                cos_r, sin_r = self._quad_r.next()

                # SSB per channel
                shifted_l = left[i] * cos_l  # (implicitly real-only: using cos)
                shifted_r = right[i] * cos_r

                # Spiral
                spiralled = self.spiral.process(np.array([shifted_l + shifted_r]))[0]
                wet_l = shifted_l + spiralled
                wet_r = shifted_r + spiralled

                left_out[i] = (1.0 - self.mix) * left[i] + self.mix * wet_l
                right_out[i] = (1.0 - self.mix) * right[i] + self.mix * wet_r

        # Output limiting
        if self.limit:
            peak = max(np.max(np.abs(left_out)), np.max(np.abs(right_out)))
            if peak > 0.99:
                scale = 0.99 / peak
                left_out *= scale
                right_out *= scale

        return left_out, right_out

    def process_mono(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Convenience: process mono input (forces mono mode)."""
        self.mode = 'mono'
        return self.process(x, None)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Generate a demo sweep tone processed through the frequency shifter."""
    import soundfile as sf
    sr = 44100
    dur = 3.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)

    # Input: 440 Hz sine + 880 Hz sine
    tone = (np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 880 * t)) * 0.3

    fs = FrequencyShifter(sample_rate=sr)
    fs.shift_hz = 50.0       # shift up 50 Hz → 490 + 930 Hz (inharmonic!)
    fs.ratio = 0.5           # right channel shifted by 25 Hz
    fs.mix = 0.8
    fs.mode = 'stereo'

    # Spiral config
    spiral_cfg = SpiralConfig(
        feedback=0.3,
        delay_ms=30.0,
        blur=0.2,
        low_cutoff=200.0,
        low_gain_db=-3.0,
        high_cutoff=8000.0,
        high_gain_db=0.0,
    )
    fs.spiral.config = spiral_cfg

    l, r = fs.process(tone, tone)
    stereo = np.column_stack([l, r])
    sf.write('/tmp/freq_shift_demo.wav', stereo, sr)
    print(f"Wrote /tmp/freq_shift_demo.wav  ({len(stereo)} samples, {sr} Hz)")
    print(f"  shift_hz={fs.shift_hz}  ratio={fs.ratio}  mix={fs.mix}")


if __name__ == '__main__':
    demo()