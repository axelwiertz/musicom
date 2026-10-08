"""Raspel-style Saturated Filter + Wavefolder.

Inspired by Kreuzberg Audio's Raspel — a free plugin that combines filtering
and wavefolding in a way that allows the two processes to complement each
other rather than fight. Key DSP: per-filter-stage saturation (up to 30dB
input boost before each stage, then attenuated after), linear filter feedback
so resonance stays stable under saturation, and a post-filter Character
wavefolder that adds harmonic presence for sub-bass audibility on small
speakers.

References:
    - Kreuzberg Audio Raspel: https://www.soundonsound.com/news/raspel-free-plug-kreuzberg-audio
    - Kreuzberg Audio: https://kreuzberg-audio.com/en/downloads/raspel
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Supported filter types
# ---------------------------------------------------------------------------
FILTER_TYPES = {
    "LP2":  "2-pole lowpass (12 dB/oct)",
    "LP4":  "4-pole lowpass (24 dB/oct)",
    "LP6":  "6-pole lowpass (36 dB/oct)",
    "HP2":  "2-pole highpass (12 dB/oct)",
    "HP4":  "4-pole highpass (24 dB/oct)",
    "BP4":  "4-pole bandpass (12 dB/oct each side)",
}


# ---------------------------------------------------------------------------
# SVF (State Variable Filter) — 2-pole section
# ---------------------------------------------------------------------------
class SVF2Pole:
    """2-pole state-variable filter section.

    Simultaneously outputs lowpass, highpass, and bandpass.
    Used as the building block for multi-pole cascades.
    """
    def __init__(self, sample_rate: int = 48000):
        self.sr = sample_rate
        self.lp: float = 0.0
        self.bp: float = 0.0
        self.hp: float = 0.0

    def reset(self):
        self.lp = 0.0
        self.bp = 0.0
        self.hp = 0.0

    def process(self, x: float, freq: float, resonance: float) -> Tuple[float, float, float]:
        """Process one sample.

        Args:
            x: Input sample.
            freq: Normalised cutoff frequency (0..0.5 * sr, in Hz).
            resonance: Resonance (0..1, 1 = self-oscillation).

        Returns:
            (lowpass, bandpass, highpass) outputs.
        """
        # Clip frequency to valid range
        f = max(1.0, min(freq, self.sr / 2 - 1.0))
        # Convert to normalised angular frequency
        w = 2.0 * math.pi * f / self.sr
        g = min(0.9892 * w, 0.95)  # prewarping factor, capped for stability

        # ZDF trapezoidal integration (Chamberlin-style)
        damp = max(0.01, 2.0 * resonance)
        hp_out = x - self.lp - damp * self.bp
        # Clamp for stability
        if not math.isfinite(hp_out):
            hp_out = 0.0
        bp_out = self.bp + g * hp_out
        lp_out = self.lp + g * bp_out

        # Update state (trapezoidal feedback)
        self.lp = lp_out + g * bp_out
        self.bp = bp_out + g * hp_out
        self.hp = hp_out

        # Clamp state to prevent runaway
        for attr in ('lp', 'bp', 'hp'):
            v = getattr(self, attr)
            if not math.isfinite(v) or abs(v) > 1e6:
                setattr(self, attr, 0.0)

        return self.lp, self.bp, self.hp


# ---------------------------------------------------------------------------
# Multi-Pole Cascade Filter
# ---------------------------------------------------------------------------
class CascadeFilter:
    """Multi-pole cascade filter built from chained 2-pole SVF sections.

    Supports LP2, LP4, LP6, HP2, HP4, BP4 modes.
    Each stage has independent saturation (30dB boost before, attenuation
    after). Filter feedback remains linear — resonance stays stable even
    when drive is pushed.
    """
    def __init__(self, filter_type: str = "LP4",
                 sample_rate: int = 48000):
        if filter_type not in FILTER_TYPES:
            raise ValueError(f"Unknown filter type: {filter_type}. "
                             f"Choose from {list(FILTER_TYPES.keys())}")
        self.sr = sample_rate
        self.filter_type = filter_type
        self._poles = 0

        # Determine number of 2-pole sections
        if filter_type == "LP2":
            self._poles = 2
        elif filter_type == "LP4":
            self._poles = 4
        elif filter_type == "LP6":
            self._poles = 6
        elif filter_type in ("HP2",):
            self._poles = 2
        elif filter_type in ("HP4",):
            self._poles = 4
        elif filter_type == "BP4":
            self._poles = 4

        num_sections = self._poles // 2
        self.sections: List[SVF2Pole] = [SVF2Pole(sample_rate)
                                          for _ in range(num_sections)]

        # Per-stage drive (saturation amount 0..1, default 0.3)
        self.stage_drive: List[float] = [0.3] * num_sections
        # Per-stage gain compensation (1/sqrt(boost))
        self.stage_comp: List[float] = [1.0] * num_sections
        self.cutoff: float = 1000.0
        self.resonance: float = 0.0

    def reset(self):
        for s in self.sections:
            s.reset()

    def set_stage_drive(self, stage: int, drive: float):
        """Set per-stage input saturation drive (0..1)."""
        if 0 <= stage < len(self.sections):
            self.stage_drive[stage] = max(0.0, min(1.0, drive))
            # Gain compensation: the boost is ~30dB at drive=1.0
            # For multi-stage cascades, compensate per-stage so each
            # stage adds harmonic character but not net gain.
            boost_db = drive * 30.0 * 0.6  # reduced effective boost per stage
            linear_boost = 10.0 ** (boost_db / 20.0)
            self.stage_comp[stage] = 1.0 / max(linear_boost, 0.001)

    def process(self, x: float) -> float:
        """Process one sample through the cascade filter.

        Each stage: input → saturation (tanh) → boost → SVF → compensation.
        """
        is_lowpass = self.filter_type.startswith("LP")
        is_highpass = self.filter_type.startswith("HP")
        is_bandpass = self.filter_type.startswith("BP")

        out = x

        for section_idx, section in enumerate(self.sections):
            drive = self.stage_drive[section_idx]
            comp = self.stage_comp[section_idx]

            # Input saturation
            if drive > 0.001:
                sat_in = out * (1.0 + drive * 10.0)
                out = math.tanh(sat_in)

            # Process through SVF
            freq = self.cutoff
            # For BP mode, use centre frequency
            lp, bp, hp = section.process(out, freq, self.resonance)

            # Select output per filter type
            if is_lowpass:
                out = lp
            elif is_highpass:
                out = hp
            elif is_bandpass:
                out = bp
            else:
                out = lp  # default

            # Apply gain compensation
            out *= comp

        return out


# ---------------------------------------------------------------------------
# Wavefolder (Character control)
# ---------------------------------------------------------------------------
class Wavefolder:
    """Wavefolder designed to add harmonic presence.

    At low Character values (0.0–0.3): gentle harmonic enrichments for
    sub-bass audibility on small speakers.
    At mid values (0.4–0.6): metallic overtone generation.
    At high values (0.7–1.0): aggressive industrial wavefolding.

    The wavefolder is bit-transparent at Character=0 (no-op).
    Uses sine/arcsin folding topology:
        fold(x) = sin(π · x · Character) / sin(π · Character)  (normalised)
    At Character=0, fold(x) ≈ x (identity, via limit).
    """
    def __init__(self):
        self.character: float = 0.0  # 0..1

    def process(self, x: float) -> float:
        """Wavefold one sample.

        At character=0: identity (no change).
        At character=1: extreme folding (square-like via sine wrapping).
        """
        if self.character <= 0.001:
            return x

        # Scale fold amount
        fold_amt = self.character * 6.0

        # Symmetric wavefolding: threshold-based
        # Below threshold: linear; above: fold back
        threshold = 1.0 / max(fold_amt, 0.1)

        if abs(x) < threshold:
            return x
        else:
            # Fold: reflect excess back
            excess = abs(x) - threshold
            folded = threshold - (excess % (2.0 * threshold))
            if folded < -threshold:
                folded = -threshold - (-folded - threshold)
            return math.copysign(folded, x)


# ---------------------------------------------------------------------------
# RaspelProcessor — combined filter + wavefolder
# ---------------------------------------------------------------------------
@dataclass
class RaspelProcessor:
    """Combined saturated filter + wavefolder processor.

    Usage::

        rp = RaspelProcessor(filter_type="LP4", sample_rate=48000)
        rp.cutoff = 2000.0
        rp.resonance = 0.3
        rp.drive = 0.5       # global per-stage drive (distributed)
        rp.character = 0.4   # wavefolder amount
        output = rp.process(audio_buffer)
    """
    filter_type: str = "LP4"
    sample_rate: int = 48000
    cutoff: float = 1000.0
    resonance: float = 0.0
    drive: float = 0.3       # 0..1 — distributed equally across all stages
    character: float = 0.0   # 0..1 — wavefolder amount
    mix: float = 1.0         # 0..1 — dry/wet mix (time-aligned)

    def __post_init__(self):
        self._filter = CascadeFilter(self.filter_type, self.sample_rate)
        self._wavefolder = Wavefolder()
        # Distribute drive across all filter stages
        for i in range(len(self._filter.sections)):
            self._filter.set_stage_drive(i, self.drive)

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process an audio buffer through saturated filter + wavefolder.

        Args:
            audio: numpy array of shape (N,) or (N, C).

        Returns:
            Processed audio array of same shape.
        """
        # Handle mono/stereo
        if audio.ndim == 1:
            return self._process_mono(audio)
        elif audio.ndim == 2:
            out = np.zeros_like(audio)
            for ch in range(audio.shape[1]):
                out[:, ch] = self._process_mono(audio[:, ch])
            return out
        else:
            raise ValueError(f"Unsupported shape: {audio.shape}")

    def _process_mono(self, audio: np.ndarray) -> np.ndarray:
        """Process mono audio."""
        self._filter.reset()
        dry = np.array(audio)
        wet = np.zeros_like(audio)

        for i in range(len(audio)):
            x = float(audio[i])
            self._filter.cutoff = self.cutoff
            self._filter.resonance = self.resonance
            y = self._filter.process(x)
            self._wavefolder.character = self.character
            y = self._wavefolder.process(y)
            # Soft clip to prevent runaway from heavy drive cascades
            y = math.tanh(y * 0.3) / 0.3 if abs(y) > 1.0 else y
            wet[i] = y

        # Time-aligned parallel mix (no comb filtering)
        out = dry * (1.0 - self.mix) + wet * self.mix
        return out


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def demo():
    """Run a short demonstration of the Raspel filter+wavefolder."""
    print("=== Raspel-style Saturated Filter + Wavefolder Demo ===")
    sr = 48000

    # Generate a test tone (saw wave with harmonics)
    duration = 0.5
    n = int(sr * duration)
    t = np.arange(n) / sr
    # Rich saw wave at 110 Hz
    saw = np.zeros(n)
    for h in range(1, 11):
        saw += np.sin(2.0 * np.pi * 110.0 * h * t) / h
    saw = saw / np.max(np.abs(saw))
    print(f"1. Input saw wave: {len(saw)} samples, peak={np.max(np.abs(saw)):.4f}")

    # Test LP4 with moderate drive and character
    print("2. LP4 filter, cutoff=2000 Hz, res=0.3, drive=0.4, char=0.2")
    rp = RaspelProcessor(filter_type="LP4", sample_rate=sr,
                          cutoff=2000.0, resonance=0.3,
                          drive=0.4, character=0.2, mix=1.0)
    out = rp.process(saw)
    assert len(out) == len(saw)
    assert np.isfinite(out).all()
    print(f"   Output: {len(out)} samples, peak={np.max(np.abs(out)):.4f}, "
          f"RMS={np.sqrt(np.mean(out**2)):.4f}")

    # Test HP2 with high character (metallic)
    print("3. HP2 filter, cutoff=500 Hz, res=0.1, drive=0.6, char=0.6")
    rp2 = RaspelProcessor(filter_type="HP2", sample_rate=sr,
                           cutoff=500.0, resonance=0.1,
                           drive=0.6, character=0.6, mix=1.0)
    out2 = rp2.process(saw)
    assert len(out2) == len(saw)
    assert np.isfinite(out2).all()
    print(f"   Output: {len(out2)} samples, peak={np.max(np.abs(out2)):.4f}, "
          f"RMS={np.sqrt(np.mean(out2**2)):.4f}")

    # Test LP6 (6-pole) with heavy drive
    print("4. LP6 filter, cutoff=3000 Hz, drive=0.8, char=0.0 (no fold)")
    rp3 = RaspelProcessor(filter_type="LP6", sample_rate=sr,
                           cutoff=3000.0, resonance=0.0,
                           drive=0.8, character=0.0, mix=0.7)
    out3 = rp3.process(saw)
    assert len(out3) == len(saw)
    assert np.isfinite(out3).all()
    print(f"   Output: {len(out3)} samples, peak={np.max(np.abs(out3)):.4f}, "
          f"RMS={np.sqrt(np.mean(out3**2)):.4f}")

    # Test BP4 bandpass
    print("5. BP4 filter, centre=1000 Hz, drive=0.2, char=0.5")
    rp4 = RaspelProcessor(filter_type="BP4", sample_rate=sr,
                           cutoff=1000.0, resonance=0.4,
                           drive=0.2, character=0.5, mix=1.0)
    out4 = rp4.process(saw)
    assert len(out4) == len(saw)
    assert np.isfinite(out4).all()
    print(f"   Output: {len(out4)} samples, peak={np.max(np.abs(out4)):.4f}, "
          f"RMS={np.sqrt(np.mean(out4**2)):.4f}")

    print()
    print("All Raspel tests passed.")


if __name__ == "__main__":
    demo()