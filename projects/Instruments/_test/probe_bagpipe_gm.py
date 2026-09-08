# -*- coding: utf-8 -*-
"""Ground truth for Bagpipe (GM109) candidate: pipeline label, SF2 names,
MidiInstrument enum exposure, stem-label quirk check."""
import inspect
import re
import struct
import sys

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

from sound.render.pipeline import RenderPipeline  # noqa: E402

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"GM_PROGRAMS list length: {len(labels)}")
for i in [100, 109, 110, 111, 112, 113, 114, 115, 25, 33]:
    print(f"  GM_PROGRAMS[{i}] = {labels[i]!r}")

from structures.instrument import MidiInstrument  # noqa: E402
exposed = {k: v for k, v in vars(MidiInstrument).items() if isinstance(v, int) and not k.startswith("_")}
print("\nMidiInstrument exposes (int attrs):", exposed)
print("  BAGPIPE in enum?", hasattr(MidiInstrument, "BAGPIPE"))

# SF2 preset names from resolved soundfont
from sound.render.fluidsynth import discover_soundfont  # noqa: E402
sf2 = discover_soundfont()
print("\nSF2:", sf2)
data = open(sf2, "rb").read()
pos = data.find(b"phdr")
size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
names = {}
for i in range(size // 38):
    off = pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, pnum)] = name
for p in [109, 110, 111, 112]:
    print(f"  SF2 bank0/pgm{p:3d} -> {names.get((0, p), 'MISSING')!r}")
