# -*- coding: utf-8 -*-
"""Measure peak, then normalize phase2 WAV to -1 dBFS via ffmpeg volume filter."""
import os
import subprocess
import wave

import numpy as np

PROJ = "/opt/data/projects/Styles/Techno/083-techno-brownian"
wav = os.path.join(PROJ, "Audio", "083-techno-brownian.wav")
norm = os.path.join(PROJ, "Audio", "_norm.wav")

with wave.open(wav, "rb") as wf:
    n = wf.getnframes()
    sr = wf.getframerate()
    raw = wf.readframes(n)
data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
if wf.getnchannels() == 2:
    data = data.reshape(-1, 2).mean(axis=1)
peak = float(np.max(np.abs(data)))
print("peak before:", round(peak, 5))

# target -1 dBFS (0.8913)
target = 10 ** (-1.0 / 20.0)
gain = target / peak
print("gain:", round(gain, 5), "dB:", round(20 * np.log10(gain), 3))

subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                "-i", wav, "-af", "volume=%.5f" % gain, norm], check=True)

with wave.open(norm, "rb") as wf:
    n = wf.getnframes()
    raw = wf.readframes(n)
data2 = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
if wf.getnchannels() == 2:
    data2 = data2.reshape(-1, 2).mean(axis=1)
print("peak after:", round(float(np.max(np.abs(data2))), 5))
os.replace(norm, wav)
print("normalized in place")
