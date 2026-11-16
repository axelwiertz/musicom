# -*- coding: utf-8 -*-
"""Probe 8: is the every-2nd-note-on silence GM117-specific?

Test programs 47 (timpani), 115 (woodblock), 116 (taiko), 117 (melodic tom)
with a 3-note sequence (56, 57, 58) at 2 s spacing, one channel.
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


def render_seq(pgm, notes, path, wav, gap_s=2.0, len_s=1.0):
    gap = int(gap_s / SPT)
    ln = int(len_s / SPT)
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=pgm, channel=0, time=0))
    m.tracks.append(trk)
    t = 0
    for n in notes:
        trk.append(mido.Message("note_on", note=n, velocity=100, channel=0, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=ln))
        t = gap - ln
    m.save(path)
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, path],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-500:])


def rms_at(wav, starts, gap_s=2.0, sr=44100):
    w = wave.open(wav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return [float(np.sqrt(np.mean(data[int(s * sr):int((s + 0.3) * sr)] ** 2)))
            for s in starts]


for pgm, nm in [(47, "Timpani"), (115, "Woodblock"), (116, "Taiko"), (117, "Melodic Tom")]:
    p = os.path.join(OUT, f"x{pgm}.mid")
    w = os.path.join(OUT, f"x{pgm}.wav")
    render_seq(pgm, [56, 57, 58], p, w)
    vals = rms_at(w, [0, 2, 4])
    print(f"GM{pgm} {nm:>12}: 56={vals[0]:.4f} 57={vals[1]:.4f} 58={vals[2]:.4f}")
