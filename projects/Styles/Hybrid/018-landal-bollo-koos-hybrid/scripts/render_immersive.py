import numpy as np
import wave

BPM = 110
SR = 44100
BEAT = 60/BPM
BAR = BEAT * 4
TOTAL_BARS = 16
total_samples = int(BAR * TOTAL_BARS * SR)
output = np.zeros(total_samples)

def generate_noise(duration, volume=0.05):
    samples = np.random.uniform(-1, 1, int(SR * duration))
    return samples * volume

# --- SECTION A: FOREST (Bars 0-8) ---
# Bear Growls (Low freq FM noise)
for i in range(4):
    start = int(i * 2 * BAR * SR)
    growl = generate_noise(0.5, 0.1) * np.sin(2 * np.pi * 50 * np.linspace(0, 0.5, int(0.5*SR)))
    output[start:start+len(growl)] += growl

# Bird Chirps (High sine sweeps)
for i in range(20):
    start = np.random.randint(0, 8 * BAR * SR)
    chirp = np.sin(2 * np.pi * np.linspace(2000, 4000, int(0.1*SR))) * 0.05
    output[start:start+len(chirp)] += chirp

# Rabbit Jumps (Short percussive blips)
for i in range(16):
    start = int(i * BEAT * 2 * SR + (BEAT*0.5*SR))
    jump = np.sin(2 * np.pi * 800 * np.linspace(0, 0.05, int(0.05*SR))) * np.exp(-50 * np.linspace(0, 0.05, int(0.05*SR)))
    output[start:start+len(jump)] += jump * 0.2

# --- SECTION B: BEACH/HOLIDAY (Bars 8-16) ---
# Ocean Waves (White noise swells)
for bar in range(8, 16):
    start = int(bar * BAR * SR)
    swell = generate_noise(BAR, 0.02) * np.sin(np.pi * np.linspace(0, 1, int(BAR*SR)))
    output[start:start+len(swell)] += swell

# "Holiday" Steel Drumish lead
scale = [70, 72, 74, 75, 77, 79, 81, 82] # Bb Major
for i in range(32, 64):
    start = int(i * BEAT * SR)
    note = scale[i % 8]
    freq = 440 * (2**((note-69)/12))
    t = np.linspace(0, BEAT*0.5, int(BEAT*0.5*SR))
    pluck = np.sin(2 * np.pi * freq * t) * np.exp(-10 * t)
    output[start:start+len(pluck)] += pluck * 0.15

# Standard Mix (Kick/Bass)
for i in range(TOTAL_BARS * 4):
    start = int(i * BEAT * SR)
    kick = np.sin(2 * np.pi * 50 * np.linspace(0, 0.1, int(0.1*SR))) * np.exp(-15 * np.linspace(0, 0.1, int(0.1*SR)))
    output[start:start+len(kick)] += kick * 0.4
    
    bass_freq = 440 * (2**((46 if i%2==0 else 53)-69)/12)
    bass = np.sin(2 * np.pi * bass_freq * np.linspace(0, BEAT*0.9, int(BEAT*0.9*SR))) * 0.2
    output[start:start+len(bass)] += bass

def save_wav(path, samples, sr=44100):
    audio = np.clip(samples, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

save_wav('/opt/data/projects/018-landal-bollo-koos-hybrid/audio/immersive_hybrid_v2.wav', output)
