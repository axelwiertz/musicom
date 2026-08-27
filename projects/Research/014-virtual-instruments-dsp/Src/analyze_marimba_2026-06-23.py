#!/usr/bin/env python3
"""Generate system graph for marimba bar experiment - frequency response + spectrogram"""
import numpy as np
import soundfile as sf
import json
import os

SAMPLE_RATE = 48000
base_dir = '/opt/data/projects/Genres/Research/virtual_instruments/'

# Load audio
audio, sr = sf.read(f'{base_dir}dev_marimba_bar_2026-06-23.wav')
print(f"Audio loaded: {len(audio)} samples @ {sr}Hz")

# ─── Compute frequency response of the first strong note ─────────────────
# First note is at sample 0, ~0.5 beats = 0.25s
n_fft = 8192
first_note = audio[:int(0.3 * sr)]
window = np.hanning(len(first_note))
first_note_w = first_note * window

freqs = np.fft.rfftfreq(len(first_note_w), 1/sr)
spectrum = np.abs(np.fft.rfft(first_note_w))
spectrum_db = 20 * np.log10(spectrum + 1e-10)

# Find peaks
peaks = []
for i in range(1, len(spectrum) - 1):
    if spectrum[i] > spectrum[i-1] and spectrum[i] > spectrum[i+1] and spectrum[i] > np.max(spectrum) * 0.01:
        peaks.append((freqs[i], spectrum[i]))

peaks.sort(key=lambda x: -x[1])
top_peaks = []
for f, a in peaks[:10]:
    if 30 < f < 10000:
        top_peaks.append((round(f, 1), round(20*np.log10(a+1e-10), 1)))
        print(f"  Peak: {f:.1f} Hz  ({20*np.log10(a+1e-10):.1f} dB)")

# ─── Generate system graph data ──────────────────────────────────────────
# Filter coefficients for the resonator tube bandpass filter
f0 = 248.55  # resonator freq
Q = 25.0
w0 = 2 * np.pi * f0 / SAMPLE_RATE
alpha = np.sin(w0) / (2 * Q)
b0 = alpha
b1 = 0
b2 = -alpha
a0 = 1 + alpha
a1 = -2 * np.cos(w0)
a2 = 1 - alpha

print(f"\nResonator Bandpass Filter Coefficients:")
print(f"  f0 = {f0} Hz, Q = {Q}")
print(f"  b = [{b0:.6f}, {b1:.6f}, {b2:.6f}]")
print(f"  a = [{a0:.6f}, {a1:.6f}, {a2:.6f}]")

# Compute frequency response of the filter
from scipy import signal
w, h = signal.freqz([b0, b1, b2], [a0, a1, a2], fs=SAMPLE_RATE, worN=4096)

print(f"\nSystem Graph — Marimba Bar with Resonator Tube (2026-06-23)")
print(f"{'='*70}")
print(f"")
print(f"PHYSICAL MODEL STRUCTURE:")
print(f"  Mallet Strike (impulse + band-limited noise)")
print(f"    └─> Bar Partials (5 inharmonic partials: f1, 4f1, 9.5f1, 17.5f1, 27f1)")
print(f"         └─> Exponential Decay (per-partial T60)")
print(f"              └─> ADSR Envelope (A={0.001}s, D={0.02}s, S={0.2}, R={0.15}s)")
print(f"                   └─> Resonator Tube (Bandpass f0={f0}Hz, Q={Q})")
print(f"                        └─> Harmonic Saturation (tanh)")
print(f"")
print(f"PARTIAL TABLE:")
print(f"  #  |  Freq (Hz) |  Amp Ratio |  Decay T60 |  Q Factor")
print(f"  ─────────────────────────────────────────────────────")
print(f"  1  |  {261.63:>9.2f} |  {1.0:>9.4f} |  {1.0:>9.2f}s |  {821.9:>8.1f}")
print(f"  2  |  {1046.52:>9.2f} |  {0.45:>9.4f} |  {0.6:>9.2f}s |  {1972.6:>8.1f}")
print(f"  3  |  {2485.49:>9.2f} |  {0.18:>9.4f} |  {0.35:>9.2f}s |  {2732.9:>8.1f}")
print(f"  4  |  {4578.52:>9.2f} |  {0.07:>9.4f} |  {0.2:>9.2f}s |  {2876.8:>8.1f}")
print(f"  5  |  {7064.01:>9.2f} |  {0.03:>9.4f} |  {0.1:>9.2f}s |  {2219.2:>8.1f}")
print(f"")
print(f"FILTER COEFFICIENTS (Resonator Tube Bandpass, 2nd-order IIR):")
print(f"  Feedforward (b): [{b0:.6f}, {b1:.6f}, {b2:.6f}]")
print(f"  Feedback    (a): [{a0:.6f}, {a1:.6f}, {a2:.6f}]")
print(f"")
print(f"MELODIC PATTERN (2 bars, C major pentatonic, 120 BPM):")
print(f"  Bar 1: C4→D4→E4→G4→A4(acc)→C5(ghost)→E4→G4")
print(f"  Bar 2: A4(acc)→G4→E4→D4→C4(held)→B3(pass)→C4")
print(f"")
print(f"SPECTRAL PEAKS (FFT, first note C4=261.63Hz):")
for f, db in top_peaks:
    label = ""
    for p in [261.63, 1046.52, 2485.49, 4578.52, 7064.01]:
        if abs(f - p) / p < 0.05:
            label = f" ← partial #{int(p/261.63 + 0.5)}"
            break
    print(f"  {f:>7.1f} Hz  ({db:>6.1f} dB){label}")

# ─── Export filter response for reference ─────────────────────────────
print(f"\nResonator filter response (selected frequencies):")
for test_freq in [100, 200, 248.55, 300, 400, 500]:
    idx = np.argmin(np.abs(w - test_freq))
    gain_db = 20 * np.log10(np.abs(h[idx]) + 1e-10)
    print(f"  {test_freq:>5.1f} Hz: {gain_db:>+6.2f} dB")

print(f"\n{'-'*70}")
print(f"FILES EXPORTED:")
for fname in ['dev_marimba_bar_2026-06-23.wav', 'dev_marimba_bar_2026-06-23.ogg',
              'dev_marimba_bar_2026-06-23.opus', 'dev_marimba_bar_2026-06-23.mid',
              'dev_marimba_bar_2026-06-23_report.json']:
    path = os.path.join(base_dir, fname)
    size = os.path.getsize(path)
    print(f"  ✓ {fname:45s} ({size//1024:>4d} KB)")
print(f"{'-'*70}")