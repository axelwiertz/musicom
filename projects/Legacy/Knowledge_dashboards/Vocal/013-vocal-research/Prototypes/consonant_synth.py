import numpy as np
import wave
import scipy.signal as signal
import os

# Ensure directory exists
os.makedirs('/opt/data/projects/013-vocal-research/Prototypes', exist_ok=True)

def generate_white_noise(duration, sample_rate=44100):
    return np.random.uniform(-1, 1, int(sample_rate * duration))

def apply_envelope(data, attack, decay, release, sample_rate=44100):
    n = len(data)
    env = np.ones(n)
    
    a_samples = int(attack * sample_rate)
    d_samples = int(decay * sample_rate)
    r_samples = int(release * sample_rate)
    
    if a_samples > 0:
        env[:a_samples] = np.linspace(0, 1, a_samples)
    if r_samples > 0:
        env[-r_samples:] = np.linspace(1, 0, r_samples)
        
    return data * env

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def synth_s(duration=0.2, sample_rate=44100):
    noise = generate_white_noise(duration, sample_rate)
    b, a = butter_highpass(5000, sample_rate)
    s_noise = signal.lfilter(b, a, noise)
    return apply_envelope(s_noise, 0.05, 0, 0.05, sample_rate)

def synth_sh(duration=0.2, sample_rate=44100):
    noise = generate_white_noise(duration, sample_rate)
    # SH is lower frequency than S, usually centered around 2-4kHz
    b, a = butter_bandpass(2000, 5000, sample_rate)
    sh_noise = signal.lfilter(b, a, noise)
    return apply_envelope(sh_noise, 0.05, 0, 0.05, sample_rate)

def synth_vowel_a(duration=0.5, f0=220, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Sawtooth carrier
    carrier = signal.sawtooth(2 * np.pi * f0 * t)
    
    # Formants for [A]: 730, 1090, 2440
    def add_formant(sig, freq, bw=100):
        b, a = signal.iirpeak(freq, freq/bw, fs=sample_rate)
        return signal.lfilter(b, a, sig)
    
    vocal = add_formant(carrier, 730) + add_formant(carrier, 1090) + add_formant(carrier, 2440)
    # Normalize
    vocal = vocal / np.max(np.abs(vocal))
    return apply_envelope(vocal, 0.1, 0, 0.1, sample_rate)

def save_wav(path, data, sample_rate=44100):
    data = (data * 32767).astype(np.int16)
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(data.tobytes())

# Generate S and SH for prototype check
s_sound = synth_s()
sh_sound = synth_sh()

# Task 3: Combine S + A
s_part = synth_s(0.15)
a_part = synth_vowel_a(0.5, f0=200)
sa_sound = np.concatenate([s_part, a_part])

save_wav('/opt/data/projects/013-vocal-research/Prototypes/sa_test.wav', sa_sound)
print("Files generated.")
