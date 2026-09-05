#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Render phase-2 MIDI to WAV + OGG via the workflow adapter (SP-001)."""
import os
import sys
import json
import subprocess

from workflows.musicom_workflow import produce
from sound.render.fluidsynth import discover_soundfont

PROJ = "/opt/data/projects/Styles/Cuban/086-son-markov-guajira"
MIDI = os.path.join(PROJ, "MIDI", "086-son-markov-guajira.mid")
AUDIO = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO, exist_ok=True)

sf = discover_soundfont()
print("soundfont:", sf)
assert sf and os.path.exists(sf)

res = produce(MIDI, method="SP-001", out_dir=AUDIO)
print("produced:", res.wav_path)
print("ogg:", res.ogg_path)
wav = str(res.wav_path)
ogg = str(res.ogg_path)
assert os.path.getsize(wav) > 1000
assert os.path.getsize(ogg) > 40

# silence / RMS profile (verification)
import numpy as np
import wave
with wave.open(wav, "rb") as wf:
    sr = wf.getframerate()
    n = wf.getnframes()
    ch = wf.getnchannels()
    raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
mono = data.reshape(-1, ch).mean(axis=1) if ch > 1 else data
dur = len(mono) / sr
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
# per-second RMS map
rms_map = []
for i in range(0, len(mono), sr):
    seg = mono[i:i + sr]
    rms_map.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
peak = float(np.max(np.abs(mono))) if len(mono) else 0.0
stats = {
    "wav": wav, "ogg": ogg,
    "wav_bytes": os.path.getsize(wav), "ogg_bytes": os.path.getsize(ogg),
    "sr": sr, "channels": ch, "duration_s": round(dur, 2),
    "peak": round(peak, 3), "silence_ratio": round(silent, 4),
    "per_second_rms": [round(x, 4) for x in rms_map],
    "method": "SP-001",
}
with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(stats, f, indent=2)
print(json.dumps(stats, indent=2))
