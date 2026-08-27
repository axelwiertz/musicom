import numpy as np
import wave
import os
from scipy.signal import butter, lfilter

def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def apply_filter(data, b, a):
    return lfilter(b, a, data)

def generate_noise(duration, fs):
    return np.random.uniform(-1, 1, int(duration * fs))

def apply_envelope(signal, attack, release, fs):
    n = len(signal)
    att_n = int(attack * fs)
    rel_n = int(release * fs)
    env = np.ones(n)
    if att_n > 0:
        env[:att_n] = np.linspace(0, 1, att_n)
    if rel_n > 0:
        env[-rel_n:] = np.linspace(1, 0, rel_n)
    return signal * env

def synth_s(duration, fs):
    noise = generate_noise(duration, fs)
    # Higher cutoff, lower order for less 'whistle'
    b, a = butter_highpass(6000, fs, order=2)
    s_noise = apply_filter(noise, b, a)
    # Faster envelope for crispness
    return apply_envelope(s_noise, 0.01, 0.05, fs)

def synth_vowel(vowel_type, duration, fs, freq=220):
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)
    # Carrier: Pulse wave with noise floor (humanity)
    # Pulse width modulation or rich sawtooth
    source = (t * freq) % 1.0
    source = np.where(source < 0.3, 1.0, -1.0) # Pulse
    source += np.random.normal(0, 0.02, len(source)) # Air noise
    
    # Formants (F1, F2, F3)
    formants = {
        'a': [730, 1090, 2440], # Father
        'e': [360, 2220, 2960], # Bed
        'i': [270, 2290, 3010], # Meet
        'o': [570, 840, 2410],  # Boat
        'u': [300, 870, 2240]   # Boot
    }
    
    f_list = formants.get(vowel_type, [730, 1090, 2440])
    res = np.zeros_like(source)
    
    # Render with wider bandwidth (100Hz instead of 50Hz) to avoid 'brass'
    for f in f_list:
        b, a = butter_bandpass(f-80, f+80, fs, order=2)
        res += apply_filter(source, b, a) * 0.5
        
    # Add vibrato (5.5Hz)
    vibrato = 1.0 + 0.005 * np.sin(2 * np.pi * 5.5 * t)
    res = res * vibrato
    
    # Smoother attack/release
    return apply_envelope(res, 0.1, 0.1, fs)

def save_wav(path, data, fs):
    # Normalize with headroom
    data = 0.8 * data / np.max(np.abs(data))
    data_int16 = (data * 32767).astype(np.int16)
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(data_int16.tobytes())

if __name__ == "__main__":
    fs = 44100
    s_part = synth_s(0.15, fs)
    a_part = synth_vowel('a', 0.6, fs, freq=196) # G3
    sa = np.concatenate([s_part, a_part])
    
    # Test other vowels
    e = synth_vowel('e', 0.5, fs, freq=196)
    i = synth_vowel('i', 0.5, fs, freq=196)
    o = synth_vowel('o', 0.5, fs, freq=196)
    u = synth_vowel('u', 0.5, fs, freq=196)
    
    path = "/opt/data/projects/013-vocal-research/Prototypes/vocal_fix.wav"
    save_wav(path, sa, fs)
    save_wav("/opt/data/projects/013-vocal-research/Prototypes/vowels_all.wav", np.concatenate([a_part, e, i, o, u]), fs)
    print(path)
