# -*- coding: utf-8 -*-
"""Probe 7: GM117 fill realism — 16th-note fill, envelope, chord."""
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


def rms(x):
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0


# --- 1. 16th-note fill at 104 bpm (the verify pattern)
bpm = 104
sp16 = 60.0 / bpm / 4  # 16th note seconds
fill = [57, 60, 62, 64, 62, 60, 57, 55, 57, 60, 62, 64, 65, 64, 62, 60]
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
t16 = int(sp16 / (60.0 / bpm / TPB))
t = 0
for n in fill:
    trk.append(mido.Message("note_on", note=n, velocity=96, channel=0, time=t))
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=t16 // 2))
    t = t16 - t16 // 2
midi = os.path.join(OUT, "fill16.mid")
wav = os.path.join(OUT, "fill16.wav")
m.save(midi)
render(midi, wav)
data, sr = read_wav(wav)
print("16th fill at", bpm, "bpm (note, rms in 16th window, peak):")
for i, n in enumerate(fill):
    seg = data[int(i * sp16 * sr):int((i + 1) * sp16 * sr)]
    print(f"  {i:>2} note {n:>3}: rms={rms(seg):.4f} peak={float(np.max(np.abs(seg))):.4f}")

# --- 2. envelope of (56, 57) gap 2s — is the quiet note delayed or missing?
bpm2 = 120
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm2), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
gap = int(2.0 / (60.0 / bpm2 / TPB))
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=gap // 2))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=gap // 2))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=gap // 2))
midi = os.path.join(OUT, "env.mid")
wav = os.path.join(OUT, "env.wav")
m.save(midi)
render(midi, wav)
data, sr = read_wav(wav)
print("\nenvelope 50ms blocks (56@0s, 57@2s):")
for i in range(0, int(4.0 / 0.05)):
    seg = data[int(i * 0.05 * sr):int((i + 1) * 0.05 * sr)]
    r = rms(seg)
    if r > 0.005:
        print(f"  {i * 0.05:4.2f}s rms={r:.4f}")

# --- 3. chord: three notes simultaneous
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
for n in [56, 60, 64]:
    trk.append(mido.Message("note_on", note=n, velocity=96, channel=0, time=0))
for n in [56, 60, 64]:
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=960))
midi = os.path.join(OUT, "chord.mid")
wav = os.path.join(OUT, "chord.wav")
m.save(midi)
render(midi, wav)
data, sr = read_wav(wav)
seg = data[: int(1.5 * sr)]
print(f"\nchord 56+60+64: rms={rms(seg):.4f} peak={float(np.max(np.abs(seg))):.4f}")

# --- 4. two notes same time (56,57 together)
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
for n in [56, 57]:
    trk.append(mido.Message("note_on", note=n, velocity=96, channel=0, time=0))
for n in [56, 57]:
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=960))
midi = os.path.join(OUT, "pair.mid")
wav = os.path.join(OUT, "pair.wav")
m.save(midi)
render(midi, wav)
data, sr = read_wav(wav)
seg = data[: int(1.5 * sr)]
print(f"pair 56+57: rms={rms(seg):.4f} peak={float(np.max(np.abs(seg))):.4f}")
