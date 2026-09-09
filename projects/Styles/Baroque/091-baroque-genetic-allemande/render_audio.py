# -*- coding: utf-8 -*-
"""Render phase-2 MIDI -> WAV -> OGG via the sanctioned workflow adapter
(SP-001 FluidSynth). Falls back to direct fluidsynth + ffmpeg."""
import os

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/091-baroque-genetic-allemande"
MIDI = os.path.join(PROJ, "MIDI", "091-baroque-genetic-allemande.mid")

from workflows.musicom_workflow import produce  # noqa: E402

r = produce(MIDI, method="SP-001", out_dir=os.path.join(PROJ, "Audio"))
print("WAV:", r.wav_path, os.path.getsize(r.wav_path) if os.path.exists(r.wav_path) else "MISSING")
print("OGG:", r.ogg_path, os.path.getsize(r.ogg_path) if os.path.exists(r.ogg_path) else "MISSING")
print("info:", r.info)