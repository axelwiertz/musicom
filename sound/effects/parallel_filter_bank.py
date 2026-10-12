"""Filtopia-style Parallel SEM Filter Bank — 5 parallel 12dB/oct filters.

Inspired by Analogue Solutions Filtopia, a hardware monosynth that uses five
Oberheim SEM-inspired analogue filters wired in parallel. Each filter is
12dB/oct (2-pole SVF) with independent cutoff offset. Filters 1 and 5 are
switchable between lowpass and bandpass; filters 2, 3, and 4 are fixed
bandpass. Filter outputs sum to produce complex multiband sweeps and
vowel-like formant clusters.

Key DSP concept:
- Signal is split across 5 parallel 2-pole filters
- Each filter has its own cutoff frequency = base_cutoff + offset_N
- Each filter has independent resonance (Q) control
- Filter types: LP-BP switchable on ch1/ch5, fixed BP on ch2/ch3/ch4
- Offsets can be modulated independently for animated filter sweeps
- Output mixing: per-filter volume trim before sum

Reference:
  - Analogue Solutions Filtopia: https://www.soundonsound.com/news/analogue-solutions-ship-second-filtopia-batch
  - https://www.analoguesolutions.com/filtopia

Usage:
    from sound.effects.parallel_filter_bank import ParallelSEMFilterBank

    bank = ParallelSEMFilterBank(sample_rate=44100)
    output = bank.process(audio, base_cutoff=800.0)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# 2-pole State-Variable Filter section (SEM-inspired)
# ---------------------------------------------------------------------------
class SEMFilter2Pole:
    """2-pole state-variable filter (12 dB/oct), Oberheim SEM-inspired.

    Parameters
    ----------
    sample_rate : int
        Sample rate in Hz.
    mode : str
        'lp' for lowpass, 'bp' for bandpass.
    """

    MODES = ("lp", "bp")

    def __init__(self, sample_rate: int = 44100, mode: str = "lp"):
        if mode not in self.MODES:
            raise ValueError(f"mode must be one of {self.MODES}, got {mode!r}")
        self.sample_rate = sample_rate
        self.mode = mode
        # State variables
        self.lp = 0.0
        self.bp = 0.0
        self.hp = 0.0

        self._cutoff = 1000.0
        self._resonance = 0.5
        self._f = 0.0
        self._q = 0.5
        self._update_coeffs()

    def _update_coeffs(self):
        """Pre-compute SVF coefficients from cutoff and resonance."""
        f = 2.0 * np.sin(np.pi * min(self._cutoff, self.sample_rate / 2.0 - 1.0)
                         / self.sample_rate)
        q = 1.0 - self._resonance * 0.9  # SEM-style Q: 0=no damping, ~1=max damp
        self._f = f
        self._q = q if q > 0.01 else 0.01

    def set_cutoff(self, cutoff_hz: float):
        """Set filter cutoff frequency.

        Parameters
        ----------
        cutoff_hz : float
            Cutoff in Hz (clamped to Nyquist).
        """
        self._cutoff = max(20.0, min(cutoff_hz, self.sample_rate / 2.0 - 1.0))
        self._update_coeffs()

    def set_resonance(self, resonance: float):
        """Set filter resonance 0.0–1.0.

        Parameters
        ----------
        resonance : float
            Resonance (0.0 = none, 1.0 = self-oscillation).
        """
        self._resonance = max(0.0, min(1.0, resonance))
        self._update_coeffs()

    def process_sample(self, x: float) -> float:
        """Process one sample through the SVF.

        Parameters
        ----------
        x : float
            Input sample.

        Returns
        -------
        float
            Filtered output sample (mode-dependent).
        """
        f = self._f
        q = self._q

        # Chamberlin SVF recurrence
        self.hp = x - self.lp - q * self.bp
        self.bp = self.bp + f * self.hp
        self.lp = self.lp + f * self.bp

        if self.mode == "lp":
            return self.lp
        else:  # bp
            return self.bp

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process a whole buffer.

        Parameters
        ----------
        audio : np.ndarray
            1-D or 2-D (channels, samples) float array.

        Returns
        -------
        np.ndarray
            Filtered output, same shape as input.
        """
        was_1d = audio.ndim == 1
        if was_1d:
            audio = audio[np.newaxis, :]  # (1, N)
        out = np.zeros_like(audio)
        for ch in range(audio.shape[0]):
            for i in range(audio.shape[1]):
                out[ch, i] = self.process_sample(float(audio[ch, i]))
        if was_1d:
            return out[0]
        return out


# ---------------------------------------------------------------------------
# Per-filter configuration
# ---------------------------------------------------------------------------
@dataclass
class FilterSlot:
    """Configuration for one of the 5 parallel filter slots.

    Parameters
    ----------
    cutoff_offset : float
        Offset in Hz added to the base cutoff.
    resonance : float
        Resonance 0.0–1.0.
    mode : str
        'lp' or 'bp'.
    mix : float
        Output mix level (0.0–1.0) for this slot's contribution.
    active : bool
        If False, this slot is bypassed.
    """
    cutoff_offset: float = 0.0
    resonance: float = 0.4
    mode: str = "bp"
    mix: float = 1.0
    active: bool = True


# ---------------------------------------------------------------------------
# Default Filtopia-style preset
# ---------------------------------------------------------------------------
def filtopia_preset() -> List[FilterSlot]:
    """Return a Filtopia-inspired 5-filter configuration.

    Filters 1,5 default to LP; filters 2,3,4 default to BP (as on the
    original hardware, where 1&5 are switchable and 2/3/4 are fixed BP).
    Offset pattern creates a spread formant-like cluster.
    """
    return [
        FilterSlot(cutoff_offset=-300.0, resonance=0.5, mode="lp", mix=0.8),
        FilterSlot(cutoff_offset=-100.0, resonance=0.3, mode="bp", mix=0.6),
        FilterSlot(cutoff_offset=0.0,     resonance=0.4, mode="bp", mix=1.0),
        FilterSlot(cutoff_offset=200.0,   resonance=0.3, mode="bp", mix=0.6),
        FilterSlot(cutoff_offset=500.0,   resonance=0.5, mode="lp", mix=0.8),
    ]


# ---------------------------------------------------------------------------
# Main parallel filter bank
# ---------------------------------------------------------------------------
class ParallelSEMFilterBank:
    """5-parallel SEM-style filter bank (Filtopia-style).

    Parameters
    ----------
    sample_rate : int
        Sample rate in Hz.
    slots : List[FilterSlot], optional
        5 filter slot configurations. If None, uses `filtopia_preset()`.
    """

    def __init__(self, sample_rate: int = 44100,
                 slots: Optional[List[FilterSlot]] = None):
        self.sample_rate = sample_rate
        if slots is not None and len(slots) != 5:
            raise ValueError("Must provide exactly 5 filter slots (or None for default).")
        self.slots = slots or filtopia_preset()
        # Build the 5 filters
        self.filters: List[SEMFilter2Pole] = []
        for s in self.slots:
            filt = SEMFilter2Pole(sample_rate, mode=s.mode)
            filt.set_cutoff(1000.0 + s.cutoff_offset)
            filt.set_resonance(s.resonance)
            self.filters.append(filt)

    def set_base_cutoff(self, cutoff_hz: float):
        """Set the base cutoff for all filters (applies offsets).

        Parameters
        ----------
        cutoff_hz : float
            Base cutoff in Hz.
        """
        for i, filt in enumerate(self.filters):
            s = self.slots[i]
            filt.set_cutoff(cutoff_hz + s.cutoff_offset)

    def set_cutoff_offset(self, slot_idx: int, offset_hz: float,
                          base_cutoff: float = 1000.0):
        """Set a specific slot's cutoff offset.

        Parameters
        ----------
        slot_idx : int
            Which slot (0–4).
        offset_hz : float
            New offset in Hz.
        base_cutoff : float
            Current base cutoff to add offset to.
        """
        self.slots[slot_idx].cutoff_offset = offset_hz
        self.filters[slot_idx].set_cutoff(base_cutoff + offset_hz)

    def set_resonance(self, slot_idx: int, resonance: float):
        """Set a specific slot's resonance.

        Parameters
        ----------
        slot_idx : int
            Which slot (0–4).
        resonance : float
            Resonance 0.0–1.0.
        """
        self.slots[slot_idx].resonance = resonance
        self.filters[slot_idx].set_resonance(resonance)

    def set_mode(self, slot_idx: int, mode: str):
        """Switch a slot's mode (only effective on 0/4 for Filtopia-style use).

        Parameters
        ----------
        slot_idx : int
            Which slot (0–4).
        mode : str
            'lp' or 'bp'.
        """
        self.slots[slot_idx].mode = mode
        self.filters[slot_idx].mode = mode

    def set_mix(self, slot_idx: int, mix: float):
        """Set a slot's output mix level.

        Parameters
        ----------
        slot_idx : int
            Which slot (0–4).
        mix : float
            Mix level 0.0–1.0.
        """
        self.slots[slot_idx].mix = max(0.0, min(1.0, mix))

    def set_active(self, slot_idx: int, active: bool):
        """Enable/disable a filter slot.

        Parameters
        ----------
        slot_idx : int
            Which slot (0–4).
        active : bool
            True to include, False to bypass.
        """
        self.slots[slot_idx].active = active

    def process(self, audio: np.ndarray,
                base_cutoff: Optional[float] = None) -> np.ndarray:
        """Process audio through the parallel filter bank.

        Parameters
        ----------
        audio : np.ndarray
            Input audio, 1-D or 2-D (channels, samples).
        base_cutoff : float, optional
            If given, update base cutoff before processing.

        Returns
        -------
        np.ndarray
            Sum of all active filter outputs.
        """
        if base_cutoff is not None:
            self.set_base_cutoff(base_cutoff)

        was_1d = audio.ndim == 1
        if was_1d:
            audio = audio[np.newaxis, :]  # (1, N)

        out = np.zeros_like(audio, dtype=np.float64)

        for i, (filt, slot) in enumerate(zip(self.filters, self.slots)):
            if not slot.active:
                continue
            filtered = filt.process(audio)
            out += filtered * slot.mix

        if was_1d:
            return out[0]
        return out


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def demo():
    """Run a quick demo: sweep a sawtooth through the bank."""
    sr = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Sawtooth at 220 Hz
    saw = 2.0 * (t * 220.0 - np.floor(t * 220.0 + 0.5))

    bank = ParallelSEMFilterBank(sample_rate=sr)
    # Sweep base cutoff from 200 Hz to 4000 Hz
    chunk_samples = int(sr * 0.05)
    output = np.zeros_like(saw)
    freq = 200.0
    for start in range(0, len(saw), chunk_samples):
        end = min(start + chunk_samples, len(saw))
        chunk = saw[start:end]
        bank.set_base_cutoff(freq)
        output[start:end] = bank.process(chunk)
        freq *= 1.05  # exponential sweep
        if freq > 8000.0:
            freq = 8000.0

    rms = float(np.sqrt(np.mean(output ** 2)))
    peak = float(np.max(np.abs(output)))
    print(f"Parallel Filter Bank demo ({sr} Hz, {duration:.1f}s)")
    print(f"  Input: sawtooth 220 Hz")
    print(f"  Cutoff sweep: 200→8000 Hz")
    print(f"  Output RMS: {rms:.4f}, Peak: {peak:.4f}")
    print(f"  Output length: {len(output)} samples")
    assert len(output) == len(saw), "Output length mismatch"
    assert rms > 0.001, "Output too quiet — filter bank produced silence"
    print("  OK")
    return output


if __name__ == "__main__":
    demo()