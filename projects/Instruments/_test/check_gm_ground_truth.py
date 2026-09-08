# -*- coding: utf-8 -*-
"""Ground truth: pipeline GM_PROGRAMS labels + TimGM6mb.sf2 preset names."""
import struct
import sys

sys.path.insert(0, "/opt/data/repos/musicom")

from sound.render.pipeline import RenderPipeline  # noqa: E402

# Extract GM_PROGRAMS from the actual module source (it's a local var in render_stems)
import inspect
import re

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"GM_PROGRAMS list length: {len(labels)}")
for idx in [40, 41, 42, 43, 56, 57, 58, 59, 60, 61, 73, 74, 75]:
    print(f"  GM_PROGRAMS[{idx}] = {labels[idx]!r}")

# Now parse TimGM6mb.sf2 preset headers (phdr)
sf2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
data = open(sf2, "rb").read()

def find_chunk(data, ck_id, start=0):
    while True:
        pos = data.find(ck_id, start)
        if pos < 0:
            return None
        size = struct.unpack("<I", data[pos+4:pos+8])[0]
        return pos, size

# Find LIST pdta
pos = data.find(b"pdta")
pdta_off = pos - 8  # 'LIST' + size before 'pdta'
pdta_size = struct.unpack("<I", data[pdta_off+4:pdta_off+8])[0]
print(f"\npdta at {pdta_off}, size {pdta_size}")

# phdr chunk inside pdta
phdr_pos = data.find(b"phdr", pdta_off, pdta_off + pdta_size)
phdr_size = struct.unpack("<I", data[phdr_pos+4:phdr_pos+8])[0]
print(f"phdr at {phdr_pos}, size {phdr_size}, entries={(phdr_size)//38}")

presets = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off+20:off+24])
    presets[(bank, preset_num)] = name

for bank, num in [(0, 56), (0, 57), (0, 58), (0, 59), (0, 60), (0, 40), (0, 41), (0, 42), (0, 73), (0, 74), (0, 75), (0, 1), (0, 25)]:
    print(f"  bank={bank} preset={num} -> {presets.get((bank, num), 'MISSING')!r}")
