import numpy as np
import wave
import os

def violin_synthesis(freq, duration, sample_rate=44100):
    """
    Simulates a violin sound using sawtooth summation and vibrato.
    Violins have rich harmonics (sawtooth base) and a characteristic 
    'vibrato' and slow 'attack' (bowing speed).
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 1. Vibrato: Frequency modulation (usually 5-7 Hz)
    vibrato_rate = 6.0
    vibrato_depth = freq * 0.02
    fm = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    
    # 2. Rich Harmonics: Sawtooth wave simulation
    # A violin's resonance is complex; we'll use a sum of harmonics with specific weights
    # and a slight low-pass filtering effect.
    samples = np.zeros_like(t)
    num_harmonics = 10
    for h in range(1, num_harmonics + 1):
        # Amplitudes decrease with harmonic number
        amp = 1.0 / (h ** 0.8)
        samples += amp * np.sin(2 * np.pi * (freq * h) * t + (h * fm))
        
    # 3. Bowing Envelope (Attack/Decay/Sustain/Release)
    # Slow attack for bowing (approx 100-200ms)
    attack_len = int(0.15 * sample_rate)
    decay_len = int(0.1 * sample_rate)
    release_len = int(0.2 * sample_rate)
    sustain_len = len(t) - attack_len - decay_len - release_len
    
    env = np.concatenate([
        np.linspace(0, 1, attack_len),
        np.linspace(1, 0.8, decay_len),
        np.full(sustain_len, 0.8),
        np.linspace(0.8, 0, release_len)
    ])
    
    # Ensure envelope length matches samples
    if len(env) < len(samples):
        env = np.pad(env, (0, len(samples) - len(env)), mode='constant')
    else:
        env = env[:len(samples)]
        
    return samples * env

def save_wav(samples, filename, sample_rate=44100):
    samples = np.clip(samples, -1.0, 1.0)
    samples = (samples * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sample_rate)
        f.writeframes(samples.tobytes())

if __name__ == "__main__":
    SR = 44100
    DUR = 2.0
    freq_a4 = 440.0
    
    # Generate Violin A4
    violin_note = violin_synthesis(freq_a4, DUR, SR)
    save_wav(violin_note, "projects/002-sound-synthesis/audio/violin_a4.wav", SR)
    
    # Generate Violin Melody (A-C-E)
    melody_midis = [69, 72, 76]
    note_dur = 0.8
    full_audio = np.array([])
    for midi in melody_midis:
        freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        note = violin_synthesis(freq, note_dur, SR)
        full_audio = np.concatenate([full_audio, note])
    
    save_wav(full_audio, "projects/002-sound-synthesis/audio/violin_melody.wav", SR)
    print("Synthesized violin samples.")
