# -*- coding: utf-8 -*-
"""Probe 4: GM117 in TimGM6mb vs FluidR3 — isolated note RMS + peaks."""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

import mido  # noqa: E402
import numpy as np  # noqa: E402
import wave  # noqa: E402

OUT = "/opt/data/projects/Instruments/_test/_probe_melodic_tom"
TPB = 480
BPM = 120
SPT = 60.0 / BPM / TPB
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

SF2S = {
    "FluidR3": "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2",
    "TimGM6mb": "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2",
}


def render_notes(notes, path, sf2, vel=100, gap_s=2.0):
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


def render(midi, wav, sf2):
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, sf2, midi],
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


def top_peaks(x, sr, k=3, flo=50, fhi=8000):
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    m = (freqs >= flo) & (freqs <= fhi)
    idx = np.argsort(spec[m])[::-1][:k]
    return [(float(freqs[m][i]), float(spec[m][i])) for i in sorted(idx)]


notes = list(range(36, 85))
win = int(0.30 * 44100)
for name, sf2 in SF2S.items():
    if not os.path.exists(sf2):
        print(f"{name}: MISSING {sf2}")
        continue
    midi_path = os.path.join(OUT, f"iso_{name}.mid")
    wav_path = os.path.join(OUT, f"iso_{name}.wav")
    render_notes(notes, midi_path, sf2)
    render(midi_path, wav_path, sf2)
    data, sr = read_wav(wav_path)
    print(f"\n=== {name} ({os.path.getsize(wav_path)} bytes) ===")
    print(f"{'note':>4} {'expHz':>7} {'rms':>9}  peaks(Hz:amp)")
    loud = []
    for i, n in enumerate(notes):
        start = int(i * 2.0 * sr)
        seg = data[start:start + win]
        if len(seg) < sr // 5:
            break
        r = float(np.sqrt(np.mean(seg ** 2)))
        if r > 0.02:
            loud.append(n)
        pks = top_peaks(seg, sr)
        ps = " ".join(f"{p[0]:.0f}:{p[1]:.0f}" for p in pks)
        print(f"{n:>4} {440 * 2 ** ((n - 69) / 12):>7.1f} {r:>9.5f}  {ps}")
    print(f"loud (>0.02 rms): {loud[0]}..{loud[-1]} ({len(loud)}/{len(notes)})")
