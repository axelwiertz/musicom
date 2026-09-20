# -*- coding: utf-8 -*-
"""Render audio for 098-funk-som using SP-001 (FluidSynth)."""
import os
from workflows.musicom_workflow import produce

PROJ = "/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")

for name in ("098-funk-som", "098-funk-som-phase1"):
    mid = os.path.join(MIDI_DIR, name + ".mid")
    r = produce(mid, method="SP-001", out_dir=AUDIO_DIR)
    print(name, "->", os.path.basename(r.wav_path), os.path.getsize(r.wav_path),
          "|", os.path.basename(r.ogg_path), os.path.getsize(r.ogg_path))
