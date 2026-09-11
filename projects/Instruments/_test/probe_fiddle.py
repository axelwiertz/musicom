# -*- coding: utf-8 -*-
"""Probe FluidR3 preset names for Fiddle (GM110) + pipeline label."""
import struct
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print("SF2:", sf2)
data = open(sf2, "rb").read()
pos = data.find(b"phdr")
size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
names = {}
for i in range(size // 38):
    off = pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, pnum)] = name
print("Total presets:", len(names))
for p in [40, 41, 109, 110, 111]:
    print(f"  bank0/pgm{p:3d} -> {names.get((0, p), 'MISSING')!r}")

# pipeline label
from sound.render.pipeline import RenderPipeline
import inspect
import re
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("GM_PROGRAMS len:", len(labels))
for idx in [108, 109, 110, 111, 112]:
    print(f"  [{idx}] = {labels[idx]!r}")