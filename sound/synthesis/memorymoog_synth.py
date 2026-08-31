"""Stacked-oscillator Memorymoog-style synthesizer — Cherry Audio Memorymode 2 logic.

Replicable logic from Memorymode 2 (Synthtopia 2026-08-29), a software
expansion of the Moog Memorymoog: a polyphonic analog-modeling synth whose
signature sound comes from **stacking three oscillators per voice** with a
dedicated **whole-tone detune mode** (the 3 oscillators are tuned to form
a major-2nd/whole-tone cluster for huge unison), a per-voice mix of
saw/pulse/triangle waveforms, and the Memorymoog's "3/6/9 voice" doubling
selector (each of 3 voices may be doubled/tripled).

What is replicated here:
- Per-voice 3-oscillator stack with two detune strategies:
  * ``unison``: narrow symmetric detune (cents) around the base pitch.
  * ``whole_tone``: oscillators locked to -/+ a whole tone (major 2nd,
    ratio 2^(2/12)) from the base — the Memorymoog signature cluster.
- Per-oscillator waveform (saw / pulse / triangle) and level mix.
- 4-pole analog-style lowpass (cascaded one-pole) with resonance drive.
- Voice doubling: "3 voices" mode renders each note through 1, 2, or 3
  stacked voices (polyphonic thickening), the Memorymoog voice-count trick.

Not replicated: the exact Curtis CEM3340 filter curve, the LFO/sample-hold
mod matrix, arpeggiator, preset library (UI/content concerns).

Usage:
    from sound.synthesis.memorymoog_synth import MemorymoogVoice

    v = MemorymoogVoice(sample_rate=44100)
    v.detune_mode = "whole_tone"
    v.osc_levels = (1.0, 0.8, 0.8)
    audio = v.render_note(freq=220.0, duration=1.0, doubling=3)
"""

from typing import Tuple

import numpy as np

__all__ = ["MemorymoogVoice", "WHOLE_TONE_CENTS"]


WHOLE_TONE_CENTS = 200.0  # major 2nd == 2 semitones == 200 cents


class MemorymoogVoice:
    """Three-stacked-oscillator analog-style voice with whole-tone detune mode.

    Parameters
    ----------
    sample_rate : int
        Sampling rate in Hz.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self.detune_mode: str = "unison"      # "unison" | "whole_tone"
        self.unison_cents: float = 6.0        # ± detune for unison mode
        self.waveforms: Tuple[str, str, str] = ("saw", "saw", "saw")
        self.osc_levels: Tuple[float, float, float] = (1.0, 0.8, 0.8)
        # filter
        self.cutoff: float = 2000.0
        self.resonance: float = 0.4
        # envelope
        self.attack: float = 0.005
        self.decay: float = 0.25
        self.sustain: float = 0.7
        self.release: float = 0.3

    # -- tuning ------------------------------------------------------------- #
    def _osc_detune(self, index: int) -> float:
        """Return detune (in cents) for oscillator ``index`` (0..2).

        unison: narrow symmetric detune centered on the middle oscillator.
        whole_tone: offsets at -1, 0, +1 whole tones from the base pitch.
        """
        if self.detune_mode == "whole_tone":
            return (index - 1) * WHOLE_TONE_CENTS
        # unison: symmetric cents around base
        if index == 1:
            return 0.0
        if index == 0:
            return -self.unison_cents
        return +self.unison_cents

    # -- oscillators -------------------------------------------------------- #
    def _osc(self, waveform: str, freq: float, n: int) -> np.ndarray:
        """Generate one oscillator cycle buffer (freq is exact, applied detune done by caller)."""
        phase = 2 * np.pi * freq * np.arange(n) / self.sr
        if waveform == "saw":
            x = (phase / np.pi) % 2.0 - 1.0  # -1..1 saw (band-limited-ish via polyblep skip)
            return x
        if waveform == "triangle":
            x = (phase / np.pi) % 2.0
            return 1.0 - 4.0 * np.abs(x - 0.5)
        if waveform == "pulse":
            x = (phase / np.pi) % 2.0
            return np.where(x < 0.5, 1.0, -1.0)
        if waveform == "sine":
            return np.sin(phase)
        raise ValueError(f"unknown waveform {waveform}")

    # -- filter ------------------------------------------------------------- #
    def _lowpass4(self, x: np.ndarray) -> np.ndarray:
        """Cascaded 4-pole one-pole lowpass with resonance (Moog-ish 24 dB/oct)."""
        sr = self.sr
        fc = min(self.cutoff, sr * 0.45)
        # resonance feedback
        k = 4.0 * self.resonance
        buf = np.zeros(4)
        y = np.zeros(len(x))
        g = np.tan(np.pi * fc / sr)  # BLT-ish coefficient
        a1 = 1.0 / (1.0 + g)
        for i, s in enumerate(x):
            inp = s - k * buf[3]
            for p in range(4):
                buf[p] = a1 * (g * (inp - buf[p]) + buf[p])
                inp = buf[p]
            y[i] = buf[3]
        return y

    # -- envelope ----------------------------------------------------------- #
    def _env(self, n: int) -> np.ndarray:
        """Simple ADSR (attack->decay->sustain, truncated release)."""
        a = max(1, int(self.attack * self.sr))
        d = max(1, int(self.decay * self.sr))
        e = np.empty(n)
        if n <= a + d:
            e[:] = 0.0
            return e
        e[:a] = np.linspace(0.0, 1.0, a)
        e[a:a + d] = np.linspace(1.0, self.sustain, d)
        e[a + d:] = self.sustain
        return e

    # -- render ------------------------------------------------------------- #
    def render_note(self, freq: float, duration: float,
                    doubling: int = 1) -> np.ndarray:
        """Render one note.

        Args:
            freq: Base frequency in Hz (note pitch).
            duration: Note duration in seconds.
            doubling: 1..3 — stack this many identical voices (voice-count
                thickening). 1 = single voice (Memorymoog "3 voices").

        Returns:
            float32 mono audio in [-1, 1].
        """
        n = int(duration * self.sr)
        if n <= 0:
            return np.zeros(0, dtype=np.float32)
        doubling = max(1, int(doubling))
        mix = np.zeros(n)
        for d in range(doubling):
            osc_mix = np.zeros(n)
            for i, wave in enumerate(self.waveforms):
                cents = self._osc_detune(i)
                # doubling adds a small per-voice detune (spread across the
                # stack) so doubled voices chorusing — Memorymoog 6/9 voice mode
                if doubling > 1:
                    cents += (d - (doubling - 1) / 2.0) * 2.5
                f = freq * (2.0 ** (cents / 1200.0))
                osc_mix += self.osc_levels[i] * self._osc(wave, f, n)
            env = self._env(n)
            voice = self._lowpass4(osc_mix) * env
            # normalize each stacked voice
            peak = np.max(np.abs(voice)) if len(voice) else 0.0
            if peak > 1e-6:
                voice = voice / peak
            mix += voice
        if len(mix):
            peak = np.max(np.abs(mix))
            if peak > 1e-6:
                mix = mix / peak
        return mix.astype(np.float32)


def demo() -> str:
    """Render two short notes (unison vs whole-tone) and report RMS."""
    import numpy as np
    v = MemorymoogVoice(sample_rate=44100)
    v.detune_mode = "unison"
    a = v.render_note(220.0, 0.5, doubling=1)
    v.detune_mode = "whole_tone"
    b = v.render_note(220.0, 0.5, doubling=3)
    return f"unison rms={np.sqrt(np.mean(a**2)):.4f} whole_tone x3 rms={np.sqrt(np.mean(b**2)):.4f} len={len(b)}"


if __name__ == "__main__":
    print(demo())
