# -*- coding: utf-8 -*-
"""Silence ratio + per-second RMS profile for 082 renders + pitch verification."""
import json
import os
import wave

import numpy as np

PROJ = "/opt/data/projects/Styles/Ambient/082-ambient-perlin"


def load_mono(path):
    with wave.open(path, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if wf.getnchannels() == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    return data, sr


def analyze(path):
    data, sr = load_mono(path)
    dur = len(data) / sr
    silent = np.sum(np.abs(data) < 0.001) / len(data)
    # per-second RMS map
    secs = int(np.floor(dur))
    rms = []
    for i in range(secs):
        seg = data[i * sr:(i + 1) * sr]
        r = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        rms.append(r)
    silent_secs = sum(1 for r in rms if r < 0.005)
    return {
        "file": os.path.basename(path),
        "duration_s": round(dur, 3),
        "silence_ratio": round(float(silent), 4),
        "silent_seconds": silent_secs,
        "total_seconds": secs,
        "peak": round(float(np.max(np.abs(data))), 4),
        "rms_mean": round(float(np.sqrt(np.mean(data ** 2))), 5),
        "rms_per_second": [round(r, 5) for r in rms],
    }


out = {}
for name in ("082-ambient-perlin", "082-ambient-perlin-phase1"):
    p = os.path.join(PROJ, "Audio", name + ".wav")
    a = analyze(p)
    out[name] = a
    print(name, "dur", a["duration_s"], "silence_ratio", a["silence_ratio"],
          "silent_secs", a["silent_seconds"], "/", a["total_seconds"],
          "peak", a["peak"])

with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(out, f, indent=2)
print("render_stats.json written")
