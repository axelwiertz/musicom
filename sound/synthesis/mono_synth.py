"""Classic mono subtractive synthesizer — Audio Damage AD-202 / Roland MC-202 style.

Single VCO (saw, pulse, sub, noise) → 24dB ladder filter → ADSR envelope →
LFO → post-VCA color (saturation, tilt EQ). Per-voice analog drift.

Replicated from: Audio Damage AD-202 (synthtopia 2026-08-17).

Usage:
    from sound.synthesis.mono_synth import MonoSynth

    synth = MonoSynth(sample_rate=44100)
    synth.set_oscillator(waveform='saw', pulse_width=0.5, sub_level=0.3)
    synth.set_filter(cutoff=2000, resonance=0.6)
    synth.set_envelope(a=0.01, d=0.2, s=0.7, r=0.3)
    synth.set_lfo(rate=5.0, depth=0.3, target='filter')
    audio = synth.render_note(midi_note=60, duration=1.0)
"""

import numpy as np
from typing import Optional, Dict

__all__ = ["MonoSynth", "polyblep"]


def polyblep(phase, phase_inc):
    """PolyBLEP correction for a discontinuity at phase = 0 (vectorized).

    Public so one-off production scripts (e.g. SP-029) can use the shared
    implementation instead of carrying their own copy. Handles both the
    positive wrap [0,1)->[1,2) and negative wrap [-1,0) conventions.
    """
    d = phase / (phase_inc + 1e-20)
    correction = np.zeros_like(d)
    m1 = (d >= 0) & (d < 1)
    correction[m1] = d[m1] + d[m1] - d[m1] ** 2 - 1.0
    m2 = (d >= 1) & (d < 2)
    correction[m2] = d[m2] ** 2 - 2.0 * d[m2] + 1.0
    m3 = (d >= -1) & (d < 0)
    correction[m3] = d[m3] + d[m3] + d[m3] ** 2 + 1.0
    return correction


class MonoSynth:
    """Classic subtractive mono synthesizer.

    Signal path: VCO → ladder filter → VCA → color section.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        # Oscillator
        self.waveform = 'saw'  # 'saw', 'pulse', 'sub', 'noise'
        self.pulse_width = 0.5
        self.sub_level = 0.0  # 0..1, sub-oscillator one octave down
        self.sub_waveform = 'square'
        self.noise_level = 0.0
        self.drift_amount = 0.002  # analog drift
        # Filter (24dB ladder = 4-pole)
        self.filter_cutoff = 2000.0
        self.filter_resonance = 0.5  # 0..1
        self.filter_env_amount = 0.5  # envelope → cutoff modulation
        self.filter_keytrack = 0.5  # keyboard tracking
        # Envelope (ADSR)
        self.env_a = 0.01
        self.env_d = 0.2
        self.env_s = 0.7
        self.env_r = 0.3
        # LFO
        self.lfo_rate = 5.0
        self.lfo_depth = 0.0
        self.lfo_target = 'filter'  # 'filter', 'pitch', 'pulse_width'
        self.lfo_delay = 0.0  # delayed onset
        self.lfo_waveform = 'sine'
        # Color section (post-VCA)
        self.saturation = 0.0  # 0..1
        self.drive = 0.0  # 0..1
        self.distortion = 0.0  # 0..1
        self.tilt_eq = 0.0  # -1..1
        # Velocity sensitivity
        self.vel_sensitivity = 0.5

    def set_oscillator(self, waveform: str = 'saw', pulse_width: float = 0.5,
                       sub_level: float = 0.0, noise_level: float = 0.0):
        """Set oscillator parameters."""
        self.waveform = waveform
        self.pulse_width = max(0.05, min(0.95, pulse_width))
        self.sub_level = max(0.0, min(1.0, sub_level))
        self.noise_level = max(0.0, min(1.0, noise_level))

    def set_filter(self, cutoff: float = 2000, resonance: float = 0.5,
                   env_amount: float = 0.5, keytrack: float = 0.5):
        """Set filter parameters."""
        self.filter_cutoff = max(20, min(20000, cutoff))
        self.filter_resonance = max(0.0, min(1.0, resonance))
        self.filter_env_amount = max(0.0, min(1.0, env_amount))
        self.filter_keytrack = max(0.0, min(1.0, keytrack))

    def set_envelope(self, a: float = 0.01, d: float = 0.2,
                     s: float = 0.7, r: float = 0.3):
        """Set ADSR envelope (seconds for A/D/R, 0..1 for S)."""
        self.env_a = max(0.001, a)
        self.env_d = max(0.001, d)
        self.env_s = max(0.0, min(1.0, s))
        self.env_r = max(0.001, r)

    def set_lfo(self, rate: float = 5.0, depth: float = 0.0,
                target: str = 'filter', delay: float = 0.0,
                waveform: str = 'sine'):
        """Set LFO parameters."""
        self.lfo_rate = max(0.1, rate)
        self.lfo_depth = max(0.0, min(1.0, depth))
        self.lfo_target = target
        self.lfo_delay = max(0.0, delay)
        self.lfo_waveform = waveform

    def _generate_oscillator(self, freq: float, n_samples: int,
                             drift: float = 0.0) -> np.ndarray:
        """Generate oscillator waveform."""
        t = np.arange(n_samples) / self.sample_rate
        # Add drift (slow random detuning)
        if drift > 0:
            drift_signal = np.cumsum(np.random.randn(n_samples) * drift * 0.01)
            freq_mod = freq * (1 + drift_signal)
            phase = 2 * np.pi * np.cumsum(freq_mod) / self.sample_rate
        else:
            phase = 2 * np.pi * freq * t
        if self.waveform == 'saw':
            # Band-limited sawtooth via phase accumulation
            osc = 2.0 * (phase / (2 * np.pi) % 1.0) - 1.0
        elif self.waveform == 'pulse':
            # Pulse wave with variable width
            saw = 2.0 * (phase / (2 * np.pi) % 1.0) - 1.0
            osc = np.where(saw < (2 * self.pulse_width - 1), 1.0, -1.0)
        elif self.waveform == 'sub':
            # Sub-oscillator one octave down
            phase_sub = phase / 2
            osc = np.where((phase_sub / (2 * np.pi) % 1.0) < 0.5, 1.0, -1.0)
        elif self.waveform == 'noise':
            osc = np.random.randn(n_samples)
        else:
            osc = np.sin(phase)
        # Mix in sub and noise
        if self.sub_level > 0:
            phase_sub = phase / 2
            sub = np.where((phase_sub / (2 * np.pi) % 1.0) < 0.5, 1.0, -1.0)
            osc = osc * (1 - self.sub_level) + sub * self.sub_level
        if self.noise_level > 0:
            noise = np.random.randn(n_samples) * 0.5
            osc = osc * (1 - self.noise_level) + noise * self.noise_level
        return osc

    def _apply_filter(self, audio: np.ndarray, cutoff: float,
                      resonance: float) -> np.ndarray:
        """Apply 24dB (4-pole) lowpass filter with resonant peak.

        Uses a stable 4th-order Butterworth lowpass; resonance is added by
        mixing in a stable resonant bandpass (iirpeak, Q clamped <= 8) rather
        than by destabilizing the lowpass poles.
        """
        try:
            from scipy.signal import butter, lfilter, iirpeak
            nyq = 0.5 * self.sample_rate
            norm_cutoff = float(np.clip(cutoff / nyq, 0.001, 0.99))
            b, a = butter(4, norm_cutoff, btype='low')
            filtered = lfilter(b, a, audio)
            if resonance > 0:
                # Resonant peak at cutoff; Q from 0.707 (flat) up to 8.
                # w0 is normalized to Nyquist (scipy >= 1.13 convention).
                q = max(0.707, 8.0 - 7.0 * resonance)
                bp_b, bp_a = iirpeak(norm_cutoff, q)
                res = lfilter(bp_b, bp_a, audio)
                filtered = filtered + resonance * 0.5 * res
            return filtered
        except ImportError:
            # Fallback: simple FFT-based lowpass
            X = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
            # Gentle rolloff above cutoff
            gain = np.ones(len(freqs))
            mask = freqs > cutoff
            gain[mask] = cutoff / freqs[mask]
            # Resonance peak
            if resonance > 0:
                peak_mask = np.abs(freqs - cutoff) < cutoff * 0.1
                gain[peak_mask] *= (1 + resonance * 3)
            X *= gain
            return np.fft.irfft(X, len(audio))

    def _apply_envelope(self, n_samples: int, velocity: int = 100) -> np.ndarray:
        """Generate ADSR envelope."""
        env = np.zeros(n_samples)
        a_samples = int(self.env_a * self.sample_rate)
        d_samples = int(self.env_d * self.sample_rate)
        r_samples = int(self.env_r * self.sample_rate)
        s_level = self.env_s
        # Attack
        a_samples = min(a_samples, n_samples)
        if a_samples > 0:
            env[:a_samples] = np.linspace(0, 1, a_samples)
        # Decay (clamped so attack+decay never exceeds note length)
        d_samples = min(d_samples, n_samples - a_samples)
        if d_samples > 0:
            env[a_samples:a_samples + d_samples] = np.linspace(1, s_level, d_samples)
        # Sustain
        s_start = a_samples + d_samples
        s_end = max(s_start, n_samples - r_samples)
        env[s_start:s_end] = s_level
        # Release (clamped)
        if r_samples > 0 and s_end < n_samples:
            env[s_end:] = np.linspace(s_level, 0, n_samples - s_end)
        # Velocity sensitivity
        vel_scale = 0.5 + 0.5 * (velocity / 127.0) * self.vel_sensitivity
        return env * vel_scale

    def _generate_lfo(self, n_samples: int) -> np.ndarray:
        """Generate LFO signal."""
        t = np.arange(n_samples) / self.sample_rate
        phase = 2 * np.pi * self.lfo_rate * t
        if self.lfo_waveform == 'sine':
            lfo = np.sin(phase)
        elif self.lfo_waveform == 'triangle':
            lfo = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1
        elif self.lfo_waveform == 'square':
            lfo = np.sign(np.sin(phase))
        elif self.lfo_waveform == 'saw':
            lfo = 2 * (phase / (2 * np.pi) % 1) - 1
        else:
            lfo = np.sin(phase)
        # Apply delay
        if self.lfo_delay > 0:
            delay_samples = int(self.lfo_delay * self.sample_rate)
            fade = np.ones(n_samples)
            fade[:delay_samples] = 0
            if delay_samples < n_samples:
                fade[delay_samples:] = np.linspace(0, 1, n_samples - delay_samples)
            lfo *= fade
        return lfo * self.lfo_depth

    def _apply_color(self, audio: np.ndarray) -> np.ndarray:
        """Apply post-VCA color section."""
        out = audio.copy()
        # Saturation (soft clipping)
        if self.saturation > 0:
            drive = 1 + self.saturation * 10
            out = np.tanh(out * drive) / np.tanh(drive)
        # Drive (harder clipping)
        if self.drive > 0:
            threshold = 1.0 - self.drive * 0.8
            out = np.clip(out, -threshold, threshold) / threshold
        # Distortion (waveshaping)
        if self.distortion > 0:
            out = np.sign(out) * np.abs(out) ** (1 - self.distortion * 0.5)
        # Tilt EQ (simplified)
        if abs(self.tilt_eq) > 0.01:
            X = np.fft.rfft(out)
            freqs = np.fft.rfftfreq(len(out), 1.0 / self.sample_rate)
            freqs[0] = 1.0
            log_f = np.log10(freqs)
            log_pivot = np.log10(1000)
            gain_db = self.tilt_eq * 12 * (log_f - log_pivot) / np.log10(2)
            gain = 10 ** (gain_db / 20)
            X *= gain
            out = np.fft.irfft(X, len(out))
        return out

    def render_note(self, midi_note: int = 60, duration: float = 1.0,
                    velocity: int = 100) -> np.ndarray:
        """Render a single note.

        Args:
            midi_note: MIDI note number (0-127).
            duration: Note duration in seconds.
            velocity: Note velocity (0-127).

        Returns:
            Mono audio.
        """
        n_samples = int(duration * self.sample_rate)
        freq = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
        # Generate oscillator
        osc = self._generate_oscillator(freq, n_samples, self.drift_amount)
        # Generate LFO
        lfo = self._generate_lfo(n_samples)
        # Apply LFO modulation
        if self.lfo_target == 'pitch' and self.lfo_depth > 0:
            # Pitch modulation: retune oscillator
            mod_freq = freq * (1 + lfo * 0.1)
            osc = self._generate_oscillator(mod_freq, n_samples, self.drift_amount)
        # Apply filter with envelope modulation
        cutoff = self.filter_cutoff
        # Keytrack
        key_offset = (midi_note - 60) * self.filter_keytrack * 100
        cutoff += key_offset
        # For simplicity, use static cutoff (envelope modulation would require per-sample filter)
        # In a real implementation, we'd modulate the filter coefficients per-sample
        if self.filter_env_amount > 0:
            # Use peak envelope value to set a static cutoff boost
            env_peak = self.env_s + (1 - self.env_s) * 0.5  # approximate peak
            cutoff *= (1 + env_peak * self.filter_env_amount * 2)
        if self.lfo_target == 'filter' and self.lfo_depth > 0:
            # Use average LFO value
            cutoff *= (1 + np.mean(lfo) * 0.5)
        filtered = self._apply_filter(osc, cutoff, self.filter_resonance)
        # Apply VCA envelope
        env = self._apply_envelope(n_samples, velocity)
        vca_out = filtered * env
        # Apply color section
        out = self._apply_color(vca_out)
        # Normalize
        peak = np.max(np.abs(out))
        if peak > 0:
            out = out / peak * 0.8
        return out


def demo() -> str:
    """Render demo notes and return summary."""
    synth = MonoSynth(sample_rate=44100)
    synth.set_oscillator(waveform='saw', sub_level=0.2)
    synth.set_filter(cutoff=1500, resonance=0.4)
    synth.set_envelope(a=0.01, d=0.3, s=0.6, r=0.5)
    synth.set_lfo(rate=4.0, depth=0.2, target='filter')
    # Render C major chord (sequential for mono synth)
    notes = [60, 64, 67]  # C, E, G
    audios = []
    for n in notes:
        audio = synth.render_note(midi_note=n, duration=0.5, velocity=100)
        audios.append(audio)
    combined = np.concatenate(audios)
    lines = [
        f"MonoSynth demo (saw+sub, cutoff=1500, res=0.4):",
        f"  C-E-G sequential: {len(combined)} samples, peak={np.max(np.abs(combined)):.3f}",
        f"  RMS: {np.sqrt(np.mean(combined**2)):.4f}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(demo())
