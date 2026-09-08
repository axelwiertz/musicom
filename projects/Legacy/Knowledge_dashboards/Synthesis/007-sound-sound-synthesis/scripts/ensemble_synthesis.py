import numpy as np
import wave
import os

# --- SYNTHESIS ENGINES ---

def guitar_ks(freq, duration, sample_rate=44100):
    N = int(sample_rate / freq)
    ring_buf = np.random.uniform(-1, 1, N)
    num_samples = int(duration * sample_rate)
    samples = np.zeros(num_samples)
    for i in range(num_samples):
        samples[i] = ring_buf[0]
        avg = 0.5 * (ring_buf[0] + ring_buf[1]) * 0.996
        ring_buf = np.append(ring_buf[1:], avg)
    return samples

def piano_synth(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    s = (0.6 * np.sin(2 * np.pi * freq * t) + 
         0.3 * np.sin(2 * np.pi * 2 * freq * t) + 
         0.1 * np.sin(2 * np.pi * 3 * freq * t))
    env = np.exp(-4 * t)
    return s * env

def violin_synth(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Refined Vibrato: Reduced rate to 5.5Hz and depth to 0.8% for a more subtle, natural feel
    vibrato_rate = 5.5
    vibrato_depth = freq * 0.008
    vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    
    samples = np.zeros_like(t)
    # Increased harmonics for a smoother, silkier string texture
    for h in range(1, 12):
        # Slightly steeper harmonic roll-off for a warmer tone
        amp = 1.0 / (h ** 1.1)
        samples += amp * np.sin(2 * np.pi * (freq * h) * t + (h * vibrato))
    
    # Smoother Bowing Envelope
    attack = int(0.25 * sample_rate)
    release = int(0.3 * sample_rate)
    env = np.ones_like(t)
    if len(t) > (attack + release):
        env[:attack] = np.linspace(0, 1, attack)
        env[-release:] = np.linspace(1, 0, release)
    else:
        # Fallback for very short notes
        env = np.sin(np.pi * np.linspace(0, 1, len(t)))
        
    return samples * env * 0.4

# --- MIXING LOGIC ---

def save_wav(samples, filename, sample_rate=44100):
    samples = np.clip(samples, -1.0, 1.0)
    samples = (samples * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sample_rate)
        f.writeframes(samples.tobytes())

if __name__ == "__main__":
    SR = 44100
    # Progression: Am - F - G - C (Simple 4-chord loop)
    # Chords (Piano): [A3, C4, E4], [F3, A3, C4], [G3, B3, D4], [C3, E3, G3]
    progression = [
        [57, 60, 64], # Am
        [53, 57, 60], # F
        [55, 59, 62], # G
        [48, 52, 55]  # C
    ]
    # Melody (Violin): E5, F5, G5, E5
    melody = [76, 77, 79, 76]
    # Bass / Pluck (Guitar): A2, F2, G2, C2
    bass = [45, 41, 43, 36]
    
    chord_dur = 1.0
    total_samples = int(chord_dur * len(progression) * SR)
    mix = np.zeros(total_samples)
    
    for i in range(len(progression)):
        start = int(i * chord_dur * SR)
        end = start + int(chord_dur * SR)
        
        # 1. Piano Chords (Polyphonic)
        chord_mix = np.zeros(int(chord_dur * SR))
        for midi in progression[i]:
            f = 440.0 * (2.0 ** ((midi - 69) / 12.0))
            chord_mix += piano_synth(f, chord_dur, SR)
        mix[start:end] += chord_mix * 0.3
        
        # 2. Guitar Bass (Monophonic Pluck)
        f_bass = 440.0 * (2.0 ** ((bass[i] - 69) / 12.0))
        mix[start:end] += guitar_ks(f_bass, chord_dur, SR) * 0.4
        
        # 3. Violin Melody (Monophonic Lead)
        f_lead = 440.0 * (2.0 ** ((melody[i] - 69) / 12.0))
        mix[start:end] += violin_synth(f_lead, chord_dur, SR) * 0.3

    save_wav(mix, "projects/002-sound-synthesis/audio/full_ensemble_loop.wav", SR)
    print("Synthesized full ensemble loop.")
