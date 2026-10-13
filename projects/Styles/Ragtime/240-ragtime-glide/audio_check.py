# -*- coding: utf-8 -*-
"""Audio analysis: peak/RMS, silence ratio, per-second RMS map."""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "Audio")

results = {}
for name in ["240-ragtime-glide.wav", "240-ragtime-glide-phase1.wav"]:
    path = os.path.join(AUDIO, name)
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    if sw == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    else:
        x = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
    if nch > 1:
        x = x.reshape(-1, nch).mean(axis=1)
    dur = len(x) / sr
    peak = float(np.max(np.abs(x)))
    rms = float(np.sqrt(np.mean(x ** 2)))
    rms_db = 20 * np.log10(rms + 1e-12)
    silent = float(np.sum(np.abs(x) < 0.001) / len(x))
    # per-second RMS map (0.5 s windows, 1 s stride)
    win = int(sr * 0.5)
    step = int(sr * 1.0)
    sec_rms = []
    for i in range(0, len(x) - win, step):
        seg = x[i:i + win]
        sec_rms.append(float(np.sqrt(np.mean(seg ** 2) + 1e-12)))
    # mid-track gaps: 1s windows with rms below -40 dB (excluding tail)
    mid_gaps = 0
    for i, v in enumerate(sec_rms):
        if 20 * np.log10(v + 1e-12) < -40.0:
            mid_gaps += 1
    results[name] = {
        "path": path,
        "sample_rate": sr,
        "channels": nch,
        "duration_s": round(dur, 2),
        "peak": round(peak, 4),
        "rms": round(rms, 4),
        "rms_db": round(rms_db, 2),
        "silence_ratio": round(silent, 4),
        "silence_pct": round(silent * 100, 2),
        "per_sec_rms": [round(v, 4) for v in sec_rms],
        "mid_track_gaps_below_-40dB": mid_gaps,
        "file_size_bytes": os.path.getsize(path),
    }
    print(name, "dur=%.2fs peak=%.4f rms=%.2fdB silence=%.1f%% gaps=%d" %
          (dur, peak, rms_db, silent * 100, mid_gaps))

with open(os.path.join(HERE, "Analysis", "render_stats.json"), "w") as f:
    json.dump(results, f, indent=2)
print("wrote Analysis/render_stats.json")
