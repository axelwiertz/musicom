# -*- coding: utf-8 -*-
"""Analyze existing _cand_* probe WAVs for lead candidates 82-87 (note 60 + 84)."""
import wave, os
import numpy as np

d = "/opt/data/projects/Instruments/_test"
for pgm in [55, 82, 83, 84, 85, 86, 87]:
    w = os.path.join(d, f"_cand_{pgm}.wav")
    if not os.path.exists(w):
        print(f"{pgm:3d}  no wav")
        continue
    with wave.open(w, "rb") as f:
        sr = f.getframerate()
        n = f.getnframes()
        raw = np.frombuffer(f.readframes(n), dtype=np.int16).astype(np.float64)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    rms = float(np.sqrt(np.mean(mono ** 2)))
    spec = np.abs(np.fft.rfft(mono[:sr]))
    freqs = np.fft.rfftfreq(sr, 1 / sr)
    cen = float((spec * freqs).sum() / max(spec.sum(), 1e-9))
    # 4-8 kHz buzz fraction
    buzz = spec[(freqs >= 4000) & (freqs < 8000)].sum() / max(spec[(freqs >= 50) & (freqs < 16000)].sum(), 1e-9)
    print(f"{pgm:3d}  size={os.path.getsize(w):8d} rms={rms:8.1f} centroid={cen:7.0f}Hz buzz4-8k={buzz*100:4.1f}%")
