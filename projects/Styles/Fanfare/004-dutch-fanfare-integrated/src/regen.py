#!/usr/bin/env python3
import os
import sys
import numpy as np
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from scipy.io import wavfile

# Force project root into path
sys.path.insert(0, '/opt/data/repos')

# Now import the library we fixed!
from musicom.structures.unit import MusicUnit, MusicEvent
from musicom.rules.progression import PatternMovement
from musicom.rules.counterpoint import Counterpoint

project_dir = "/opt/data/projects/Styles/Fanfare/004-dutch-fanfare-integrated"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)

TPB = 480
TEMPO_BPM = 132
TEMPO = bpm2tempo(TEMPO_BPM)
BAR = TPB * 4
TOTAL = BAR * 8

# Use library progression: Cyclic Fifths (1, 4, 7, 3, 6, 2, 5, 1)
progression = PatternMovement.fifths_down_progression
key_root = 58  # Bb

def build_mid_track(name, events, channel, program):
    tr = MidiTrack()
    tr.name = name
    tr.append(Message('program_change', program=program, channel=channel, time=0))
    
    # Sort events by time
    events.sort(key=lambda x: x.start_tick)
    
    cur = 0
    for e in events:
        dt = e.start_tick - cur
        tr.append(Message('note_on', note=e.pitch, velocity=e.volume, channel=channel, time=dt))
        tr.append(Message('note_off', note=e.pitch, velocity=0, channel=channel, time=e.duration))
        cur = e.start_tick + e.duration
    
    tr.append(MetaMessage('end_of_track', time=max(0, TOTAL - cur)))
    return tr

# Generate Trumpet (Lead) and Tuba (Bass) as MusicUnits for rule checking
trumpet_events = []
tuba_events = []

for i, degree in enumerate(progression):
    start = i * BAR
    scale = [0, 2, 4, 5, 7, 9, 11]
    bass_p = key_root - 12 + scale[degree-1]
    lead_p = key_root + 12 + scale[degree-1]
    
    tuba_events.append(MusicEvent(pitch=bass_p, start_tick=start, end_tick=start+BAR-10, volume=80))
    trumpet_events.append(MusicEvent(pitch=lead_p, start_tick=start, end_tick=start+BAR-10, volume=100))

trumpet_unit = MusicUnit(events=trumpet_events)
tuba_unit = MusicUnit(events=tuba_events)

# RULE CHECK: Parallel Perfect Intervals
cp = Counterpoint(trumpet_unit, tuba_unit)
if cp.has_parallel_perfect_intervals():
    print("WARNING: Parallel perfect intervals detected. Adjusting Lead...")
    # Basic fix: shift trumpet up a third
    for e in trumpet_unit.events:
        e.pitch += 4

# MIDI Export
mid = MidiFile(ticks_per_beat=TPB)
meta = MidiTrack()
meta.append(MetaMessage('set_tempo', tempo=TEMPO))
meta.append(MetaMessage('end_of_track', time=TOTAL))
mid.tracks.append(meta)

mid.tracks.append(build_mid_track("Trumpet", trumpet_unit.events, 0, 56))
mid.tracks.append(build_mid_track("Tuba", tuba_unit.events, 1, 58))

mid.save(f"{project_dir}/MIDI/loop.mid")

# Audio Render (Sines)
sr = 44100
audio = np.zeros(int(sr * (TOTAL/TPB * 60/TEMPO_BPM)), dtype=np.float32)
m2f = lambda n: 440.0 * (2 ** ((n - 69) / 12.0))

for e in trumpet_unit.events + tuba_unit.events:
    st = int(e.start_tick / TPB * 60 / TEMPO_BPM * sr)
    dur_s = e.duration / TPB * 60 / TEMPO_BPM
    en = st + int(dur_s * sr)
    t = np.arange(en - st) / sr
    audio[st:en] += (e.volume/127) * 0.1 * np.sin(2 * np.pi * m2f(e.pitch) * t)

wavfile.write(f"{project_dir}/Audio/loop.wav", sr, (audio * 0.9 / np.max(np.abs(audio))).astype(np.float32))
print("ok")
