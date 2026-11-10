# -*- coding: utf-8 -*-
"""Final sanity: registry reload + artifact sizes."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as R

sb = R.by_name("slap bass")
print("count:", len(R.ALL_INSTRUMENTS))
print("slap bass:", sb)
print("by_program(36):", R.by_program(36))
print("table row:", [l for l in R.registry_table().split("\n") if "Slap Bass" in l][0])
assert sb is R.SLAP_BASS and sb.midi_program == 36
assert R.by_name("slap bass 1") is sb
assert R.by_program(36) is sb
print("OK")

print("--- artifacts ---")
for p in [
    "Bass/slap_bass/instrument.md",
    "Bass/slap_bass/slap_bass.py",
    "Bass/slap_bass/REPORT.md",
    "_test/verify_slap_bass.py",
    "_test/slap_bass_test.mid",
    "_test/slap_bass_test.wav",
    "_test/registry_out_slap_bass.txt",
    "_test/stems_slap_bass/track00_Slap_Bass_1.wav",
    "_test/stems_slap_bass/track01_Drums.wav",
]:
    full = os.path.join("/opt/data/projects/Instruments", p)
    print(f"  {p} ({os.path.getsize(full)} bytes)" if os.path.exists(full) else f"  {p} MISSING")
