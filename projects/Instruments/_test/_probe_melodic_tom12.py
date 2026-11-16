# -*- coding: utf-8 -*-
"""Probe 12: does omitting note_offs fix the alternation? (mechanism nail)"""
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
GAP = int(2.0 / SPT)


def rms_at(wav, starts, gap_s=2.0):
    w = wave.open(wav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return [float(np.sqrt(np.mean(d[int(s * sr):int((s + 0.3) * sr)] ** 2)))
            for s in starts]


def run(m, name):
    p = os.path.join(OUT, f"{name}.mid")
    w = os.path.join(OUT, f"{name}.wav")
    m.save(p)
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", w, SF2, p],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-300:])
    return w


# A: no note_offs at all — 3 overlapping notes
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
for i, n in enumerate([56, 57, 58]):
    trk.append(mido.Message("note_on", note=n, velocity=100, channel=0,
                            time=0 if i == 0 else GAP))
w = run(m, "noff")
print("A no note_offs      :", [f"{v:.4f}" for v in rms_at(w, [0, 2, 4])])

# B: note_off BEFORE the next note_on (0.3s before) — explicit separation
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=GAP - 144))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=144))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=GAP - 144))
trk.append(mido.Message("note_on", note=58, velocity=100, channel=0, time=144))
trk.append(mido.Message("note_off", note=58, velocity=0, channel=0, time=GAP - 144))
w = run(m, "sep")
print("B note_off 0.3s early:", [f"{v:.4f}" for v in rms_at(w, [0, 2, 4])])

# C: two tracks (track1 = note 56, track2 = notes 57,58) — separate MIDI tracks
m = mido.MidiFile(ticks_per_beat=TPB)
trk1 = mido.MidiTrack()
trk1.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
trk1.append(mido.Message("program_change", program=117, channel=0, time=0))
trk1.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk1.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=GAP // 2))
trk2 = mido.MidiTrack()
trk2.append(mido.Message("program_change", program=117, channel=0, time=0))
trk2.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=GAP // 2))
trk2.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=GAP // 2))
trk2.append(mido.Message("note_on", note=58, velocity=100, channel=0, time=GAP // 2))
trk2.append(mido.Message("note_off", note=58, velocity=0, channel=0, time=GAP // 2))
m.tracks = [trk1, trk2]
w = run(m, "twotrk")
print("C two MIDI tracks    :", [f"{v:.4f}" for v in rms_at(w, [0, 2, 4])])
