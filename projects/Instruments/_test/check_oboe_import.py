#!/usr/bin/env python
"""Final import sanity check for oboe constants."""
import sys
sys.path.insert(0, '/opt/data/projects/Instruments')
from Woodwind.oboe.oboe import (
    MIDI_PROGRAM, GM_NAME, STEM_LABEL, RANGE_MIN, RANGE_MAX,
    SOLO_RANGE, SYNTHESIS, REVERB_TAIL, PAN,
)
assert MIDI_PROGRAM == 68, MIDI_PROGRAM
assert STEM_LABEL == 'Oboe', STEM_LABEL
print('oboe.py import OK:', MIDI_PROGRAM, GM_NAME, RANGE_MIN, RANGE_MAX,
      SOLO_RANGE, SYNTHESIS, REVERB_TAIL, PAN)
