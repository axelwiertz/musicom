"""Tape delay + sample playback + drum machine — VST Classics / Sculpture style.

Implements:
- TapeDelay: tape-style delay with saturation + wow/flutter (Karlette)
- SamplePlayer: sample playback with pitch shifting (Sculpture/Sonuscore)
- DrumMachine: LM-7-style sample drum patterns

Reference: surveillance report Aug 2026, VST Classics (Karlette, LM-7),
Sonuscore The Sculpture (sample playback).

Usage:
    from sound.effects.tape_delay import TapeDelay, SamplePlayer, DrumMachine

    td = TapeDelay(sample_rate=44100)
    audio_out = td.process(audio, delay_seconds=0.25, feedback=0.4)
"""

import numpy as np
from typing import List, Optional, Tuple, Dict

__all__ = ["TapeDelay", "SamplePlayer", "DrumMachine"]


class TapeDelay:
    """Tape-style delay with saturation and wow/flutter modulation.

    Reference: Steinberg Karlette (tape delay).

    Parameters
    ----------
    sample_rate : int
        Sampling rate.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self._buffer: Optional[np.ndarray] = None
        self._write_idx = 0

    def process(self, audio: np.ndarray,
                delay_seconds: float = 0.25,
                feedback: float = 0.4,
                saturation: float = 0.3,
                wow_rate: float = 0.5,
                flutter_rate: float = 6.0) -> np.ndarray:
        """Process audio through tape delay.

        Parameters
        ----------
        audio : np.ndarray
            Input audio (1D).
        delay_seconds : float
            Delay time in seconds.
        feedback : float
            Feedback amount (0-1).
        saturation : float
            Tape saturation amount (0-1), soft-clip waveshaper.
        wow_rate : float
            Slow pitch modulation rate (Hz) — tape wow.
        flutter_rate : float
            Fast pitch modulation rate (Hz) — tape flutter.

        Returns
        -------
        np.ndarray
            Delayed audio (dry + wet).
        """
        n = len(audio)
        delay_samples = max(1, int(delay_seconds * self.sr))
        out_len = n + delay_samples  # capture feedback tail
        if self._buffer is None or len(self._buffer) < delay_samples + out_len:
            self._buffer = np.zeros(delay_samples + out_len + self.sr)
            self._write_idx = 0

        buf = self._buffer
        t = np.arange(out_len) / self.sr
        # wow/flutter: modulate the read position
        wow = 1.0 + 0.002 * np.sin(2 * np.pi * wow_rate * t)
        flutter = 1.0 + 0.0005 * np.sin(2 * np.pi * flutter_rate * t)
        mod = wow * flutter

        out = np.zeros(out_len)
        wi = self._write_idx
        for i in range(out_len):
            # write input + feedback into buffer
            src = audio[i] if i < n else 0.0
            fb = out[i - delay_samples] if i >= delay_samples else 0.0
            buf[wi] = src + fb
            # read delayed (modulated)
            read_delay = int(delay_samples * mod[i])
            ri = (wi - read_delay) % len(buf)
            delayed = buf[ri]
            # tape saturation (soft clip)
            sat = np.tanh(delayed * (1.0 + 3.0 * saturation)) / np.tanh(1.0 + 3.0 * saturation)
            out[i] = delayed * (1.0 - feedback) + sat * feedback
            wi = (wi + 1) % len(buf)
        self._write_idx = wi
        return out.astype(np.float32)


class SamplePlayer:
    """Sample playback with pitch shifting (time-stretch-free).

    Reference: Sonuscore The Sculpture (sample playback), LM-7 (drum samples).

    Parameters
    ----------
    sample_rate : int
        Sampling rate.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self._sample: Optional[np.ndarray] = None

    def load(self, sample: np.ndarray):
        """Load a sample buffer (1D float in [-1, 1])."""
        self._sample = np.asarray(sample, dtype=float)

    def play(self, duration: float, pitch_shift: float = 1.0,
             start_offset: float = 0.0, volume: float = 1.0) -> np.ndarray:
        """Play the loaded sample.

        Parameters
        ----------
        duration : float
            Output duration in seconds.
        pitch_shift : float
            Playback rate multiplier (1.0 = original, 2.0 = octave up).
        start_offset : float
            Fractional offset into the sample (0-1).
        volume : float
            Output gain.

        Returns
        -------
        np.ndarray
            Played sample (looped if shorter than duration).
        """
        if self._sample is None:
            raise ValueError("No sample loaded — call load() first")
        n = int(duration * self.sr)
        idx = np.arange(n) / self.sr
        # sample position in seconds
        pos = start_offset * len(self._sample) / self.sr + idx * pitch_shift
        pos_sec = pos * self.sr
        pos_sec = np.mod(pos_sec, len(self._sample))  # loop
        out = np.interp(pos_sec, np.arange(len(self._sample)), self._sample)
        return (out * volume).astype(np.float32)

    def play_adsr(self, duration: float, pitch_shift: float = 1.0,
                  attack: float = 0.01, release: float = 0.1,
                  volume: float = 1.0) -> np.ndarray:
        """Play sample with ADSR envelope."""
        raw = self.play(duration, pitch_shift, volume=volume)
        n = len(raw)
        env = np.ones(n)
        a = int(attack * self.sr)
        r = int(release * self.sr)
        if a > 0:
            env[:a] = np.linspace(0, 1, a)
        if r > 0:
            env[-r:] = np.linspace(1, 0, r)
        return (raw * env).astype(np.float32)


class DrumMachine:
    """Simple sample drum machine (LM-7 style).

    Plays a pattern of drum hits (kick/snare/hat) from loaded samples
    or synthesized impulses.

    Parameters
    ----------
    sample_rate : int
        Sampling rate.
    bpm : float
        Tempo.
    """

    def __init__(self, sample_rate: int = 44100, bpm: float = 120.0):
        self.sr = sample_rate
        self.bpm = bpm
        self.samples: Dict = {}

    def add_sample(self, name: str, sample: np.ndarray):
        """Register a drum sample."""
        self.samples[name] = np.asarray(sample, dtype=float)

    def _default_kick(self) -> np.ndarray:
        """Synthesize a kick drum (sine pitch drop)."""
        n = int(0.3 * self.sr)
        t = np.arange(n) / self.sr
        freq = 150.0 * np.exp(-t * 20.0) + 40.0
        phase = 2 * np.pi * np.cumsum(freq) / self.sr
        return np.sin(phase) * np.exp(-t * 12.0)

    def _default_snare(self) -> np.ndarray:
        """Synthesize a snare (noise burst + tone)."""
        n = int(0.2 * self.sr)
        t = np.arange(n) / self.sr
        noise = np.random.default_rng(0).uniform(-1, 1, n) * np.exp(-t * 40.0)
        tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30.0)
        return (0.7 * noise + 0.3 * tone).astype(np.float32)

    def _default_hat(self) -> np.ndarray:
        """Synthesize a hi-hat (high-passed noise)."""
        n = int(0.1 * self.sr)
        t = np.arange(n) / self.sr
        noise = np.random.default_rng(1).uniform(-1, 1, n) * np.exp(-t * 80.0)
        # crude high-pass: diff
        hp = np.diff(noise, prepend=0)
        return (hp * 0.5).astype(np.float32)

    def get_sample(self, name: str) -> np.ndarray:
        """Get a sample (synthesized if not registered)."""
        if name in self.samples:
            return self.samples[name]
        if name == "kick":
            return self._default_kick()
        if name == "snare":
            return self._default_snare()
        if name == "hat":
            return self._default_hat()
        raise ValueError(f"Unknown drum: {name}")

    def play_pattern(self, pattern: List[str],
                     steps_per_bar: int = 16, bars: int = 1,
                     volume: float = 1.0) -> np.ndarray:
        """Play a drum pattern.

        Parameters
        ----------
        pattern : list of str
            Step labels ('kick', 'snare', 'hat', or '' for rest).
            Length must be >= steps_per_bar (looped).
        steps_per_bar : int
            Steps per bar (16 = 16th notes).
        bars : int
            Number of bars.

        Returns
        -------
        np.ndarray
            Mixed drum audio.
        """
        step_dur = 60.0 / self.bpm / 4.0  # 16th note
        n_steps = steps_per_bar * bars
        out_len = int(n_steps * step_dur * self.sr)
        out = np.zeros(out_len)

        for i in range(n_steps):
            step = pattern[i % len(pattern)]
            if not step:
                continue
            sample = self.get_sample(step)
            s0 = int(i * step_dur * self.sr)
            s1 = min(s0 + len(sample), out_len)
            if s1 > s0:
                out[s0:s1] += sample[:s1 - s0]
        peak = np.max(np.abs(out)) if len(out) else 1.0
        if peak > 0:
            out = out / peak * volume
        return out.astype(np.float32)
