# -*- coding: utf-8 -*-
"""Probe FluidR3 SF2 preset names for guitar programs."""
import struct
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print("SF2:", sf2)
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
for p in [24, 25, 26, 27, 28, 29, 30]:
    print(f"  preset {p} (bank 0): {preset_names.get((0, p), 'MISSING')!r}")
