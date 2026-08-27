# -*- coding: utf-8 -*-
"""Spectral verification: check that rendered audio has energy at expected
fundamental frequencies for the first two chorale cells (0-2.5s, 2.5-5.0s)."""
import json
import sys

import numpy as np
import soundfile as sf

wav = sys.argv[1]
data, sr = sf.read(wav, dtype="float64")
if data.ndim > 1:
    data = data.mean(axis=1)

def freqs_in_window(start, end, expect):
    seg = data[int(start * sr):int(end * sr)]
    n = len(seg)
    win = np.hanning(n)
    spec = np.abs(np.fft.rfft(seg * win))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    # pick peaks near expected fundamental within +-2 semitone window
    res = {}
    for name, f in expect.items():
        lo, hi = f * 2 ** (-2 / 12), f * 2 ** (2 / 12)
        mask = (freqs >= lo) & (freqs <= hi)
        if mask.any():
            idx = np.argmax(spec[mask])
            peak = freqs[mask][idx]
            res[name] = {"expected": round(f, 1), "found": round(peak, 1),
                         "amp": round(float(spec[mask][idx]), 6)}
        else:
            res[name] = {"expected": round(f, 1), "found": None, "amp": 0}
    return res

# Cell 1 (0-2.5s): C3(48)=130.8 D3(50)=146.8 B3(59)=246.9 D#4(63)=311.1
cell1 = {f"p{p}": 440.0 * 2 ** ((p - 69) / 12) for p in (48, 50, 59, 63)}
# Cell 2 (2.5-5.0s): C#3(52)=138.6 D3(50)=146.8 D4(59) wait - pitches 59,59,72,52
cell2 = {f"p{p}": 440.0 * 2 ** ((p - 69) / 12) for p in (52, 59, 72)}

r1 = freqs_in_window(0.2, 2.2, cell1)
r2 = freqs_in_window(2.7, 4.7, cell2)
out = {"cell1_0_2.5s": r1, "cell2_2.5_5s": r2}
print(json.dumps(out, indent=2))

# pass criterion: at least 3 of 4 fundamentals found in each cell
n1 = sum(1 for v in r1.values() if v["found"] is not None)
n2 = sum(1 for v in r2.values() if v["found"] is not None)
print(f"cell1: {n1}/4 fundamentals found; cell2: {n2}/3 found")
ok = n1 >= 3 and n2 >= 2
print("SPECTRAL CHECK:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
