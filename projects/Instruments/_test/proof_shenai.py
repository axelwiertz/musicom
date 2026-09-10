# -*- coding: utf-8 -*-
"""Registration proof — Shenai via registry (standalone)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instrument_registry import by_name, by_program, SHENAI, ALL_INSTRUMENTS, registry_table

print("by_name('shenai')   =", by_name("shenai"))
print("by_program(111)     =", by_program(111))
print("SHENAI constant     =", SHENAI)
print("ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
t = registry_table()
assert "| World | Shenai | 111 |" in t
print("registry_table() includes Shenai row: OK")
print("SHENAI.midi_program =", SHENAI.midi_program, "| stem_label =", SHENAI.stem_label)
print("REGISTRATION PROOF PASSED")
