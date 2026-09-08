import numpy as np
import scipy.signal as signal
import wave

# Append path for scipy if needed
import sys
sys.path.append('/opt/data/.local/lib/python3.13/site-packages')

def generate_carrier(freq, duration, sr=44100):
    t = np.linspace(0, duration, int(sr * duration), False)
    # Pulse-like (sum of sines for harmonics)
    carrier = np.zeros_like(t)
    for i in range(1, 15):
        carrier += (1.0/i) * np.sin(2 * np.pi * freq * i * t)
    return carrier / np.max(np.abs(carrier))

def apply_formant(data, f_freq, sr=44100, bw=100):
    sos = signal.butter(4, [f_freq - bw/2, f_freq + bw/2], 'bp', fs=sr, output='sos')
    return signal.sosfilt(sos, data)

def synth_vowel_a(duration, freq, sr=44100):
    # Formants for [A]: 730, 1090, 2440
    carrier = generate_carrier(freq, duration, sr)
    f1 = apply_formant(carrier, 730, sr, 80)
    f2 = apply_formant(carrier, 1090, sr, 100)
    f3 = apply_formant(carrier, 2440, sr, 150)
    vocal = f1 + f2 + f3
    vocal = vocal / np.max(np.abs(vocal))
    
    # Envelope
    att = int(0.05 * sr)
    dec = int(0.1 * sr)
    env = np.ones_like(vocal)
    env[:att] = np.linspace(0, 1, att)
    env[-dec:] = np.linspace(1, 0, dec)
    return vocal * env

def synth_s(duration, sr=44100):
    noise = np.random.uniform(-1, 1, int(sr * duration))
    sos = signal.butter(10, 5000, 'hp', fs=sr, output='sos')
    s_noise = signal.sosfilt(sos, noise)
    # Fade out S slightly as it meets vowel
    env = np.ones_like(s_noise)
    env[-int(0.02*sr):] = np.linspace(1, 0.3, int(0.02*sr))
    return s_noise * 0.4 # Lower volume

def main():
    sr = 44100
    s_part = synth_s(0.15, sr)
    a_part = synth_vowel_a(0.5, 220, sr) # A3 note
    
    # Mix with small overlap or direct concat
    output = np.concatenate([s_part, a_part])
    
    # Normalize
    output = output / np.max(np.abs(output))
    
    # Save
    data_int = (output * 32767).astype(np.int16)
    with wave.open("/opt/data/projects/013-vocal-research/Prototypes/sa_test.wav", 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(data_int.tobytes())

if __name__ == "__main__":
    main()
