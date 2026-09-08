"""Smoke check: instrument_registry loads Saxophone + all instruments."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import (
    ALL_INSTRUMENTS, SAXOPHONE, by_name, by_program, registry_table,
)
print(f"Total instruments: {len(ALL_INSTRUMENTS)}")
print(f"SAXOPHONE: {SAXOPHONE}")
print(f"SAXOPHONE.midi_program={SAXOPHONE.midi_program} stem={SAXOPHONE.stem_label!r} sweet={SAXOPHONE.sweet_spot}")
assert SAXOPHONE.midi_program == 65
assert SAXOPHONE.stem_label == "Alto_Sax"
assert by_name("saxophone") is SAXOPHONE
assert by_program(65) is SAXOPHONE
assert len(ALL_INSTRUMENTS) == 16, f"expected 16, got {len(ALL_INSTRUMENTS)}"
print("\n--- registry table ---")
print(registry_table())
print("\nALL REGISTRY CHECKS PASSED")
