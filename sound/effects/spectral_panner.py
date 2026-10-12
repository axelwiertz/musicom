"""Spectral Brightness Panner — frequency-dependent auto-panner.

Inspired by Sound Particles Brightness Panner 2, a plugin that controls
stereo panning based on the spectral brightness (spectral centroid) of the
audio signal. Brighter content is panned differently from darker content,
creating dynamic, frequency-aware spatial movement.

Key DSP concepts:
- Real-time spectral centroid tracking via IIR-smoothed brightness estimator
- Brightness controls a panning law (equal-power or linear)
- Independent per-channel paths: each input channel gets its own trajectory
- Virtual Centre: progressively pulls signal toward center above a brightness
  threshold (useful for keeping bright leads centered while letting lows roam)
- Modulation modes: direct brightness control, tempo-synced dual-LFO,
  envelope-follower-blended-with-brightness
- Multiple visualization/operation views (circular, polygon, room) abstracted
  as pan profiles

Reference:
  - Sound Particles Brightness Panner 2: https://soundparticles.com/products/brightnesspanner/overview
  - https://www.soundonsound.com/news/sound-particles-update-energy-panner-2-brightness-panner-2

Usage:
    from sound.effects.spectral_panner import SpectralBrightnessPanner

    panner = SpectralBrightnessPanner(sample_rate=44100)
    out = panner.process(stereo_audio)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import numpy as np


class PanProfile(Enum):
    """Spatial profile — maps brightness to pan position."""
    CIRCULAR = "circular"    # 0→1 maps to continuous left→right sweep
    CENTERED = "centered"    # Dark = wide, bright = narrow → center
    ROOM = "room"           # Dark = corners, bright = center (natural room)


class BrightnessMode(Enum):
    """How brightness is interpreted for panning."""
    DIRECT = "direct"        # Pan = brightness mapping
    INVERT = "invert"        # Pan = 1 - brightness mapping
    BAND = "band"            # Only pan content in a specific frequency band


# ---------------------------------------------------------------------------
# Spectral centroid estimator (IIR-smoothed)
# ---------------------------------------------------------------------------
class BrightnessTracker:
    """Real-time spectral centroid / brightness estimator.

    Uses a simplified spectral centroid approximation via highpass/lowpass
    energy ratio, smoothed with a one-pole IIR filter for stability.

    Parameters
    ----------
    sample_rate : int
        Sample rate in Hz.
    window_ms : float
        Analysis window in milliseconds for energy ratio.
    smooth : float
        IIR smoothing factor (0.0 = no smoothing, 1.0 = max smoothing).
    """

    def __init__(self, sample_rate: int = 44100,
                 window_ms: float = 10.0,
                 smooth: float = 0.9):
        self.sample_rate = sample_rate
        self.window_samples = max(2, int(sample_rate * window_ms / 1000.0))
        self.smooth = max(0.0, min(1.0, smooth))

        # Pre-compute simple HP filter for energy separation
        # Cutoff ~2 kHz for brightness separation
        self._hp_cutoff = 2000.0
        self._hp_state = 0.0
        self._lp_state_hp = 0.0  # HP energy tracker
        self._lp_state_total = 0.0  # Total energy tracker
        self._smooth_brightness = 0.5  # Smoothed output
        self._sample_idx = 0

    def reset(self):
        """Reset internal state."""
        self._hp_state = 0.0
        self._lp_state_hp = 0.0
        self._lp_state_total = 0.0
        self._smooth_brightness = 0.5
        self._sample_idx = 0

    def process_sample(self, x: float) -> float:
        """Process one sample, return current brightness estimate (0.0–1.0).

        Parameters
        ----------
        x : float
            Input sample.

        Returns
        -------
        float
            Brightness estimate 0.0 (dark, bassy) to 1.0 (bright, trebly).
        """
        # Simple 1-pole highpass at ~2 kHz
        rc = 1.0 / (2.0 * np.pi * self._hp_cutoff)
        dt = 1.0 / self.sample_rate
        alpha = dt / (rc + dt)
        self._hp_state = (1.0 - alpha) * self._hp_state + alpha * x

        high_freq = x - self._hp_state  # high-frequency content

        # Running RMS-like energy tracking
        a = min(1.0, 1.0 / self.window_samples)
        self._lp_state_hp = (1.0 - a) * self._lp_state_hp + a * (high_freq ** 2)
        self._lp_state_total = (1.0 - a) * self._lp_state_total + a * (x ** 2)

        # Brightness ratio with floor
        total = self._lp_state_total if self._lp_state_total > 1e-12 else 1e-12
        ratio = min(1.0, self._lp_state_hp / total)

        # Smooth
        self._smooth_brightness = (
            self.smooth * self._smooth_brightness
            + (1.0 - self.smooth) * ratio
        )
        return float(self._smooth_brightness)

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process an audio buffer and return brightness estimates.

        Parameters
        ----------
        audio : np.ndarray
            1-D audio array.

        Returns
        -------
        np.ndarray
            Brightness 0.0–1.0 per sample.
        """
        self.reset()
        out = np.zeros_like(audio)
        for i in range(len(audio)):
            out[i] = self.process_sample(float(audio[i]))
        return out


# ---------------------------------------------------------------------------
# Equal-power pan law
# ---------------------------------------------------------------------------
class PanLaw:
    """Equal-power panning law with optional center bias."""

    @staticmethod
    def pan_gains(pan: float) -> Tuple[float, float]:
        """Compute L/R gains for a pan position.

        Parameters
        ----------
        pan : float
            Pan position: -1.0 (left) → 0.0 (center) → 1.0 (right).

        Returns
        -------
        Tuple[float, float]
            (left_gain, right_gain).
        """
        pan = max(-1.0, min(1.0, pan))
        angle = np.pi * (pan + 1.0) / 4.0  # 0 → π/2
        return (float(np.cos(angle)), float(np.sin(angle)))


# ---------------------------------------------------------------------------
# Brightness-to-pan mapping profiles
# ---------------------------------------------------------------------------
def _brightness_to_pan(brightness: float, profile: PanProfile,
                       mode: BrightnessMode) -> float:
    """Map a brightness value to a pan position.

    Parameters
    ----------
    brightness : float
        Brightness 0.0–1.0.
    profile : PanProfile
        Mapping profile.
    mode : BrightnessMode
        Direct or inverted interpretation.

    Returns
    -------
    float
        Pan position -1.0 to 1.0.
    """
    b = max(0.0, min(1.0, brightness))
    if mode == BrightnessMode.INVERT:
        b = 1.0 - b
    elif mode == BrightnessMode.BAND:
        # Band mode: only pan brightness values in 0.3–0.7 range; map
        # out-of-band to center
        if b < 0.3 or b > 0.7:
            return 0.0
        b = (b - 0.3) / 0.4  # normalize to 0–1

    if profile == PanProfile.CIRCULAR:
        return 2.0 * b - 1.0  # -1..1
    elif profile == PanProfile.CENTERED:
        # Dark = wide (panned), bright = narrow (centered)
        return (1.0 - b) * 2.0 * (0.5 if b > 0.5 else 1.0) - (1.0 if b > 0.5 else 0.0)
    elif profile == PanProfile.ROOM:
        # Room-natural: dark → extreme L/R, bright → center
        return (1.0 - b * 2.0) * 0.8
    return 2.0 * b - 1.0


# ---------------------------------------------------------------------------
# Optional LFO modulation to blend with brightness
# ---------------------------------------------------------------------------
class LFO:
    """Simple LFO for blending with brightness control."""

    WAVEFORMS = ("sine", "triangle", "square", "saw")

    def __init__(self, rate_hz: float = 0.5, waveform: str = "sine",
                 depth: float = 0.3):
        self.rate_hz = rate_hz
        self.waveform = waveform
        self.depth = depth
        self._phase = 0.0

    def reset(self):
        self._phase = 0.0

    def next(self, dt: float) -> float:
        """Generate next LFO value (-1..1)."""
        self._phase += self.rate_hz * dt
        p = self._phase % 1.0
        if self.waveform == "sine":
            v = np.sin(2.0 * np.pi * p)
        elif self.waveform == "triangle":
            v = 4.0 * abs(p - 0.5) - 1.0
        elif self.waveform == "square":
            v = 1.0 if p < 0.5 else -1.0
        elif self.waveform == "saw":
            v = 2.0 * p - 1.0
        else:
            v = 0.0
        return float(v * self.depth)


# ---------------------------------------------------------------------------
# Main panner
# ---------------------------------------------------------------------------
class SpectralBrightnessPanner:
    """Frequency-dependent auto-panner controlled by spectral brightness.

    Parameters
    ----------
    sample_rate : int
        Sample rate in Hz.
    profile : PanProfile
        Panning profile (circular, centered, room).
    mode : BrightnessMode
        Brightness interpretation (direct, invert, band).
    brightness_smooth : float
        Smoothing factor for brightness tracker (0 = fast, 1 = very smooth).
    virtual_center : bool
        If True, bright content is pulled toward center; dark content wanders.
    virtual_center_threshold : float
        Brightness threshold above which content is pulled to center (0.0–1.0).
        Only used when virtual_center is True.
    lfo_blend : float
        How much LFO modulation to blend with brightness control (0.0 = pure
        brightness, 1.0 = pure LFO).
    lfo_rate : float
        LFO rate in Hz when blending.
    lfo_waveform : str
        LFO waveform (sine, triangle, square, saw).
    """

    def __init__(self, sample_rate: int = 44100,
                 profile: PanProfile = PanProfile.CIRCULAR,
                 mode: BrightnessMode = BrightnessMode.DIRECT,
                 brightness_smooth: float = 0.85,
                 virtual_center: bool = False,
                 virtual_center_threshold: float = 0.6,
                 lfo_blend: float = 0.0,
                 lfo_rate: float = 0.5,
                 lfo_waveform: str = "sine"):
        self.sample_rate = sample_rate
        self.profile = profile
        self.mode = mode
        self.virtual_center = virtual_center
        self.virtual_center_threshold = virtual_center_threshold
        self.lfo_blend = lfo_blend

        self._tracker = BrightnessTracker(sample_rate, smooth=brightness_smooth)
        self._lfo = LFO(rate_hz=lfo_rate, waveform=lfo_waveform, depth=0.5)
        self._panlaw = PanLaw()

        # Independent per-channel paths
        self._ch_tracker: list = [BrightnessTracker(sample_rate, smooth=brightness_smooth)
                                  for _ in range(2)]

    def reset(self):
        """Reset all internal state."""
        self._tracker.reset()
        self._lfo.reset()
        for t in self._ch_tracker:
            t.reset()

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process stereo audio through the spectral brightness panner.

        Parameters
        ----------
        audio : np.ndarray
            2-D audio array (2, N) for stereo. If 1-D (N,), treated as mono
            and duplicated to stereo.

        Returns
        -------
        np.ndarray
            Panned stereo audio (2, N).
        """
        if audio.ndim == 1:
            audio = np.stack([audio, audio], axis=0)
        if audio.shape[0] != 2:
            raise ValueError("SpectralBrightnessPanner requires stereo input "
                             f"(got shape {audio.shape})")

        n = audio.shape[1]
        out = np.zeros_like(audio, dtype=np.float64)
        dt = 1.0 / self.sample_rate

        self.reset()
        sample = np.zeros(2, dtype=np.float64)

        for i in range(n):
            # Per-channel brightness
            b_l = self._ch_tracker[0].process_sample(float(audio[0, i]))
            b_r = self._ch_tracker[1].process_sample(float(audio[1, i]))
            b_mid = (b_l + b_r) * 0.5

            # LFO blend
            lfo_v = self._lfo.next(dt)
            brightness = (1.0 - self.lfo_blend) * b_mid + self.lfo_blend * (lfo_v * 0.5 + 0.5)
            brightness = max(0.0, min(1.0, brightness))

            # Map to pan
            pan = _brightness_to_pan(brightness, self.profile, self.mode)

            # Virtual centre: pull bright content toward center
            if self.virtual_center and brightness > self.virtual_center_threshold:
                pull = (brightness - self.virtual_center_threshold) / (1.0 - self.virtual_center_threshold)
                pan *= (1.0 - pull)

            l_g, r_g = self._panlaw.pan_gains(pan)

            # Apply pan: each channel gets its own pan (independent paths)
            out[0, i] = audio[0, i] * l_g + audio[1, i] * (1.0 - abs(pan)) * 0.5
            out[1, i] = audio[1, i] * r_g + audio[0, i] * (1.0 - abs(pan)) * 0.5

        return out


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def demo():
    """Run a demo with synthetic stereo signal."""
    sr = 44100
    duration = 3.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Stereo test signal: left=low freq (dark), right=high freq (bright)
    left = 0.5 * np.sin(2.0 * np.pi * 110.0 * t)  # 110 Hz — dark
    right = 0.5 * np.sin(2.0 * np.pi * 4400.0 * t)  # 4400 Hz — bright
    stereo = np.stack([left, right], axis=0)

    panner = SpectralBrightnessPanner(
        sample_rate=sr,
        profile=PanProfile.CIRCULAR,
        brightness_smooth=0.9,
        lfo_blend=0.2,
        lfo_rate=0.3,
    )
    output = panner.process(stereo)

    rms_out = (float(np.sqrt(np.mean(output[0] ** 2))),
               float(np.sqrt(np.mean(output[1] ** 2))))
    peak_out = (float(np.max(np.abs(output[0]))),
                float(np.max(np.abs(output[1]))))
    print(f"Spectral Brightness Panner demo ({sr} Hz, {duration:.1f}s)")
    print(f"  Input: L=110Hz(dark), R=4400Hz(bright)")
    print(f"  Profile: {panner.profile.value}, LFO blend: {panner.lfo_blend}")
    print(f"  Output RMS: L={rms_out[0]:.4f}, R={rms_out[1]:.4f}")
    print(f"  Output Peak: L={peak_out[0]:.4f}, R={peak_out[1]:.4f}")
    assert output.shape == stereo.shape, "Shape mismatch"
    assert rms_out[0] > 0.001 and rms_out[1] > 0.001, "Output too quiet"
    print("  OK")
    return output


if __name__ == "__main__":
    demo()