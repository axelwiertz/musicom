#!/usr/bin/env python3
"""Print the GM_PROGRAMS mapping from pipeline.py."""
import sys
sys.path.insert(0, '/opt/data/repos/musicom')
import importlib.util
spec = importlib.util.spec_from_file_location('pipeline', '/opt/data/repos/musicom/sound/render/pipeline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
for k in sorted(mod.GM_PROGRAMS):
    print(f'{k:3d} -> {mod.GM_PROGRAMS[k]}')