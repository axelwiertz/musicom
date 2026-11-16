# -*- coding: utf-8 -*-
"""Probe 10: woodblock_test.wav per-stroke levels + fluidsynth option tests."""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

import numpy as np  # noqa: E402
import wave  # noqa: E402

OUT = "/opt/data/projects/Instruments/_test/_probe_melodic_tom"
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"

# --- 1. woodblock_test.wav: per-stroke levels
w = wave.open("/opt/data/projects/Instruments/_test/woodblock_test.wav", "rb")
sr = w.getframerate()
n = w.getnframes()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
w.close()
print("woodblock_test.wav sr", sr, "dur", n / sr)
# strokes at 104bpm 16ths: 240 ticks = 0.144s; measure 0.10s windows at each stroke
bpm = 104
sp16 = 60.0 / bpm / 4
print("per-stroke rms (0.10s window at stroke onset):")
for i in range(16):
    t0 = i * sp16
    seg = data[int(t0 * sr):int((t0 + 0.10) * sr)]
    print(f"  stroke {i:>2}: rms={float(np.sqrt(np.mean(seg ** 2))):.4f} "
          f"peak={float(np.max(np.abs(seg))):.4f}")

# --- 2. fluidsynth option tests on GM117 3-note sequence
import mido  # noqa: E402

TPB = 480
BPM = 120
SPT = 60.0 / BPM / TPB


def mk(notes, path):
    gap = int(2.0 / SPT)
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    t = 0
    for n in notes:
        trk.append(mido.Message("note_on", note=n, velocity=100, channel=0, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=gap // 2))
        t = gap - gap // 2
    m.save(path)


def rms_at(wav, starts, gap_s=2.0):
    w = wave.open(wav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return [float(np.sqrt(np.mean(d[int(s * sr):int((s + 0.3) * sr)] ** 2)))
            for s in starts]


midi = os.path.join(OUT, "opt.mid")
mk([56, 57, 58], midi)
for label, opts in [
    ("default", []),
    ("polyphony=1024", ["-o", "synth.polyphony=1024"]),
    ("reverb=0", ["-o", "synth.reverb.active=0"]),
    ("chorus=0", ["-o", "synth.chorus.active=0"]),
    ("poly=1024+rev=0", ["-o", "synth.polyphony=1024", "-o", "synth.reverb.active=0"]),
]:
    wav = os.path.join(OUT, f"opt_{label.replace('=', '_').replace('+', '_')}.wav")
    r = subprocess.run([FS, "-ni", "-g", "1.2"] + opts + ["-F", wav, SF2, midi],
                       capture_output=True)
    if r.returncode != 0:
        print(label, "FAILED", r.stderr.decode()[-200:])
        continue
    vals = rms_at(wav, [0, 2, 4])
    print(f"  {label:>20}: {vals[0]:.4f} {vals[1]:.4f} {vals[2]:.4f}")
