# -*- coding: utf-8 -*-
"""088 normalize: peak-normalize rendered WAVs to -1 dB, re-encode OGG."""
import subprocess
import os
from pathlib import Path

ROOT = Path("/opt/data/projects/Styles/Funk/088-funk-hawkes")
AUDIO = ROOT / "Audio"

for name in ("088-funk-hawkes", "088-funk-hawkes-phase1"):
    wav = AUDIO / f"{name}.wav"
    if not wav.exists():
        continue
    tmp = AUDIO / f"{name}.norm.wav"
    # try peaknorm; fall back to volume 0.89 if filter missing
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-af", "peaknorm=level=-1", str(tmp)],
        capture_output=True, text=True)
    if r.returncode != 0 or not tmp.exists():
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
             "-af", "volume=0.89", str(tmp)],
            capture_output=True, text=True)
    os.replace(tmp, wav)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
         str(AUDIO / f"{name}.ogg")],
        capture_output=True, text=True)
    print(name, "normalized, wav bytes:", wav.stat().st_size)
