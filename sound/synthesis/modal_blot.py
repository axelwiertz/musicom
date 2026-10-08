"""BLOT-style Geometric Modal Resonator Network.

Inspired by Laboratory 0's BLOT — an experimental modal synthesizer where the
geometry of a lump on screen is the patch. Each piece of the lump is a modal
resonator: eight damped oscillators tuned by size with just-intonation ratios.
Pieces interact via ring modulation, waveguide strings, formant filters,
multiband saturation, and a feedback delay network memory.

References:
    - BLOT: https://www.synthtopia.com/content/2026/10/06/free-experimental-modal-synthesizer-blot/
    - Laboratory 0: https://laboratory0.gumroad.com/l/BLOT
"""

import math
import random
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_SR = 48000
JUST_RATIOS = np.array([1.0, 1.125, 1.25, 1.333, 1.5, 1.667, 1.875, 2.0],
                        dtype=np.float64)
"""Just-intonation ratios for the 8 modal resonators (octave + Pythagorean/
Ptolemaic intervals within)."""


# ---------------------------------------------------------------------------
# Modal Resonator
# ---------------------------------------------------------------------------
@dataclass
class ModalResonator:
    """A single modal resonator: eight damped oscillators tuned to just-
    intonation ratios of a root frequency.

    The resonator is characterised by its *size* (1.0 = reference, smaller
    values = higher pitch) and *shape* (spreads the modes apart), *brightness*
    (amplitude scaling of higher modes), and *ring time* (per-mode decay).

    The eight modes are damped sinusoids at ``root_freq * JUST_RATIOS``.
    """
    size: float = 1.0            # 0.1 .. 10.0; small → high root
    shape: float = 0.5           # 0..1; mode spread factor
    brightness: float = 0.7      # 0..1; higher → more high-mode energy
    ring_time: float = 1.0       # seconds for lowest mode to decay -60 dB
    heat: float = 0.0            # 0..1; mode stretch and saturation drive

    # Internal state
    _phase: np.ndarray = field(default_factory=lambda: np.zeros(8))
    _amplitude: np.ndarray = field(default_factory=lambda: np.zeros(8))
    _decay: np.ndarray = field(default_factory=lambda: np.ones(8))

    def __post_init__(self):
        self.reset(seed=0)

    def reset(self, seed: int = 0):
        rng = random.Random(seed)
        self._phase = np.zeros(8)
        self._amplitude = np.zeros(8)
        # Decay rates: lowest mode decays at ring_time, higher modes faster
        self._decay = np.exp(
            -np.arange(1, 9) / (self.ring_time * DEFAULT_SR)
        )

    def root_frequency(self, midi_root: float) -> float:
        """Return the root frequency in Hz for a given MIDI note."""
        return 440.0 * 2.0 ** ((midi_root - 69.0) / 12.0)

    def mode_frequencies(self, midi_root: float) -> np.ndarray:
        """Return the 8 mode frequencies for this resonator."""
        root = self.root_frequency(midi_root)
        # Size: smaller size → higher pitch (inverse relationship)
        size_factor = 1.0 / max(self.size, 0.01)
        # Shape: spreads modes apart
        spread = 1.0 + self.shape * 0.5  # 1.0..1.5
        ratios = JUST_RATIOS ** spread
        return root * size_factor * ratios

    def compute_brightness_gain(self) -> np.ndarray:
        """Per-mode amplitude scaling from brightness (0..1)."""
        # Brighter = more energy in higher modes
        b = np.clip(self.brightness, 0.0, 1.0)
        gains = np.ones(8)
        for i in range(1, 8):
            gains[i] = b ** (i / 4.0)
        return gains

    def strike(self, velocity: float = 0.5):
        """Excite all modes with a strike impulse."""
        gains = self.compute_brightness_gain()
        self._amplitude = velocity * gains * 0.5

    def process_sample(self, midi_root: float) -> float:
        """Process one sample, returning the summed output of all modes."""
        freqs = self.mode_frequencies(midi_root)
        gains = self.compute_brightness_gain()
        # Heat stretches modes (pitch shift up with heat)
        heat_stretch = 1.0 + self.heat * 0.2

        out = 0.0
        for i in range(8):
            self._phase[i] += 2.0 * math.pi * freqs[i] * heat_stretch / DEFAULT_SR
            if self._phase[i] > 2.0 * math.pi:
                self._phase[i] -= 2.0 * math.pi
            self._amplitude[i] *= self._decay[i]
            out += gains[i] * self._amplitude[i] * math.sin(self._phase[i])

        # Heat saturation (tanh soft clip)
        if self.heat > 0.0:
            drive = 1.0 + self.heat * 4.0
            out = math.tanh(out * drive) / math.tanh(drive)

        return out


# ---------------------------------------------------------------------------
# Waveguide String
# ---------------------------------------------------------------------------
class WaveguideString:
    """A plucked waveguide string realised as a Karplus-Strong delay line.

    Pitch is determined by length (delay in samples).  A tendril pulled out
    of the lump becomes a waveguide string.
    """
    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sr = sample_rate
        self._delay_line: List[float] = []
        self._write_idx = 0
        self._length_samples = 0
        self._feedback = 0.99

    def set_pitch(self, freq: float):
        """Set string pitch by adjusting delay line length."""
        self._length_samples = max(4, int(self.sr / freq))
        self._delay_line = [0.0] * self._length_samples
        self._write_idx = 0
        # Slight high-frequency loss for realism
        self._feedback = 0.996 - 0.2 / self._length_samples

    def pluck(self, velocity: float = 0.5):
        """Fill delay line with random noise scaled by velocity."""
        if not self._delay_line:
            return
        rng = np.random.RandomState()
        noise = (rng.rand(self._length_samples) - 0.5) * 2.0 * velocity
        self._delay_line = list(noise)

    def process_sample(self) -> float:
        """Read one output sample, write back filtered sample."""
        if not self._delay_line:
            return 0.0
        out = self._delay_line[self._write_idx]
        # Two-point averaging lowpass (loss)
        delayed = self._delay_line[(self._write_idx + 1) % self._length_samples]
        new_val = self._feedback * 0.5 * (out + delayed)
        self._delay_line[self._write_idx] = new_val
        self._write_idx = (self._write_idx + 1) % self._length_samples
        return out


# ---------------------------------------------------------------------------
# Formant Filter (vowel mouth)
# ---------------------------------------------------------------------------
# Formant frequencies for vowels (after Klatt)
_FORMANT_TABLE = {
    'a': (800, 1200, 2400),   # "ah"
    'e': (500, 1800, 2600),   # "eh"
    'i': (300, 2200, 3100),   # "ee"
    'o': (400, 900, 2300),    # "oh"
    'u': (300, 800, 2000),    # "oo"
}


class FormantFilter:
    """Three-band resonator filter shaping input audio into a vowel formant.

    A dent pressed into the lump becomes a formant filter (mouth).
    """
    def __init__(self, vowel: str = 'a', sample_rate: int = DEFAULT_SR):
        self.sr = sample_rate
        self.set_vowel(vowel)
        # State for two-pole resonators
        self._state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def set_vowel(self, vowel: str):
        """Set vowel to one of 'a', 'e', 'i', 'o', 'u'."""
        vowel = vowel.lower()
        if vowel not in _FORMANT_TABLE:
            vowel = 'a'
        self.vowel = vowel
        self._formants = _FORMANT_TABLE[vowel]

    def process_sample(self, x: float) -> float:
        """Apply three-series formant filter."""
        out = x
        for f_idx, f in enumerate(self._formants):
            if f <= 0 or f >= self.sr / 2:
                continue
            radius = 0.99  # pole radius
            r2 = radius * radius
            theta = 2.0 * math.pi * f / self.sr
            b1 = 2.0 * radius * math.cos(theta)
            b2 = -r2
            gain = (1.0 - r2) / (1.0 + b1 + b2) if (1.0 + b1 + b2) != 0 else 0.0
            # Direct form II transposed
            s0 = self._state[f_idx * 2]
            s1 = self._state[f_idx * 2 + 1]
            y = gain * out + s0
            s0 = gain * out + s1 - b1 * y
            s1 = -b2 * y
            self._state[f_idx * 2] = s0
            self._state[f_idx * 2 + 1] = s1
            out = y
        return out


# ---------------------------------------------------------------------------
# Multiband Saturator
# ---------------------------------------------------------------------------
class MultibandSaturator:
    """4× oversampled 3-band saturator with feedback comb.

    Splits signal into low/mid/high bands, saturates each independently,
    and adds a feedback comb tuned to the root frequency.
    """
    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sr = sample_rate
        self._comb_buffer: List[float] = []
        self._comb_len = 0
        self._comb_idx = 0
        self._lp_state = [0.0, 0.0, 0.0]
        self._hp_state = [0.0, 0.0]
        self.heat_drive: float = 0.0

    def set_root(self, freq_hz: float):
        """Set comb feedback delay to match root frequency."""
        self._comb_len = max(2, int(self.sr / freq_hz))
        self._comb_buffer = [0.0] * self._comb_len
        self._comb_idx = 0

    def process_sample(self, x: float) -> float:
        """Process one sample through 3-band saturator + comb feedback."""
        drive = 1.0 + self.heat_drive * 6.0

        # Simple 3-band split using 1-pole LP/HP
        # Low band: LP at 800 Hz
        lp_cut = 800.0 / self.sr
        lp_a = math.exp(-2.0 * math.pi * lp_cut)
        self._lp_state[0] += (1.0 - lp_a) * (x - self._lp_state[0])

        # Clamp state to prevent NaN
        if not math.isfinite(self._lp_state[0]):
            self._lp_state[0] = 0.0
        low = self._lp_state[0]

        # High band: HP at 4000 Hz
        hp_cut = 4000.0 / self.sr
        hp_a = math.exp(-2.0 * math.pi * hp_cut)
        self._hp_state[0] = hp_a * (self._hp_state[0] + x - self._hp_state[1])
        self._hp_state[1] = x

        if not math.isfinite(self._hp_state[0]):
            self._hp_state[0] = 0.0
        high = self._hp_state[0]

        # Mid band = everything else (clamped)
        mid = x - low - high
        if not math.isfinite(mid):
            mid = 0.0

        # Saturate each band (tanh)
        low_sat = math.tanh(low * drive)
        mid_sat = math.tanh(mid * drive * 0.7)
        high_sat = math.tanh(high * drive * 0.3)

        # Recombine
        out = low_sat + mid_sat + high_sat

        # Feedback comb tuned to root
        if self._comb_len > 2:
            comb_read = self._comb_buffer[self._comb_idx]
            self._comb_buffer[self._comb_idx] = out + 0.3 * comb_read
            self._comb_idx = (self._comb_idx + 1) % self._comb_len
            out += 0.15 * comb_read

        return out


# ---------------------------------------------------------------------------
# Feedback Delay Network (memory)
# ---------------------------------------------------------------------------
class FeedbackDelayNetwork:
    """Eight-line feedback delay network serving as the lump's memory.

    Holds what the matter has played; can be mixed into the output.
    """
    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sr = sample_rate
        # Eight delay lines with coprime lengths (Schroeder-style)
        self._delays: List[List[float]] = []
        self._lengths = [479, 503, 541, 577, 613, 647, 673, 701]
        self._idxs = [0] * 8
        for L in self._lengths:
            self._delays.append([0.0] * L)
        self.mix: float = 0.0       # 0..1 wet mix
        self.feedback: float = 0.7

    def process_sample(self, x: float) -> float:
        """Process one sample through FDN, return wet signal."""
        wet = 0.0
        for i in range(8):
            L = self._lengths[i]
            idx = self._idxs[i]
            out = self._delays[i][idx]
            self._delays[i][idx] = (
                self.feedback * out + x * (1.0 - self.feedback) * 0.125
            )
            self._idxs[i] = (idx + 1) % L
            wet += out
        return wet * self.mix


# ---------------------------------------------------------------------------
# BLOT Lump — the main composition engine
# ---------------------------------------------------------------------------
@dataclass
class LumpPiece:
    """A piece of the lump: a modal resonator with optional string/ formant.

    Attributes:
        resonator: core modal resonator
        waveguide: optional Karplus-Strong string (None if no tendril)
        formant: optional formant filter (None if no dent)
        x, y: position on the lump surface (for ring modulation proximity)
        ring_mod_pair: another piece index to ring-modulate with
    """
    resonator: ModalResonator
    waveguide: Optional[WaveguideString] = None
    formant: Optional[FormantFilter] = None
    x: float = 0.0
    y: float = 0.0
    ring_mod_pair: Optional[int] = None


class BLOTEngine:
    """Geometric modal resonator network — the main BLOT synthesis engine.

    Manages a collection of LumpPieces that interact through proximity-based
    ring modulation, a shared multiband saturator, and a feedback delay
    network memory.

    Usage::

        engine = BLOTEngine(sample_rate=48000)
        # Add a piece
        piece = LumpPiece(resonator=ModalResonator(size=1.0, shape=0.3))
        engine.add_piece(piece)
        # Render a note
        audio = engine.render(midi_root=60, num_samples=DEFAULT_SR * 2)
    """
    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sr = sample_rate
        self.pieces: List[LumpPiece] = []
        self.saturator = MultibandSaturator(sample_rate)
        self.fdn = FeedbackDelayNetwork(sample_rate)
        self.midi_root: float = 60.0
        self.breath_noise_amp: float = 0.02
        self.droplet_rate: float = 0.0  # droplets per sample
        self._droplet_phase: float = 0.0
        self.intense_mode: bool = False
        self._struck: bool = False
        self._has_strike: bool = False  # set True after strike_all()

    def add_piece(self, piece: LumpPiece):
        """Add a piece to the lump."""
        self.pieces.append(piece)

    def set_piece_ring_mod(self, idx_a: int, idx_b: int):
        """Set two pieces to ring-modulate each other."""
        if 0 <= idx_a < len(self.pieces):
            self.pieces[idx_a].ring_mod_pair = idx_b
        if 0 <= idx_b < len(self.pieces):
            self.pieces[idx_b].ring_mod_pair = idx_a

    def strike_all(self, velocity: float = 0.5):
        """Strike every piece. Resets resonators first so strike energy sticks."""
        for i, p in enumerate(self.pieces):
            p.resonator.reset(seed=42 + i)
            p.resonator.strike(velocity)
            if p.waveguide is not None:
                p.waveguide.pluck(velocity)
        self._has_strike = True

    def render(self, midi_root: float = 60.0,
               num_samples: int = DEFAULT_SR * 2,
               seed: int = 42) -> np.ndarray:
        """Render audio from the current lump configuration.

        Args:
            midi_root: MIDI root note for tuning.
            num_samples: Number of samples to render.
            seed: Random seed for stochastic processes.

        Returns:
            np.ndarray of shape (num_samples,) with float32 audio.
        """
        self.midi_root = midi_root
        self.saturator.set_root(440.0 * 2.0 ** ((midi_root - 69.0) / 12.0))
        rng = random.Random(seed)
        np_rng = np.random.RandomState(seed)

        # Reset all resonators ONLY if no strike was issued
        if not self._has_strike:
            for i, p in enumerate(self.pieces):
                p.resonator.reset(seed + i)

        output = np.zeros(num_samples, dtype=np.float64)

        for s in range(num_samples):
            sample = 0.0

            # Breath noise (slow breathing)
            breath = self.breath_noise_amp * math.sin(
                2.0 * math.pi * 0.5 * s / self.sr
            )
            breath_noise = breath * (rng.random() - 0.5) * 2.0

            # Droplets (short tones above ringing when hot)
            self._droplet_phase += self.droplet_rate
            if self._droplet_phase >= 1.0:
                self._droplet_phase -= 1.0
                droplet_pitch = midi_root + 24 + rng.randint(0, 24)
                droplet_samples = int(0.05 * self.sr)
                if s + droplet_samples < num_samples:
                    droplet_freq = 440.0 * 2.0 ** ((droplet_pitch - 69.0) / 12.0)
                    for ds in range(droplet_samples):
                        if s + ds < num_samples:
                            env = math.exp(-ds / (0.02 * self.sr))
                            output[s + ds] += env * 0.3 * math.sin(
                                2.0 * math.pi * droplet_freq * (ds) / self.sr
                            )

            # Process each piece
            for i, p in enumerate(self.pieces):
                res_out = p.resonator.process_sample(midi_root)

                # Waveguide string
                wg_out = 0.0
                if p.waveguide is not None:
                    wg_out = p.waveguide.process_sample()

                # Formant filter
                fmt_out = 0.0
                if p.formant is not None:
                    fmt_out = p.formant.process_sample(res_out + breath_noise)

                # Ring modulation between paired pieces
                if p.ring_mod_pair is not None and p.ring_mod_pair < len(self.pieces):
                    partner = self.pieces[p.ring_mod_pair]
                    # Proximity = distance on lump surface (lower = stronger mod)
                    dx = p.x - partner.x
                    dy = p.y - partner.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < 0.5:
                        ring_amt = (0.5 - dist) * 2.0  # 0..1
                        partner_out = partner.resonator._amplitude[0] * math.sin(
                            partner.resonator._phase[0]
                        )
                        res_out *= (1.0 - ring_amt * 0.5)
                        res_out += ring_amt * 0.5 * res_out * partner_out

                # Combine
                piece_out = res_out + wg_out + fmt_out * 0.3
                sample += piece_out

            # Multiband saturator (with heat drive from all pieces)
            avg_heat = sum(p.resonator.heat for p in self.pieces) / max(
                len(self.pieces), 1
            )
            self.saturator.heat_drive = avg_heat
            sample = self.saturator.process_sample(sample)

            # FDN memory
            fdn_wet = self.fdn.process_sample(sample)
            sample += fdn_wet * self.fdn.mix

            output[s] = sample

        # Normalise to [-1, 1] range
        peak = np.max(np.abs(output))
        if peak > 0.0:
            output = output / peak * 0.9

        # Reset strike flag so next render with different params is clean
        self._has_strike = False

        return output.astype(np.float32)


# ---------------------------------------------------------------------------
# Preset factories
# ---------------------------------------------------------------------------
def bell_like_patch() -> BLOTEngine:
    """Create a bell/chime-like lump: small pieces with low shape (spread)."""
    engine = BLOTEngine(sample_rate=DEFAULT_SR)
    for i in range(3):
        size = 0.5 + i * 0.2
        shape = 0.2 + i * 0.1
        heat = 0.1
        res = ModalResonator(size=size, shape=shape, brightness=0.6,
                             ring_time=2.0, heat=heat)
        piece = LumpPiece(resonator=res, x=i * 0.2, y=i * 0.15)
        engine.add_piece(piece)
    engine.breath_noise_amp = 0.01
    engine.droplet_rate = 0.001
    engine.fdn.mix = 0.2
    return engine


def drone_pad_patch() -> BLOTEngine:
    """Create a slow-evolving drone pad with formant mouth."""
    engine = BLOTEngine(sample_rate=DEFAULT_SR)
    # Main drone resonator
    res1 = ModalResonator(size=2.0, shape=0.3, brightness=0.5,
                          ring_time=4.0, heat=0.2)
    p1 = LumpPiece(resonator=res1, x=0.0, y=0.0,
                   formant=FormantFilter(vowel='a'))
    engine.add_piece(p1)

    # Higher shimmer piece
    res2 = ModalResonator(size=0.3, shape=0.1, brightness=0.8,
                          ring_time=1.5, heat=0.1)
    p2 = LumpPiece(resonator=res2, x=0.5, y=0.0)
    engine.add_piece(p2)

    # Plucked string
    wg = WaveguideString(sample_rate=DEFAULT_SR)
    wg.set_pitch(220.0)
    res3 = ModalResonator(size=1.5, shape=0.4, brightness=0.3,
                          ring_time=0.5, heat=0.0)
    p3 = LumpPiece(resonator=res3, x=0.3, y=0.4, waveguide=wg)
    engine.add_piece(p3)

    engine.set_piece_ring_mod(0, 1)
    engine.breath_noise_amp = 0.03
    engine.droplet_rate = 0.0005
    engine.fdn.mix = 0.3
    return engine


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def demo():
    """Run a short demonstration of BLOT engine synthesis."""
    print("=== BLOT-style Modal Resonator Network Demo ===")
    print()

    # Bell-like patch with strike
    print("1. Bell-like chime patch (root=60, 2 sec)")
    engine = bell_like_patch()
    engine.strike_all(velocity=0.5)
    audio = engine.render(midi_root=60, num_samples=DEFAULT_SR * 2)
    print(f"   Rendered {len(audio)} samples, peak={np.max(np.abs(audio)):.4f}")
    assert len(audio) == DEFAULT_SR * 2
    assert np.isfinite(audio).all()
    assert np.max(np.abs(audio)) > 0.0
    print("   OK — audio finite, non-empty, has signal")

    # Drone pad patch
    print("2. Drone pad patch (root=48, 3 sec)")
    engine2 = drone_pad_patch()
    engine2.strike_all(velocity=0.6)
    audio2 = engine2.render(midi_root=48, num_samples=DEFAULT_SR * 3)
    print(f"   Rendered {len(audio2)} samples, peak={np.max(np.abs(audio2)):.4f}")
    assert len(audio2) == DEFAULT_SR * 3
    assert np.isfinite(audio2).all()
    assert np.max(np.abs(audio2)) > 0.0
    print("   OK — audio finite, non-empty, has signal")

    # Rapid arpeggio — repeated strikes
    print("3. Quick strike test (root=72, 1 sec)")
    engine3 = bell_like_patch()
    engine3.strike_all(velocity=0.8)
    audio3 = engine3.render(midi_root=72, num_samples=DEFAULT_SR)
    print(f"   Rendered {len(audio3)} samples, peak={np.max(np.abs(audio3)):.4f}")
    assert len(audio3) == DEFAULT_SR
    assert np.isfinite(audio3).all()
    assert np.max(np.abs(audio3)) > 0.0
    print("   OK — audio finite, non-empty, has signal")

    print()
    print("All BLOT tests passed.")


if __name__ == "__main__":
    demo()