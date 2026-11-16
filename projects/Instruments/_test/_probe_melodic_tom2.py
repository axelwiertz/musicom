# -*- coding: utf-8 -*-
"""Probe 2: band-limited pitch tracking + per-semitone RMS for GM117."""
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
GAP = 600  # ticks between onsets (0.625 s at 96 bpm)
LEN = 480
BPM = 96
SPT = 60.0 / BPM / TPB


def render_notes(notes, path, vel=100):
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    t = 0
    for n in notes:
        trk.append(mido.Message("note_on", note=n, velocity=vel, channel=0, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=LEN))
        t = GAP - LEN
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


def band_peak(x, sr, flo, fhi):
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    m = (freqs >= flo) & (freqs <= fhi)
    if not m.any():
        return 0.0, 0.0
    idx = int(np.argmax(spec[m]))
    return float(freqs[m][idx]), float(spec[m][idx])


notes = list(range(36, 97))
midi_path = os.path.join(OUT, "sweep1.mid")
wav_path = os.path.join(OUT, "sweep1.wav")
render_notes(notes, midi_path)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
step = GAP * SPT
win = int(0.18 * sr)
print(f"note expect  rms     f0band     f0bandE  loE    ratio")
rows = []
for i, n in enumerate(notes):
    start = int(i * step * sr)
    seg = data[start:start + win]
    if len(seg) < sr // 10:
        break
    r = float(np.sqrt(np.mean(seg ** 2)))
    f0 = 440.0 * 2.0 ** ((n - 69) / 12.0)
    pk, pkamp = band_peak(seg, sr, f0 * 0.80, f0 * 1.30)
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    f0bandE = float(spec[(freqs >= f0 * 0.8) & (freqs <= f0 * 1.3)].sum())
    loE = float(spec[(freqs >= 50) & (freqs <= 200)].sum())
    ratio = f0bandE / max(loE, 1e-9)
    rows.append((n, f0, r, pk, pkamp, f0bandE, loE, ratio))
    print(f"{n:>4} {f0:>6.1f} {r:>7.5f} {pk:>7.1f} {pkamp:>8.1f} {f0bandE:>9.1f} {loE:>7.1f} {ratio:>6.2f}")

# pitch-following verdict: fraction of notes where f0-band peak is within 15% of f0
follow = [row for row in rows if row[3] > 0 and abs(row[3] - row[1]) / row[1] < 0.15]
print(f"\nf0-band peak within 15% of expected: {len(follow)}/{len(rows)}")
print("non-following:", [r[0] for r in rows if not (r[3] > 0 and abs(r[3] - r[1]) / r[1] < 0.15)])

# where is the pitch actually? cluster the f0-band peaks
peaks = sorted(set(round(r[3], 1) for r in rows if r[3] > 0))
print("distinct f0-band peaks:", peaks[:40])
