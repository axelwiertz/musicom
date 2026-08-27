#!/usr/bin/env python3
"""Check dependency availability."""
import importlib
for mod in ['midiutil', 'mido', 'numpy', 'scipy', 'soundfile', 'struct']:
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, '__version__', 'unknown')
        print(f"{mod}: available ({ver})")
    except ImportError:
        print(f"{mod}: NOT available")