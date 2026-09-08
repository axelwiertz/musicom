# -*- coding: utf-8 -*-
"""Empirical pitch sweep of FluidR3 GM105 Banjo via FluidSynth.

Renders single notes 24..96 (each 0.2 s, spaced 0.35 s), then measures the
RMS of each note window in the WAV to find the patch's audible range.
Anchors RANGE_MIN/RANGE_MAX for banjo.py on what the SoundFont actually
produces (verify-don't-trust).
"""
import os
import subprocess
import sys
import wave

import mido
import numpy as np

sys.path.insert(0, "/opt/data/projects/Instruments")
from sound.render.fluidsynth import discover_soundfont

SF2 = discover_soundfont()
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SR = 44100
DUR = 0.20        # note length, s
GAP = 0.15        # inter-note gap, s
STEP = DUR + GAP
P0, P1 = 24, 96   # sweep range

mid = mido.MidiFile(ticks_per_beat=480)
tr = mido.MidiTrack()
mid.tracks.append(tr)
tps = 960.0  # ticks per second at 120 bpm, 480 tpb

tr.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))  # 120 bpm
tr.append(mido.Message("program_change", program=105, channel=0, time=0))
for i, p in enumerate(range(P0, P1 + 1)):
    tr.append(mido.Message("note_on", note=p, velocity=92, channel=0, time=0))
    tr.append(mido.Message("note_off", note=p, velocity=0, channel=0,
                           time=int(DUR * tps)))
    tr.append(mido.Message("note_on", note=p, velocity=0, channel=0,
                           time=int(GAP * tps)))  # dummy event to burn gap
    tr.append(mido.Message("note_off", note=p, velocity=0, channel=0, time=0))

midi_path = "/opt/data/projects/Instruments/_test/banjo_sweep.mid"
wav_path = "/opt/data/projects/Instruments/_test/banjo_sweep.wav"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
mid.save(midi_path)
r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav_path, SF2, midi_path],
                   capture_output=True)
if r.returncode != 0:
    sys.exit("fluidsynth failed: " + r.stderr.decode()[-500:])

w = wave.open(wav_path, "rb")
nch = w.getnchannels()
n = w.getnframes()
raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
w.close()
if nch == 2:
    raw = raw.reshape(-1, 2).mean(axis=1)

per = int(STEP * SR)
res = []
for i, p in enumerate(range(P0, P1 + 1)):
    seg = raw[i * per:int(i * per + DUR * SR)]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    res.append((p, rms))
mx = max(r for _, r in res) or 1e-9
print(f"SF2: {SF2}")
print(f"WAV: {wav_path} ({os.path.getsize(wav_path)} bytes)")
aud = []
for p, r in res:
    db = 20 * np.log10(r / mx + 1e-12)
    ok = r >= 0.01 * mx
    if ok:
        aud.append(p)
    if p % 2 == 0 or (p in (aud[0] if aud else 0,)) or (p in (res[-1][0],)):
        print(f"{p:4d} : rms={r:.6f}  {db:7.1f} dB  audible={ok}")
lo, hi = aud[0], aud[-1]
missing = [pp for pp in range(lo, hi + 1) if pp not in aud]
print(f"\nAudible (>=1% of peak RMS): {lo}..{hi}  ({len(aud)} notes)")
print("Gaps inside audible span:", missing if missing else "none")
