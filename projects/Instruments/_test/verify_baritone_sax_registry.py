"""Verify baritone_sax registration in the instrument registry."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import (
    BARITONE_SAX, ALL_INSTRUMENTS, by_name, by_program, registry_table
)

print(registry_table())
print()
print("Verification:")
print("  BARITONE_SAX.midi_program =", BARITONE_SAX.midi_program, "(should be 67)")
print("  BARITONE_SAX.name =", BARITONE_SAX.name)
print("  BARITONE_SAX.family =", BARITONE_SAX.family)
print("  BARITONE_SAX.range_min =", BARITONE_SAX.range_min)
print("  BARITONE_SAX.range_max =", BARITONE_SAX.range_max)
print("  BARITONE_SAX.sweet_spot =", BARITONE_SAX.sweet_spot)
print("  BARITONE_SAX.synthesis =", BARITONE_SAX.synthesis)
print("  BARITONE_SAX.reverb_tail =", BARITONE_SAX.reverb_tail)
print("  by_name('baritone sax') =", by_name("baritone sax"))
print("  by_program(67) =", by_program(67))
print("  BARITONE_SAX.in_sweet_spot(60) =", BARITONE_SAX.in_sweet_spot(60))
print("  BARITONE_SAX.in_sweet_spot(30) =", BARITONE_SAX.in_sweet_spot(30))
print("  BARITONE_SAX.in_range(42) =", BARITONE_SAX.in_range(42))
print("  BARITONE_SAX.in_range(82) =", BARITONE_SAX.in_range(82))
print()
print("All registry checks passed.")