# -*- coding: utf-8 -*-
"""081-funk-schillinger audio verification: silence ratio + per-second RMS + FFT tonal check."""
import json
import os
import wave

import numpy as np

PROJ = "/opt/data/projects/Styles/Funk/081-funk-schillinger"


def analyze(wav_path):
    with wave.open(wav_path, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        ch = wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        raw = raw.reshape(-1, ch).mean(axis=1)
    mono = raw
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    dur = len(mono) / sr
    # per-second RMS
    secs = int(dur)
    rms = []
    for i in range(secs):
        seg = mono[i * sr:(i + 1) * sr]
        if len(seg):
            rms.append(float(np.sqrt(np.mean(seg ** 2))))
    rms = np.array(rms)
    # FFT tonal check: dominant peak per 0.5s window in 50-1000 Hz
    win = int(0.5 * sr)
    n_wins = len(mono) // win
    tonal = 0
    for i in range(n_wins):
        seg = mono[i * win:(i + 1) * win]
        w = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * w))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        m = (freqs >= 50) & (freqs <= 1000)
        if m.any():
            peak_f = freqs[m][np.argmax(spec[m])]
            if peak_f > 0:
                tonal += 1
    return {
        "duration_s": round(dur, 2),
        "silence_ratio": round(silent, 4),
        "rms_mean": round(float(rms.mean()), 4),
        "rms_min": round(float(rms.min()), 4),
        "rms_max": round(float(rms.max()), 4),
        "rms_first20": [round(float(x), 4) for x in rms[:20]],
        "fft_tonal_windows": f"{tonal}/{n_wins}",
    }


out = {}
for name in ("081-funk-schillinger", "081-funk-schillinger-phase1"):
    wav = os.path.join(PROJ, "Audio", name + ".wav")
    stats = analyze(wav)
    out[name] = stats
    print(name, json.dumps(stats))

with open(os.path.join(PROJ, "Analysis/render_stats.json"), "w") as f:
    json.dump(out, f, indent=2)
print("written Analysis/render_stats.json")
