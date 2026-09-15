# -*- coding: utf-8 -*-
"""Compare silence profile dry vs wet to prove tail-only."""
import wave
from pathlib import Path
import numpy as np

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues")

def read_mono(p):
    with wave.open(str(p), "rb") as wf:
        n = wf.getnframes(); ch = wf.getnchannels()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a.astype(np.float64)

for name in ["dry_full_mix.wav", "SP074-drummachine-delta-blues.wav"]:
    a = read_mono(OUT / name)
    m = np.abs(a) < 0.001
    print(f"== {name}: total {m.mean()*100:.2f}% dur {len(a)/SR:.2f}s")
    per = [m[i*SR:(i+1)*SR].mean()*100 for i in range(int(len(a)/SR))]
    print("   " + " ".join(f"{v:4.1f}" for v in per))
