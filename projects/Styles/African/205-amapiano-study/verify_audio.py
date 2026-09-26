# -*- coding: utf-8 -*-
"""Audio verification for 205-amapiano-study: level, silence, tonal content."""
import json
import os
import wave
import numpy as np

PROJ = "/opt/data/repos/musicom/projects/Styles/African/205-amapiano-study"
WAV = os.path.join(PROJ, "Audio", "205-amapiano-study.wav")

w = wave.open(WAV)
sr = w.getframerate()
n = w.getnframes()
ch = w.getnchannels()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
mono = data.reshape(-1, ch).mean(axis=1)
dur = n / sr

peak = float(np.max(np.abs(mono)))
rms = float(np.sqrt(np.mean(mono ** 2)))
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

def midi_to_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def band_rms(sig, lo, hi):
    X = np.fft.rfft(sig)
    f = np.fft.rfftfreq(len(sig), 1 / sr)
    m = (f >= lo) & (f < hi)
    return float(np.sqrt(np.mean(np.abs(X[m]) ** 2)))

def spectrum_at(t0, label, dur_s=0.25):
    i0 = int(t0 * sr)
    seg = mono[i0:i0 + int(dur_s * sr)]
    seg = seg - seg.mean()
    seg = seg * np.hanning(len(seg))
    X = np.fft.rfft(seg)
    f = np.fft.rfftfreq(len(seg), 1 / sr)
    mag = np.abs(X)
    lo = np.sum(mag[(f >= 30) & (f < 150)] ** 2)
    mid = np.sum(mag[(f >= 150) & (f < 2500)] ** 2)
    hi = np.sum(mag[(f >= 2500) & (f < 12000)] ** 2)
    tot = lo + mid + hi
    peakf = f[1 + np.argmax(mag[1:])]
    print(f"  {label} t={t0:.2f}s: lo%={100*lo/tot:.0f} "
          f"mid%={100*mid/tot:.0f} hi%={100*hi/tot:.0f} peak={peakf:.0f}Hz")

print(f"sr={sr} ch={ch} dur={dur:.2f}s")
print(f"peak={peak:.4f} rms={rms:.4f} silence={100*silent:.1f}%")

# Section boundaries: Intro 0-4 bars, GrooveA 4-12, GrooveB 12-20,
# Breakdown 20-24, Climax 24-32, Outro 32-36. bar = 60/112*4 = 2.1429s
BAR_S = 60 / 112 * 4
print(f"bar_s={BAR_S:.3f}s")
print("spectral checks:")
# Intro bar 1 (~1.0s): shaker + kick, no log drum
spectrum_at(1.0, "Intro (kick+shaker)")
# GrooveA bar 1 (~9.5s): log drum enters
spectrum_at(9.5, "GrooveA (log drum in)")
# Climax bar 1 (~53s): full + dense log drum
spectrum_at(53.0, "Climax (dense)")

# Log drum expected: A2=45 -> 110 Hz, F2=41 -> 87.3 Hz, D2=38 -> 73.4 Hz
# Check low-band pitch presence in GrooveA
print("log-drum fundamental candidates (A2=110, F2=87, D2=73, E2=82 Hz):")
i0 = int(9.5 * sr)
seg = mono[i0:i0 + int(2.0 * sr)]
seg = seg - seg.mean()
X = np.fft.rfft(seg * np.hanning(len(seg)))
f = np.fft.rfftfreq(len(seg), 1 / sr)
for name, freq in [("A2", 110.0), ("F2", 87.31), ("D2", 73.42), ("E2", 82.41)]:
    m = (f >= freq - 3) & (f <= freq + 3)
    print(f"  {name} {freq:.1f}Hz: mag={np.max(np.abs(X[m])):.1f}")

result = {
    "sr": sr, "channels": ch, "duration_s": round(dur, 2),
    "peak": round(peak, 4), "rms": round(rms, 4),
    "silence_ratio": round(silent, 4), "silence_flag_30pct": silent > 0.3,
}
with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(result, f, indent=2)
print("wrote Analysis/render_stats.json")
