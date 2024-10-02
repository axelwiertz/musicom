import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt


def get_piano_notes():
    # White keys are in Uppercase and black keys (sharps) are in lowercase
    octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B']
    base_freq = 440  # Frequency of Note A4
    keys = np.array([x + str(y) for y in range(0, 9) for x in octave])
    # Trim to standard 88 keys
    start = np.where(keys == 'A0')[0][0]
    end = np.where(keys == 'C8')[0][0]
    keys = keys[start:end + 1]

    note_freqs = dict(zip(keys, [2 ** ((n + 1 - 49) / 12) * base_freq for n in range(len(keys))]))
    note_freqs[''] = 0.0  # stop
    return note_freqs

def get_sine_wave(frequency, duration, sample_rate=44100, amplitude=4096):
    t = np.linspace(0, duration, int(sample_rate*duration)) # Time axis
    wave = amplitude*np.sin(2*np.pi*frequency*t)
    return wave


# Get middle C frequency
note_freqs = get_piano_notes()
frequency = note_freqs['C4']

# Pure sine wave
sine_wave = get_sine_wave(frequency, duration=2, amplitude=2048)
wavfile.write('pure_c.wav', rate=44100, data=sine_wave.astype(np.int16))





plt.style.use('seaborn-dark')

# Load data from wav file
sample_rate, middle_c = wavfile.read('data/piano_c.wav')

# Plot sound wave
plt.plot(middle_c[500:2500])
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('Sound Wave of Middle C on Piano')
plt.grid()


# Load data from wav file
sample_rate, middle_c = wavfile.read('data/piano_c.wav')

#FFT
t = np.arange(middle_c.shape[0])
freq = np.fft.fftfreq(t.shape[-1])*sample_rate
sp = np.fft.fft(middle_c)

# Plot spectrum
plt.plot(freq, abs(sp.real))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Spectrum of Middle C Recording on Piano')
plt.xlim((0, 2000))
plt.grid()



# Get positive frequency
idx = np.where(freq > 0)[0]
freq = freq[idx]
sp = sp[idx]

# Get dominant frequencies
sort = np.argsort(-abs(sp.real))[:100]
dom_freq = freq[sort]

# Round and calculate amplitude ratio
freq_ratio = np.round(dom_freq/frequency)
unique_freq_ratio = np.unique(freq_ratio)
amp_ratio = abs(sp.real[sort]/np.sum(sp.real[sort]))
factor = np.zeros((int(unique_freq_ratio[-1]), ))
for i in range(factor.shape[0]):
    idx = np.where(freq_ratio==i+1)[0]
    factor[i] = np.sum(amp_ratio[idx])
factor = factor/np.sum(factor)


def apply_overtones(frequency, duration, factor, sample_rate=44100, amplitude=4096):
    assert abs(1 - sum(factor)) < 1e-8

    frequencies = np.minimum(np.array([frequency * (x + 1) for x in range(len(factor))]), sample_rate // 2)
    amplitudes = np.array([amplitude * x for x in factor])

    fundamental = get_sine_wave(frequencies[0], duration, sample_rate, amplitudes[0])
    for i in range(1, len(factor)):
        overtone = get_sine_wave(frequencies[i], duration, sample_rate, amplitudes[i])
        fundamental += overtone
    return fundamental


# Construct harmonic series
note = apply_overtones(frequency, duration=2.5, factor=factor)


def get_adsr_weights(frequency, duration, length, decay, sustain_level, sample_rate=44100):
    assert abs(sum(length) - 1) < 1e-8
    assert len(length) == len(decay) == 4

    intervals = int(duration * frequency)
    len_A = np.maximum(int(intervals * length[0]), 1)
    len_D = np.maximum(int(intervals * length[1]), 1)
    len_S = np.maximum(int(intervals * length[2]), 1)
    len_R = np.maximum(int(intervals * length[3]), 1)

    decay_A = decay[0]
    decay_D = decay[1]
    decay_S = decay[2]
    decay_R = decay[3]

    A = 1 / np.array([(1 - decay_A) ** n for n in range(len_A)])
    A = A / np.nanmax(A)
    D = np.array([(1 - decay_D) ** n for n in range(len_D)])
    D = D * (1 - sustain_level) + sustain_level
    S = np.array([(1 - decay_S) ** n for n in range(len_S)])
    S = S * sustain_level
    R = np.array([(1 - decay_R) ** n for n in range(len_R)])
    R = R * S[-1]

    weights = np.concatenate((A, D, S, R))
    smoothing = np.array([0.1 * (1 - 0.1) ** n for n in range(5)])
    smoothing = smoothing / np.nansum(smoothing)
    weights = np.convolve(weights, smoothing, mode='same')

    weights = np.repeat(weights, int(sample_rate * duration / intervals))
    tail = int(sample_rate * duration - weights.shape[0])
    if tail > 0:
        weights = np.concatenate((weights, weights[-1] - weights[-1] / tail * np.arange(tail)))
    return weights



# Get sound wave
note = apply_overtones(frequency, duration=2.5, factor=factor)

# Apply smooth ADSR weights
weights = get_adsr_weights(frequency, duration=2.5, length=[0.05, 0.25, 0.55, 0.15],
                           decay=[0.075,0.02,0.005,0.1], sustain_level=0.1)

# Write to file
data = note*weights
data = data*(4096/np.max(data)) # Adjusting the Amplitude
wavfile.write('synthetic_c.wav', sample_rate, data.astype(np.int16))
