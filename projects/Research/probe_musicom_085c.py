# -*- coding: utf-8 -*-
"""Probe: soundfont discovery, produce paths, instrument program numbers."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from instrument_registry import (VIOLIN, VIOLA, CELLO, DOUBLE_BASS, PIANO,
                                 ORGAN, TRUMPET, TROMBONE, FRENCH_HORN, TUBA,
                                 FLUTE, CLARINET, OBOE, BASSOON, SAXOPHONE,
                                 ACOUSTIC_GUITAR, DRUM_KIT, MARIMBA, SITAR)
for inst in (VIOLIN, VIOLA, CELLO, DOUBLE_BASS, PIANO, ORGAN, TRUMPET,
             TROMBONE, FRENCH_HORN, TUBA, FLUTE, CLARINET, OBOE, BASSOON,
             SAXOPHONE, ACOUSTIC_GUITAR, DRUM_KIT, MARIMBA, SITAR):
    print(f"{inst.name:16s} prog={inst.midi_program:3d} range={inst.range_min}-{inst.range_max} sweet={inst.sweet_spot}")
print("---")
import sound.render.fluidsynth as fs
print("fluidsynth module:", [n for n in dir(fs) if not n.startswith("_")])
try:
    print("sf:", fs.discover_soundfont())
except Exception as e:
    print("sf err:", e)
print("---")
from workflows.musicom_workflow import _produce_fluidsynth
import inspect
print(inspect.getsource(_produce_fluidsynth))
