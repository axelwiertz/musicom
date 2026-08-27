from music21 import stream, note, chord, instrument, tempo, meter, midi, percussion
import math, wave, struct, os

ROOT = '/opt/data/projects/014-rock-apprenticeship'
MIDI_PATH = ROOT + '/MIDI/first-riff-engine.mid'
WAV_PATH = ROOT + '/Audio/first-riff-engine.wav'
OGG_PATH = ROOT + '/Audio/first-riff-engine.ogg'
os.makedirs(ROOT + '/MIDI', exist_ok=True)
os.makedirs(ROOT + '/Audio', exist_ok=True)

BPM = 128
BEAT = 60.0 / BPM
SR = 44100

# --- MIDI score ---
score = stream.Score(id='First Riff Engine')
score.append(tempo.MetronomeMark(number=BPM))
score.append(meter.TimeSignature('4/4'))

# Guitar riff: E blues scale. E2-ish guitar range.
guitar = stream.Part(id='Distorted rhythm guitar')
guitar.insert(0, instrument.ElectricGuitar())
# 2 bars of eighth slots: None = rest
riff = ['E3', None, 'E3', 'G3', None, 'A3', 'B-3', None, 'B3', None, 'D4', None, 'B3', 'A3', None, 'E3']
for repeat in range(6):
    for p in riff:
        if p is None:
            guitar.append(note.Rest(quarterLength=0.5))
        else:
            guitar.append(note.Note(p, quarterLength=0.5, volume=90))

# Bass doubles root motion simpler.
bass = stream.Part(id='Bass')
bass.insert(0, instrument.ElectricBass())
bass_riff = ['E2', None, 'E2', None, 'G2', None, 'A2', None, 'B1', None, 'D2', None, 'B1', 'A1', None, 'E2']
for repeat in range(6):
    for p in bass_riff:
        bass.append(note.Rest(quarterLength=0.5) if p is None else note.Note(p, quarterLength=0.5, volume=95))

# Power chords: intro/verse/chorus roots.
chords = stream.Part(id='Power chords')
chords.insert(0, instrument.ElectricGuitar())
roots = ['E3','E3','G3','A3','E3','E3','D3','A3','E3','G3','A3','B3']
for r in roots:
    n = note.Note(r)
    fifth = n.transpose(7).nameWithOctave
    octave = n.transpose(12).nameWithOctave
    c = chord.Chord([r, fifth, octave], quarterLength=4.0)
    c.volume.velocity = 78
    chords.append(c)

# Drum part: General MIDI percussion channel usually handled by instrument.
drums = stream.Part(id='Rock drums')
drums.insert(0, instrument.Woodblock())
# Use unpitched percussion-ish notes on MIDI pitches: kick 36, snare 38, hihat 42.
for bar in range(12):
    for slot in range(8):
        # hi-hat every eighth
        hh = note.Note(42, quarterLength=0.5)
        hh.volume.velocity = 45
        drums.append(hh)
# Put actual drum hits in separate part for better MIDI note stacking.
drum_hits = stream.Part(id='Kick Snare')
drum_hits.insert(0, instrument.Woodblock())
for bar in range(12):
    for slot in range(8):
        hits = []
        if slot in [0,4]:
            hits.append(36)
        if slot in [2,6]:
            hits.append(38)
        if hits:
            c = chord.Chord(hits, quarterLength=0.5)
            c.volume.velocity = 100
            drum_hits.append(c)
        else:
            drum_hits.append(note.Rest(quarterLength=0.5))

score.insert(0, guitar)
score.insert(0, bass)
score.insert(0, chords)
score.insert(0, drums)
score.insert(0, drum_hits)

mf = midi.translate.streamToMidiFile(score)
with open(MIDI_PATH, 'wb') as f:
    f.write(mf.writestr())

# --- Fast synth WAV: simple rock-ish tones, no external deps ---
def env(n, attack=0.005, release=0.04):
    a = max(1, int(attack*SR)); r = max(1, int(release*SR))
    s = max(0, n-a-r)
    return [i/a for i in range(a)] + [1.0]*s + [1-i/r for i in range(r)]

def freq(midi_num):
    return 440.0 * (2 ** ((midi_num - 69)/12))

PITCH = {'C':0,'C#':1,'D-':1,'D':2,'D#':3,'E-':3,'E':4,'F':5,'F#':6,'G-':6,'G':7,'G#':8,'A-':8,'A':9,'A#':10,'B-':10,'B':11}
def midi_num(name):
    if name is None: return None
    if len(name) >= 3 and name[1] in ['#','-']:
        pc = name[:2]; octv = int(name[2:])
    else:
        pc = name[0]; octv = int(name[1:])
    return 12*(octv+1)+PITCH[pc]

def add_tone(buf, start, dur, m, amp=0.2, dist=False):
    n = int(dur*SR); st = int(start*SR); f = freq(m)
    e = env(n)
    for i in range(n):
        t = i/SR
        x = math.sin(2*math.pi*f*t) + 0.45*math.sin(2*math.pi*2*f*t) + 0.18*math.sin(2*math.pi*3*f*t)
        if dist:
            x = math.tanh(2.8*x)
        buf[st+i] += amp*x*e[i]

def add_noise(buf, start, dur, amp=0.2, kind='snare'):
    import random
    n = int(dur*SR); st = int(start*SR); e = env(n,0.001,0.08)
    for i in range(n):
        x = random.uniform(-1,1)
        if kind == 'kick':
            x = math.sin(2*math.pi*(90-50*i/max(1,n))*i/SR)
        elif kind == 'hat':
            x = x if i % 2 == 0 else -x
        buf[st+i] += amp*x*e[i]

bars = 12
duration = bars*4*BEAT + 1.0
buf = [0.0] * int(duration*SR)

# riff + bass
for rep in range(6):
    base = rep*8*0.5*BEAT
    for idx,p in enumerate(riff):
        if p: add_tone(buf, base+idx*0.5*BEAT, 0.42*BEAT, midi_num(p), 0.16, True)
    for idx,p in enumerate(bass_riff):
        if p: add_tone(buf, base+idx*0.5*BEAT, 0.46*BEAT, midi_num(p), 0.18, False)

# power chords
for i,r in enumerate(roots):
    m = midi_num(r)
    start = i*4*BEAT
    for off in [0,7,12]:
        add_tone(buf, start, 3.7*BEAT, m+off, 0.08, True)

# drums
for bar in range(bars):
    b0 = bar*4*BEAT
    for slot in range(8):
        ts = b0 + slot*0.5*BEAT
        add_noise(buf, ts, 0.08, 0.035, 'hat')
        if slot in [0,4]: add_noise(buf, ts, 0.18, 0.28, 'kick')
        if slot in [2,6]: add_noise(buf, ts, 0.16, 0.18, 'snare')

peak = max(abs(x) for x in buf) or 1.0
scale = 0.88/peak
with wave.open(WAV_PATH, 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    frames = b''.join(struct.pack('<h', int(max(-1,min(1,x*scale))*32767)) for x in buf)
    w.writeframes(frames)

print(MIDI_PATH)
print(WAV_PATH)
