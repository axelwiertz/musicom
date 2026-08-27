import numpy as np
import scipy.signal as signal
import wave
import os

# Env setup
SAMPLE_RATE = 44100

def generate_white_noise(duration):
    return np.random.uniform(-1, 1, int(SAMPLE_RATE * duration))

def apply_bandpass(data, lowcut, highcut, order=5):
    nyq = 0.5 * SAMPLE_RATE
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.lfilter(b, a, data)

def apply_highpass(data, cut, order=5):
    nyq = 0.5 * SAMPLE_RATE
    low = cut / nyq
    b, a = signal.butter(order, low, btype='high')
    return signal.lfilter(b, a, data)

def create_envelope(data, attack, decay):
    n_total = len(data)
    n_attack = int(attack * SAMPLE_RATE)
    n_decay = int(decay * SAMPLE_RATE)
    
    env = np.ones(n_total)
    if n_attack > 0:
        env[:n_attack] = np.linspace(0, 1, n_attack)
    if n_decay > 0:
        env[-n_decay:] = np.linspace(1, 0, n_decay)
    return data * env

def synth_s(duration=0.2):
    noise = generate_white_noise(duration)
    # S: High-pass > 5000Hz
    filtered = apply_highpass(noise, 5000)
    return create_envelope(filtered, 0.05, 0.05)

def synth_sh(duration=0.2):
    noise = generate_white_noise(duration)
    # SH: Lower than S, bandpass around 2000-4000Hz
    filtered = apply_bandpass(noise, 2000, 4500)
    return create_envelope(filtered, 0.05, 0.05)

def synth_vowel_a(duration=0.5, freq=220):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Sawtooth carrier
    saw = signal.sawtooth(2 * np.pi * freq * t)
    
    # Formants for [A]: F1=730, F2=1090, F3=2440
    def add_formant(sig, f, bw=100):
        # Using iirpeak for resonance
        b, a = signal.iirpeak(f, f / bw, fs=SAMPLE_RATE)
        return signal.lfilter(b, a, sig)
    
    vocal = add_formant(saw, 730) + add_formant(saw, 1090) + add_formant(saw, 2440)
    return create_envelope(vocal / np.max(np.abs(vocal)), 0.05, 0.1)

def save_wav(path, data):
    data = (data * 32767).astype(np.int16)
    with wave.open(path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(data.tobytes())

if __name__ == "__main__":
    # 1. Generate S and SH
    s_noise = synth_s()
    sh_noise = synth_sh()
    
    # 2. Combine for 'SA'
    vowel_a = synth_vowel_a()
    sa_sound = np.concatenate([s_noise, vowel_a])
    
    save_wav("/opt/data/projects/013-vocal-research/Prototypes/sa_test.wav", sa_sound)
    print("Files generated.")
