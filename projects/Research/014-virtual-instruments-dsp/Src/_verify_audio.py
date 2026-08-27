#!/usr/bin/env python3
"""Verify audio output - check levels, spectral content."""
import numpy as np
import soundfile as sf
from scipy.signal import spectrogram

data, sr = sf.read('/opt/data/projects/Research/014-virtual-instruments-dsp/Audio/steel_guitar_2026-06-24.wav')
print(f"Sample rate: {sr}")
print(f"Duration: {len(data)/sr:.2f}s")
print(f"Peak amplitude: {np.max(np.abs(data)):.4f}")
print(f"RMS: {np.sqrt(np.mean(data**2)):.4f}")
print(f"Min: {np.min(data):.4f}, Max: {np.max(data):.4f}")

# Check that audio isn't silent
non_zero = np.count_nonzero(np.abs(data) > 0.001)
print(f"Non-silent samples: {non_zero}/{len(data)} ({100*non_zero/len(data):.1f}%)")

# Quick spectral check
spec = np.abs(np.fft.rfft(data[:sr*2]))  # First 2 seconds
freqs = np.fft.rfftfreq(sr*2, 1/sr)
peak_idx = np.argmax(spec[10:]) + 10
print(f"Dominant freq (first 2s): {freqs[peak_idx]:.1f} Hz")
print(f"Audio OK: {'YES' if non_zero > 1000 else 'NO'}")