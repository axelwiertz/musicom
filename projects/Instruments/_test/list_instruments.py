#!/usr/bin/env python3
"""List all registered instruments sorted by program number."""
import sys
sys.path.insert(0, '/opt/data/projects/Instruments')
from instrument_registry import ALL_INSTRUMENTS

for name in sorted(ALL_INSTRUMENTS, key=lambda n: ALL_INSTRUMENTS[n].midi_program or 999):
    inst = ALL_INSTRUMENTS[name]
    print(f'{inst.midi_program or 0:3d}  {inst.name:30s}  {inst.family}')