#!/usr/bin/env python3
"""Analyze single-note spectral content."""
import numpy as np
from scipy.io.wavfile import read

sr, audio = read('/opt/data/projects/Genres/Research/virtual_instruments/dev_steel_plate_2026-06-23.wav')

# First note: A3 at 220 Hz, starts at beat 0, lasts 1 beat (0.5s)
# Samples 0 to 0.5*sr
start_n = int(0 * sr)
note = audio[start_n:int(start_n + sr*0.4)].astype(np.float64)  # 0.4s to avoid release tail of next note
fft = np.abs(np.fft.rfft(note))
freqs = np.fft.rfftfreq(len(note), 1/sr)

# Find peaks
peaks = []
for i in range(5, len(fft)-1):
    if fft[i] > fft[i-1] and fft[i] > fft[i+1] and fft[i] > np.median(fft)*3:
        peaks.append((freqs[i], fft[i]))
peaks.sort(key=lambda x: -x[1])

expected = [220, 607, 660, 1188, 1276, 1474, 1958, 2024, 2684, 2926, 3564]

print('Single Note (A3=220Hz) Spectral Peaks:')
print(f'{"Freq (Hz)":>10} {"Magnitude":>10} {"Expected":>10}  Error')
print('-' * 50)
for f, m in peaks[:min(15, len(peaks))]:
    closest = min(expected, key=lambda x: abs(x-f))
    err_pct = abs(f - closest) / closest * 100
    match = 'OK' if err_pct < 5 else 'OFF'
    print(f'{f:>10.1f} {m:>10.0f} {closest:>10.1f}  {match} ({err_pct:.1f}%)')

print('\nNote: Comb filter creates harmonic series (f0, 2*f0, 3*f0...)',
      'which interleaves with the inharmonic partial bank.')