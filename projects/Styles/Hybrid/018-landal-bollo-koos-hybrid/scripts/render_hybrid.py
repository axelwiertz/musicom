import numpy as np
import wave
import os

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def generate_sample(freq, duration, sample_rate=44100, wave_type='sine'):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    if wave_type == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == 'sawtooth':
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    elif wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    
    # Envelope
    env = np.ones_like(t)
    attack = int(0.01 * sample_rate)
    release = int(0.05 * sample_rate)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return wave * env

def save_wav(path, samples, sr=44100):
    audio = np.clip(samples, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

# --- Composition Setup ---
BPM = 110
SR = 44100
BEAT = 60/BPM
BAR = BEAT * 4
TOTAL_BARS = 8
total_samples = int(BAR * TOTAL_BARS * SR)
output = np.zeros(total_samples)

# 1. Minidisco Kick (Euphoria)
for i in range(TOTAL_BARS * 4):
    start = int(i * BEAT * SR)
    kick = np.sin(2 * np.pi * 50 * np.linspace(0, 0.1, int(0.1*SR))) * np.exp(-10 * np.linspace(0, 0.1, int(0.1*SR)))
    output[start:start+len(kick)] += kick * 0.5

# 2. Bollo Walking Bass (Bb-F)
bass_pattern = [46, 53, 46, 53] # Bb1, F2
for bar in range(TOTAL_BARS):
    for b in range(4):
        start = int((bar * 4 + b) * BEAT * SR)
        note = bass_pattern[b]
        sample = generate_sample(midi_to_freq(note), BEAT*0.9, SR, 'sine')
        output[start:start+len(sample)] += sample * 0.3

# 3. Hybrid Hook (Koos + Polo motif)
# Bb Major hook: Bb4, C5, D5, Bb4, F5, Eb5, D5, C5
hook = [70, 72, 74, 70, 77, 75, 74, 72]
for bar in range(TOTAL_BARS // 2):
    for i, note in enumerate(hook):
        start = int((bar * 8 + i) * (BEAT/2) * SR)
        sample = generate_sample(midi_to_freq(note), (BEAT/2)*0.8, SR, 'sawtooth')
        output[start:start+len(sample)] += sample * 0.15

save_wav('/opt/data/projects/018-landal-bollo-koos-hybrid/audio/hybrid_draft_v1.wav', output)

print("Rendered 018 Hybrid Draft.")
