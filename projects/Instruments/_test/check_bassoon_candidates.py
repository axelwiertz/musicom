# -*- coding: utf-8 -*-
"""Ground-truth check: SF2 preset names + pipeline stem labels for candidates."""
import struct
import inspect
import re
import sys

sf2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name

# Pipeline GM_PROGRAMS (0-indexed)
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]

candidates = [6, 11, 12, 19, 47, 65, 66, 68, 70, 88]
print(f"{'pgm':>4} {'pipeline label':<32} {'SF2 preset':<24} match")
for p in candidates:
    sf2_name = preset_names.get((0, p), "MISSING")
    pipe = labels[p]
    match = "OK" if sf2_name.lower().replace(" ", "") == pipe.lower().replace(" ", "").replace("(", "").replace(")", "") else "DIFF"
    print(f"{p:>4} {pipe:<32} {sf2_name:<24} {match}")
