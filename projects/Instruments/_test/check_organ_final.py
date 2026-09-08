# -*- coding: utf-8 -*-
"""Final sanity: registry loads organ, files present."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

from instrument_registry import ALL_INSTRUMENTS, ORGAN, by_name, by_program  # noqa: E402

print("total instruments:", len(ALL_INSTRUMENTS))
print("ORGAN:", ORGAN)
print("by_program(19):", by_program(19))
print("by_name('organ'):", by_name("organ"))
print("in_range(36):", ORGAN.in_range(36), "in_sweet_spot(60):", ORGAN.in_sweet_spot(60))

base = "/opt/data/projects/Instruments"
for p in [
    "Keys/organ/instrument.md",
    "Keys/organ/organ.py",
    "Keys/organ/REPORT.md",
    "_test/verify_organ.py",
    "_test/organ_test.mid",
    "_test/organ_test.wav",
    "_test/stems_organ/track00_Church_Organ.wav",
]:
    fp = os.path.join(base, p)
    print(f"{'OK ' if os.path.exists(fp) else 'MISS'} {p} ({os.path.getsize(fp)} bytes)" if os.path.exists(fp) else f"MISS {p}")
