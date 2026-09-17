# -*- coding: utf-8 -*-
"""097 audio render: workflows.musicom_workflow.produce(midi, "SP-001")."""
import os

from workflows.musicom_workflow import produce

PROJ = "/opt/data/repos/musicom/projects/Styles/Jazz/097-jazz-bebop-changes"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")

for name in ("097-jazz-bebop-changes", "097-jazz-bebop-changes-phase1"):
    mid = os.path.join(MIDI_DIR, name + ".mid")
    r = produce(mid, method="SP-001", out_dir=AUDIO_DIR)
    print(name, "->", os.path.basename(r.wav_path), os.path.getsize(r.wav_path),
          "|", os.path.basename(r.ogg_path), os.path.getsize(r.ogg_path))
