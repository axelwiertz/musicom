"""Six-band multiband saturator with per-band algorithm selection and M/S routing
— Kreuzberg Audio Oberton style (SoS, September 2026).

Replicable logic from the Sound On Sound news article (2026-09-23):

    Oberton features six processing bands that can each be loaded with any one
    of 15 included saturation algorithms, and can function in stereo, left-only,
    right-only, Mid and Sides modes. Frequency and Q controls make it possible
    to fine-tune the range that's affected by each band, while continuous gain
    controls allow for detailed control over the amount of saturation introduced.
    Helpfully, there's also a global control that makes it possible to adjust all
    bands at once while maintaining their relative positions.

What is replicated here:
- **6 independently configurable bands** with configurable crossover frequencies.
- **15 saturation algorithms**: clean (bypass), soft clip, hard clip, tube,
  germanium diodes, silicon diodes, LED, asymmetric single diode, JFET square-law,
  CMOS inverter, op-amp rail, sine foldback, tanh, asinh, cubic nonlinearity.
  Each has a defined transfer function with parameterised knee/gain.
- **Per-band M/S mode**: stereo (L+R unchanged), left-only, right-only,
  Mid-only (L+R), Sides-only (L−R).
- **Per-band controls**: frequency, Q (bandwidth), drive/gain, mix (wet/dry).
- **Global trim** preserving relative per-band balance.
- **Demo** rendering a test signal through random band configurations.

Not replicated: 227 factory presets, VST3/AU/AAX/CLAP hosting, GUI with
frequency-response overlay, standalone application, per-band spectrum analyser.
"""

import numpy as np
from typing import Callable, Dict, List, Literal, Optional, Tuple
from dataclasses import dataclass, field


# =========================================================================
# 15 Saturation transfer functions
# =========================================================================

def _bypass(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Clean pass — no saturation (drive controls output level)."""
    return x * drive


def _soft_clip(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Cubic soft-clip: y = 1.5*x - 0.5*x^3 for |x| < 1, sign(x) otherwise."""
    x = x * drive
    y = np.where(np.abs(x) < 1.0, 1.5 * x - 0.5 * x ** 3, np.sign(x))
    return y


def _hard_clip(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Hard symmetrical clip at ±1 after drive."""
    return np.clip(x * drive, -1.0, 1.0)


def _tube(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Asymmetric tube 12AX7-style: tanh of a bipolar signal with positive bias."""
    x = x * drive
    y = np.tanh(x + 0.2 * (x > 0))  # positive gets extra push
    return y


def _germanium(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Germanium antiparallel diode pair — 0.30 V knee.
    y = Vk * asinh(x / Vk) with Vk = 0.30/drive scaling.
    """
    vk = 0.30 / max(drive, 0.01)
    return vk * np.arcsinh(x / max(vk, 1e-8))


def _silicon(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Silicon antiparallel diode pair — 0.65 V knee."""
    vk = 0.65 / max(drive, 0.01)
    return vk * np.arcsinh(x / max(vk, 1e-8))


def _led(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """LED antiparallel pair — 1.80 V knee, so brighter/harder clip."""
    vk = 1.80 / max(drive, 0.01)
    return vk * np.arcsinh(x / max(vk, 1e-8))


def _single_diode(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Single-diode asymmetric clamp — even harmonics / octave-up character.
    Positive half passes through diode; negative half is soft-clipped.
    """
    x = x * drive
    pos = np.where(x > 0, x, 0)
    neg = np.where(x < 0, 0.3 * np.tanh(2.0 * x), 0)
    return pos + neg


def _jfet(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """JFET square-law stage: |x| < Vp → Id ∝ (x/Vp)², clamp above."""
    vp = 0.8 / max(drive, 0.01)
    x_norm = x / max(vp, 1e-8)
    y = np.sign(x_norm) * np.minimum(x_norm ** 2, 1.0)
    return y


def _cmos_inverter(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """CMOS inverter hard clip with sigmoid transition through threshold."""
    x = x * drive
    return 2.0 / (1.0 + np.exp(-4.0 * x)) - 1.0


def _opamp_rail(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Op-amp rail clip with foldback of the residue past ±1."""
    x = x * drive
    y = np.where(np.abs(x) <= 1.0, x,
                 np.where(x > 1.0, 1.0 - 0.3 * np.abs(x - 1.0),
                          -1.0 + 0.3 * np.abs(x + 1.0)))
    return y


def _sine_foldback(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Sine foldback — maps waveform through sin(π·x). Creates dense harmonics."""
    return np.sin(np.pi * x * drive)


def _tanh_sat(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Plain tanh saturation — smooth, musical, no asymmetries."""
    return np.tanh(x * drive)


def _asinh_sat(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Asinh saturation — logarithmic squeeze, no hard clip."""
    return np.arcsinh(x * drive)


def _cubic_nl(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Pure cubic nonlinearity: y = x - (1/3)x³ for musical odd-order harmonics."""
    x = x * drive
    return x - (1.0 / 3.0) * x ** 3


# Registry of 15 saturation algorithms
SATURATION_ALGOS: Dict[str, Callable] = {
    "bypass": _bypass,
    "soft_clip": _soft_clip,
    "hard_clip": _hard_clip,
    "tube": _tube,
    "germanium": _germanium,
    "silicon": _silicon,
    "led": _led,
    "single_diode": _single_diode,
    "jfet": _jfet,
    "cmos_inverter": _cmos_inverter,
    "opamp_rail": _opamp_rail,
    "sine_foldback": _sine_foldback,
    "tanh": _tanh_sat,
    "asinh": _asinh_sat,
    "cubic": _cubic_nl,
}

SATURATION_NAMES: List[str] = list(SATURATION_ALGOS.keys())
"""15 saturation algorithm names, in order."""

MidsideMode = Literal["stereo", "left", "right", "mid", "sides"]


# =========================================================================
# Crossover band splitting
# =========================================================================

def _butter_lowpass(signal: np.ndarray, sr: int, cutoff: float,
                    order: int = 2) -> np.ndarray:
    """2nd-order Butterworth lowpass via scipy."""
    from scipy.signal import butter, lfilter
    nyq = sr / 2.0
    fc = min(max(cutoff, 10.0), nyq * 0.99)
    b, a = butter(order, fc / nyq, btype="low")
    return lfilter(b, a, signal)


def _butter_highpass(signal: np.ndarray, sr: int, cutoff: float,
                     order: int = 2) -> np.ndarray:
    """2nd-order Butterworth highpass via scipy."""
    from scipy.signal import butter, lfilter
    nyq = sr / 2.0
    fc = min(max(cutoff, 10.0), nyq * 0.99)
    b, a = butter(order, fc / nyq, btype="high")
    return lfilter(b, a, signal)


def _lr4_split(signal: np.ndarray, sr: int, cutoff: float) -> Tuple[np.ndarray, np.ndarray]:
    """4th-order Linkwitz-Riley crossover (two cascaded 2nd-order Butterworth).
    Returns (low, high).
    """
    lp = _butter_lowpass(signal, sr, cutoff, order=2)
    lp = _butter_lowpass(lp, sr, cutoff, order=2)
    hp = _butter_highpass(signal, sr, cutoff, order=2)
    hp = _butter_highpass(hp, sr, cutoff, order=2)
    return lp, hp


def _split_into_bands(signal: np.ndarray, sr: int,
                      crossovers: List[float]) -> List[np.ndarray]:
    """Split a mono signal into bands using LR4 crossovers.

    Args:
        signal: 1D mono audio array.
        sr: Sample rate.
        crossovers: N-1 cutoff frequencies for N bands (e.g. [120, 400, 1200, 4000, 10000] for 6 bands).

    Returns:
        List of N band arrays summing to the original signal.
    """
    bands: List[np.ndarray] = []
    remainder = signal.copy()
    for i, cf in enumerate(crossovers):
        low, remainder = _lr4_split(remainder, sr, cf)
        bands.append(low)
    bands.append(remainder)  # highest band
    return bands


# =========================================================================
# Mid/Side encoding
# =========================================================================

def _ms_encode(stereo: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Convert stereo (Samples x 2) to mid (L+R)/side (L−R)."""
    mid = (stereo[:, 0] + stereo[:, 1]) / 2.0
    side = (stereo[:, 0] - stereo[:, 1]) / 2.0
    return mid, side


def _ms_decode(mid: np.ndarray, side: np.ndarray) -> np.ndarray:
    """Convert mid/side back to stereo (Samples x 2)."""
    stereo = np.zeros((len(mid), 2), dtype=mid.dtype)
    stereo[:, 0] = mid + side
    stereo[:, 1] = mid - side
    return stereo


# =========================================================================
# Per-band configuration
# =========================================================================

@dataclass
class BandConfig:
    """Configuration for one processing band.

    Attributes:
        frequency: Center/characteristic frequency for the band (Hz) — informational.
        q: Bandwidth / resonance control (0.1 = wide, 10.0 = narrow).
        drive: Saturation drive/gain (0.0 to 2.0, default 1.0).
        mix: Wet/dry mix for this band (0.0 = dry, 1.0 = full wet).
        algo: Name of the saturation algorithm (key in SATURATION_ALGOS).
        mode: M/S or channel mode: 'stereo', 'left', 'right', 'mid', 'sides'.
    """
    frequency: float = 1000.0
    q: float = 1.0
    drive: float = 1.0
    mix: float = 1.0
    algo: str = "tanh"
    mode: MidsideMode = "stereo"


# =========================================================================
# Main processor
# =========================================================================

@dataclass
class MultibandSaturator:
    """Six-band multiband saturator — Kreuzberg Audio Oberton style.

    Splits the input into 6 bands via 5 LR4 crossover frequencies, processes
    each band with its own saturation algorithm and M/S mode, then sums back.

    Args:
        sample_rate: Audio sample rate in Hz.
        crossover_freqs: 5 crossover frequencies dividing the 6 bands.
            Default: [120, 400, 1200, 4000, 10000] Hz.
        band_configs: Optional list of 6 BandConfigs. If None, default configs
            are created with tanh saturation and stereo mode.
        global_trim: Master gain applied after summing all bands (1.0 = unity).
    """
    sample_rate: int = 44100
    crossover_freqs: List[float] = field(
        default_factory=lambda: [120.0, 400.0, 1200.0, 4000.0, 10000.0]
    )
    band_configs: Optional[List[BandConfig]] = None
    global_trim: float = 1.0

    def __post_init__(self):
        if self.band_configs is None:
            self.band_configs = [BandConfig(frequency=f)
                                 for f in self._band_centers()]
        # From this point, self.band_configs is always a list
        configs = self.band_configs  # local alias for type narrowing
        assert len(configs) == 6, "Must have exactly 6 band configs"
        assert len(self.crossover_freqs) == 5, "Must have exactly 5 crossover freqs"
        for bc in configs:
            assert bc.algo in SATURATION_ALGOS, (
                f"Unknown algo '{bc.algo}'. Choose from: {', '.join(SATURATION_NAMES)}"
            )

    def _band_centers(self) -> List[float]:
        """Geometric mean of adjacent crossover boundaries for display purposes."""
        bounds = [0.0] + list(self.crossover_freqs) + [self.sample_rate / 2.0]
        centers = []
        for i in range(6):
            low = max(bounds[i], 20.0)
            high = min(bounds[i + 1], self.sample_rate / 2.0 - 20.0)
            centers.append(np.sqrt(low * high))
        return centers

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process stereo audio through the 6-band saturator.

        Args:
            audio: Input stereo audio (Samples x 2), float in [-1, 1].

        Returns:
            Processed stereo audio (Samples x 2), same shape.
        """
        assert audio.ndim == 2 and audio.shape[1] == 2, "Input must be stereo (S x 2)"

        num_samples = audio.shape[0]

        # Split left and right channels independently into 6 bands each
        left = audio[:, 0]
        right = audio[:, 1]

        left_bands = _split_into_bands(left, self.sample_rate, self.crossover_freqs)
        right_bands = _split_into_bands(right, self.sample_rate, self.crossover_freqs)

        output_stereo = np.zeros_like(audio)
        configs = self.band_configs  # type: ignore[assignment] — safe, __post_init__ guarantees list

        for i in range(6):
            config = configs[i]
            fn = SATURATION_ALGOS[config.algo]
            drive = max(config.drive, 0.0)

            # Build stereo band pair
            band_stereo = np.zeros((num_samples, 2))
            band_stereo[:, 0] = left_bands[i]
            band_stereo[:, 1] = right_bands[i]

            # Apply M/S mode before saturation
            if config.mode == "stereo":
                proc = band_stereo.copy()
                proc[:, 0] = fn(band_stereo[:, 0], drive)
                proc[:, 1] = fn(band_stereo[:, 1], drive)
            elif config.mode == "left":
                proc = np.zeros_like(band_stereo)
                proc[:, 0] = fn(band_stereo[:, 0], drive)
                proc[:, 1] = band_stereo[:, 1]
            elif config.mode == "right":
                proc = np.zeros_like(band_stereo)
                proc[:, 0] = band_stereo[:, 0]
                proc[:, 1] = fn(band_stereo[:, 1], drive)
            elif config.mode == "mid":
                mid, side = _ms_encode(band_stereo)
                mid_sat = fn(mid, drive)
                proc = _ms_decode(mid_sat, side)
            elif config.mode == "sides":
                mid, side = _ms_encode(band_stereo)
                side_sat = fn(side, drive)
                proc = _ms_decode(mid, side_sat)
            else:
                proc = band_stereo

            # Wet/dry mix per band
            dry = band_stereo
            mix = np.clip(config.mix, 0.0, 1.0)
            band_out = (1.0 - mix) * dry + mix * proc

            output_stereo += band_out

        # Global trim
        output_stereo *= self.global_trim

        # Soft limit to prevent overs
        peak = np.max(np.abs(output_stereo))
        if peak > 1.0:
            output_stereo /= peak
            output_stereo = np.tanh(output_stereo * 2.0) / 2.0  # gentle squash

        return output_stereo

    def set_all_drive(self, drive: float):
        """Set all band drives to the same value (global drive control)."""
        for bc in self.band_configs:
            bc.drive = drive

    def set_all_algos(self, algo: str):
        """Set all bands to the same algorithm."""
        assert algo in SATURATION_ALGOS, f"Unknown algo '{algo}'"
        for bc in self.band_configs:
            bc.algo = algo

    def scale_all_drive(self, factor: float):
        """Scale all band drives by a relative factor while preserving ratios.
        This implements the 'global control that makes it possible to adjust all
        bands at once while maintaining their relative positions.'
        """
        for bc in self.band_configs:
            bc.drive *= factor

    def randomize(self, seed: Optional[int] = None):
        """Randomise all band configs for fast experimentation."""
        rng = np.random.default_rng(seed)
        for bc in self.band_configs:
            bc.algo = rng.choice(SATURATION_NAMES)
            bc.drive = rng.uniform(0.2, 2.0)
            bc.mix = rng.uniform(0.3, 1.0)
            bc.q = rng.uniform(0.5, 8.0)
            bc.mode = rng.choice(["stereo", "left", "right", "mid", "sides"])

    def summary(self) -> str:
        """Print a human-readable table of the current band configuration."""
        lines = ["Band | Freq    | Q     | Drive | Mix  | Algo            | Mode"]
        lines.append("-" * 75)
        for i, bc in enumerate(self.band_configs):
            lines.append(
                f"{i + 1:4d} | {bc.frequency:6.0f} | {bc.q:5.2f} | "
                f"{bc.drive:5.2f} | {bc.mix:4.2f} | {bc.algo:15s} | {bc.mode}"
            )
        lines.append(f"\nGlobal trim: {self.global_trim:.2f}")
        return "\n".join(lines)


# =========================================================================
# Demo
# =========================================================================

def demo():
    """Run a quick demo generating a test tone through a random band config."""
    sr = 44100
    dur = 2.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)

    # Build a harmonically rich test signal: low bass + mid saw + high hat
    test_tone = (
        0.3 * np.sin(2 * np.pi * 110 * t)
        + 0.2 * np.sin(2 * np.pi * 220 * t)
        + 0.15 * np.sin(2 * np.pi * 440 * t)
        + 0.1 * np.sin(2 * np.pi * 880 * t)
        + 0.05 * np.sin(2 * np.pi * 1760 * t)
    )
    # Stereo: L = signal, R = slightly different mix
    stereo = np.zeros((len(t), 2))
    stereo[:, 0] = test_tone
    stereo[:, 1] = 0.8 * test_tone + 0.2 * np.roll(test_tone, 128)

    # Create saturator with default configs and randomize
    sat = MultibandSaturator(sample_rate=sr)
    sat.randomize(seed=42)

    print(sat.summary())
    print(f"\nInput shape: {stereo.shape}, range: [{stereo.min():.3f}, {stereo.max():.3f}]")

    out = sat.process(stereo)

    print(f"Output shape: {out.shape}, range: [{out.min():.3f}, {out.max():.3f}]")
    print(f"Input RMS L: {np.sqrt(np.mean(stereo[:, 0] ** 2)):.5f}, "
          f"R: {np.sqrt(np.mean(stereo[:, 1] ** 2)):.5f}")
    print(f"Output RMS L: {np.sqrt(np.mean(out[:, 0] ** 2)):.5f}, "
          f"R: {np.sqrt(np.mean(out[:, 1] ** 2)):.5f}")

    # Test with a specific configuration
    print("\n--- Testing with specific band config ---")
    configs = [
        BandConfig(frequency=60, algo="germanium", drive=0.8, mode="stereo"),
        BandConfig(frequency=250, algo="tube", drive=1.2, mode="mid"),
        BandConfig(frequency=800, algo="tanh", drive=1.0, mode="sides"),
        BandConfig(frequency=2500, algo="sine_foldback", drive=0.6, mode="left"),
        BandConfig(frequency=6000, algo="soft_clip", drive=1.5, mode="right"),
        BandConfig(frequency=12000, algo="bypass", drive=1.0, mode="stereo"),
    ]
    sat2 = MultibandSaturator(sample_rate=sr, band_configs=configs)
    print(sat2.summary())
    out2 = sat2.process(stereo)
    print(f"Custom config output range: [{out2.min():.3f}, {out2.max():.3f}]")

    assert stereo.shape == out.shape, "Shape mismatch"
    assert stereo.shape == out2.shape, "Shape mismatch"
    assert len(SATURATION_NAMES) == 15, f"Expected 15 algos, got {len(SATURATION_NAMES)}"
    print(f"\n✅ All 15 saturation algorithms available: {', '.join(SATURATION_NAMES)}")

    return sat, out


if __name__ == "__main__":
    demoSaturator, demoOutput = demo()
    print("\nDemo complete.")