# -*- coding: utf-8 -*-
"""Audio provenance sidecars for 095 OGGs (ODA rule: every artifact -> sidecar)."""
import os
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli"
for fn, phase in (("095-klezmer-tintinnabuli.ogg", "2"),
                  ("095-klezmer-tintinnabuli-phase1.ogg", "1")):
    p = os.path.join(PROJ, "Audio", fn)
    assert os.path.getsize(p) > 40, p
    write_provenance(p, classification=AI_ASSISTED,
                     generator="SP-001 FluidSynth (FluidR3_GM) + ffmpeg Opus",
                     parameters={"phase": phase, "project": "095-klezmer-tintinnabuli"},
                     notes="OGG render of phase-%s MIDI." % phase)
    print("provenance for", fn)
