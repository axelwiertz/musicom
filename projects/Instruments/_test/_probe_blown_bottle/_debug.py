# -*- coding: utf-8 -*-
"""Debug: is GM76 silent in FluidR3, or is the probe MIDI broken?"""
import os
import subprocess
import sys
import wave

import numpy as np

FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"

import mido

out = "/opt/data/projects/Instruments/_test/_probe_blown_bottle/debug"


def build(pgm, notes_vel):
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    mid.tracks.append(tr)
    tr = mido.MidiTrack()
    tr.append(mido.Message("program_change", program=pgm, time=0))
    prev = 0
    for n, vel, dur in notes_vel:
        tr.append(mido.Message("note_on", note=n, velocity=vel, time=n - prev if False else 0))
        # NOTE: time=0 delta between consecutive program/notes is fine for a chord
        prev = n
        tr.append(mido.Message("note_off", note=n, velocity=0, time=dur))
        prev = dur
    mid.tracks.append(tr)
    return mid


def rms_of(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return float(np.sqrt(np.mean(data ** 2))), float(np.max(np.abs(data))), sr, n / sr


os.makedirs(out, exist_ok=True)

# 1. dump the sweep midi
sweep = "/opt/data/projects/Instruments/_test/_probe_blown_bottle/sweep.mid"
m = mido.MidiFile(sweep)
print("sweep.mid tracks:", len(m.tracks))
for ti, t in enumerate(m.tracks):
    print(f"  track {ti}: {len(t)} msgs; first 5: {[(x.type, getattr(x, 'note', None), getattr(x, 'time', None)) for x in t[:5]]}")
    print(f"    last 3: {[(x.type, getattr(x, 'note', None), getattr(x, 'time', None)) for x in t[-3:]]}")

# 2. control: single C4 (60) piano
for pgm, name in [(0, "piano"), (76, "bottle"), (75, "panflute")]:
    mid = build(pgm, [(60, 100, 720)])
    p = os.path.join(out, f"{name}.mid")
    mid.save(p)
    wv = p.replace(".mid", ".wav")
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wv, SF2, p], capture_output=True)
    rms, pk, sr, dur = rms_of(wv)
    print(f"{name} pgm={pgm}: rms={rms:.4f} peak={pk:.4f} dur={dur:.2f}s rc={r.returncode}")

# 3. chord of three bottle notes (check polyphony/register)
for notes in [[48, 60, 72], [60, 72, 84], [72, 84, 96]]:
    mid = build(76, [(n, 100, 720) for n in notes])
    p = os.path.join(out, f"bottle_{notes[0]}.mid")
    mid.save(p)
    wv = p.replace(".mid", ".wav")
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wv, SF2, p], capture_output=True)
    rms, pk, sr, dur = rms_of(wv)
    print(f"bottle chord {notes}: rms={rms:.4f} peak={pk:.4f}")
