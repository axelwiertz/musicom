# -*- coding: utf-8 -*-
"""Probe 6: GM117 sequence artifact mechanics.

Finding so far: isolated notes loud; consecutive DIFFERENT pitches on one
channel -> every other note quiet. Map the mechanism.
"""
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


def build(notes_chans, path, gap_s=2.0, len_s=1.0):
    """notes_chans: list of (note, channel, vel)."""
    gap = int(gap_s / SPT)
    ln = int(len_s / SPT)
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    t = 0
    for n, ch, vel in notes_chans:
        trk.append(mido.Message("note_on", note=n, velocity=vel, channel=ch, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=ch, time=ln))
        t = gap - ln
    m.save(path)


def render(midi, wav):
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, midi],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-500:])


def read_wav(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return data, sr


def meas(path, starts, gap_s=2.0, sr=44100):
    data, sr = read_wav(path)
    out = []
    for s in starts:
        seg = data[int(s * sr):int((s + 0.3) * sr)]
        out.append(float(np.sqrt(np.mean(seg ** 2))))
    return out


# 1: three different notes, one channel
p = os.path.join(OUT, "m1.mid"); w = os.path.join(OUT, "m1.wav")
build([(56, 0, 100), (57, 0, 100), (58, 0, 100)], p)
render(p, w)
print("1. 56,57,58 one ch :", [f"{v:.4f}" for v in meas(w, [0, 2, 4])])

# 2: same pitch twice then different
p = os.path.join(OUT, "m2.mid"); w = os.path.join(OUT, "m2.wav")
build([(56, 0, 100), (56, 0, 100), (57, 0, 100)], p)
render(p, w)
print("2. 56,56,57 one ch  :", [f"{v:.4f}" for v in meas(w, [0, 2, 4])])

# 3: alternate channels (56 on ch0, 57 on ch1)
p = os.path.join(OUT, "m3.mid"); w = os.path.join(OUT, "m3.wav")
build([(56, 0, 100), (57, 1, 100), (58, 0, 100)], p)
render(p, w)
print("3. 56ch0,57ch1,58ch0:", [f"{v:.4f}" for v in meas(w, [0, 2, 4])])

# 4: long gap (6 s) between two different notes
p = os.path.join(OUT, "m4.mid"); w = os.path.join(OUT, "m4.wav")
build([(56, 0, 100), (57, 0, 100)], p, gap_s=6.0)
render(p, w)
print("4. 56,57 gap 6s     :", [f"{v:.4f}" for v in meas(w, [0, 6], gap_s=6.0)])

# 5: reverse order (57 then 56)
p = os.path.join(OUT, "m5.mid"); w = os.path.join(OUT, "m5.wav")
build([(57, 0, 100), (56, 0, 100)], p)
render(p, w)
print("5. 57,56 one ch     :", [f"{v:.4f}" for v in meas(w, [0, 2])])

# 6: 4 different notes
p = os.path.join(OUT, "m6.mid"); w = os.path.join(OUT, "m6.wav")
build([(56, 0, 100), (58, 0, 100), (60, 0, 100), (62, 0, 100)], p)
render(p, w)
print("6. 56,58,60,62 one ch:", [f"{v:.4f}" for v in meas(w, [0, 2, 4, 6])])

# 7: same pitch twice (different pitches separated by silence? no - same pitch)
p = os.path.join(OUT, "m7.mid"); w = os.path.join(OUT, "m7.wav")
build([(56, 0, 100), (56, 0, 100), (56, 0, 100)], p)
render(p, w)
print("7. 56,56,56 one ch  :", [f"{v:.4f}" for v in meas(w, [0, 2, 4])])

# 8: note-off ONLY for first note before second (same as build, sanity) + short overlap
p = os.path.join(OUT, "m8.mid"); w = os.path.join(OUT, "m8.wav")
build([(56, 0, 100), (57, 0, 100)], p, gap_s=0.5, len_s=0.25)
render(p, w)
data, sr = read_wav(w)
r56 = float(np.sqrt(np.mean(data[int(0.0 * sr):int(0.3 * sr)] ** 2)))
r57 = float(np.sqrt(np.mean(data[int(0.5 * sr):int(0.8 * sr)] ** 2)))
print("8. 56,57 gap 0.5s   :", [f"{r56:.4f}", f"{r57:.4f}"])
