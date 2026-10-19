#!/usr/bin/env python3
"""Print GM_PROGRAMS mapping - run from musicom root."""
import sys
import os
sys.path.insert(0, '/opt/data/repos/musicom')
os.chdir('/opt/data/repos/musicom')
from sound.render.pipeline import GM_PROGRAMS
for k in sorted(GM_PROGRAMS):
    print(f'{k:3d} -> {GM_PROGRAMS[k]}')