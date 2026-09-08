# -*- coding: utf-8 -*-
"""Render stems for trombone test MIDI via RenderPipeline."""
import os
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from sound.render.pipeline import RenderPipeline

sf2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
p = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                   soundfont_path=sf2, gain=1.2)
stems = p.render_stems(
    "/opt/data/projects/Instruments/_test/trombone_test.mid",
    "/opt/data/projects/Instruments/_test/stems_trombone",
)
for name, path in stems.items():
    print(f"{name} -> {path} ({os.path.getsize(path)} bytes)")
