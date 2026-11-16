# -*- coding: utf-8 -*-
"""Probe 11: dummy-event toggle test — workaround hunt."""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

import mido  # noqa: E402
import numpy as np  # noqa: E402
import wave  # noqa: E402

OUT = "/opt/data/projects/Instruments/_test/_probe_melodic_tom"
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
TPB = 480
BPM = 120
SPT = 60.0 / BPM / TPB


def rms_at(wav, starts, gap_s=2.0):
    w = wave.open(wav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return [float(np.sqrt(np.mean(d[int(s * sr):int((s + 0.3) * sr)] ** 2)))
            for s in starts]


def run(m, wav):
    p = os.path.join(OUT, "t.mid")
    m.save(p)
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, p],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-300:])
    return p


def base_track():
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    return m, trk


GAP = int(2.0 / SPT)
HALF = GAP // 2

# A: baseline 56,57,58
m, trk = base_track()
t = 0
for n in [56, 57, 58]:
    trk.append(mido.Message("note_on", note=n, velocity=100, channel=0, time=t))
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=HALF))
    t = HALF
wav = os.path.join(OUT, "tA.wav")
run(m, wav)
print("A baseline 56,57,58       :", [f"{v:.4f}" for v in rms_at(wav, [0, 2, 4])])

# B: CC64 (sustain) between note 1 and note 2
m, trk = base_track()
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=HALF))
trk.append(mido.Message("control_change", control=64, value=1, channel=0, time=HALF))
trk.append(mido.Message("control_change", control=64, value=0, channel=0, time=0))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=HALF))
trk.append(mido.Message("note_on", note=58, velocity=100, channel=0, time=HALF))
trk.append(mido.Message("note_off", note=58, velocity=0, channel=0, time=HALF))
wav = os.path.join(OUT, "tB.wav")
run(m, wav)
print("B CC64 between 1 and 2    :", [f"{v:.4f}" for v in rms_at(wav, [0, 2, 4])])

# C: ghost note_on (vel 1) on ch9 between 1 and 2
m, trk = base_track()
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=HALF))
trk.append(mido.Message("note_on", note=35, velocity=1, channel=9, time=HALF))
trk.append(mido.Message("note_off", note=35, velocity=0, channel=9, time=0))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=HALF))
trk.append(mido.Message("note_on", note=58, velocity=100, channel=0, time=HALF))
trk.append(mido.Message("note_off", note=58, velocity=0, channel=0, time=HALF))
wav = os.path.join(OUT, "tC.wav")
run(m, wav)
print("C ghost ch9 between 1 and 2:", [f"{v:.4f}" for v in rms_at(wav, [0, 2, 4])])

# D: SHORT note 1 (note_off 0.2s) — does early release change note 2?
m, trk = base_track()
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=96))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=GAP - 96))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=HALF))
trk.append(mido.Message("note_on", note=58, velocity=100, channel=0, time=HALF))
trk.append(mido.Message("note_off", note=58, velocity=0, channel=0, time=HALF))
wav = os.path.join(OUT, "tD.wav")
run(m, wav)
print("D short note1 (0.2s)       :", [f"{v:.4f}" for v in rms_at(wav, [0, 2, 4])])

# E: note 2 with velocity 127 (does max vel break the silence?)
m, trk = base_track()
t = 0
for n, vel in [(56, 100), (57, 127), (58, 100)]:
    trk.append(mido.Message("note_on", note=n, velocity=vel, channel=0, time=t))
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=HALF))
    t = HALF
wav = os.path.join(OUT, "tE.wav")
run(m, wav)
print("E note2 vel=127            :", [f"{v:.4f}" for v in rms_at(wav, [0, 2, 4])])

# F: note 2 pitch = note 1 pitch (56,56,58) — same pitch event 2
m, trk = base_track()
t = 0
for n in [56, 56, 58]:
    trk.append(mido.Message("note_on", note=n, velocity=100, channel=0, time=t))
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=HALF))
    t = HALF
wav = os.path.join(OUT, "tF.wav")
run(m, wav)
print("F same pitch 56,56,58      :", [f"{v:.4f}" for v in rms_at(wav, [0, 2, 4])])
