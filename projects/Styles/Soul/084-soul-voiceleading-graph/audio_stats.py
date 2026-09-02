# -*- coding: utf-8 -*-
"""084 audio analysis: silence ratio + RMS profile + spectral buzz check.

Follows the 083 audio_stats pattern, extended with the 4-8kHz buzz check
(comb-filtered unison doubling guard — see Instruments/_test/render_audio.py).
"""
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, "/opt/data/projects/Instruments")
PROJ = "/opt/data/projects/Styles/Soul/084-soul-voiceleading-graph"


def load_mono(path):
    with wave.open(path, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        raw = wf.readframes(n)
        ch = wf.getnchannels()
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    return data, sr


def analyze(path):
    data, sr = load_mono(path)
    dur = len(data) / sr
    silent = np.sum(np.abs(data) < 0.001) / len(data)
    secs = int(np.floor(dur))
    rms = []
    for i in range(secs):
        seg = data[i * sr:(i + 1) * sr]
        r = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        rms.append(r)
    silent_secs = sum(1 for r in rms if r < 0.005)
    # buzz check: 4-8 kHz energy vs audible band (50-16000 Hz)
    from numpy.fft import rfft
    seg = data[: int(0.5 * sr)]
    spec = np.abs(rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    buzz = spec[(freqs >= 4000) & (freqs < 8000)].sum()
    aud = spec[(freqs >= 50) & (freqs < 16000)].sum()
    buzz_frac = float(buzz / max(aud, 1e-9))
    return {
        "file": os.path.basename(path),
        "duration_s": round(dur, 3),
        "silence_ratio": round(float(silent), 4),
        "silent_seconds": silent_secs,
        "total_seconds": secs,
        "peak": round(float(np.max(np.abs(data))), 4),
        "rms_mean": round(float(np.sqrt(np.mean(data ** 2))), 5),
        "buzz_4_8k_frac": round(buzz_frac, 4),
        "rms_per_second": [round(r, 5) for r in rms],
    }


out = {}
for name in ("084-soul-voiceleading-graph", "084-soul-voiceleading-graph-phase1"):
    p = os.path.join(PROJ, "Audio", name + ".wav")
    a = analyze(p)
    out[name] = a
    print(name, "dur", a["duration_s"], "silence_ratio", a["silence_ratio"],
          "silent_secs", a["silent_seconds"], "/", a["total_seconds"],
          "peak", a["peak"], "rms_mean", a["rms_mean"],
          "buzz_4_8k", a["buzz_4_8k_frac"])
    assert a["silence_ratio"] < 0.30, f"too much silence in {name}"
    assert a["buzz_4_8k_frac"] < 0.20, f"buzz in {name}"

with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(out, f, indent=2)
print("render_stats.json written")
print("AUDIO ANALYSIS PASS")
