# -*- coding: utf-8 -*-
"""Probe FluidR3 preset names around GM6 + pipeline labels."""
import struct
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print("SF2:", sf2)
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, preset_num)] = name
for p in range(0, 16):
    print(p, repr(names.get((0, p), "MISSING")))
print("---")
for p in [6, 11, 12, 13, 14]:
    print(p, repr(names.get((0, p), "MISSING")))
