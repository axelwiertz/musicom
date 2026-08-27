import numpy as np
import wave
import mido
from mido import Message, MidiFile, MidiTrack

BPM = 120
SR = 44100
BEAT = 60/BPM
BAR = BEAT * 4
TOTAL_BARS = 16
SR_TICKS = 480 

def midi_to_freq(n): return 440 * (2**((n-69)/12))

def gen_tone(n, dur, type='sine', amp=0.1):
    n_samples = int(dur*SR)
    t = np.linspace(0, dur, n_samples, False)
    f = midi_to_freq(n)
    if type == 'sine': w = np.sin(2*np.pi*f*t)
    elif type == 'saw': w = 2*(t*f-np.floor(0.5+t*f))
    env = np.ones_like(t)
    r = int(0.05*SR)
    if len(env)>r: env[-r:] = np.linspace(1,0,r)
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
    
    # KICK
    for b in range(4):
        s = start_bar_idx + int(b * BEAT * SR)
        k_dur = int(0.1*SR)
        output[s:s+k_dur] += np.sin(2*np.pi*50*np.linspace(0,0.1,k_dur))*0.4
    
    # Layer 1 (Berendans)
    for i, n in enumerate(berendans):
        start = start_bar_idx + int(i * (BAR/4) * SR)
        dur = BAR/4
        tone = gen_tone(n, dur*0.8, 'sine', 0.08)
        output[start:start+len(tone)] += tone
        
    # Layer 2 (Koos) - Overlay from bar 4
    if bar >= 4:
        for i, n in enumerate(koos):
            start = start_bar_idx + int(i * (BAR/4) * SR)
            dur = BAR/4
            tone = gen_tone(n, dur*0.8, 'saw', 0.05)
            output[start:start+len(tone)] += tone

    # Layer 3 (Polo) - Overlay from bar 8
    if bar >= 8:
        for i, n in enumerate(polo):
            start = start_bar_idx + int(i * (BAR/len(polo)) * SR)
            dur = BAR/len(polo)
            tone = gen_tone(n, dur*0.8, 'sine', 0.08)
            output[start:start+len(tone)] += tone

# MIDI Weave
for bar in range(TOTAL_BARS):
    # Just simple sequential for now to ensure valid MIDI file
    if bar < 4:
        for n in berendans: add_midi_event(n, SR_TICKS)
    elif bar < 8:
        for n in koos: add_midi_event(n, SR_TICKS)
    else:
        for n in polo: add_midi_event(n, int(BAR*SR_TICKS/len(polo)))

with wave.open('/opt/data/projects/018-landal-bollo-koos-hybrid/audio/interwoven_v4_overlay.wav', 'w') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    samples = np.clip(output, -1.0, 1.0)
    wf.writeframes((samples * 32767).astype(np.int16).tobytes())

mid.save('/opt/data/projects/018-landal-bollo-koos-hybrid/midi/interwoven_v4_overlay.mid')
