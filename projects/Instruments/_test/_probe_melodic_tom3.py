# -*- coding: utf-8 -*-
"""Probe 3: isolated GM117 notes — is the loud/quiet alternation real?

Renders each note with a 2 s gap (no overlap), measures RMS + dominant
spectral peaks (full 50-8000 Hz) per note.
"""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

import mido  # noqa: E402
import numpy as np  # noqa: E402
import wave  # noqa: E402

from sound.render.fluidsynth import discover_soundfont  # noqa: E402

OUT = "/opt/data/projects/Instruments/_test/_probe_melodic_tom"
SF2 = discover_soundfont()
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
TPB = 480
BPM = 120
SPT = 60.0 / BPM / TPB


def render_notes(notes, path, vel=100, gap_s=2.0):
    gap = int(gap_s / SPT)
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    t = 0
    for n in notes:
        trk.append(mido.Message("note_on", note=n, velocity=vel, channel=0, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=gap // 2))
        t = gap - gap // 2
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


def top_peaks(x, sr, k=4, flo=50, fhi=8000):
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    m = (freqs >= flo) & (freqs <= fhi)
    idx = np.argsort(spec[m])[::-1][:k]
    return [(float(freqs[m][i]), float(spec[m][i])) for i in sorted(idx)]


notes = list(range(30, 79))
midi_path = os.path.join(OUT, "iso.mid")
wav_path = os.path.join(OUT, "iso.wav")
render_notes(notes, midi_path, gap_s=2.0)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
print("rendered", os.path.getsize(wav_path), "bytes, sr", sr)

gap = 2.0
win = int(0.30 * sr)
print(f"\n{'note':>4} {'expHz':>7} {'rms':>8} {'peaks(Hz,amp)':>42}")
loud, quiet = [], []
for i, n in enumerate(notes):
    start = int(i * gap * sr)
    seg = data[start:start + win]
    if len(seg) < sr // 5:
        break
    r = float(np.sqrt(np.mean(seg ** 2)))
    pks = top_peaks(seg, sr)
    ps = " ".join(f"{p[0]:.0f}:{p[1]:.0f}" for p in pks[:3])
    print(f"{n:>4} {440 * 2 ** ((n - 69) / 12):>7.1f} {r:>8.5f} {ps:>42}")
    (loud if r > 0.05 else quiet).append(n)
print(f"\nloud: {loud}")
print(f"quiet: {quiet}")

# spectral centroid per loud note (timbre movement)
print("\ncentroid + low/high split for the loud notes:")
for i, n in enumerate(notes):
    start = int(i * gap * sr)
    seg = data[start:start + win]
    r = float(np.sqrt(np.mean(seg ** 2)))
    if r <= 0.05:
        continue
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    m = (freqs >= 50) & (freqs <= 8000)
    cen = float((freqs[m] * spec[m]).sum() / max(spec[m].sum(), 1e-9))
    loE = float(spec[(freqs >= 50) & (freqs < 250)].sum())
    hiE = float(spec[(freqs >= 250) & (freqs < 4000)].sum())
    f0 = 440.0 * 2.0 ** ((n - 69) / 12.0)
    print(f"  {n:>3} exp {f0:6.1f} Hz  centroid {cen:6.0f} Hz  lo/hi {loE / max(hiE, 1e-9):.2f}")
