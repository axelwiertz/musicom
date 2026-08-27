# -*- coding: utf-8 -*-
"""Write audio provenance sidecars for 074-groove-gpc."""
import os
from workflows.provenance import write_provenance, AI_GENERATED

PROJ = "/opt/data/projects/Styles/Groove/074-groove-gpc"
SEED = 20260820

for stem, phase in (("074-groove-gpc", "2"), ("074-groove-gpc-phase1", "1")):
    for ext in ("wav", "ogg"):
        p = os.path.join(PROJ, "Audio", f"{stem}.{ext}")
        if os.path.exists(p):
            write_provenance(
                p, AI_GENERATED, "FluidSynth TimGM6mb.sf2 render (SP-001)",
                parameters={"bpm": 106, "key": "G natural minor", "phase": phase,
                            "soundfont": "TimGM6mb.sf2", "gain": 0.89,
                            "seed": SEED},
                notes=f"FluidSynth CLI render of phase {phase} MIDI, peak-normalized volume=0.89, Opus 48k")
            print("provenance", os.path.basename(p))

for f in ("Analysis/grid_visualization.txt", "Analysis/summary.json"):
    p = os.path.join(PROJ, f)
    write_provenance(
        p, AI_GENERATED, "GPC (Method 061 Gaussian Process Composition)",
        parameters={"bpm": 106, "key": "G natural minor", "seed": SEED},
        notes="analysis artifact")
    print("provenance", os.path.basename(p))
