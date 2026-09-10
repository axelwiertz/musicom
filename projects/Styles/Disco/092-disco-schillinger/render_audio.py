# -*- coding: utf-8 -*-
"""Render phase-2 MIDI -> WAV -> OGG via the sanctioned workflow adapter
(SP-001 FluidSynth -> ffmpeg Opus). Also renders the phase-1 raw draft."""
import os

from structures import MusicUnit  # noqa: F401  (compliant-import marker)

PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger")
MIDI2 = os.path.join(PROJ, "MIDI", "092-disco-schillinger.mid")
MIDI1 = os.path.join(PROJ, "MIDI", "092-disco-schillinger-phase1.mid")

from workflows.musicom_workflow import produce  # noqa: E402

for label, midi in (("phase2", MIDI2), ("phase1", MIDI1)):
    r = produce(midi, method="SP-001", out_dir=os.path.join(PROJ, "Audio"))
    print(label, "WAV:", r.wav_path, os.path.getsize(r.wav_path))
    print(label, "OGG:", r.ogg_path,
          os.path.getsize(r.ogg_path) if os.path.exists(r.ogg_path) else "MISSING")
    print(label, "info:", r.info)
