#!/usr/bin/env python3
"""Analyze spectral peaks of rendered steel plate audio."""
import numpy as np
from scipy.io.wavfile import read

sr, audio = read('/opt/data/projects/Genres/Research/virtual_instruments/dev_steel_plate_2026-06-23.wav')
segment = audio[:int(sr*2)].astype(np.float64)
fft = np.abs(np.fft.rfft(segment))
freqs = np.fft.rfftfreq(len(segment), 1/sr)

peaks = []
for i in range(10, len(fft)-1):
    if fft[i] > fft[i-1] and fft[i] > fft[i+1] and fft[i] > np.median(fft)*5:
        peaks.append((freqs[i], fft[i]))
peaks.sort(key=lambda x: -x[1])

expected = [220, 607, 660, 1188, 1276, 1474, 1958, 2024, 2684, 2926, 3564]

print('Measured Spectral Peaks:')
print(f'{"Freq (Hz)":>10} {"Magnitude":>10} {"Expected":>10}  Match')
print('-' * 50)
for f, m in peaks[:15]:
    closest = min(expected, key=lambda x: abs(x-f))
    err = abs(f - closest) / closest * 100
    match = 'OK' if err < 5 else 'OFF'
    print(f'{f:>10.1f} {m:>10.0f} {closest:>10.1f}  {match} ({err:.1f}%)')