# -*- coding: utf-8 -*-
"""Probe 9: scope the every-2nd-note-on silence — melodic patches + channels."""
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


def render_seq(pgm, notes, path, wav, chans=None, gap_s=2.0, len_s=1.0):
    gap = int(gap_s / SPT)
    ln = int(len_s / SPT)
    if chans is None:
        chans = [0] * len(notes)
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    for ch in sorted(set(chans)):
        trk.append(mido.Message("program_change", program=pgm, channel=ch, time=0))
    m.tracks.append(trk)
    t = 0
    for n, ch in zip(notes, chans):
        trk.append(mido.Message("note_on", note=n, velocity=100, channel=ch, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=ch, time=ln))
        t = gap - ln
    m.save(path)
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, path],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-500:])


def rms_at(wav, starts, gap_s=2.0):
    w = wave.open(wav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return [float(np.sqrt(np.mean(data[int(s * sr):int((s + 0.3) * sr)] ** 2)))
            for s in starts]


print("melodic patches, 56,57,58 @2s on ch0:")
for pgm, nm in [(0, "Piano"), (40, "Violin"), (73, "Flute"), (33, "E.Bass")]:
    p = os.path.join(OUT, f"y{pgm}.mid")
    w = os.path.join(OUT, f"y{pgm}.wav")
    render_seq(pgm, [56, 57, 58], p, w)
    vals = rms_at(w, [0, 2, 4])
    print(f"  GM{pgm:>3} {nm:>8}: {vals[0]:.4f} {vals[1]:.4f} {vals[2]:.4f}")

print("\nGM117, 3 channels (56ch0, 57ch1, 58ch2), each with program change:")
p = os.path.join(OUT, "z3ch.mid")
w = os.path.join(OUT, "z3ch.wav")
render_seq(117, [56, 57, 58], p, w, chans=[0, 1, 2])
vals = rms_at(w, [0, 2, 4])
print(f"  {vals[0]:.4f} {vals[1]:.4f} {vals[2]:.4f}")

print("\nGM117, ONE note per channel (56ch0, 57ch1, 58ch2), SAME time 0:")
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
for ch in [0, 1, 2]:
    trk.append(mido.Message("program_change", program=117, channel=ch, time=0))
m.tracks.append(trk)
for n, ch in [(56, 0), (57, 1), (58, 2)]:
    trk.append(mido.Message("note_on", note=n, velocity=100, channel=ch, time=0))
for n, ch in [(56, 0), (57, 1), (58, 2)]:
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=ch, time=960))
p = os.path.join(OUT, "z3sim.mid")
w = os.path.join(OUT, "z3sim.wav")
m.save(p)
r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", w, SF2, p], capture_output=True)
if r.returncode != 0:
    raise RuntimeError(r.stderr.decode()[-500:])
w2 = wave.open(w, "rb")
sr = w2.getframerate()
n = w2.getnframes()
data = np.frombuffer(w2.readframes(n), dtype=np.int16).astype(np.float32) / 32768
w2.close()
seg = data[: int(1.5 * sr)]
print(f"  simultaneous 3 notes: rms={float(np.sqrt(np.mean(seg ** 2))):.4f}")

print("\nGM117, 3 notes same channel but note 2 is a CHORD (56,57 together) then 58:")
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=960))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=960))
trk.append(mido.Message("note_on", note=60, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=960))
trk.append(mido.Message("note_off", note=60, velocity=0, channel=0, time=960))
trk.append(mido.Message("note_on", note=58, velocity=100, channel=0, time=960))
trk.append(mido.Message("note_off", note=58, velocity=0, channel=0, time=960))
p = os.path.join(OUT, "zchord.mid")
w = os.path.join(OUT, "zchord.wav")
m.save(p)
r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", w, SF2, p], capture_output=True)
if r.returncode != 0:
    raise RuntimeError(r.stderr.decode()[-500:])
vals = rms_at(w, [0, 2, 4])
print(f"  56={vals[0]:.4f} 57+60={vals[1]:.4f} 58={vals[2]:.4f}")
