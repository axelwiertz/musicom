"""Sound Wave Synthesis and Analysis Module"""

"""
TODO:
- Split into multiple files (synthesis, analysis, utils)
- Implement more waveforms (square, triangle, sawtooth)
- Add effects (reverb, delay)
- Improve ADSR envelope customization
"""

import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt



class SoundWave:
    def __init__(self,
                 sample_rate: int =44100,
                 duration: float =2.0,
                 frequency: float =440.0,
                 amplitude: int =4096):

        self.sample_rate = sample_rate
        self.duration = duration
        self.frequency = frequency
        self.amplitude = amplitude

        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        self.wavedata = self.amplitude * np.sin(2*np.pi*self.frequency * self.t)

    def create_sine_wave(self, amplitude=4096):
        # Generate a sine wave at the specified frequency and duration
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        # Create a sine wave
        self.wavedata = amplitude * np.sin(2 * np.pi * self.frequency * t)

    def apply_overtones(self, factor, amplitude=4096):
        # Synthesize a note with overtones
        assert abs(1 - sum(factor)) < 1e-8

        # Calculate frequencies and amplitudes for each overtone
        frequencies = np.minimum(np.array([self.frequency * (x + 1) for x in range(len(factor))]),
                                 self.sample_rate // 2)
        amplitudes = np.array([amplitude * x for x in factor])

        self.frequency = frequencies[0]
        self.fundamental = self.create_sine_wave(amplitudes[0])
        for i in range(1, len(factor)):
            self.frequency = frequencies[i]
            overtone = self.create_sine_wave(amplitudes[i])
            self.fundamental += overtone

    def get_adsr_weights(self, length, decay, sustain_level):
        assert abs(sum(length) - 1) < 1e-8
        assert len(length) == len(decay) == 4

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
        self.weights = np.convolve(weights, smoothing, rotation='same')

        self.weights = np.repeat(weights, int(self.sample_rate * self.duration / intervals))
        tail = int(self.sample_rate * self.duration - weights.shape[0])
        if tail > 0:
            self.weights = np.concatenate((weights, weights[-1] - weights[-1] / tail * np.arange(tail)))

    def save (self, wave_file: str):
        # Write to file
        self.wave_file = wave_file
        wavfile.write(wave_file, self.sample_rate, self.wavedata.astype(np.int16))

    def load (self, wave_file: str):
        # Load data from wav file
        self.wave_file = wave_file
        self.sample_rate, self.wavarray = wavfile.read(wave_file)

    def plot_time(self):
        # Plot sound wave
        plt.plot(self.wavarray[500:2500])
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.title('Sound Wave of ' + self.wave_file)
        plt.style.use('dark_background')
        plt.grid()
        plt.show()

    def plot_spectrum(self):
        # Plot spectrum
        plt.plot(self.spectrum_frequency, abs(self.spectrum_amplitude.real))
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.title('Spectrum of ' + self.wave_file)
        plt.xlim((0, 2000))
        plt.style.use('dark_background')
        plt.grid()
        plt.show()

    def fft_analyze (self):
        # FFT analysis of the wave
        t = np.arange(self.wavarray.shape[0])
        self.spectrum_frequency = np.fft.fftfreq(t.shape[-1]) * self.sample_rate
        self.spectrum_amplitude = np.fft.fft(self.wavarray)

def synthesize_wave (wave: SoundWave):
    # Synthesize sound wave based on the FFT analysis
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


def main():
    sw = SoundWave()
    sw.load('piano_c.wav')
    sw.plot_time()
    sw.create_sine_wave()
    sw.save('pure_c.wav')

    sw.plot_time()

    synthesize_wave(sw)
    sw.save('synthetic_c.wav')


if __name__ == "__main__":
    main()
