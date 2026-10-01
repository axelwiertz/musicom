# -*- coding: utf-8 -*-
"""
Haas Zone Processor — multi-tap modulated short-delay processor.

Replicates the Verbos Electronics Haas Zone Processor concept:
- 3-tap delay bank (Tap1: 0.1–20 ms, Tap2 chained +1–20 ms, Tap3: 9–42 ms)
- Voltage-controlled LFO modulator (sine, triangle, square, sawtooth; 0.0167 Hz to audio rate)
- Envelope follower on input
- 2-pole HP + 2-pole LP cascaded bandpass filter (sweepable freq + bandwidth)
- VC mixer blending dry + 3 taps
- Feedback path through BPF

Inspired by the Marshall Time Modulator / Verbos Electronics Haas Zone Processor.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Callable


# ---------------------------------------------------------------------------
# LFO — modulation oscillator
# ---------------------------------------------------------------------------

class ModulationLFO:
    """Voltage-controlled LFO for delay-time modulation.

    Waveforms: sine, triangle, square, sawtooth.
    Frequency range: ~0.0167 Hz (1 cycle/min) to audio rate (~500 Hz usable).
    Output range: 0–1 (unipolar) or -1..1 (bipolar).
    """

    WAVEFORMS = ("sine", "triangle", "square", "sawtooth")

    def __init__(self, frequency: float = 1.0, waveform: str = "sine",
                 phase: float = 0.0, bipolar: bool = True):
        if waveform not in self.WAVEFORMS:
            raise ValueError(f"waveform must be one of {self.WAVEFORMS}")
        self.frequency = frequency
        self.waveform = waveform
        self.phase = phase
        self.bipolar = bipolar

    def render(self, num_samples: int, sr: int) -> np.ndarray:
        """:return array of length num_samples with modulator values."""
        t = np.arange(num_samples) / sr
        angle = 2.0 * np.pi * self.frequency * t + self.phase

        if self.waveform == "sine":
            raw = np.sin(angle)
        elif self.waveform == "triangle":
            raw = 2.0 * np.abs(2.0 * ((angle / (2.0 * np.pi) + 0.25) % 1.0) - 1.0) - 1.0
        elif self.waveform == "square":
            raw = np.where(np.sin(angle) >= 0, 1.0, -1.0)
        elif self.waveform == "sawtooth":
            raw = 2.0 * ((angle / (2.0 * np.pi)) % 1.0) - 1.0
        else:
            raw = np.sin(angle)

        if not self.bipolar:
            raw = raw * 0.5 + 0.5
        return raw


# ---------------------------------------------------------------------------
# Envelope Follower
# ---------------------------------------------------------------------------

class EnvelopeFollower:
    """Simple RMS-based envelope follower with adjustable attack/release."""

    def __init__(self, attack_ms: float = 10.0, release_ms: float = 100.0, sr: int = 44100):
        self.attack = attack_ms / 1000.0
        self.release = release_ms / 1000.0
        self.sr = sr
        self._env: float = 0.0

    def process(self, block: np.ndarray) -> np.ndarray:
        """:return envelope array matching block shape (0..1 normalized)."""
        abs_sig = np.abs(block)
        out = np.empty_like(block)
        attack_coeff = 1.0 - np.exp(-1.0 / (self.attack * self.sr))
        release_coeff = 1.0 - np.exp(-1.0 / (self.release * self.sr))
        for i, val in enumerate(abs_sig):
            if val > self._env:
                self._env += attack_coeff * (val - self._env)
            else:
                self._env += release_coeff * (val - self._env)
            out[i] = self._env
        return out


# ---------------------------------------------------------------------------
# Two-pole bandpass filter (cascaded HP + LP)
# ---------------------------------------------------------------------------

class BandpassFilter:
    """Cascaded 2-pole high-pass → 2-pole low-pass bandpass filter.

    Frequency sweepable (20–20000 Hz), bandwidth 0.01–1.0 (fraction of octave).
    Uses biquad sections.
    """

    def __init__(self, frequency: float = 1000.0, bandwidth: float = 0.5, sr: int = 44100):
        self.frequency = frequency
        self.bandwidth = max(0.01, min(1.0, bandwidth))
        self.sr = sr
        self._hp_state = np.zeros(4)  # 2 biquad delay states for HP
        self._lp_state = np.zeros(4)  # 2 biquad delay states for LP
        self._update_coeffs()

    def _update_coeffs(self):
        f = max(20.0, min(self.frequency, 20000.0))
        bw = self.bandwidth
        # High-pass: 2nd-order Butterworth at f
        w0 = 2.0 * np.pi * f / self.sr
        alpha = np.sin(w0) * np.sqrt(2.0) / 2.0  # Q = 0.707
        cos_w0 = np.cos(w0)
        self._hp_b = np.array([(1.0 + cos_w0) / 2.0,
                               -(1.0 + cos_w0),
                               (1.0 + cos_w0) / 2.0])
        self._hp_a = np.array([1.0 + alpha, -2.0 * cos_w0, 1.0 - alpha])
        # Low-pass: 2nd-order at f * (1 + bw/2) — stretch upper edge
        lp_f = min(f * (1.0 + bw / 2.0), 20000.0)
        w1 = 2.0 * np.pi * lp_f / self.sr
        alpha_lp = np.sin(w1) * np.sqrt(2.0) / 2.0
        cos_w1 = np.cos(w1)
        self._lp_b = np.array([(1.0 - cos_w1) / 2.0,
                               1.0 - cos_w1,
                               (1.0 - cos_w1) / 2.0])
        self._lp_a = np.array([1.0 + alpha_lp, -2.0 * cos_w1, 1.0 - alpha_lp])

    def process(self, x: np.ndarray) -> np.ndarray:
        """Apply HP → LP cascade."""
        self._update_coeffs()
        y = np.empty_like(x)
        # biquad HP
        for i in range(len(x)):
            in_s = x[i]
            out_s = (self._hp_b[0] * in_s + self._hp_state[0]) / self._hp_a[0]
            self._hp_state[0] = self._hp_b[1] * in_s - self._hp_a[1] * out_s + self._hp_state[1]
            self._hp_state[1] = self._hp_b[2] * in_s - self._hp_a[2] * out_s
            y[i] = out_s
        # biquad LP
        z = np.empty_like(y)
        for i in range(len(y)):
            in_s = y[i]
            out_s = (self._lp_b[0] * in_s + self._lp_state[0]) / self._lp_a[0]
            self._lp_state[0] = self._lp_b[1] * in_s - self._lp_a[1] * out_s + self._lp_state[1]
            self._lp_state[1] = self._lp_b[2] * in_s - self._lp_a[2] * out_s
            z[i] = out_s
        return z


# ---------------------------------------------------------------------------
# Haas Zone Processor — main class
# ---------------------------------------------------------------------------

@dataclass
class TapConfig:
    """Configuration for one delay tap."""
    delay_ms: float = 10.0        # delay time in milliseconds
    gain: float = 0.5             # tap gain (0..1)
    modulate_depth: float = 0.0   # LFO modulation depth (fraction of delay_ms)
    modulate_enabled: bool = True # whether LFO modulates this tap


class HaasZoneProcessor:
    """Multi-tap modulated short-delay processor.

    Architecture::

        input ─┬─→ [Envelope Follower] ─→ LFO rate mod
               ├─→ Delay Tap1 (0.1–20 ms) ─→┐
               ├─→ Delay Tap2 (1–20 ms chained) ─→┤
               ├─→ Delay Tap3 (9–42 ms) ─→┤
               └─→ Dry ─→┐
                         [VC Mixer]
                            ↓
                    [Bandpass Filter] ─→ feedback → Tap1 input
                            ↓
                         output

    Parameters
    ----------
    sr : int
        Sample rate.
    tap1_ms, tap2_ms, tap3_ms : float
        Initial delay times in ms.
    dry_gain, tap1_gain, tap2_gain, tap3_gain : float
        Mix gains.
    feedback : float
        Feedback gain from BPF output back into delay input (0..0.99).
    lfo_freq : float
        LFO frequency in Hz.
    lfo_waveform : str
        One of 'sine', 'triangle', 'square', 'sawtooth'.
    lfo_depth : float
        Global LFO depth (fraction of delay time, 0..1).
    bp_freq : float
        Bandpass center frequency in Hz.
    bp_bandwidth : float
        Bandwidth fraction (0.01..1.0).
    """

    def __init__(self, sr: int = 44100,
                 tap1_ms: float = 5.0, tap2_ms: float = 12.0, tap3_ms: float = 25.0,
                 dry_gain: float = 0.3, tap1_gain: float = 0.6, tap2_gain: float = 0.4,
                 tap3_gain: float = 0.3, feedback: float = 0.15,
                 lfo_freq: float = 1.0, lfo_waveform: str = "sine",
                 lfo_depth: float = 0.3,
                 bp_freq: float = 2000.0, bp_bandwidth: float = 0.5):
        self.sr = sr
        self.dry_gain = dry_gain
        self.feedback = max(0.0, min(0.99, feedback))

        # Taps
        self.taps = [
            TapConfig(delay_ms=tap1_ms, gain=tap1_gain, modulate_depth=0.4),
            TapConfig(delay_ms=tap2_ms, gain=tap2_gain, modulate_depth=0.3),
            TapConfig(delay_ms=tap3_ms, gain=tap3_gain, modulate_depth=0.2),
        ]

        # Modulation LFO
        self.lfo = ModulationLFO(frequency=lfo_freq, waveform=lfo_waveform,
                                 bipolar=True)
        self.lfo_depth = max(0.0, min(1.0, lfo_depth))

        # Envelope follower
        self.env_follower = EnvelopeFollower(attack_ms=10.0, release_ms=100.0, sr=sr)

        # Bandpass filter
        self.bp_filter = BandpassFilter(frequency=bp_freq, bandwidth=bp_bandwidth, sr=sr)

        # Internal delay lines (max delay 50 ms = ~2205 samples @ 44100)
        self._max_delay_samples = int(0.050 * sr) + 1
        self._delay_buf = np.zeros(self._max_delay_samples)
        self._delay_pos = 0

    def _read_delay(self, delay_samples: float) -> float:
        """Linear-interpolated read from circular delay buffer."""
        pos = self._delay_pos - delay_samples
        while pos < 0:
            pos += self._max_delay_samples
        frac = pos - int(pos)
        idx = int(pos) % self._max_delay_samples
        nxt = (idx + 1) % self._max_delay_samples
        return self._delay_buf[idx] * (1.0 - frac) + self._delay_buf[nxt] * frac

    def _write_delay(self, sample: float):
        self._delay_buf[self._delay_pos] = sample
        self._delay_pos = (self._delay_pos + 1) % self._max_delay_samples

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio block through the Haas zone.

        Parameters
        ----------
        audio : ndarray, shape (N,) or (N, C)
            Mono audio block.

        Returns
        -------
        output : ndarray, shape (N,)
            Processed stereo or mono output.
        """
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)  # collapse to mono

        out = np.empty_like(audio)
        mod = self.lfo.render(len(audio), self.sr)
        env = self.env_follower.process(audio)

        bp_input_accum = 0.0
        for i in range(len(audio)):
            # LFO modulation value for this sample (bipolar -1..1)
            lfo_val = mod[i] * self.lfo_depth

            # Envelope modulates LFO rate slightly (normalized)
            env_mod = env[i] * 0.3  # subtle

            # --- tap processing ---
            wet = 0.0
            for tap in self.taps:
                delay_s = (tap.delay_ms / 1000.0) * (1.0 + lfo_val * tap.modulate_depth + env_mod)
                delay_s = max(0.00005, min(0.050, delay_s))  # clamp 0.05–50 ms
                delay_samp = delay_s * self.sr
                tap_sig = self._read_delay(delay_samp)
                wet += tap_sig * tap.gain

            # Dry + wet mix
            sample = audio[i] * self.dry_gain + wet

            # Bandpass filter
            sample = self.bp_filter.process(np.array([sample]))[0]

            # Feedback
            fb = sample * self.feedback
            self._write_delay(audio[i] + bp_input_accum + fb)
            bp_input_accum = 0.0

            out[i] = sample

        return out


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo(output_wav: str = "/tmp/haas_zone_demo.wav", duration: float = 4.0):
    """Generate a demo: dry pulse train through Haas Zone Processor."""
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Input: decaying impulse train (pulse every 0.5 s)
    audio = np.zeros_like(t)
    for start in np.arange(0, duration, 0.5):
        idx = int(start * sr)
        if idx < len(audio):
            audio[idx] = 0.8
            # short exponential tail
            tail_len = min(int(0.05 * sr), len(audio) - idx)
            audio[idx:idx + tail_len] += 0.8 * np.exp(-np.arange(tail_len) / (0.01 * sr))

    hz = HaasZoneProcessor(sr=sr, tap1_ms=6.0, tap2_ms=15.0, tap3_ms=30.0,
                           dry_gain=0.2, tap1_gain=0.7, tap2_gain=0.5, tap3_gain=0.3,
                           feedback=0.2, lfo_freq=2.5, lfo_waveform="triangle",
                           lfo_depth=0.3, bp_freq=3000.0, bp_bandwidth=0.4)
    output = hz.process(audio)

    # Normalize
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * 0.95

    try:
        import soundfile as sf
        sf.write(output_wav, output, sr)
        print(f"Wrote {output_wav}")
    except ImportError:
        try:
            from scipy.io import wavfile
            wavfile.write(output_wav, sr, (output * 32767).astype(np.int16))
            print(f"Wrote {output_wav} (scipy)")
        except ImportError:
            import struct, wave
            with wave.open(output_wav, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(struct.pack(f"<{len(output)}h",
                                           *(np.clip(output * 32767, -32768, 32767).astype(int))))
            print(f"Wrote {output_wav} (built-in wave)")
    print("HaasZoneProcessor demo done.")
    return output_wav


if __name__ == "__main__":
    demo()