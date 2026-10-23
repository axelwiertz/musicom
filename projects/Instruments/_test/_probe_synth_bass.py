# -*- coding: utf-8 -*-
"""Probe FluidR3 preset 38 + registry health."""
import struct
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print("SoundFont:", sf2)

data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
for pgm in [38, 39, 35, 32, 34, 36, 37]:
    print(f"  preset {pgm:3d} -> {preset_names.get((0, pgm), 'MISSING')!r}")

# registry health
from instrument_registry import ALL_INSTRUMENTS, registry_table, by_name, by_program
print("\nRegistry instruments:", len(ALL_INSTRUMENTS))
missing = [k for k in ALL_INSTRUMENTS if ALL_INSTRUMENTS[k].midi_program is None]
print("Instruments with None program:", missing)
print("\nRegistry table (first 8 rows):")
tbl = registry_table().splitlines()
print("\n".join(tbl[:8]))
print("...")
print("\nRegistry loads OK")
