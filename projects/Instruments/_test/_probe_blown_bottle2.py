# -*- coding: utf-8 -*-
"""Probe 2: GM76 Blown Bottle — single-note envelope, spectrum, velocity."""
import os
import subprocess
import sys
import wave

import numpy as np
from numpy.fft import rfft

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
OUT = "/opt/data/projects/Instruments/_test/_probe_blown_bottle/p2"
os.makedirs(OUT, exist_ok=True)

import mido


def render(note, vel, dur_beats=6, name=None):
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    mid.tracks.append(tr)
    tr = mido.MidiTrack()
    tr.append(mido.Message("program_change", program=76, time=0))
    tr.append(mido.Message("note_on", note=note, velocity=vel, time=0))
    tr.append(mido.Message("note_off", note=note, velocity=0, time=dur_beats * 480))
    mid.tracks.append(tr)
    name = name or f"n{note}_v{vel}"
    p = os.path.join(OUT, f"{name}.mid")
    mid.save(p)
    wv = p.replace(".mid", ".wav")
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wv, SF2, p],
                   capture_output=True, check=True)
    w = wave.open(wv, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return data, sr


def analyze(data, sr, label):
    dur = len(data) / sr
    peak = float(np.max(np.abs(data)))
    rms = float(np.sqrt(np.mean(data ** 2)))
    # envelope: amplitude over 20 ms windows
    wl = int(0.02 * sr)
    nw = len(data) // wl
    env = np.array([np.sqrt(np.mean(data[i * wl:(i + 1) * wl] ** 2)) for i in range(nw)])
    # attack 10->90%
    tmax = float(env.max())
    i10 = np.argmax(env >= 0.1 * tmax) if np.any(env >= 0.1 * tmax) else 0
    i90 = np.argmax(env >= 0.9 * tmax) if np.any(env >= 0.9 * tmax) else len(env)
    attack = (i90 - i10) * 0.02
    # sustain: mean env in 40-70% of note vs peak
    a, b = int(0.4 * nw), int(0.7 * nw)
    sustain = float(np.mean(env[a:b])) / max(tmax, 1e-9)
    # release: time for env to drop from 90% to 10% after last max
    tail = env[int(0.7 * nw):]
    # steady-state spectrum (middle 1 s)
    ss = data[int(0.5 * sr):int(1.5 * sr)]
    spec = np.abs(rfft(ss))
    freqs = np.fft.rfftfreq(len(ss), 1 / sr)
    aud = (freqs >= 50) & (freqs < 16000)
    cent = float(np.sum(freqs[aud] * spec[aud]) / max(np.sum(spec[aud]), 1e-9))
    # band energies
    def band_e(lo, hi):
        b = (freqs >= lo) & (freqs < hi)
        return float(np.sum(spec[b]))
    tot = band_e(50, 16000)
    b48 = band_e(4000, 8000) / max(tot, 1e-9) * 100
    b8 = band_e(8000, 16000) / max(tot, 1e-9) * 100
    # top 6 partial peaks (excluding DC)
    pk_idx = np.argsort(spec)[-12:][::-1]
    pk_idx = [i for i in pk_idx if freqs[i] > 40][:8]
    partials = [(float(freqs[i]), float(spec[i])) for i in pk_idx]
    # fundamental dominance: energy at expected f0 band vs total
    exp_f0 = 440.0 * 2 ** ((note - 69) / 12)
    bnd = (freqs >= exp_f0 * 0.85) & (freqs <= exp_f0 * 1.15)
    f0_e = float(np.sum(spec[bnd]))
    print(f"{label}: peak={peak:.3f} rms={rms:.4f} attack10-90={attack * 1000:.0f}ms "
          f"sustain={sustain:.2f} centroid={cent:.0f}Hz 4-8k={b48:.1f}% 8-16k={b8:.1f}%")
    print(f"   partials: " + ", ".join(f"{f:.0f}Hz({100 * a / max(f0_e,1e-9):.0f}%of_f0)" for f, a in partials[:5]))
    return dict(peak=peak, rms=rms, attack=attack, sustain=sustain, centroid=cent,
                b48=b48, b8=b8, f0_e=f0_e)


print("=== single notes (vel 100, 3 s) ===")
for note in (48, 60, 72, 84, 96):
    data, sr = render(note, 100, dur_beats=6)
    analyze(data, sr, f"note {note}")

print("\n=== velocity response (note 72) ===")
for vel in (20, 40, 60, 80, 100, 120):
    data, sr = render(72, vel, dur_beats=6)
    r = analyze(data, sr, f"vel {vel}")
    print(f"   -> peak {r['peak']:.4f}")

print("\n=== envelope shape note 72 vel 100 (20 ms windows, first 1.2 s) ===")
data, sr = render(72, 100, dur_beats=6)
wl = int(0.02 * sr)
nw = 60
env = np.array([np.sqrt(np.mean(data[i * wl:(i + 1) * wl] ** 2)) for i in range(nw)])
print("   " + " ".join(f"{v:.3f}" for v in env[:40]))
