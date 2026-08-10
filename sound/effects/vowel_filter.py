"""Vowel filter bank — formant-based phonetic vowel filtering (Vowel Blender style).

Implements phonetic vowel filters using F1/F2/F3 formant frequencies.
Blending between vowels = crossfading filter coefficients.

Reference: surveillance report Aug 2026, UB DSP Vowel Blender.

Usage:
    from sound.effects.vowel_filter import VowelFilterBank, VOWEL_FORMANTS

    vfb = VowelFilterBank(sample_rate=44100)
    audio_vowel = vfb.process(audio, vowel='a')
    audio_blend = vfb.blend(audio, 'a', 'i', amount=0.5)
"""

import numpy as np
from typing import Dict, Optional, List, Tuple

__all__ = ["VOWEL_FORMANTS", "VowelFilterBank"]

# Standard phonetic formant frequencies (F1, F2, F3) in Hz
# Source: standard phonetic values (Peterson & Barney 1952 / Catford)
VOWEL_FORMANTS: Dict[str, Tuple[float, float, float]] = {
    "a": (730.0, 1090.0, 2440.0),    # /a/ father
    "e": (530.0, 1840.0, 2480.0),    # /e/ bet
    "i": (270.0, 2290.0, 3010.0),    # /i/ see
    "o": (570.0, 840.0, 2410.0),     # /o/ boat
    "u": (300.0, 870.0, 2240.0),     # /u/ boot
    "ae": (660.0, 1720.0, 2410.0),   # /ae/ cat
    "schwa": (500.0, 1500.0, 2500.0),  # /ə/ about
    "open": (850.0, 1200.0, 2800.0),  # open mouth
    "closed": (250.0, 2100.0, 2900.0), # closed mouth
    "front": (400.0, 2400.0, 3200.0),  # fronted
    "back": (700.0, 1000.0, 2300.0),   # backed
}


class VowelFilterBank:
    """Bank of phonetic vowel filters.

    Each vowel = 3 bandpass filters at F1/F2/F3 (standard phonetic values).
    Blend = crossfade filter coefficients between two vowels.

    Parameters
    ----------
    sample_rate : int
        Sampling rate in Hz.
    q : float
        Bandpass Q factor (default 4.0 — formant width).
    """

    def __init__(self, sample_rate: int = 44100, q: float = 4.0):
        self.sr = sample_rate
        self.q = q

    def _bandpass(self, audio: np.ndarray, freq: float, q: float) -> np.ndarray:
        """Apply a 2nd-order bandpass filter at `freq`."""
        from scipy.signal import butter, lfilter
        nyq = 0.5 * self.sr
        if freq >= nyq or freq <= 0:
            return np.zeros_like(audio)
        # bandwidth in Hz
        bw = freq / q
        low = max(1e-6, (freq - bw / 2) / nyq)
        high = min(1.0 - 1e-6, (freq + bw / 2) / nyq)
        b, a = butter(2, [low, high], btype='band')
        return lfilter(b, a, audio)

    def process(self, audio: np.ndarray, vowel: str,
                character: float = 0.0) -> np.ndarray:
        """Filter audio through a vowel's formant frequencies.

        Parameters
        ----------
        audio : np.ndarray
            Input audio (1D).
        vowel : str
            Vowel name from VOWEL_FORMANTS.
        character : float
            0-1 character amount (transpose formants = "alien" knob).

        Returns
        -------
        np.ndarray
            Filtered audio.
        """
        if vowel not in VOWEL_FORMANTS:
            raise ValueError(f"Unknown vowel: {vowel}. Use: {list(VOWEL_FORMANTS.keys())}")
        f1, f2, f3 = VOWEL_FORMANTS[vowel]
        # character knob: transpose formants up (alien voice)
        if character > 0:
            shift = 1.0 + character * 0.5  # up to +50%
            f1, f2, f3 = f1 * shift, f2 * shift, f3 * shift
        out = np.zeros_like(audio)
        for f in (f1, f2, f3):
            out += self._bandpass(audio, f, self.q)
        # normalize to avoid clipping
        peak = np.max(np.abs(out)) if len(out) else 1.0
        if peak > 0:
            out = out / peak * (np.max(np.abs(audio)) if len(audio) else 1.0)
        return out

    def blend(self, audio: np.ndarray,
              vowel1: str, vowel2: str,
              amount: float = 0.5) -> np.ndarray:
        """Blend between two vowel filters by crossfading coefficients.

        Parameters
        ----------
        audio : np.ndarray
            Input audio.
        vowel1, vowel2 : str
            Vowels to blend.
        amount : float
            0.0 = pure vowel1, 1.0 = pure vowel2.

        Returns
        -------
        np.ndarray
            Blended output.
        """
        amount = np.clip(amount, 0.0, 1.0)
        if vowel1 not in VOWEL_FORMANTS or vowel2 not in VOWEL_FORMANTS:
            raise ValueError(f"Unknown vowel. Use: {list(VOWEL_FORMANTS.keys())}")
        v1 = self.process(audio, vowel1)
        v2 = self.process(audio, vowel2)
        return v1 * (1.0 - amount) + v2 * amount

    def xy_position(self, audio: np.ndarray,
                    x: float, y: float) -> np.ndarray:
        """Filter based on phonetic chart position (X/Y pad).

        x : 0-1 front/back (0=front, 1=back)
        y : 0-1 open/closed (0=open, 1=closed)

        Uses nearest-vowel interpolation (like Vowel Blender's cursor).
        """
        # target formants interpolated from chart corners
        front_formants = VOWEL_FORMANTS["front"]  # front
        back_formants = VOWEL_FORMANTS["back"]    # back
        open_formants = VOWEL_FORMANTS["open"]    # open
        closed_formants = VOWEL_FORMANTS["closed"]  # closed

        x = np.clip(x, 0.0, 1.0)
        y = np.clip(y, 0.0, 1.0)

        # interpolate: horizontal = front/back, vertical = open/closed
        f_fb = [a + (b - a) * x for a, b in zip(front_formants, back_formants)]
        f_oc = [a + (b - a) * y for a, b in zip(open_formants, closed_formants)]
        f1, f2, f3 = [(a + b) / 2 for a, b in zip(f_fb, f_oc)]

        out = np.zeros_like(audio)
        for f in (f1, f2, f3):
            out += self._bandpass(audio, f, self.q)
        peak = np.max(np.abs(out)) if len(out) else 1.0
        if peak > 0:
            out = out / peak * (np.max(np.abs(audio)) if len(audio) else 1.0)
        return out
