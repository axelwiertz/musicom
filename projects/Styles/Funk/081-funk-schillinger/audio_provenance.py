# -*- coding: utf-8 -*-
"""081 audio provenance sidecars."""
import os
from workflows.provenance import write_provenance, AI_GENERATED

PROJ = "/opt/data/projects/Styles/Funk/081-funk-schillinger"
for name, phase, note in (
        ("081-funk-schillinger.wav", "2", "FluidSynth CLI render (TimGM6mb.sf2, -g 1.2) of rules-processed MIDI"),
        ("081-funk-schillinger.ogg", "2", "Opus (voip 48k) of full mix"),
        ("081-funk-schillinger-phase1.wav", "1", "FluidSynth CLI render (TimGM6mb.sf2, -g 1.2) of raw Schillinger draft"),
        ("081-funk-schillinger-phase1.ogg", "1", "Opus (voip 48k) of raw draft"),
):
    p = os.path.join(PROJ, "Audio", name)
    write_provenance(p, AI_GENERATED, "FluidSynth CLI (SP-001) render",
                     parameters={"bpm": 100, "key": "Bb major", "phase": phase,
                                 "soundfont": "TimGM6mb.sf2", "gain": 1.2},
                     notes=note)
    print("provenance:", name)
print("done")
