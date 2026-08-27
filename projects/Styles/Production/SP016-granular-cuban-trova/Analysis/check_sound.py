#!/usr/bin/env python3
"""Verify SP-016 output: loudness, spectral content, non-silence, duration."""
import numpy as np
import wave
import os

wav = "/opt/data/projects/Styles/Production/SP016-granular-cuban-trova/Audio/SP016-granular-cuban-trova.wav"

with wave.open(wav, 'rb') as wf:
    nch = wf.getnchannels()
    sw = wf.getsampwidth()
    fr = wf.getframerate()
    n = wf.getnframes()
    raw = wf.readframes(n)
data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
data = data.reshape(n, nch)
mono = data.mean(axis=1)

print(f"channels={nch} sr={fr} duration={n/fr:.2f}s")
print(f"peak={np.max(np.abs(mono)):.4f}")
print(f"rms={np.sqrt(np.mean(mono**2)):.4f}")
sil = np.sum(np.abs(mono) < 0.001) / len(mono)
print(f"silence_fraction={sil:.4f}")

# Spectral check: FFT over middle 4s
seg = mono[int(2*fr):int(6*fr)]
spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
freqs = np.fft.rfftfreq(len(seg), 1/fr)
# Find top peaks
top_idx = np.argsort(spec)[-8:][::-1]
print("top spectral peaks (Hz):", [round(freqs[i], 1) for i in top_idx])

# Energy across 3 bands
def band_energy(f0, f1):
    mask = (freqs >= f0) & (freqs < f1)
    return float(np.sqrt(np.mean(spec[mask]**2)))
print(f"bass 20-250Hz: {band_energy(20, 250):.1f}")
print(f"mid 250-4k:   {band_energy(250, 4000):.1f}")
print(f"high 4k-20k:  {band_energy(4000, 20000):.1f}")

# Non-silent frame ratio in each second (no dead zones)
for i, s in enumerate(range(0, len(mono), fr)):
    seg2 = mono[s:s+fr]
    if len(seg2) < fr // 2:
        continue
    r = np.sqrt(np.mean(seg2**2))
    print(f"sec {i}: rms={r:.4f}")