# -*- coding: utf-8 -*-
"""Probe FluidR3 preset names for candidate instruments."""
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

candidates = [
    (8, "Celesta"),
    (10, "Music Box"),
    (14, "Tubular Bells"),
    (7, "Clavi"),
    (73, "Flute"),
    (75, "Pan Flute"),
    (76, "Blown Bottle"),
    (77, "Shakuhachi"),
    (78, "Whistle"),
    (79, "Ocarina"),
    (21, "Accordion"),
    (22, "Harmonica"),
]

for p, label in candidates:
    print(f"pgm {p:3d} ({label:15s}) -> SF2 preset: {names.get((0, p), 'MISSING')!r}")
