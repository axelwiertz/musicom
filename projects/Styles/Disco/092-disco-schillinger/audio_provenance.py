# -*- coding: utf-8 -*-
"""Provenance sidecars for the rendered OGG artifacts (092-disco-schillinger)."""
import os

from structures import MusicUnit  # noqa: F401  (compliant-import marker)
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger")
for label, phase, midi in (
        ("092-disco-schillinger.ogg", 2, "092-disco-schillinger.mid"),
        ("092-disco-schillinger-phase1.ogg", 1,
         "092-disco-schillinger-phase1.mid")):
    p = os.path.join(PROJ, "Audio", label)
    if not os.path.exists(p):
        print("skip (missing):", p)
        continue
    path = write_provenance(
        p, classification=AI_ASSISTED,
        generator="workflows.musicom_workflow.produce(method='SP-001')",
        parameters={"phase": phase,
                    "source_midi": midi,
                    "engine": "FluidSynth SoundFont -> WAV -> ffmpeg libopus",
                    "bpm": 118,
                    "key": "Eb major"},
        notes="Disco / Schillinger method-018 render.")
    print("wrote", path)
