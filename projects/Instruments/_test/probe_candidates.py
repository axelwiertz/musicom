# -*- coding: utf-8 -*-
"""Probe FluidR3 preset names for candidate instruments (phdr chunk)."""
import struct
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
for p in [6, 7, 15, 25, 26, 27, 28, 29, 49, 80, 81, 88, 89, 90, 109, 110, 111, 112, 113, 114, 115]:
    print(f"  bank0/pgm{p:3d} -> {names.get((0, p), 'MISSING')!r}")
