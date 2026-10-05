"""Final verification of Soprano Saxophone registration."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import ALL_INSTRUMENTS, SOPRANO_SAX, by_name, by_program

s = SOPRANO_SAX
print(f"Name: {s.name}")
print(f"Family: {s.family}")
print(f"Program: {s.midi_program}")
print(f"Range: {s.range_min}-{s.range_max}")
print(f"Sweet spot: {s.sweet_spot}")
print(f"Synth: {s.synthesis}")
print(f"Reverb: {s.reverb_tail}")
print(f"Stem label: {s.stem_label}")
print(f"Zones: {s.zones}")
print(f"Arts: {list(s.articulations.keys()) if s.articulations else None}")

print()
print(f"by_name('soprano sax'): {by_name('soprano sax').name}")
print(f"by_program(64): {by_program(64).name}")
print(f"in_range(60): {s.in_range(60)}")
print(f"in_sweet_spot(72): {s.in_sweet_spot(72)}")

print()
print("SATB sax quartet status:")
for sax_key in ["soprano_sax", "saxophone", "tenor_sax", "baritone_sax"]:
    i = ALL_INSTRUMENTS[sax_key]
    print(f"  {sax_key:15s} -> {i.name:25s} GM{i.midi_program}")