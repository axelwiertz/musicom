#!/usr/bin/env python3
"""Verify Clean Electric Guitar registration in instrument_registry."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import CLEAN_ELECTRIC, by_name, by_program

print("=== Clean Electric Guitar (GM27) ===")
print(f"  CLEAN_ELECTRIC.midi_program = {CLEAN_ELECTRIC.midi_program}  (should be 27)")
print(f"  by_name('clean electric') = {by_name('clean electric')}")
print(f"  by_program(27) = {by_program(27)}")
print(f"  CLEAN_ELECTRIC.name = {CLEAN_ELECTRIC.name!r}")
print(f"  CLEAN_ELECTRIC.gm_name = {CLEAN_ELECTRIC.gm_name!r}")
print(f"  CLEAN_ELECTRIC.stem_label = {CLEAN_ELECTRIC.stem_label!r}")
print(f"  CLEAN_ELECTRIC.family = {CLEAN_ELECTRIC.family!r}")
print(f"  CLEAN_ELECTRIC.range_min = {CLEAN_ELECTRIC.range_min}")
print(f"  CLEAN_ELECTRIC.range_max = {CLEAN_ELECTRIC.range_max}")
print(f"  CLEAN_ELECTRIC.sweet_spot = {CLEAN_ELECTRIC.sweet_spot}")
print(f"  CLEAN_ELECTRIC.synthesis = {CLEAN_ELECTRIC.synthesis!r}")
print(f"  CLEAN_ELECTRIC.reverb_tail = {CLEAN_ELECTRIC.reverb_tail}")
print(f"  CLEAN_ELECTRIC.pan = {CLEAN_ELECTRIC.pan}")
print(f"  CLEAN_ELECTRIC.in_sweet_spot(52) = {CLEAN_ELECTRIC.in_sweet_spot(52)}")
print(f"  CLEAN_ELECTRIC.in_sweet_spot(30) = {CLEAN_ELECTRIC.in_sweet_spot(30)}")
print(f"  CLEAN_ELECTRIC.in_sweet_spot(72) = {CLEAN_ELECTRIC.in_sweet_spot(72)}")
print()
print("=== ALL Guitar instruments ===")
for inst in sorted((v for v in sys.modules['instrument_registry'].ALL_INSTRUMENTS.values() if v.family == 'Guitar'), key=lambda i: i.midi_program):
    print(f"  {inst.name} (GM{inst.midi_program}): range {inst.range_min}-{inst.range_max}, synth={inst.synthesis}")