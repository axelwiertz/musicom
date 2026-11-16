# -*- coding: utf-8 -*-
"""List covered + missing GM programs in the registry."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import instrument_registry as R

progs = sorted(set(i.midi_program for i in R.ALL_INSTRUMENTS.values()))
print("N instruments:", len(R.ALL_INSTRUMENTS))
print("Programs covered:", progs)
missing = [p for p in range(0, 128) if p not in progs]
print("Missing GM programs:", missing)
