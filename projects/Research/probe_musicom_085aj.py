# -*- coding: utf-8 -*-
"""Probe: instrument module field names (MIDI_PROGRAM, GM_NAME etc)."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
import importlib
m = importlib.import_module("Woodwind.saxophone.saxophone")
names = [n for n in dir(m) if n.isupper()]
print(names)
