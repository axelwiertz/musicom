# -*- coding: utf-8 -*-
"""List registered instruments by program + identify missing clusters."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as R

progs = {}
for i in R.ALL_INSTRUMENTS.values():
    progs.setdefault(i.midi_program, []).append(i.name)

for p in sorted(progs):
    print(f"{p:3d}  {progs[p][0]}")
print("\nmissing:", [p for p in range(128) if p not in progs])
