"""Multiband Auto-Panner and Stereo Sculptor (Orbit-style).

Splits stereo or mono input into Low, Mid, and High frequency bands using
Linkwitz-Riley 4th-order (24 dB/oct) crossover filters.
Each band possesses independent:
- Pan (-1.0 left to +1.0 right) with pan law compensation
- Stereo Width (0.0 mono to 2.0 extra-wide) via mid/side processing
- Volume gain (linear scale or dB)
- Dedicated LFO modulators (sine, triangle, square, random-walk sample-and-hold,
  or envelope follower driven by band amplitude)
- Host BPM tempo synchronization or free Hz rate
- Saturated modulation option (soft saturation of the LFO modulation curve)
- Per-band parameter randomization (dice function)
"""

from dataclasses import dataclass
import math
from typing import Dict, Optional, Tuple, Union

import numpy as np


class Biquad:
    """Standard biquad filter section for Linkwitz-Riley crossovers."""

    def __init__(self, b0: float, b1: float, b2: float, a1: float, a2: float):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a1 = a1
        self.a2 = a2
        self.x1_l = self.x2_l = self.y1_l = self.y2_l = 0.0
        self.x1_r = self.x2_r = self.y1_r = self.y2_r = 0.0

    def reset(self):
        self.x1_l = self.x2_l = self.y1_l = self.y2_l = 0.0
        self.x1_r = self.x2_r = self.y1_r = self.y2_r = 0.0

    def process(self, x: np.ndarray) -> np.ndarray:
        """Process 2-channel buffer (channels, samples)."""
        num_channels, num_samples = x.shape
        y = np.zeros_like(x)
        # Vectorized lfilter or recursive filter
        from scipy.signal import lfilter
        b = np.array([self.b0, self.b1, self.b2], dtype=np.float64)
        a = np.array([1.0, self.a1, self.a2], dtype=np.float64)
        for ch in range(num_channels):
            zi = np.array([self.y1_l, self.y2_l] if ch == 0 else [self.y1_r, self.y2_r], dtype=np.float64)
            # scipy lfilter
            yc, zf = lfilter(b, a, x[ch].astype(np.float64), zi=np.zeros(2, dtype=np.float64))
            y[ch] = yc.astype(np.float32)
        return y


def design_butterworth_lp(fc: float, fs: float) -> Tuple[float, float, float, float, float]:
    """2nd-order Butterworth low-pass filter coefficients."""
    omega = 2.0 * math.pi * fc / fs
    theta = omega / 2.0
    sn = math.sin(theta)
    cs = math.cos(theta)
    if sn == 0:
        return 1.0, 0.0, 0.0, 0.0, 0.0
    alpha = sn / (math.sqrt(2.0) * cs)
    beta = math.sqrt(2.0) * sn * cs

    b0 = (1.0 - cs) / (2.0 * (1.0 + beta))
    b1 = (1.0 - cs) / (1.0 + beta)
    b2 = b0
    a1 = -2.0 * cs / (1.0 + beta)
    a2 = (1.0 - beta) / (1.0 + beta)
    return b0, b1, b2, a1, a2


def design_butterworth_hp(fc: float, fs: float) -> Tuple[float, float, float, float, float]:
    """2nd-order Butterworth high-pass filter coefficients."""
    omega = 2.0 * math.pi * fc / fs
    theta = omega / 2.0
    sn = math.sin(theta)
    cs = math.cos(theta)
    if sn == 0:
        return 1.0, 0.0, 0.0, 0.0, 0.0
    beta = math.sqrt(2.0) * sn * cs

    b0 = (1.0 + cs) / (2.0 * (1.0 + beta))
    b1 = -(1.0 + cs) / (1.0 + beta)
    b2 = b0
    a1 = -2.0 * cs / (1.0 + beta)
    a2 = (1.0 - beta) / (1.0 + beta)
    return b0, b1, b2, a1, a2


class LinkwitzRiley4Crossover:
    """Linkwitz-Riley 4th order (LR4) 3-band crossover (2 cascaded Butterworth 2-pole filters)."""

    def __init__(self, low_mid_cross: float = 250.0, mid_high_cross: float = 3500.0, fs: int = 44100):
        self.fs = fs
        self.update_crossovers(low_mid_cross, mid_high_cross)

    def update_crossovers(self, low_mid: float, mid_high: float):
        self.low_mid = min(max(20.0, low_mid), self.fs * 0.45)
        self.mid_high = min(max(self.low_mid + 20.0, mid_high), self.fs * 0.45)

        # Split 1: Low-Mid crossover (LP1 + HP1)
        lp1 = design_butterworth_lp(self.low_mid, self.fs)
        hp1 = design_butterworth_hp(self.low_mid, self.fs)
        self.lp1_stage1 = Biquad(*lp1)
        self.lp1_stage2 = Biquad(*lp1)
        self.hp1_stage1 = Biquad(*hp1)
        self.hp1_stage2 = Biquad(*hp1)

        # Split 2: Mid-High crossover on HP1 branch (LP2 + HP2)
        lp2 = design_butterworth_lp(self.mid_high, self.fs)
        hp2 = design_butterworth_hp(self.mid_high, self.fs)
        self.lp2_stage1 = Biquad(*lp2)
        self.lp2_stage2 = Biquad(*lp2)
        self.hp2_stage1 = Biquad(*hp2)
        self.hp2_stage2 = Biquad(*hp2)

    def reset(self):
        for f in (self.lp1_stage1, self.lp1_stage2, self.hp1_stage1, self.hp1_stage2,
                  self.lp2_stage1, self.lp2_stage2, self.hp2_stage1, self.hp2_stage2):
            f.reset()

    def process(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Split input buffer (channels, samples) into (low, mid, high)."""
        # Low band: input -> LP1 -> LP1
        low = self.lp1_stage2.process(self.lp1_stage1.process(x))

        # Rest (mid+high): input -> HP1 -> HP1
        mid_high = self.hp1_stage2.process(self.hp1_stage1.process(x))

        # Mid band: mid_high -> LP2 -> LP2
        mid = self.lp2_stage2.process(self.lp2_stage1.process(mid_high))

        # High band: mid_high -> HP2 -> HP2
        high = self.hp2_stage2.process(self.hp2_stage1.process(mid_high))

        return low, mid, high


@dataclass
class ModulatorConfig:
    shape: str = "sine"  # sine, triangle, square, random, env
    rate_hz: float = 1.0  # rate in Hz
    tempo_sync: bool = False
    division: str = "1/4"  # 1/1, 1/2, 1/4, 1/8, 1/16, etc.
    depth: float = 0.0  # 0.0 to 1.0
    saturated: bool = False  # soft-clip modulation wave


@dataclass
class BandConfig:
    pan: float = 0.0  # -1.0 to 1.0
    width: float = 1.0  # 0.0 (mono) to 2.0 (extra wide)
    gain_db: float = 0.0  # -60 to +12 dB
    pan_mod: Optional[ModulatorConfig] = None
    width_mod: Optional[ModulatorConfig] = None
    volume_mod: Optional[ModulatorConfig] = None

    def __post_init__(self):
        if self.pan_mod is None:
            self.pan_mod = ModulatorConfig()
        if self.width_mod is None:
            self.width_mod = ModulatorConfig()
        if self.volume_mod is None:
            self.volume_mod = ModulatorConfig()


SYNC_DIVISIONS: Dict[str, float] = {
    "4/1": 16.0,
    "2/1": 8.0,
    "1/1": 4.0,
    "1/2": 2.0,
    "1/4": 1.0,
    "1/8": 0.5,
    "1/16": 0.25,
    "1/32": 0.125,
    "1/64": 0.0625,
    "1/4T": 2.0 / 3.0,
    "1/8T": 1.0 / 3.0,
    "1/16T": 0.5 / 3.0,
    "1/4D": 1.5,
    "1/8D": 0.75,
}


class OrbitalBandProcessor:
    """Processes one frequency band: pan, stereo width, and volume with dynamic modulators."""

    def __init__(self, config: BandConfig, fs: int = 44100, bpm: float = 120.0, seed: Optional[int] = None):
        self.config = config
        self.fs = fs
        self.bpm = bpm
        self.rng = np.random.RandomState(seed)

    def _generate_lfo(self, mod: Optional[ModulatorConfig], num_samples: int, audio_for_env: Optional[np.ndarray] = None) -> np.ndarray:
        if mod is None or mod.depth <= 1e-4:
            return np.zeros(num_samples, dtype=np.float32)

        if mod.shape == "env":
            # Envelope follower on audio_for_env
            if audio_for_env is None:
                return np.zeros(num_samples, dtype=np.float32)
            mono_env = np.mean(np.abs(audio_for_env), axis=0)
            # Smooth envelope with 20ms attack / 100ms release
            alpha_att = math.exp(-1.0 / (0.02 * self.fs))
            alpha_rel = math.exp(-1.0 / (0.10 * self.fs))
            env = np.zeros(num_samples, dtype=np.float32)
            cur = 0.0
            for i in range(num_samples):
                x = mono_env[i]
                if x > cur:
                    cur = alpha_att * cur + (1.0 - alpha_att) * x
                else:
                    cur = alpha_rel * cur + (1.0 - alpha_rel) * x
                env[i] = cur
            # Normalize peak to ~1.0
            pk = np.max(env)
            if pk > 1e-5:
                env = env / pk
            lfo = (env * 2.0 - 1.0) * mod.depth
        else:
            if mod.tempo_sync:
                beats = SYNC_DIVISIONS.get(mod.division, 1.0)
                freq = (self.bpm / 60.0) / beats
            else:
                freq = max(0.01, mod.rate_hz)

            t = np.arange(num_samples, dtype=np.float32) / self.fs
            phase = 2.0 * np.pi * freq * t

            if mod.shape == "sine":
                raw = np.sin(phase)
            elif mod.shape == "triangle":
                norm_p = (phase / (2.0 * np.pi)) % 1.0
                raw = 2.0 * np.abs(2.0 * (norm_p - np.floor(norm_p + 0.5))) - 1.0
            elif mod.shape == "square":
                raw = np.sign(np.sin(phase))
            elif mod.shape == "random":
                # Sample & Hold at frequency intervals
                step_samples = max(1, int(self.fs / freq))
                num_steps = int(math.ceil(num_samples / step_samples)) + 1
                random_levels = self.rng.uniform(-1.0, 1.0, size=num_steps)
                raw = np.repeat(random_levels, step_samples)[:num_samples]
            else:
                raw = np.sin(phase)

            if mod.saturated:
                # Analog drive / soft saturation curve
                raw = np.tanh(raw * 2.5) / np.tanh(2.5)

            lfo = raw * mod.depth

        return lfo.astype(np.float32)

    def process(self, band_audio: np.ndarray) -> np.ndarray:
        """Takes band_audio of shape (2, num_samples) and applies pan, width, and gain."""
        channels, num_samples = band_audio.shape
        if channels == 1:
            band_audio = np.vstack([band_audio, band_audio])

        # 1. Modulations
        pan_lfo = self._generate_lfo(self.config.pan_mod, num_samples, band_audio)
        width_lfo = self._generate_lfo(self.config.width_mod, num_samples, band_audio)
        vol_lfo = self._generate_lfo(self.config.volume_mod, num_samples, band_audio)

        # Dynamic parameter trajectories
        pan_curve = np.clip(self.config.pan + pan_lfo, -1.0, 1.0)
        width_curve = np.clip(self.config.width + width_lfo * 1.5, 0.0, 2.5)
        # Volume gain curve
        base_gain = 10.0 ** (self.config.gain_db / 20.0)
        gain_curve = np.clip(base_gain * (1.0 + vol_lfo), 0.0, 4.0)

        # 2. Mid/Side Width Processing
        mid = 0.5 * (band_audio[0] + band_audio[1])
        side = 0.5 * (band_audio[1] - band_audio[0])

        mod_side = side * width_curve
        left = mid - mod_side
        right = mid + mod_side

        # 3. Pan Law (Constant Power Pan Law: cos/sin)
        pan_angle = (pan_curve + 1.0) * (math.pi / 4.0)  # 0 to pi/2
        gain_l = np.cos(pan_angle) * math.sqrt(2.0)
        gain_r = np.sin(pan_angle) * math.sqrt(2.0)

        out_l = left * gain_l * gain_curve
        out_r = right * gain_r * gain_curve

        return np.vstack([out_l, out_r])


class OrbitalStereoSculptor:
    """3-Band Orbital Stereo Sculptor / AutoPanner (SP-090).

    Splits signal into Low, Mid, and High bands via LR4 crossover.
    Independently pans, widens, and volume-modulates each frequency band.
    """

    def __init__(
        self,
        low_mid_cross: float = 250.0,
        mid_high_cross: float = 3500.0,
        fs: int = 44100,
        bpm: float = 120.0,
        seed: Optional[int] = 42,
    ):
        self.fs = fs
        self.bpm = bpm
        self.crossover = LinkwitzRiley4Crossover(low_mid_cross, mid_high_cross, fs=fs)

        self.low_config = BandConfig(pan=0.0, width=0.0, gain_db=0.0)  # Lows centered & mono by default
        self.mid_config = BandConfig(pan=0.0, width=1.0, gain_db=0.0)
        self.high_config = BandConfig(pan=0.0, width=1.4, gain_db=0.0)

        self.low_proc = OrbitalBandProcessor(self.low_config, fs=fs, bpm=bpm, seed=seed)
        self.mid_proc = OrbitalBandProcessor(self.mid_config, fs=fs, bpm=bpm, seed=(seed + 1 if seed else None))
        self.high_proc = OrbitalBandProcessor(self.high_config, fs=fs, bpm=bpm, seed=(seed + 2 if seed else None))

    def randomize_band(self, band: str = "high", seed: Optional[int] = None):
        """Randomize parameters on a specific band (dice button behavior)."""
        rng = np.random.RandomState(seed)
        shapes = ["sine", "triangle", "square", "random", "env"]
        sync_divs = ["1/1", "1/2", "1/4", "1/8", "1/16", "1/8T", "1/16T"]

        cfg = getattr(self, f"{band}_config")
        cfg.pan = float(rng.uniform(-0.6, 0.6))
        cfg.width = float(rng.uniform(0.5, 1.8))
        cfg.gain_db = float(rng.uniform(-2.0, 2.0))

        # Pan mod
        cfg.pan_mod.shape = str(rng.choice(shapes))
        cfg.pan_mod.rate_hz = float(rng.uniform(0.2, 5.0))
        cfg.pan_mod.tempo_sync = bool(rng.choice([True, False]))
        cfg.pan_mod.division = str(rng.choice(sync_divs))
        cfg.pan_mod.depth = float(rng.uniform(0.2, 0.9))
        cfg.pan_mod.saturated = bool(rng.choice([True, False]))

        # Width mod
        cfg.width_mod.shape = str(rng.choice(shapes))
        cfg.width_mod.rate_hz = float(rng.uniform(0.1, 3.0))
        cfg.width_mod.tempo_sync = bool(rng.choice([True, False]))
        cfg.width_mod.division = str(rng.choice(sync_divs))
        cfg.width_mod.depth = float(rng.uniform(0.1, 0.7))

        # Vol mod
        cfg.volume_mod.shape = str(rng.choice(shapes))
        cfg.volume_mod.depth = float(rng.uniform(0.0, 0.4))

    @staticmethod
    def mono_correlation(audio: np.ndarray) -> float:
        """Calculate mono correlation coefficient (-1.0 to +1.0) of a stereo buffer."""
        if audio.shape[0] < 2:
            return 1.0
        l = audio[0]
        r = audio[1]
        denom = math.sqrt(float(np.sum(l ** 2) * np.sum(r ** 2)))
        if denom < 1e-9:
            return 1.0
        return float(np.sum(l * r) / denom)

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process input audio (mono or stereo 2xN). Returns stereo 2xN buffer."""
        if audio.ndim == 1:
            audio = np.vstack([audio, audio])
        elif audio.shape[0] == 1:
            audio = np.vstack([audio, audio])

        # 1. 3-band LR4 split
        low_raw, mid_raw, high_raw = self.crossover.process(audio)

        # 2. Per-band orbital sculpting
        low_proc = self.low_proc.process(low_raw)
        mid_proc = self.mid_proc.process(mid_raw)
        high_proc = self.high_proc.process(high_raw)

        # 3. Sum reconstructed bands
        out = low_proc + mid_proc + high_proc
        return out.astype(np.float32)


def demo():
    """Demonstrate OrbitalStereoSculptor on synthetic multi-instrument chord."""
    fs = 44100
    bpm = 128.0
    dur = 4.0  # 4 seconds
    num_samples = int(dur * fs)
    t = np.arange(num_samples) / fs

    # Synthetic test signal: Bass (110 Hz) + Mid Keys (440 Hz) + High Hi-Hat Noise
    bass = 0.5 * np.sin(2 * np.pi * 110 * t)
    keys = 0.3 * (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 554.37 * t))
    hats = 0.15 * np.random.uniform(-1, 1, num_samples) * (np.sin(2 * np.pi * 8 * t) > 0.8)
    mono_mix = (bass + keys + hats).astype(np.float32)
    stereo_in = np.vstack([mono_mix, mono_mix])

    sculptor = OrbitalStereoSculptor(low_mid_cross=200.0, mid_high_cross=2500.0, fs=fs, bpm=bpm)

    # Low band: centered mono
    sculptor.low_config.pan = 0.0
    sculptor.low_config.width = 0.0

    # Mid band: tempo-synced sine autopan (1/2 note)
    sculptor.mid_config.pan_mod = ModulatorConfig(
        shape="sine", tempo_sync=True, division="1/2", depth=0.8, saturated=True
    )
    sculptor.mid_config.width = 1.2

    # High band: random S&H wide panner (1/16 note)
    sculptor.high_config.pan_mod = ModulatorConfig(
        shape="random", tempo_sync=True, division="1/16", depth=1.0
    )
    sculptor.high_config.width = 1.8

    stereo_out = sculptor.process(stereo_in)
    corr_in = OrbitalStereoSculptor.mono_correlation(stereo_in)
    corr_out = OrbitalStereoSculptor.mono_correlation(stereo_out)

    print(f"OrbitalStereoSculptor Demo:")
    print(f"  Input shape: {stereo_in.shape}, Mono correlation: {corr_in:.3f}")
    print(f"  Output shape: {stereo_out.shape}, Mono correlation: {corr_out:.3f}")
    print(f"  Peak output: {np.max(np.abs(stereo_out)):.3f}")
    print(f"  Success!")


if __name__ == "__main__":
    demo()
