# -*- coding: utf-8 -*-
"""Reference: FluidSynth render of the same jazz MIDI, then same tonality check."""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.render.fluidsynth import discover_soundfont

SRC = Path("/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid")
OUT = Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Analysis/ref_fluidsynth.wav")

sf = discover_soundfont()
print("soundfont:", sf)
subprocess.run(["/opt/data/micromamba/envs/musicom/bin/fluidsynth", "-ni", "-g", "1.2",
                "-F", str(OUT), sf, str(SRC)],
               check=True, capture_output=True)
print("ref size:", OUT.stat().st_size)

with wave.open(str(OUT), "rb") as wf:
    sr = wf.getframerate()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
mono = raw.reshape(-1, 2).mean(axis=1)
dur = len(mono) / sr
print(f"ref dur={dur:.2f}s")

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
print(f"REF tonality%: mean={np.mean(tones):.1f} median={np.median(tones):.1f} min={min(tones):.1f}")
low = [r for r in results if r["f0"] and r["tonality"] < 10]
print(f"REF windows tonality<10%: {len(low)}")
Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Analysis/ref_tonality.json").write_text(json.dumps(results, indent=1))
print("REF DONE")
