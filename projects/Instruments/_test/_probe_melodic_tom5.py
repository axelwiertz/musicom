# -*- coding: utf-8 -*-
"""Probe 5: GM117 one-note-per-file isolation — parity effect real or artifact?"""
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


def one_note(n, vel, path, note_ticks=1920, bpm=60):
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    trk.append(mido.Message("note_on", note=n, velocity=vel, channel=0, time=0))
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=note_ticks))
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


print("single-note-per-file, vel=100, 2 s note at 60 bpm:")
for n in [36, 37, 38, 39, 40, 41, 42, 43, 56, 57, 58, 59]:
    midi = os.path.join(OUT, f"one_{n}.mid")
    wav = os.path.join(OUT, f"one_{n}.wav")
    one_note(n, 100, midi)
    render(midi, wav)
    data, sr = read_wav(wav)
    seg = data[: int(0.3 * sr)]
    r = float(np.sqrt(np.mean(seg ** 2)))
    pk = float(np.max(np.abs(seg)))
    print(f"  note {n:>3}: rms={r:.6f} peak={pk:.5f}")

print("\nnote 57 alone at different velocities:")
for vel in [60, 100, 127]:
    midi = os.path.join(OUT, f"one57_v{vel}.mid")
    wav = os.path.join(OUT, f"one57_v{vel}.wav")
    one_note(57, vel, midi)
    render(midi, wav)
    data, sr = read_wav(wav)
    seg = data[: int(0.3 * sr)]
    r = float(np.sqrt(np.mean(seg ** 2)))
    print(f"  vel {vel:>3}: rms={r:.6f}")

print("\nnote 56 then 57 in one file (2 s apart) — does 57 change?")
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
trk.append(mido.Message("note_on", note=56, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=56, velocity=0, channel=0, time=960))
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=960))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=960))
midi = os.path.join(OUT, "seq_56_57.mid")
wav = os.path.join(OUT, "seq_56_57.wav")
m.save(midi)
render(midi, wav)
data, sr = read_wav(wav)
seg56 = data[int(0.0 * sr):int(0.3 * sr)]
seg57 = data[int(2.0 * sr):int(2.3 * sr)]
print(f"  note 56 rms={float(np.sqrt(np.mean(seg56 ** 2))):.6f}")
print(f"  note 57 rms={float(np.sqrt(np.mean(seg57 ** 2))):.6f}")
