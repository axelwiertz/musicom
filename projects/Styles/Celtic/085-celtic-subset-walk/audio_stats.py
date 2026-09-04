#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""085 audio verification: silence ratio + per-second RMS + pitch content.

Uses the same approach as previous nightly projects (078/080/081/082/083):
silent = frac(|x| < 0.001), per-second RMS profile, FFT tonal check in the
50-1000 Hz band (dominant peak should match expected fundamentals, not be
broadband noise).
"""
import json
import os

import numpy as np

PROJ = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk"
AUDIO_DIR = os.path.join(PROJ, "Audio")
OUT = os.path.join(PROJ, "Analysis", "render_stats.json")


def load_wav(path):
    import wave
    with wave.open(path, "rb") as wf:
        ch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
    if sw == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    else:
        x = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def analyze(path):
    x, sr = load_wav(path)
    dur = len(x) / sr
    mono = x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    # per-second RMS
    secs = int(dur)
    rms = []
    for i in range(secs):
        seg = mono[i * sr:(i + 1) * sr]
        rms.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
    # tonal check: FFT dominant peak per 0.5 s window in 50-1000 Hz
    win = int(sr * 0.5)
    dom_peaks = []
    for i in range(0, len(x) - win, win):
        seg = x[i:i + win]
        if np.abs(seg).max() < 0.002:
            continue
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        band = (freqs >= 50) & (freqs <= 1000)
        if band.any():
            f = freqs[band][np.argmax(spec[band])]
            dom_peaks.append(float(f))
    low_rms = sum(1 for r in rms if r < 0.005)
    print(f"{os.path.basename(path)}: dur={dur:.1f}s silent={silent*100:.1f}% "
          f"lowRMSsecs={low_rms}/{len(rms)} domPeaks(50-1000Hz)={len(dom_peaks)}")
    if dom_peaks:
        import collections
        c = collections.Counter(round(p, 1) for p in dom_peaks)
        print("   top dominant freqs:", c.most_common(5))
    return {"file": os.path.basename(path), "duration_s": round(dur, 2),
            "silence_ratio": round(silent, 4),
            "low_rms_seconds": low_rms, "total_seconds": len(rms),
            "tonal_windows": len(dom_peaks),
            "rms_profile": [round(r, 4) for r in rms]}


stats = {}
for f in ("085-celtic-subset-walk.wav", "085-celtic-subset-walk-phase1.wav"):
    p = os.path.join(AUDIO_DIR, f)
    stats[f] = analyze(p)

with open(OUT, "w") as fh:
    json.dump(stats, fh, indent=2)
print("stats written", OUT)
