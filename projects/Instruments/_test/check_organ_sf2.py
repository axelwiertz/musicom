# -*- coding: utf-8 -*-
"""Check organ SF2 presets + pipeline labels for organ candidates."""
import inspect
import re
import struct
import sys

sys.path.insert(0, "/opt/data/repos/musicom")

from sound.render.pipeline import RenderPipeline  # noqa: E402

# Pipeline GM_PROGRAMS (0-indexed)
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"GM_PROGRAMS list length: {len(labels)}")
for idx in [16, 17, 18, 19, 20, 21, 88, 89, 90]:
    print(f"  GM_PROGRAMS[{idx}] = {labels[idx]!r}")

# TimGM6mb.sf2 phdr preset names
sf2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
data = open(sf2, "rb").read()
pos = data.find(b"pdta")
pdta_off = pos - 8
pdta_size = struct.unpack("<I", data[pdta_off + 4:pdta_off + 8])[0]
phdr_pos = data.find(b"phdr", pdta_off, pdta_off + pdta_size)
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
presets = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    presets[(bank, preset_num)] = name

print("\nTimGM6mb.sf2 presets (bank 0):")
for num in [16, 17, 18, 19, 20, 21, 88, 89, 90]:
    print(f"  preset={num} -> {presets.get((0, num), 'MISSING')!r}")

# Check FluidR3_GM.sf2 too if present
import glob
for path in glob.glob("/opt/data/**/FluidR3*.sf2", recursive=True) + \
           glob.glob("/opt/data/soundfonts/*.sf2"):
    print(f"\nSF2 found: {path} ({os.path.getsize(path) if (os := __import__('os')) else '?'} bytes)")
