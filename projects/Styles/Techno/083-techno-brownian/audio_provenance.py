# -*- coding: utf-8 -*-
"""Audio provenance sidecars for 083 renders (SP-001 FluidSynth)."""
import os

from workflows.provenance import write_provenance, AI_GENERATED

PROJ = "/opt/data/projects/Styles/Techno/083-techno-brownian"
SF = "TimGM6mb.sf2 (FluidR3-compatible GM via pretty_midi, FluidSynth CLI)"

for name, mid_src, note in (
    ("083-techno-brownian", "MIDI/083-techno-brownian.mid",
     "Phase-2 full arrangement rendered via FluidSynth CLI SP-001, -g 1.2, peak-normalized, Opus 48k"),
    ("083-techno-brownian-phase1", "MIDI/083-techno-brownian-phase1.mid",
     "Phase-1 raw Brownian draft rendered via FluidSynth CLI SP-001, -g 1.2"),
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
