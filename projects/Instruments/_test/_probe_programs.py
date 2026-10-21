import sys, os
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from instrument_registry import ALL_INSTRUMENTS
rows = sorted((i.midi_program, i.gm_name, i.family) for i in ALL_INSTRUMENTS.values())
used = {}
for p, n, f in rows:
    used.setdefault(p, []).append(n)
print("unique programs:", len(used), "instruments:", len(ALL_INSTRUMENTS))
for p in range(0, 128):
    print(p, used.get(p, "---"))
