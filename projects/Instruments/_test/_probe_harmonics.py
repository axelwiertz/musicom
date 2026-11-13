# -*- coding: utf-8 -*-
"""Probe GM 31 Guitar Harmonics in FluidR3_GM.sf2."""
import os, subprocess, sys, wave
import numpy as np
import mido

SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
OUT = "/tmp/probe31"
os.makedirs(OUT, exist_ok=True)


def render(notes, pgm=31, dur=1.6, name="p"):
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    tr.append(mido.Message("program_change", program=pgm, channel=0, time=0))
    t = 0
    for n in notes:
        tr.append(mido.Message("note_on", note=n, velocity=90, channel=0, time=t))
        tr.append(mido.Message("note_off", note=n, velocity=0, channel=0,
                               time=int(dur * 480)))
        t = 0
    path = os.path.join(OUT, name + ".mid")
    mid.save(path)
    wav = os.path.join(OUT, name + ".wav")
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, path],
                   capture_output=True, check=True)
    return wav


def load(wav):
    w = wave.open(wav, "rb"); sr = w.getframerate()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return sr, d


# 1) single-note sweeps for range audibility
print("== note sweep (program 31) ==")
for n in [28, 33, 40, 45, 52, 55, 60, 64, 67, 72, 76, 79, 84, 88, 91, 96]:
    wav = render([n], name=f"n{n}")
    sr, d = load(wav)
    rms = float(np.sqrt(np.mean(d ** 2)))
    peak = float(np.max(np.abs(d)))
    print(f"  note {n:3d} ({440*2**((n-69)/12):7.1f} Hz) rms={rms:.4f} peak={peak:.3f}")

# 2) harmonic structure: fundamental C4 (60) and E4 (64)
print("\n== partial structure ==")
for n in [52, 60, 67]:
    wav = render([n], name=f"s{n}")
    sr, d = load(wav)
    seg = d[int(0.05 * sr):int(0.45 * sr)]
    win = np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg * win))
    fr = np.fft.rfftfreq(len(seg), 1 / sr)
    f0 = 440 * 2 ** ((n - 69) / 12)
    print(f"  note {n} f0={f0:.1f}Hz")
    amps = []
    for k in range(1, 7):
        idx = np.argmin(np.abs(fr - k * f0))
        a = spec[max(0, idx - 3):idx + 4].max()
        amps.append(a)
    tot = max(amps[0], 1e-9)
    print("    partials %:", ", ".join(f"{k+1}x={100*a/tot:5.1f}%" for k, a in enumerate(amps)))

# 3) decay / ring length
print("\n== decay (note 64) ==")
wav = render([64], dur=3.0, name="dec")
sr, d = load(wav)
peak = float(np.max(np.abs(d)))
for a, b in [(0.0, 0.2), (0.2, 0.6), (0.6, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 2.5)]:
    seg = d[int(a * sr):int(b * sr)]
    if len(seg):
        print(f"  {a}-{b}s rms/peak={float(np.sqrt(np.mean(seg**2)))/peak:.4f}")
