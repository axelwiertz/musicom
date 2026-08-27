#!/usr/bin/env python3
"""Project 014 — Study 02: Blues Rock Shuffle Engine.
Generates paired MIDI + WAV + OGG using mido + FluidSynth.
"""
from pathlib import Path
import subprocess
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

ROOT = Path('/opt/data/projects/014-rock-apprenticeship')
MIDI_DIR = ROOT / 'MIDI'
AUDIO_DIR = ROOT / 'Audio'
MIDI_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

TITLE = 'study-02-blues-rock-shuffle-engine'
MIDI_PATH = MIDI_DIR / f'{TITLE}.mid'
WAV_RAW = AUDIO_DIR / f'{TITLE}-raw.wav'
WAV_PATH = AUDIO_DIR / f'{TITLE}.wav'
OGG_PATH = AUDIO_DIR / f'{TITLE}.ogg'
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'

TPB = 480
BPM = 112
BAR = TPB * 4
LONG = TPB * 2 // 3   # shuffle long eighth
SHORT = TPB // 3      # shuffle short eighth
VEL_GTR = 96
VEL_BASS = 102
VEL_DRUM = 96

NOTE = {
    'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
    'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11,
}

def n(name):
    if isinstance(name, int):
        return name
    if name[1:2] in ['#','b']:
        pc, octv = name[:2], int(name[2:])
    else:
        pc, octv = name[:1], int(name[1:])
    return 12 * (octv + 1) + NOTE[pc]

def add_note(events, start, dur, pitch, vel, channel):
    pitch = n(pitch)
    events.append((start, Message('note_on', note=pitch, velocity=vel, channel=channel, time=0)))
    events.append((start + dur, Message('note_off', note=pitch, velocity=0, channel=channel, time=0)))

def add_chord(events, start, dur, pitches, vel, channel):
    for p in pitches:
        add_note(events, start, dur, p, vel, channel)

def to_track(events, name, program=None, channel=0):
    tr = MidiTrack()
    tr.append(MetaMessage('track_name', name=name, time=0))
    if program is not None:
        tr.append(Message('program_change', program=program, channel=channel, time=0))
    events = sorted(events, key=lambda x: (x[0], 0 if x[1].type == 'note_off' else 1))
    last = 0
    for t, msg in events:
        msg.time = max(0, t - last)
        tr.append(msg)
        last = t
    tr.append(MetaMessage('end_of_track', time=1))
    return tr

# 24-bar form: two 12-bar choruses in E blues.
# 12-bar degrees: I I I I | IV IV I I | V IV I V(turnaround)
prog = ['E','E','E','E','A','A','E','E','B','A','E','B'] * 2
root_low = {'E':'E2','A':'A2','B':'B2'}
root_gtr = {'E':'E3','A':'A3','B':'B3'}
# dominant color note for riff/chord flavor
flat7 = {'E':'D4','A':'G4','B':'A4'}
third = {'E':'G#3','A':'C#4','B':'D#4'}
fifth = {'E':'B3','A':'E4','B':'F#4'}

# Rhythm DNA: shuffle slots within each beat: long attack then snap/offbeat.
guitar_events, bass_events, lead_events, drum_events = [], [], [], []

# Guitar: call-response boogie riff + power/dominant stabs.
for bar_i, root in enumerate(prog):
    b = bar_i * BAR
    r = n(root_gtr[root])
    # boogie cells: root-5, root-6, root-b7, root-6 across beats
    sixth = {'E':'C#4','A':'F#4','B':'G#4'}[root]
    cell = [(r, n(fifth[root])), (r, n(sixth)), (r, n(flat7[root])), (r, n(sixth))]
    for beat, pitches in enumerate(cell):
        t = b + beat * TPB
        add_chord(guitar_events, t, LONG - 18, pitches, VEL_GTR, 0)
        add_chord(guitar_events, t + LONG, SHORT - 18, [pitches[0], pitches[1]], VEL_GTR - 10, 0)
    # bar-end blues bite on measures 4, 8, 12, etc.
    if bar_i % 4 == 3:
        add_chord(guitar_events, b + 3*TPB + LONG, SHORT, [r, r+10, r+12], 112, 0)

# Bass: walking shuffle, locked to kick.
for bar_i, root in enumerate(prog):
    b = bar_i * BAR
    r = n(root_low[root])
    pattern = [0, 7, 9, 10, 9, 7, 3, 0]  # root, 5, 6, b7, 6, 5, blue 3rd, root
    times = [0, LONG, TPB, TPB+LONG, 2*TPB, 2*TPB+LONG, 3*TPB, 3*TPB+LONG]
    durs = [SHORT if i % 2 else LONG for i in range(8)]
    for off, dur, interval in zip(times, durs, pattern):
        add_note(bass_events, b + off, dur - 12, r + interval, VEL_BASS, 1)

# Drums: shuffle ride/hat, backbeat snare, kick roots.
for bar_i in range(len(prog)):
    b = bar_i * BAR
    for beat in range(4):
        t = b + beat * TPB
        # closed hat/ride shuffle pulse: beat + triplet offbeat
        add_note(drum_events, t, 45, 42, 54, 9)
        add_note(drum_events, t + LONG, 45, 42, 46, 9)
        # kick on 1 and 3, ghost extra on 3& for drive
        if beat in [0, 2]:
            add_note(drum_events, t, 70, 36, 105, 9)
        if beat == 2:
            add_note(drum_events, t + LONG, 65, 36, 78, 9)
        # snare on 2 and 4, ghost before 4 sometimes
        if beat in [1, 3]:
            add_note(drum_events, t, 80, 38, 112, 9)
    if bar_i % 2 == 1:
        add_note(drum_events, b + 3*TPB + LONG, 50, 38, 68, 9)

# Lead guitar: second chorus E blues licks. Leave first 12 bars as riff lesson.
lick_notes = ['E4','G4','A4','Bb4','B4','D5','B4','A4','G4','E4']
lick_rhythm = [LONG, SHORT, LONG, SHORT, TPB, LONG, SHORT, LONG, SHORT, TPB]
start = 12 * BAR
cursor = start + BAR // 2
for phrase in range(6):
    for i, p in enumerate(lick_notes if phrase % 2 == 0 else list(reversed(lick_notes))):
        dur = lick_rhythm[i % len(lick_rhythm)]
        # micro-space before note-off prevents smear.
        add_note(lead_events, cursor, max(60, dur - 20), p, 86 + (i % 3) * 8, 2)
        cursor += dur
    cursor += TPB // 2

mid = MidiFile(ticks_per_beat=TPB)
meta = MidiTrack()
meta.append(MetaMessage('track_name', name='014 Study 02 Blues Rock Shuffle Engine', time=0))
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(BPM), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
meta.append(MetaMessage('text', text='E blues. 24 bars. Shuffle eighths = 2:1 triplet feel. I-IV-V 12-bar form twice.', time=0))
meta.append(MetaMessage('end_of_track', time=1))
mid.tracks.append(meta)
# GM programs: 29 overdriven guitar, 30 distortion guitar, 33 fingered bass.
mid.tracks.append(to_track(guitar_events, 'Overdriven shuffle rhythm guitar', program=29, channel=0))
mid.tracks.append(to_track(bass_events, 'Electric bass boogie lock', program=33, channel=1))
mid.tracks.append(to_track(lead_events, 'Blues lead guitar licks', program=30, channel=2))
mid.tracks.append(to_track(drum_events, 'GM rock shuffle drums', program=None, channel=9))
mid.save(MIDI_PATH)

# Render with FluidSynth, then normalize and encode OGG/Opus.
subprocess.run(['fluidsynth', '-ni', SF2, str(MIDI_PATH), '-F', str(WAV_RAW), '-r', '44100'], check=True)
subprocess.run([
    'ffmpeg', '-y', '-i', str(WAV_RAW),
    '-af', 'volume=0.95,alimiter=limit=0.95', str(WAV_PATH)
], check=True)
subprocess.run([
    'ffmpeg', '-y', '-i', str(WAV_PATH),
    '-codec:a', 'libopus', '-application', 'voip', '-b:a', '64k', str(OGG_PATH)
], check=True)
print(MIDI_PATH)
print(WAV_PATH)
print(OGG_PATH)
