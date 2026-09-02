"""Additive synthesis and sound wave analysis.

Includes sine wave generation, overtone synthesis, ADSR envelopes, and FFT analysis.
Promoted from research/audio/soundwave.py.
"""

import numpy as np
from typing import List, Optional

from ..utils.io import write_wav, read_wav


class SoundWave:
    """Sound wave synthesis and analysis.
    
    Supports sine wave generation, overtone synthesis, ADSR envelopes,
    and FFT-based spectral analysis.
    """
    
    def __init__(self,
                 sample_rate: int = 44100,
                 duration: float = 2.0,
                 frequency: float = 440.0,
                 amplitude: int = 4096):
        """
        Args:
            sample_rate: Sample rate in Hz
            duration: Duration in seconds
            frequency: Base frequency in Hz
            amplitude: Base amplitude
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.frequency = frequency
        self.amplitude = amplitude

        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        self.wavedata = self.amplitude * np.sin(2*np.pi*self.frequency * self.t)

    def create_sine_wave(self, amplitude: int = 4096) -> None:
        """Generate a pure sine wave at the current frequency."""
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        self.wavedata = amplitude * np.sin(2 * np.pi * self.frequency * t)

    def apply_overtones(self, factor: List[float], amplitude: int = 4096) -> None:
        """Synthesize a note with overtones.

        Args:
            factor: List of overtone amplitudes (must sum to 1.0)
            amplitude: Base amplitude
        """
        assert abs(1 - sum(factor)) < 1e-8, "Overtone factors must sum to 1.0"

        # Calculate frequencies and amplitudes for each overtone
        frequencies = np.minimum(np.array([self.frequency * (x + 1) for x in range(len(factor))]),
                                 self.sample_rate // 2)
        amplitudes = np.array([amplitude * x for x in factor])

        self.frequency = frequencies[0]
        self.create_sine_wave(amplitudes[0])          # sets self.wavedata
        self.fundamental = self.wavedata.copy()
        for i in range(1, len(factor)):
            self.frequency = frequencies[i]
            self.create_sine_wave(amplitudes[i])      # sets self.wavedata
            self.fundamental = self.fundamental + self.wavedata

    def get_adsr_weights(self, length: List[float], decay: List[float], 
                         sustain_level: float) -> None:
        """Apply ADSR envelope weights.
        
        Args:
            length: ADSR segment lengths as proportions (must sum to 1.0)
            decay: Decay rates for each segment
            sustain_level: Sustain level (0-1)
        """
        assert abs(sum(length) - 1) < 1e-8, "Length proportions must sum to 1.0"
        assert len(length) == len(decay) == 4, "Must have 4 ADSR segments"

        intervals = int(self.duration * self.frequency)
        len_attack = np.maximum(int(intervals * length[0]), 1)
        len_decay = np.maximum(int(intervals * length[1]), 1)
        len_sustain = np.maximum(int(intervals * length[2]), 1)
        len_release = np.maximum(int(intervals * length[3]), 1)

        decay_A = decay[0]
        decay_D = decay[1]
        decay_S = decay[2]
        decay_R = decay[3]

        A = 1 / np.array([(1 - decay_A) ** n for n in range(len_attack)])
        A = A / np.nanmax(A)
        D = np.array([(1 - decay_D) ** n for n in range(len_decay)])
        D = D * (1 - sustain_level) + sustain_level
        S = np.array([(1 - decay_S) ** n for n in range(len_sustain)])
        S = S * sustain_level
        R = np.array([(1 - decay_R) ** n for n in range(len_release)])
        R = R * S[-1]

        weights = np.concatenate((A, D, S, R))
        smoothing = np.array([0.1 * (1 - 0.1) ** n for n in range(5)])
        smoothing = smoothing / np.nansum(smoothing)
        self.weights = np.convolve(weights, smoothing, mode='same')

        self.weights = np.repeat(weights, int(self.sample_rate * self.duration / intervals))
        tail = int(self.sample_rate * self.duration - weights.shape[0])
        if tail > 0:
            self.weights = np.concatenate((weights, weights[-1] - weights[-1] / tail * np.arange(tail)))

    def save(self, wave_file: str) -> str:
        """Write wave data to WAV file."""
        write_wav(wave_file, self.wavedata.astype(np.float32) / 32768.0, 
                  self.sample_rate, normalize=True)
        return wave_file

    def load(self, wave_file: str) -> None:
        """Load data from WAV file."""
        self.wavedata, self.sample_rate = read_wav(wave_file)
        self.wavedata = (self.wavedata * 32768).astype(np.int16)

    def fft_analyze(self) -> None:
        """Perform FFT analysis on the wave data."""
        t = np.arange(self.wavedata.shape[0])
        self.spectrum_frequency = np.fft.fftfreq(t.shape[-1]) * self.sample_rate
        self.spectrum_amplitude = np.fft.fft(self.wavedata)


def synthesize_wave(wave: SoundWave) -> None:
    """Synthesize sound wave based on FFT analysis.
    
    Analyzes the current wave data, extracts dominant frequencies,
    and re-synthesizes with proper overtones and ADSR envelope.
    """
    assert hasattr(wave, 'spectrum_frequency') and hasattr(wave, 'spectrum_amplitude')

    wave.fft_analyze()

    # Get positive frequencies
    idx = np.where(wave.spectrum_frequency > 0)[0]
    freq = wave.spectrum_frequency[idx]
    sp = wave.spectrum_amplitude[idx]

    # Get dominant frequencies
    sort = np.argsort(-abs(sp.real))[:100]
    dom_freq = freq[sort]

    # Round and calculate amplitude ratio
    freq_ratio = np.round(dom_freq / wave.frequency)
    # Normalize amplitude ratio
    unique_freq_ratio = np.unique(freq_ratio)
    # Amplitude ratio
    amp_ratio = abs(sp.real[sort] / np.sum(sp.real[sort]))
    # Average amplitude ratio for each harmonic
    factor = np.zeros((int(unique_freq_ratio[-1]),))
    for i in range(factor.shape[0]):
        idx = np.where(freq_ratio == i + 1)[0]
        factor[i] = np.sum(amp_ratio[idx])
    factor = factor / np.sum(factor)

    # Synthesize note with overtones
    wave.duration = 2.5
    wave.apply_overtones(factor=factor)
    # Apply smooth ADSR weights
    wave.get_adsr_weights(length=[0.05, 0.25, 0.55, 0.15],
                          decay=[0.075, 0.02, 0.005, 0.1],
                          sustain_level=0.1)

    data = wave.fundamental * wave.weights
    # Adjusting the Amplitude
    wave.wavedata = data * (4096 / np.max(data))


if __name__ == "__main__":
    sw = SoundWave()
    sw.create_sine_wave()
    sw.save('pure_c.wav')
    print("SoundWave ready. Create instance and call methods to use.")
