# -*- coding: utf-8 -*-
"""Env probe: numpy/mido/scipy availability + soundfont resolution."""
import sys
from sound.render.fluidsynth import discover_soundfont
print("sf2", discover_soundfont())

try:
    import numpy
    print("numpy", numpy.__version__)
except Exception as e:
    print("numpy ERR", e)

try:
    import mido
    print("mido", mido.__version__)
except Exception as e:
    print("mido ERR", e)

try:
    import scipy
    print("scipy", scipy.__version__)
except Exception as e:
    print("scipy ERR", e)

from sound.render.fluidsynth import discover_soundfont
print("sf2", discover_soundfont())
