# -*- coding: utf-8 -*-
"""Final audio sanity: peak, clipping, RMS profile, click detection."""
import sys

import numpy as np
import soundfile as sf

wav = sys.argv[1]
data, sr = sf.read(wav, dtype="float64")
if data.ndim > 1:
    mono = data.mean(axis=1)
else:
    mono = data

peak = np.max(np.abs(mono))
clips = np.sum(np.abs(data) >= 0.999) if data.ndim > 1 else np.sum(np.abs(mono) >= 0.999)
rms = np.sqrt(np.mean(mono ** 2))
# click detection: large sample-to-sample jumps in the first 100ms after onset would indicate discontinuities
diff = np.abs(np.diff(mono))
max_jump = diff.max()
# count frames where consecutive-sample delta > 0.25 (audible click territory)
n_clicks = int(np.sum(diff > 0.25))

# RMS per 1s window (should follow the 8 chorale cells)
win = int(sr)
rms_profile = []
for i in range(0, len(mono) - win, win):
    rms_profile.append(round(float(np.sqrt(np.mean(mono[i:i + win] ** 2))), 5))

print(f"duration={len(mono)/sr:.2f}s peak={peak:.4f} rms={rms:.4f}")
print(f"clipped_samples={clips} max_jump={max_jump:.4f} click_frames={n_clicks}")
print(f"rms_profile_1s={rms_profile}")
ok = peak < 1.0 and clips == 0 and n_clicks < 50
print("SANITY:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
