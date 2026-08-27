import numpy as np
import wave

BPM = 120 # Slight lift for weave energy
SR = 44100
BEAT = 60/BPM
BAR = BEAT * 4
TOTAL_BARS = 16
total_samples = int(BAR * TOTAL_BARS * SR)
output = np.zeros(total_samples)

def midi_to_freq(n): return 440 * (2**((n-69)/12))

def gen_tone(n, dur, type='sine', amp=0.1):
    t = np.linspace(0, dur, int(dur*SR))
    f = midi_to_freq(n)
    if type == 'sine': w = np.sin(2*np.pi*f*t)
    elif type == 'saw': w = 2*(t*f-np.floor(0.5+t*f))
    elif type == 'squ': w = np.sign(np.sin(2*np.pi*f*t))
    env = np.ones_like(t)
    r = int(0.05*SR)
    if len(env)>r: env[-r:] = np.linspace(1,0,r)
    return w * env * amp

# --- MELODY WEAVING ---

# 1. Berendans (Trad Folk Hook) - Bb Major Diatonic
# Intervals: 1-2-3-1 (Bb-C-D-Bb)
berendans_melody = [70, 72, 74, 70] 

# 2. Koos Roompot (Anthemic Mix) - Higher octave, energetic
# Intervals: 5-5-5-1 (F-F-F-Bb)
koos_melody = [77, 77, 77, 82]

# 3. Polo Beer (User Voice Motif)
# Intervals: 1-3-5-4-2 (Bb-D-F-Eb-C)
polo_melody = [70, 74, 77, 75, 72]

# --- ASSEMBLY ---
for bar in range(TOTAL_BARS):
    start_bar = int(bar * BAR * SR)
    
    # KICK & BASS (The Glue)
    for b in range(4):
        s = start_bar + int(b * BEAT * SR)
        output[s:s+int(0.1*SR)] += np.sin(2*np.pi*50*np.linspace(0,0.1,int(0.1*SR))) * 0.4
        bf = midi_to_freq(46 if b%2==0 else 53)
        bass = np.sin(2*np.pi*bf*np.linspace(0,BEAT*0.9,int(BEAT*0.9*SR))) * 0.2
        output[s:s+len(bass)] += bass

    # WEAVE MELODY
    m = []
    if bar < 4: m = berendans_melody # Intro: Traditional
    elif bar < 8: m = koos_melody     # Build: Minidisco
    else: m = polo_melody             # Release: The Polo Beer Theme
    
    for i, note in enumerate(m):
        os = start_bar + int(i * (BAR/len(m)) * SR)
        t = 'sine' if bar < 4 else 'saw'
        sample = gen_tone(note, (BAR/len(m))*0.8, t, 0.12)
        output[os:os+len(sample)] += sample

# Add Forest/Beach ambience back in
for i in range(10):
    start = np.random.randint(0, total_samples)
    chirp = np.sin(2 * np.pi * np.linspace(2000, 3500, int(0.08*SR))) * 0.03
    output[start:start+len(chirp)] += chirp

def save_wav(path, samples):
    audio = np.clip(samples, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(audio_int16.tobytes())

save_wav('/opt/data/projects/018-landal-bollo-koos-hybrid/audio/interwoven_v3.wav', output)
