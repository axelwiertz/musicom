import numpy as np
import wave
import mido
from mido import Message, MidiFile, MidiTrack

BPM = 120
SR = 44100
BEAT = 60/BPM
BAR = BEAT * 4
TOTAL_BARS = 16

def midi_to_freq(n): return 440 * (2**((n-69)/12))

def gen_instrument(n, dur, type='piano', amp=0.1):
    t = np.linspace(0, dur, int(dur*SR), False)
    f = midi_to_freq(n)
    if type == 'piano':
        # Additive with inharmonicity and fast decay
        w = np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*2.001*f*t) + 0.2*np.sin(2*np.pi*3.002*f*t)
        env = np.exp(-4 * t)
    elif type == 'guitar':
        # Karplus-Strong approximation (filtered noise/saw)
        w = 2*(t*f-np.floor(0.5+t*f))
        env = np.exp(-6 * t)
    elif type == 'synth':
        # Bright Sawtooth for Minidisco
        w = 2*(t*f-np.floor(0.5+t*f))
        env = np.ones_like(t)
    elif type == 'violin':
        # Sawtooth with vibrato
        vibrato = 1 + 0.008 * np.sin(2 * np.pi * 5.5 * t)
        w = 2*(t*f*vibrato-np.floor(0.5+t*f*vibrato))
        env = np.sin(np.pi * t / dur) # Bowing envelope
    
    r = int(0.05*SR)
    if len(env)>r: env[-r:] *= np.linspace(1,0,r)
    return w * env * amp

# DNA
berendans = [70, 72, 74, 70] 
koos = [82, 82, 82, 77]      
polo = [70, 74, 77, 75, 72]  

output = np.zeros(int(BAR * TOTAL_BARS * SR))
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

def add_midi_event(note, duration_ticks, vel=80):
    track.append(Message('note_on', note=note, velocity=vel, time=0))
    track.append(Message('note_off', note=note, velocity=vel, time=duration_ticks))

for bar in range(TOTAL_BARS):
    start_bar_idx = int(bar * BAR * SR)
    
    # 1. ORCHESTRAL FOUNDATION (Berendans) -> Violin & Piano
    for i, n in enumerate(berendans):
        start = start_bar_idx + int(i * (BAR/4) * SR)
        dur = BAR/4
        # Mix Violin and Piano for Folk-Classical feel
        tone = gen_instrument(n, dur*0.8, 'violin', 0.06) + gen_instrument(n, dur*0.8, 'piano', 0.08)
        output[start:start+len(tone)] += tone
        
    # 2. MINIDISCO POWER (Koos) -> Bright Synth Lead
    if bar >= 4:
        for i, n in enumerate(koos):
            start = start_bar_idx + int(i * (BAR/4) * SR)
            dur = BAR/4
            tone = gen_instrument(n, dur*0.8, 'synth', 0.05)
            output[start:start+len(tone)] += tone

    # 3. THE POLO THEME (Polo) -> Folk Guitar
    if bar >= 8:
        for i, n in enumerate(polo):
            start = start_bar_idx + int(i * (BAR/len(polo)) * SR)
            dur = BAR/len(polo)
            tone = gen_instrument(n, dur*0.8, 'guitar', 0.1)
            output[start:start+len(tone)] += tone

    # 4. RHYTHM SECTION
    for b in range(4):
        s = start_bar_idx + int(b * BEAT * SR)
        # Kick
        k_dur = int(0.1*SR)
        output[s:s+k_dur] += np.sin(2*np.pi*50*np.linspace(0,0.1,k_dur))*0.4
        # Bass (Deep Sine)
        bf = midi_to_freq(46 if b%2==0 else 53)
        bass = np.sin(2*np.pi*bf*np.linspace(0,BEAT*0.9,int(BEAT*0.9*SR))) * 0.2
        output[s:s+len(bass)] += bass

# Render
with wave.open('/opt/data/projects/018-landal-bollo-koos-hybrid/audio/instrumented_v5.wav', 'w') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    samples = np.clip(output, -1.0, 1.0)
    wf.writeframes((samples * 32767).astype(np.int16).tobytes())

mid.save('/opt/data/projects/018-landal-bollo-koos-hybrid/midi/instrumented_v5.mid')
