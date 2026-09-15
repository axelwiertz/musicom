# -*- coding: utf-8 -*-
"""Audio provenance sidecars for 096 OGGs (ODA rule: every artifact -> sidecar)."""
import os
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul"
for fn, phase in (("096-trap-skeleton-seoul.ogg", "2"),
                  ("096-trap-skeleton-seoul-phase1.ogg", "1")):
    p = os.path.join(PROJ, "Audio", fn)
    assert os.path.getsize(p) > 40, p
    write_provenance(p, classification=AI_ASSISTED,
                     generator="SP-001 FluidSynth (FluidR3_GM) + ffmpeg Opus",
                     parameters={"phase": phase, "project": "096-trap-skeleton-seoul"},
                     notes="OGG render of phase-%s MIDI." % phase)
    print("provenance for", fn)
