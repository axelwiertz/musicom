# -*- coding: utf-8 -*-
"""088 audio render: workflows.musicom_workflow.produce(midi, "SP-001")."""
import os

from workflows.musicom_workflow import produce

PROJ = "/opt/data/projects/Styles/Funk/088-funk-hawkes"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")

for name in ("088-funk-hawkes", "088-funk-hawkes-phase1"):
    mid = os.path.join(MIDI_DIR, name + ".mid")
    r = produce(mid, method="SP-001", out_dir=AUDIO_DIR)
    print(name, "->", os.path.basename(r.wav_path), os.path.getsize(r.wav_path),
          "|", os.path.basename(r.ogg_path), os.path.getsize(r.ogg_path))
