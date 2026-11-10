# -*- coding: utf-8 -*-
"""Probe GM program 36 (Slap Bass 1): pipeline stem label + FluidR3 preset name."""
import inspect
import re
import struct
import sys

sys.path.insert(0, "/opt/data/repos/musicom")

from sound.render.pipeline import RenderPipeline
from sound.render.fluidsynth import discover_soundfont

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("len(GM_PROGRAMS) =", len(labels))
for idx in [31, 32, 33, 34, 35, 36, 37, 38, 39, 49, 63, 112, 115, 118]:
    print(f"  [{idx}] = {labels[idx]!r}")

sf2 = discover_soundfont()
print("SF2:", sf2)
data = open(sf2, "rb").read()
phdr = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr + 4:phdr + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, pnum)] = nm
for idx in [31, 32, 33, 34, 35, 36, 37, 38, 39, 49, 63, 112, 115, 118]:
    print(f"  SF2 preset {idx} = {preset_names.get((0, idx), 'MISSING')!r}")

# MidiInstrument enum
from structures import MidiInstrument
print("\nMidiInstrument members:")
for nm in dir(MidiInstrument):
    if nm.isupper():
        print(f"  {nm} = {getattr(MidiInstrument, nm)}")
