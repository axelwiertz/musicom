# -*- coding: utf-8 -*-
"""Inspect stem lengths."""
import wave
from pathlib import Path
for f in sorted(Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues/Audio/stems_dry").glob("*.wav")):
    with wave.open(str(f), "rb") as wf:
        n = wf.getnframes(); sr = wf.getframerate(); ch = wf.getnchannels()
    print(f"{f.name}: {n/sr:.2f}s ch={ch} bytes={f.stat().st_size}")
for f in sorted(Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues").glob("*.wav")):
    with wave.open(str(f), "rb") as wf:
        n = wf.getnframes(); sr = wf.getframerate(); ch = wf.getnchannels()
    print(f"{f.name}: {n/sr:.2f}s ch={ch} bytes={f.stat().st_size}")
