# -*- coding: utf-8 -*-
"""Audio verification: silence ratio + per-second RMS on the phase-2 WAV."""
import json
import os

import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
WAV = os.path.join(HERE, "Audio", "238-neoriemannian-afro-drop.wav")

sr, data = wavfile.read(WAV)
if data.ndim == 2:
    mono = data.astype(np.float64).mean(axis=1)
else:
    mono = data.astype(np.float64)
mono /= 32768.0

silent = float(np.mean(np.abs(mono) < 0.001))
peak = float(np.max(np.abs(mono)))
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_db = 20.0 * np.log10(rms + 1e-12)

# per-second RMS map (1s windows)
win = sr
secs = []
for i in range(0, len(mono), win):
    seg = mono[i:i + win]
    secs.append(float(np.sqrt(np.mean(seg ** 2))))
active_secs = sum(1 for s in secs if s > 0.001)
n_secs = len(secs)
# mid-track silence: a "gap" = a second below threshold between active seconds
gaps = 0
for i in range(1, n_secs - 1):
    if secs[i] < 0.001 and secs[i - 1] > 0.001 and secs[i + 1] > 0.001:
        gaps += 1

out = {
    "wav": WAV,
    "sr": sr,
    "duration_s": round(len(mono) / sr, 2),
    "silence_ratio": round(silent, 4),
    "peak": round(peak, 4),
    "rms": round(rms, 5),
    "rms_db": round(rms_db, 2),
    "n_seconds": n_secs,
    "active_seconds": active_secs,
    "mid_track_gaps": gaps,
}
json.dump(out, open(os.path.join(HERE, "Analysis", "render_stats.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
