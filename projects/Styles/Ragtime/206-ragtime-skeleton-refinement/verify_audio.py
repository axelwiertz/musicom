# -*- coding: utf-8 -*-
"""Audio render verification: duration, peak, RMS, silence ratio, per-second RMS map."""
import json
import os
import wave
import numpy as np

PROJ = "/opt/data/repos/musicom/projects/Styles/Ragtime/206-ragtime-skeleton-refinement"
WAV = os.path.join(PROJ, "Audio", "206-ragtime-skeleton-refinement.wav")
OGG = os.path.join(PROJ, "Audio", "206-ragtime-skeleton-refinement.ogg")

with wave.open(WAV, "rb") as w:
    sr = w.getframerate()
    n_ch = w.getnchannels()
    n_frames = w.getnframes()
    raw = w.readframes(n_frames)

audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
if n_ch > 1:
    audio = audio.reshape(-1, n_ch)
mono = audio.mean(axis=1) if n_ch > 1 else audio

dur = len(mono) / sr
peak = float(np.max(np.abs(mono)))
rms = float(np.sqrt(np.mean(mono ** 2)))
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

# per-second RMS map
per_sec = []
for i in range(0, len(mono), sr):
    seg = mono[i:i + sr]
    per_sec.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
n_active = sum(1 for r in per_sec if r > 0.001)

# mid-track silence: look for silent seconds BETWEEN active ones (exclude leading/trailing tail)
gaps = 0
first = next((i for i, r in enumerate(per_sec) if r > 0.001), None)
last = next((i for i in range(len(per_sec) - 1, -1, -1) if per_sec[i] > 0.001), None)
if first is not None and last is not None:
    for i in range(first, last + 1):
        if per_sec[i] <= 0.001:
            gaps += 1

report = {
    "sr": sr, "channels": n_ch, "duration_s": round(dur, 2),
    "peak": round(peak, 4), "rms": round(rms, 4),
    "silence_ratio": round(silent, 4),
    "per_second_rms": per_sec,
    "active_seconds": n_active,
    "mid_track_silent_gaps": gaps,
    "wav_bytes": os.path.getsize(WAV),
    "ogg_bytes": os.path.getsize(OGG),
}
print(json.dumps(report, indent=2))
with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(report, f, indent=2)

print(f"\nSilence ratio: {100*silent:.1f}%  (tail padding ok; mid-track gaps = {gaps})")
print(f"Active seconds: {n_active}/{len(per_sec)}")
print(f"Duration: {dur:.2f}s  Peak: {peak:.4f}  RMS: {rms:.4f}")
