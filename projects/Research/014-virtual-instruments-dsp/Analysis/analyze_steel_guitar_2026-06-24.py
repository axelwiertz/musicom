#!/usr/bin/env python3
"""
Spectral analysis for steel guitar render with pitch bend tracking.
Generates analysis report JSON and plots.
"""
import numpy as np
import soundfile as sf
import json, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE / 'Audio'
ANALYSIS_DIR = BASE / 'Analysis'

data, sr = sf.read(str(AUDIO_DIR / 'steel_guitar_2026-06-24.wav'))

# Time vector
t = np.arange(len(data)) / sr

# Full spectrum
spec = np.abs(np.fft.rfft(data))
freqs = np.fft.rfftfreq(len(data), 1/sr)

# RMS per segment (16 segments for fine granularity)
n_seg = 16
seg_len = len(data) // n_seg
seg_rms = []
seg_times = []
for i in range(n_seg):
    seg = data[i*seg_len:(i+1)*seg_len]
    seg_rms.append(float(np.sqrt(np.mean(seg**2))))
    seg_times.append((i * seg_len / sr, (i+1) * seg_len / sr))

# Pitch tracking via autocorrelation per window
win_size = int(sr * 0.1)  # 100ms windows
hop = int(sr * 0.05)      # 50ms hop
pitch_track = []
time_track = []
for start in range(0, len(data) - win_size, hop):
    frame = data[start:start+win_size] * np.hanning(win_size)
    # Autocorrelation
    ac = np.correlate(frame, frame, mode='full')
    ac = ac[len(ac)//2:]
    # Find first peak after minimum pitch lag (50Hz = 882 samples)
    min_lag = int(sr / 1500)  # don't go below 1500Hz
    max_lag = int(sr / 50)    # don't go above 50Hz
    if max_lag >= len(ac):
        max_lag = len(ac) - 1
    if min_lag >= max_lag:
        continue
    # Find peak in autocorrelation
    peak_region = ac[min_lag:max_lag]
    if np.max(peak_region) > 0:
        peak_idx = np.argmax(peak_region) + min_lag
        freq_est = sr / peak_idx
        # Confidence: ratio of peak to ac[0]
        confidence = ac[peak_idx] / max(ac[0], 1e-10)
        if confidence > 0.1 and 50 < freq_est < 1500:
            pitch_track.append(float(freq_est))
            time_track.append(float(start / sr))

# Spectral centroid per segment (16 segments)
n_seg_spec = 16
seg_len_spec = len(data) // n_seg_spec
centroids = []
for i in range(n_seg_spec):
    seg = data[i*seg_len_spec:(i+1)*seg_len_spec]
    seg_spec = np.abs(np.fft.rfft(seg))
    seg_freqs = np.fft.rfftfreq(len(seg), 1/sr)
    if np.sum(seg_spec) > 0:
        c = float(np.sum(seg_freqs * seg_spec) / np.sum(seg_spec))
    else:
        c = 0.0
    centroids.append(c)

# Metrics summary
metrics = {
    'sample_rate': sr,
    'duration_s': round(len(data)/sr, 2),
    'peak_amplitude': float(np.max(np.abs(data))),
    'rms': float(np.sqrt(np.mean(data**2))),
    'crest_factor': float(np.max(np.abs(data)) / max(np.sqrt(np.mean(data**2)), 1e-10)),
    'spectral_centroid_hz': float(np.sum(freqs * spec) / max(np.sum(spec), 1e-10)),
    'spectral_rolloff_85_hz': float(freqs[np.where(np.cumsum(spec) >= 0.85*np.sum(spec))[0][0]]),
    'dominant_freq_hz': float(freqs[np.argmax(spec[10:]) + 10]),
    'pitch_track': {
        'times': time_track,
        'freqs': pitch_track,
        'min_freq_hz': round(min(pitch_track), 1) if pitch_track else 0,
        'max_freq_hz': round(max(pitch_track), 1) if pitch_track else 0,
        'pitch_bend_range_cents': round(1200 * np.log2(max(pitch_track) / min(pitch_track)), 0) if len(pitch_track) > 1 else 0
    },
    'segment_rms': seg_rms,
    'centroids': centroids,
    'segments': n_seg_spec
}

with open(ANALYSIS_DIR / 'steel_guitar_2026-06-24_analysis.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Analysis saved: {ANALYSIS_DIR / 'steel_guitar_2026-06-24_analysis.json'}")
print(f"\n=== PITCH TRACKING ({len(pitch_track)} windows) ===")
print(f"  Range: {min(pitch_track):.1f} — {max(pitch_track):.1f} Hz")
print(f"  Bend range: {1200 * np.log2(max(pitch_track)/min(pitch_track)):.0f} cents ({1200 * np.log2(max(pitch_track)/min(pitch_track))/100:.1f} semitones)")
print(f"  Windows with pitch detected: {len(pitch_track)}/{len(range(0, len(data)-win_size, hop))}")

print(f"\n=== RMS BY SEGMENT ===")
for i, ((t0, t1), r) in enumerate(zip(seg_times, seg_rms)):
    bar = '█' * int(r * 200)
    print(f"  {t0:>5.1f}s-{t1:>5.1f}s: RMS={r:.4f} {bar}")

print(f"\n=== SPECTRAL CENTROID TREND ===")
for i, c in enumerate(centroids):
    bar = '█' * int(c / 50)
    print(f"  Seg {i+1:>2d}: {c:.0f} Hz {bar}")

print(f"\nDominant freq: {metrics['dominant_freq_hz']:.1f} Hz")
print(f"Centroid: {metrics['spectral_centroid_hz']:.0f} Hz")