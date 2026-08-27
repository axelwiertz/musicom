#!/usr/bin/env python3
"""Per-second RMS of each cloud file to check tail fill."""
import numpy as np
import wave

for name in ["lead_flute", "nylon_guitar", "electric_bass", "piano"]:
    path = f"/opt/data/projects/Styles/Production/SP016-granular-cuban-trova/Audio/cloud_{name}.wav"
    with wave.open(path, 'rb') as wf:
        nch = wf.getnchannels()
        fr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        data = data.reshape(n, nch).mean(axis=1)
    rms_per_sec = []
    for s in range(0, len(data), fr):
        seg = data[s:s+fr]
        if len(seg) < fr // 2:
            continue
        rms_per_sec.append(round(float(np.sqrt(np.mean(seg**2))), 4))
    print(name, "dur", round(len(data)/fr, 2), "sec RMS:", rms_per_sec)