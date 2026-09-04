# -*- coding: utf-8 -*-
"""Per-window tonality: harmonic energy in 8 harmonics of the DETECTED f0."""
import json
import sys
import wave
from pathlib import Path

import numpy as np

WAV = Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Audio/SP011-jazz-swing-karplus-strong.wav")

with wave.open(str(WAV), "rb") as wf:
    sr = wf.getframerate()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
mono = raw.reshape(-1, 2).mean(axis=1)

win = int(0.5 * sr)
hop = int(0.25 * sr)
results = []
for w0 in range(0, len(mono) - win, hop):
    seg = mono[w0:w0 + win]
    seg = seg - seg.mean()
    if np.sum(seg ** 2) < 1e-8:
        results.append({"t": round(w0 / sr, 2), "f0": None, "tonality": 0.0})
        continue
    ac = np.correlate(seg, seg, "full")[win - 1:]
    ac /= ac[0]
    lo, hi = int(sr / 1000), int(sr / 50)
    lag = lo + int(np.argmax(ac[lo:hi]))
    f0 = sr / lag
    spec = np.abs(np.fft.rfft(seg * np.hanning(win)))
    ff = np.fft.rfftfreq(win, 1 / sr)
    full = float(np.sum(spec))
    he = 0.0
    for h in range(1, 9):
        m = (ff >= f0 * h * 0.97) & (ff <= f0 * h * 1.03)
        if m.any():
            he += float(np.sum(spec[m]))
    results.append({"t": round(w0 / sr, 2), "f0": round(f0, 1),
                    "tonality": round(100 * he / full, 1)})

tones = [r["tonality"] for r in results if r["f0"]]
print(f"windows={len(results)} pitched={len(tones)}")
print(f"tonality%: mean={np.mean(tones):.1f} median={np.median(tones):.1f} min={min(tones):.1f}")
low = [r for r in results if r["f0"] and r["tonality"] < 10]
print(f"windows_with_tonality<10%: {len(low)}")
for r in results:
    print(f"  t={r['t']:5.2f} f0={r['f0']} tonality={r['tonality']}%")

Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Analysis/tonality.json").write_text(json.dumps(results, indent=1))
print("TONALITY DONE")
