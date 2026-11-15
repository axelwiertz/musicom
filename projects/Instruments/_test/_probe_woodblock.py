# -*- coding: utf-8 -*-
"""Probe FluidR3 GM115 "Woodblock" — pitch sweep, level, decay, band energy."""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.render.fluidsynth import discover_soundfont  # noqa: E402

sys.path.insert(0, "/opt/data/projects/Instruments")
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

SF2 = discover_soundfont()
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
OUT = "/opt/data/projects/Instruments/_test"
BAR = 1920


def render_pitch(pgm, pitch, tag):
    comp = UnitMatrixComposer(bpm=90, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("X", program=pgm, channel=0)
    comp.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(pitch, 100, 0, 240))
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    comp.set_unit(0, 0, u)
    ok, msg = comp.validate()
    assert ok, msg
    mid = os.path.join(OUT, f"_wb_{tag}_{pitch}.mid")
    wav = os.path.join(OUT, f"_wb_{tag}_{pitch}.wav")
    comp.to_midi(mid)
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid],
                   capture_output=True, check=True)
    with wave.open(wav) as w:
        n = w.getnframes()
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    mono = data.reshape(-1, data.shape[1]).mean(axis=1) if data.ndim > 1 else data
    os.unlink(mid)
    os.unlink(wav)
    return mono, sr


print("SF2:", SF2)
print("\n=== pitch sweep (GM115 Woodblock), vel 100 ===")
print(f"{'note':>4} {'freq':>8} {'rms':>7} {'peak':>7} {'len_ms':>7} {'centroid':>9}")
rows = []
for pitch in list(range(48, 100, 4)):
    mono, sr = render_pitch(115, pitch, "sweep")
    rms = float(np.sqrt(np.mean(mono ** 2)))
    peak = float(np.max(np.abs(mono)))
    # audible length: last sample above 0.1% of peak
    thr = peak * 0.001
    idx = np.nonzero(np.abs(mono) > thr)[0]
    length_ms = (idx[-1] - idx[0]) / sr * 1000 if len(idx) else 0.0
    if peak > 0:
        spec = np.abs(np.fft.rfft(mono))
        freqs = np.fft.rfftfreq(len(mono), 1 / sr)
        centroid = float(np.sum(freqs * spec) / np.sum(spec)) if spec.sum() else 0.0
    else:
        centroid = 0.0
    f = 440.0 * 2 ** ((pitch - 69) / 12)
    print(f"{pitch:>4} {f:8.1f} {rms:7.4f} {peak:7.4f} {length_ms:7.1f} {centroid:9.0f}")
    rows.append((pitch, rms, peak))

print("\nsilent pitches (peak<0.002):", [p for p, r, pk in rows if pk < 0.002])
print("audible pitches:", [p for p, r, pk in rows if pk >= 0.002])

print("\n=== decay profile, pitch 72 (C5) vel 100 ===")
mono, sr = render_pitch(115, 72, "decay")
peak = float(np.max(np.abs(mono)))
print(f"sr={sr} total_ms={len(mono)/sr*1000:.0f} peak={peak:.3f}")
for t0 in (0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.2, 1.6):
    a, b = int(t0 * sr), int((t0 + 0.05) * sr)
    if b <= len(mono):
        seg = float(np.sqrt(np.mean(mono[a:b] ** 2)))
        print(f"  t={t0:4.2f}s rms={seg:.4f} ({seg/peak*100:5.1f}% of peak)")

print("\n=== velocity response, pitch 72 ===")
for vel in (20, 40, 60, 80, 100, 120):
    comp = UnitMatrixComposer(bpm=90, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("X", program=115, channel=0)
    comp.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(72, vel, 0, 240))
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    comp.set_unit(0, 0, u)
    ok, _ = comp.validate()
    assert ok
    mid = os.path.join(OUT, "_wb_vel.mid")
    wav = os.path.join(OUT, "_wb_vel.wav")
    comp.to_midi(mid)
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid],
                   capture_output=True, check=True)
    with wave.open(wav) as w:
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    d = d.reshape(-1, d.shape[1]).mean(axis=1) if d.ndim > 1 else d
    spec = np.abs(np.fft.rfft(d))
    freqs = np.fft.rfftfreq(len(d), 1 / sr)
    centroid = float(np.sum(freqs * spec) / np.sum(spec))
    print(f"  vel {vel:3d}: rms={float(np.sqrt(np.mean(d**2))):.4f} "
          f"peak={float(np.max(np.abs(d))):.3f} centroid={centroid:.0f}Hz")
os.unlink(os.path.join(OUT, "_wb_vel.mid"))
os.unlink(os.path.join(OUT, "_wb_vel.wav"))
print("\ndone")
