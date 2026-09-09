# -*- coding: utf-8 -*-
"""Render phase-1 raw draft too (SP-001), for listening comparison."""
import os

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/091-baroque-genetic-allemande"
P1 = os.path.join(PROJ, "MIDI", "091-baroque-genetic-allemande-phase1.mid")

from workflows.musicom_workflow import produce  # noqa: E402

r = produce(P1, method="SP-001", out_dir=os.path.join(PROJ, "Audio"))
print("WAV:", r.wav_path, os.path.getsize(r.wav_path) if os.path.exists(r.wav_path) else "MISSING")
print("OGG:", r.ogg_path, os.path.getsize(r.ogg_path) if os.path.exists(r.ogg_path) else "MISSING")