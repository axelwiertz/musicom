#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selection of MIDI composition + SP method for production job (2026-09-02).
Registry source of truth: workflows.musicom_workflow.SP_METHODS.
Excludes: Production/ outputs, phase1 drafts, methods used in last 7 days.
"""
import random
from pathlib import Path
from datetime import datetime, timedelta
from workflows.musicom_workflow import SP_METHODS

random.seed()

STYLES = Path('/opt/data/projects/Styles')
PROD = STYLES / 'Production'

# Existing compositions: MIDI files under Styles, excluding Production/ and phase1 drafts
midi_files = [str(p) for p in STYLES.rglob('*.mid')
              if 'phase1' not in p.name
              and PROD not in p.parents]
assert midi_files, "no midi files found"
selected = random.choice(midi_files)

# Methods used in last 7 days (dirs under Production named <METHOD>-*)
cutoff = datetime.now() - timedelta(days=7)
recent = set()
for d in PROD.iterdir():
    if d.is_dir():
        name = d.name
        # dir name starts with SP-XXX
        if name.startswith('SP-'):
            m = name[:6]  # e.g. SP-024
            recent.add(m)
# also .selection.txt style fallback: read last lines of reports? keep dir-based
pool = sorted(SP_METHODS.keys())
free = [m for m in pool if m not in recent]
if len(free) >= 4:
    pool = free
selected_method = random.choice(pool)
print(f'RECENT_USED={sorted(recent)}')
print(f'FREE_POOL={free}')
print(f'SELECTED_MIDI={selected}')
print(f'SELECTED_METHOD={selected_method}')

Path('/opt/data/projects/Styles/Production/.selection.txt').write_text(
    f'{selected}\n{selected_method}\n')
