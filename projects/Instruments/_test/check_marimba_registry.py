# -*- coding: utf-8 -*-
"""Final registry sanity check for Marimba."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import by_name, by_program, MARIMBA

print("by_name('marimba'):", by_name('marimba'))
print("by_program(12):", by_program(12))
print("MARIMBA:", MARIMBA)
print("MARIMBA.in_sweet_spot(72):", MARIMBA.in_sweet_spot(72))
assert by_name("marimba").midi_program == 12
assert by_program(12).name == "Marimba"
assert MARIMBA.gm_name == "Marimba"
print("REGISTRY OK")
