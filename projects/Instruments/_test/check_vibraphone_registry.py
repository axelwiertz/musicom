# -*- coding: utf-8 -*-
"""Count check after registering vibraphone."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import ALL_INSTRUMENTS, registry_table

print("count", len(ALL_INSTRUMENTS))
print("has vibraphone", "vibraphone" in ALL_INSTRUMENTS)
print("programs dup 11:", sorted(k for k, v in ALL_INSTRUMENTS.items() if v.midi_program == 11))
print("row:", [l for l in registry_table().splitlines() if "Vibraphone" in l])
