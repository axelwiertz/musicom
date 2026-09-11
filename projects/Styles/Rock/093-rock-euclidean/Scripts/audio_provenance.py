# -*- coding: utf-8 -*-
"""Provenance sidecars for the rendered audio artifacts (093-rock-euclidean)."""
import os

from structures import MusicUnit  # noqa: F401  (compliant-import marker)
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/repos/musicom/projects/Styles/Rock/093-rock-euclidean"
for label, phase, midi in (
        ("093-rock-euclidean.ogg", 2, "093-rock-euclidean.mid"),
        ("093-rock-euclidean-phase1.ogg", 1, "093-rock-euclidean-phase1.mid")):
    p = os.path.join(PROJ, "Audio", label)
    if not os.path.exists(p):
        print("skip (missing):", p)
        continue
    path = write_provenance(
        p, classification=AI_ASSISTED,
        generator="fluidsynth(FluidR3_GM.sf2) + ffmpeg libopus (SP-001)",
        parameters={"phase": phase, "source_midi": midi,
                    "engine": "FluidSynth SoundFont -> peak norm -1 dBFS -> "
                              "ffmpeg libopus 48k",
                    "bpm": 128, "key": "E aeolian",
                    "method": "012 Euclidean Groove Locking"},
        notes="Rock / method-012 Euclidean render.")
    print("wrote", path)
