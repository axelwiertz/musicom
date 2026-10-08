import sys
sys.path.insert(0, '/opt/data/projects/Instruments')
from instrument_registry import ALL_INSTRUMENTS
used = sorted(set(i.midi_program for i in ALL_INSTRUMENTS.values()))
print(f'Used programs ({len(used)}): {used}')
print(f'GM33 in use? {33 in used}')
print(f'GM32 in use? {32 in used}')
print(f'GM74 in use? {74 in used}')
print(f'GM73 in use? {73 in used}')
print(f'GM76 in use? {76 in used}')
print(f'GM89 in use? {89 in used}')