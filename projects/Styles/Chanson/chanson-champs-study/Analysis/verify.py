# -*- coding: utf-8 -*-
"""Verification for the chanson study — real numbers, not file-size asserts.

1. Reverse-path: analyze_midi() on the composed MIDI -> key / progression / density.
2. Spectral: WAV duration, peak, RMS, silence %, + FFT dominant-pitch check.
"""
import numpy as np
from scipy.io import wavfile

from workflows.analyze import analyze_midi

MIDI = "MIDI/chanson-champs-study.mid"
WAV = "Audio/chanson-champs-study.wav"

print("=== REVERSE ANALYSIS (analyze_midi) ===")
rep = analyze_midi(MIDI, key="C")
print(f"key={rep.key} mode={rep.mode} bpm={rep.bpm:.0f} notes={rep.total_notes} "
      f"dur={rep.duration_seconds:.1f}s")
print(f"roman progression: {'-'.join(rep.roman_progression)}")
# collapse to section-ordered unique chords
uniq = []
for r in rep.roman_progression:
    if not uniq or uniq[-1] != r:
        uniq.append(r)
print(f"ordered unique: {'-'.join(uniq)}")
print(f"forte set-classes: {rep.forte_names}")
print(f"density per track: {rep.density}")

print()
print("=== SPECTRAL (WAV) ===")
sr, data = wavfile.read(WAV)
if data.ndim == 2:
    mono = data.mean(axis=1).astype(np.float64)
else:
    mono = data.astype(np.float64)
mono /= 32768.0
dur = len(mono) / sr
peak = np.abs(mono).max()
rms = np.sqrt((mono ** 2).mean())
silence = float((np.abs(mono) < 0.001).mean())
print(f"sr={sr} dur={dur:.1f}s peak={peak:.3f} rms={rms:.3f} silence={silence*100:.1f}%")

# FFT dominant pitch per 1s window (first 8 s) — confirm tonal content
print("dominant FFT peak (Hz) per 1s window:")
N = sr  # 1s window
for w in range(min(8, int(dur))):
    seg = mono[w * N:(w + 1) * N]
    if len(seg) < N:
        break
    win = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(win))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    band = (freqs >= 60) & (freqs <= 2000)
    peak_i = np.argmax(spec[band])
    print(f"  t={w}-{w+1}s: {freqs[band][peak_i]:.0f} Hz")
