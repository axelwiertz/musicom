# -*- coding: utf-8 -*-
"""084-soul-voiceleading-graph — audio render (SP-001 FluidSynth CLI).

Follows the 083 pipeline pattern (render full + phase1, normalize, stats,
provenance) but resolves the SoundFont via discover_soundfont() (FluidR3
preferred — TimGM6mb was the thin/buzzy fallback, fixed 2026-09-01).
"""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

PROJ = "/opt/data/projects/Styles/Soul/084-soul-voiceleading-graph"
AUDIO = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO, exist_ok=True)

from sound.render.fluidsynth import discover_soundfont  # noqa: E402

SF = discover_soundfont()
if not SF:
    raise FileNotFoundError("no SoundFont — install FluidR3_GM.sf2")
print("SoundFont:", SF)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
JOBS = [
    ("084-soul-voiceleading-graph", "MIDI/084-soul-voiceleading-graph.mid"),
    ("084-soul-voiceleading-graph-phase1", "MIDI/084-soul-voiceleading-graph-phase1.mid"),
]

for name, mid_rel in JOBS:
    mid = os.path.join(PROJ, mid_rel)
    wav = os.path.join(AUDIO, name + ".wav")
    ogg = os.path.join(AUDIO, name + ".ogg")
    r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, mid],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav):
        raise RuntimeError(f"fluidsynth failed for {name}: {r.stderr[-400:]}")
    sz = os.path.getsize(wav)
    print(f"WAV {name}: {sz} bytes")
    assert sz > 1000, f"empty/corrupt WAV {name}"
    r2 = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg],
        capture_output=True, text=True)
    if r2.returncode != 0 or not os.path.exists(ogg):
        raise RuntimeError(f"ffmpeg failed for {name}: {r2.stderr[-300:]}")
    print(f"OGG {name}: {os.path.getsize(ogg)} bytes")

print("RENDER DONE")
