# -*- coding: utf-8 -*-
"""Verify SP-021 binaural output: stereo channel decorrelation, ITD/ILD cues, spectral content."""
import numpy as np
import wave

path = '/opt/data/projects/Styles/Production/SP021-binaural-here-comes-the-sun/Audio/here_comes_the_sun_binaural_SP021.wav'

with wave.open(path, 'r') as wf:
    sr = wf.getframerate()
    n = wf.getnframes()
    raw = wf.readframes(n)
stereo = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
L = stereo[0::2]
R = stereo[1::2]
n = min(len(L), len(R))
L, R = L[:n], R[:n]

print(f'Sample rate: {sr}, frames: {n}, duration: {n/sr:.1f}s')

# 1. Basic stats
print(f'\nL peak: {np.max(np.abs(L)):.4f}, R peak: {np.max(np.abs(R)):.4f}')
print(f'L RMS: {np.sqrt(np.mean(L**2)):.4f}, R RMS: {np.sqrt(np.mean(R**2)):.4f}')

# 2. Cross-correlation (ITD detection): find lag with max correlation in [-50, 50] samples
def xcorr_peak(a, b, max_lag=50):
    best_lag, best_val = 0, -1
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            seg_a, seg_b = a[:lag], b[-lag:]
        elif lag > 0:
            seg_a, seg_b = a[lag:], b[:-lag]
        else:
            seg_a, seg_b = a, b
        if len(seg_a) < 1000:
            continue
        c = np.corrcoef(seg_a, seg_b)[0, 1]
        if abs(c) > best_val:
            best_val, best_lag = abs(c), lag
    return best_lag, best_val

# Use a windowed region (first 30s, active music)
win = slice(5 * sr, 35 * sr)
lag, corr = xcorr_peak(L[win], R[win])
print(f'\nCross-correlation peak lag: {lag} samples ({lag/sr*1e6:.0f} us), corr: {corr:.4f}')
print(f'  -> ITD cue present: {"YES" if abs(lag) >= 1 else "weak/none"}')

# 3. Spectral centroid difference (ILD head shadow => far ear darker)
def spectral_centroid(x, sr, nfft=4096):
    from numpy.fft import rfft
    seg = x[:nfft]
    X = np.abs(rfft(seg * np.hanning(nfft)))
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    return np.sum(freqs * X) / (np.sum(X) + 1e-12)

# Average centroid over multiple windows
centroids = []
for start in range(5 * sr, 35 * sr, sr):
    c_l = spectral_centroid(L[start:start + sr], sr)
    c_r = spectral_centroid(R[start:start + sr], sr)
    centroids.append((c_l, c_r))
c_l_avg = np.mean([c[0] for c in centroids])
c_r_avg = np.mean([c[1] for c in centroids])
print(f'\nSpectral centroid L: {c_l_avg:.0f} Hz, R: {c_r_avg:.0f} Hz')
print(f'  -> ILD head-shadow cue present: {"YES" if abs(c_l_avg - c_r_avg) > 50 else "weak/none"}')

# 4. Silence check on full file
mono = (L + R) * 0.5
silent = np.sum(np.abs(mono) < 0.001) / len(mono)
print(f'\nSilence ratio: {silent*100:.1f}%')

# 5. Stereo width (correlation between channels over full file)
corr_full = np.corrcoef(L[::100], R[::100])[0, 1]
print(f'Stereo correlation (decimated): {corr_full:.4f} (lower = wider)')
