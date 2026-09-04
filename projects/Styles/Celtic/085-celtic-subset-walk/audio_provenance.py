#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Write provenance sidecars for the 085 audio artifacts."""
import os

from workflows.provenance import write_provenance, AI_GENERATED

PROJ = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk"
AUDIO_DIR = os.path.join(PROJ, "Audio")

pairs = [
    ("085-celtic-subset-walk.wav", "SP-001 FluidSynth SoundFont render of phase-2 MIDI (full celtic texture)"),
    ("085-celtic-subset-walk.ogg", "Opus 48k VoIP transcode of the phase-2 WAV"),
    ("085-celtic-subset-walk-phase1.wav", "SP-001 FluidSynth render of phase-1 raw subset-walk draft"),
    ("085-celtic-subset-walk-phase1.ogg", "Opus 48k VoIP transcode of the phase-1 WAV"),
]
for fname, note in pairs:
    p = os.path.join(AUDIO_DIR, fname)
    if os.path.exists(p):
        write_provenance(p, AI_GENERATED,
                         "SP-001 (workflows.musicom_workflow.produce) "
                         "FluidSynth + FluidR3_GM.sf2",
                         parameters={"bpm": 96, "key": "Ab major",
                                     "method": "ABS-002 Subset Walker",
                                     "seed": 20260903},
                         notes=note)
        print("provenance", fname)
