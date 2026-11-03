# -*- coding: utf-8 -*-
"""Final sanity: registry loads clean, count, 82 no longer missing."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as R

progs = set(i.midi_program for i in R.ALL_INSTRUMENTS.values())
missing = [p for p in range(128) if p not in progs]
print("registry loads OK, count =", len(R.ALL_INSTRUMENTS))
print("CALIOPE =", R.CALIOPE)
print("82 still missing:", 82 in missing)
print("missing count now:", len(missing))
