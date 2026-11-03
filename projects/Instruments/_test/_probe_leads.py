# -*- coding: utf-8 -*-
"""Probe FluidR3 preset names + enum + engine list for lead candidates."""
import sys, struct
sys.path.insert(0, "/opt/data/projects/Instruments")
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print("SF2:", sf2)
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, pn)] = nm

for p in [55, 82, 83, 84, 85, 86, 87]:
    print(f"GM{p:3d}: FluidR3 preset = {names.get((0, p), 'MISSING')!r}")

import inspect
from structures import instrument as inst_mod
print("\nMidiInstrument enum:")
print(inspect.getsource(inst_mod))
