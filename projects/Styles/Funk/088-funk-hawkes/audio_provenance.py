# -*- coding: utf-8 -*-
"""088 audio provenance: write per-artifact provenance.json sidecars."""
import os

from workflows.provenance import write_provenance, AI_GENERATED

PROJ = "/opt/data/projects/Styles/Funk/088-funk-hawkes"
AUDIO_DIR = os.path.join(PROJ, "Audio")

for name in ("088-funk-hawkes", "088-funk-hawkes-phase1"):
    for ext in ("wav", "ogg"):
        p = os.path.join(AUDIO_DIR, f"{name}.{ext}")
        if not os.path.exists(p):
            print("missing", p)
            continue
        write_provenance(
            p, AI_GENERATED, "musicom nightly 088-funk-hawkes produce SP-001",
            sources=["SP-001 fluidsynth FluidR3_GM", f"088 {name} midi"],
            parameters={"render": "SP-001", "phase": name.split("-")[-1]})
        print("provenance:", os.path.basename(p))
