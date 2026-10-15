#!/usr/bin/env python3
"""Verify the registry after Brass Section addition."""
import sys
sys.path.insert(0, '/opt/data/projects/Instruments')
from instrument_registry import ALL_INSTRUMENTS, by_name, by_program

print(registry_table())
print()
print("Verification:")
print("  BRASS_SECTION.midi_program =", BRASS_SECTION.midi_program, "(should be 61)")
print("  by_name('brass section') =", by_name("brass section"))
print("  by_program(61) =", by_program(61))
print("  BRASS_SECTION.in_sweet_spot(67) =", BRASS_SECTION.in_sweet_spot(67))