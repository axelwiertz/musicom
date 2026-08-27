#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Random selection of MIDI composition + SP method for production job."""
import random
from pathlib import Path

random.seed()

# Find all MIDI files (exclude phase1 drafts; keep canonical/final versions)
midi_files = [str(p) for p in Path('/opt/data/projects/Styles').rglob('*.mid')
              if 'phase1' not in p.name]
assert midi_files, "no midi files found"
selected = random.choice(midi_files)
print(f'SELECTED_MIDI={selected}')

# SP methods SP-001 .. SP-052
sp_methods = [f'SP-{i:03d}' for i in range(1, 53)]
selected_method = random.choice(sp_methods)
print(f'SELECTED_METHOD={selected_method}')

# write selection to a file for later steps
Path('/opt/data/projects/Styles/Production/.selection.txt').write_text(
    f'{selected}\n{selected_method}\n')
