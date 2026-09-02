# -*- coding: utf-8 -*-
"""Audio provenance sidecars for 084 renders (SP-001 FluidSynth)."""
import os

from workflows.provenance import write_provenance, AI_GENERATED

PROJ = "/opt/data/projects/Styles/Soul/084-soul-voiceleading-graph"
SF = "FluidR3_GM.sf2 (via discover_soundfont, FluidSynth CLI SP-001)"

for name, mid_src, note in (
    ("084-soul-voiceleading-graph", "MIDI/084-soul-voiceleading-graph.mid",
     "Phase-2 full soul arrangement rendered via FluidSynth CLI SP-001, -g 1.2, Opus 48k voip"),
    ("084-soul-voiceleading-graph-phase1", "MIDI/084-soul-voiceleading-graph-phase1.mid",
     "Phase-1 raw tonal-graph walk draft rendered via FluidSynth CLI SP-001, -g 1.2"),
):
    wav = os.path.join(PROJ, "Audio", name + ".wav")
    ogg = os.path.join(PROJ, "Audio", name + ".ogg")
    for art in (wav, ogg):
        write_provenance(
            art, AI_GENERATED, "FluidSynth CLI render (SP-001 Multi-timbral SoundFont)",
            sources=[os.path.join(PROJ, mid_src)],
            parameters={"soundfont": SF, "gain": 1.2, "opus_bitrate": 48},
            notes=note)
    print("provenance:", name)
