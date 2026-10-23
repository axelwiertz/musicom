# -*- coding: utf-8 -*-
"""Nightly probe: pipeline GM_PROGRAMS + registry coverage + candidates."""
import inspect
import re
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("GM_PROGRAMS count:", len(labels))

from instrument_registry import ALL_INSTRUMENTS, by_program

registered = {i.midi_program for i in ALL_INSTRUMENTS.values()}
print("registered programs:", sorted(registered))

# GM melodic programs 0-127 minus percussion channel programs we skip
skip = {0, 120, 121, 122, 123, 124, 125, 126, 127}  # piano/effects/noise
missing = []
for pgm in range(128):
    if pgm in registered or pgm in skip:
        continue
    missing.append((pgm, labels[pgm] if pgm < len(labels) else "?"))
print("\nMissing GM programs (with pipeline label):")
for pgm, lab in missing:
    print(f"  {pgm:3d} -> {lab!r}")
