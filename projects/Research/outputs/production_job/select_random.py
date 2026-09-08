# -*- coding: utf-8 -*-
import random
from pathlib import Path

random.seed()

# Find all MIDI files
midi_files = [f for f in Path('/opt/data/projects/Styles').rglob('*.mid')
              if 'VoiceAudio' not in str(f)]
selected = random.choice(midi_files)
print(f'SELECTED_MIDI={selected}')

# Random SP method from full range SP-001..SP-048 (methods_db has up to SP-048)
sp_methods = [f'SP-{i:03d}' for i in range(1, 49)]
selected_method = random.choice(sp_methods)
print(f'SELECTED_METHOD={selected_method}')
