"""Room reverb with early reflections + slap + diffuse tail — Hot Shower
Audio bathROOMs-style.

Replicable logic from the bathROOMs reverb (Synthtopia 2026-08-23): a
reverb engine modeling small reflective spaces (bathrooms) with controls
for perceived distance (Position), reflective character (Surface),
parallel-wall slap reflections with an independent feedback loop (Slap),
balance between discrete reflections and diffuse reverb (Wash), and tonal
character (Temp, brighter <-> warmer).

What is replicated here:
- Early reflections: a tapped delay line whose tap pattern models a small
  room (image-source approximation); Position shifts tap times (farther =
  later + brighter + wider), Surface scales tap gains.
- Slap echo: a single long feedback delay (parallel-wall path) with its
  own feedback amount — the classic slap-back loop.
- Diffuse tail: Schroeder-style comb + allpass network fed by the washed
  early-reflection bus.
- Wash: crossfade between discrete reflections and the diffuse tail.
- Temp: one-pole lowpass/highpass tilt of the wet signal (brighter vs
  warmer).

Not replicated: the five modeled bathroom impulse responses (Lavender,
Porcelain, Cove, Greenhouse, Baldosa), sidechain ducker, A/B UI.

Usage:
    from sound.effects.room_reverb import RoomReverb

    rev = RoomReverb(sample_rate=44100, room_size=0.5)
    wet = rev.process(audio, position=0.4, surface=0.6, slap=0.3,
                      wash=0.5, temp=0.5, mix=0.35)
"""

from typing import Optional

import numpy as np

__all__ = ["RoomReverb", "comb", "allpass"]


def comb(x: np.ndarray, delay: int, feedback: float) -> np.ndarray:
    """Schroeder comb filter (feedback delay line)."""
    y = np.zeros_like(x)
    for i in range(len(x)):
        j = i - delay
        y[i] = x[i] + feedback * (y[j] if j >= 0 else 0.0)
    return y


def allpass(x: np.ndarray, delay: int, feedback: float) -> np.ndarray:
    """Schroeder allpass filter (phase diffusion)."""
    y = np.zeros_like(x)
    for i in range(len(x)):
        j = i - delay
        prev = y[j] if j >= 0 else 0.0
        y[i] = -feedback * x[i] + prev + feedback * (x[j] if j >= 0 else 0.0)
    return y


class RoomReverb:
    """Small-room reverb with distance/surface/slap/wash/tone controls."""

    def __init__(self, sample_rate: int = 44100, room_size: float = 0.5):
        """Initialize.

        Args:
            sample_rate: Audio sample rate.
            room_size: 0..1 room scale (drives early-reflection spacing
                       and comb delays).
        """
        self.sr = int(sample_rate)
        self.room_size = max(0.0, min(1.0, float(room_size)))
        # comb delay times (samples) for the diffuse tail — prime-ish
        # lengths with no common divisor (Schroeder practice)
        base = int(0.025 * self.sr * (0.5 + self.room_size))
        self.comb_delays = [int(base * r) for r in (1.0, 1.35, 1.51, 1.83,
                                                    2.13, 2.47)]
        self.comb_fb = [0.78, 0.76, 0.74, 0.72, 0.70, 0.68]
        self.allpass_delays = [int(0.005 * self.sr),
                               int(0.007 * self.sr),
                               int(0.011 * self.sr)]

    # ------------------------------------------------------------------ #
    def process(self, x: np.ndarray, position: float = 0.5,
                surface: float = 0.5, slap: float = 0.0,
                wash: float = 0.5, temp: float = 0.5,
                mix: float = 0.3, slap_delay_ms: float = 90.0
                ) -> np.ndarray:
        """Process audio through the room model.

        Args:
            x: Mono input (1-D float array).
            position: 0..1 perceived distance (later/brighter reflections).
            surface: 0..1 reflective character (gain of reflections).
            slap: 0..1 amount of slap-back feedback loop.
            wash: 0..1 balance discrete reflections vs diffuse tail.
            temp: 0..1 tonal character (0 warm, 1 bright).
            mix: 0..1 dry/wet mix.
            slap_delay_ms: Slap echo delay time.
        """
        er = self._early_reflections(x, position, surface)
        tail = self._diffuse(er, wash)
        slap_sig = self._slap(x, slap, slap_delay_ms)
        wet = wash * tail + (1.0 - wash) * er + slap_sig
        wet = self._tilt(wet, temp)
        return (1.0 - mix) * x + mix * wet

    # ------------------------------------------------------------------ #
    def _early_reflections(self, x: np.ndarray, position: float,
                           surface: float) -> np.ndarray:
        """Tapped-delay early reflections (image-source room approx)."""
        n = len(x)
        out = np.zeros(n)
        # image-source tap pattern for a small room: mirrored walls
        taps_ms = [3.5, 7.0, 9.5, 12.0, 16.5, 21.0, 27.0, 34.0]
        base = 0.6 + 1.6 * position           # farther -> later
        gains = [1.0, 0.75, 0.55, 0.42, 0.30, 0.20, 0.13, 0.08]
        # surface: more reflective -> stronger later taps
        surf = 0.4 + 0.6 * surface
        for ms, g in zip(taps_ms, gains):
            delay = int(ms * base * self.sr / 1000.0)
            g2 = g * surf * (1.0 - 0.4 * position)  # distance attenuation
            if delay < n:
                out[delay:] += g2 * x[: n - delay]
        return out

    def _diffuse(self, er: np.ndarray, wash: float) -> np.ndarray:
        """Schroeder diffuse tail (combs -> allpasses)."""
        y = np.zeros_like(er)
        for d, fb in zip(self.comb_delays, self.comb_fb):
            y += comb(er, max(d, 1), fb * (0.85 + 0.15 * wash))
        y /= len(self.comb_delays)
        for d in self.allpass_delays:
            y = allpass(y, max(d, 1), 0.5)
        return y

    def _slap(self, x: np.ndarray, amount: float,
              delay_ms: float) -> np.ndarray:
        """Parallel-wall slap echo with independent feedback loop."""
        if amount <= 0.0:
            return np.zeros_like(x)
        delay = max(1, int(delay_ms * self.sr / 1000.0))
        n = len(x)
        buf = np.zeros(n + delay)
        buf[:n] = x
        out = np.zeros(n)
        fb = 0.35 * amount
        for i in range(n):
            prev = buf[i] if i < n else 0.0
            buf[i + delay] += fb * prev
            out[i] = amount * prev
        return out

    def _tilt(self, x: np.ndarray, temp: float) -> np.ndarray:
        """Tonal character: blend of lowpassed and highpassed wet signal."""
        warm = _lowpass(x, 2200.0, self.sr)
        bright = _highpass(x, 800.0, self.sr)
        # temp 0 -> warm, 1 -> bright
        return (1.0 - temp) * warm + temp * bright


def _lowpass(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    a = np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1.0 - a) * x[i] + a * acc
        y[i] = acc
    return y


def _highpass(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    a = np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    prev_x, prev_y = 0.0, 0.0
    for i in range(len(x)):
        y[i] = a * prev_y + a * (x[i] - prev_x)
        prev_x, prev_y = x[i], y[i]
    return y


def demo() -> None:
    """Run a short impulse-ish burst through the room at two settings."""
    sr = 22050
    rev = RoomReverb(sample_rate=sr, room_size=0.6)
    rng = np.random.default_rng(0)
    n = int(sr * 1.0)
    t = np.arange(n) / sr
    x = (np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20.0)
         + 0.05 * rng.standard_normal(n))
    near = rev.process(x, position=0.1, surface=0.7, slap=0.0,
                       wash=0.4, temp=0.3, mix=0.4)
    far = rev.process(x, position=0.9, surface=0.9, slap=0.5,
                      wash=0.7, temp=0.8, mix=0.6)
    print(f"dry   rms={np.sqrt(np.mean(x**2)):.4f} peak={np.max(np.abs(x)):.3f}")
    print(f"near  rms={np.sqrt(np.mean(near**2)):.4f} peak={np.max(np.abs(near)):.3f}")
    print(f"far   rms={np.sqrt(np.mean(far**2)):.4f} peak={np.max(np.abs(far)):.3f}")
    # tail check: energy should persist after the 50 ms input burst
    tail_near = np.sqrt(np.mean(near[int(0.3 * sr):] ** 2))
    tail_far = np.sqrt(np.mean(far[int(0.3 * sr):] ** 2))
    print(f"tail  near={tail_near:.5f} far={tail_far:.5f} (far has slap+wash)")
    assert tail_far > tail_near, "far setting should ring longer"


if __name__ == "__main__":
    demo()
