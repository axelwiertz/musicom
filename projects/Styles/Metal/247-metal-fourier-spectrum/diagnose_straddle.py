# -*- coding: utf-8 -*-
"""Diagnose the 18 readback out-of-chord notes: are they bar-boundary straddles?"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
from compose import CHORDS, POOL_BY_SECTION, section_of_bar, TOTAL_BARS, BAR, MIDI_PATH

import mido

mid = mido.MidiFile(MIDI_PATH)
straddles = []
for tr in mid.tracks:
    ch = None
    for m in tr:
        if m.type == "program_change":
            ch = m.channel
    if ch == 9:
        continue
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0 and m.note > 0:
            pc = m.note % 12
            bar = min(TOTAL_BARS - 1, t // BAR)
            cpc = set(CHORDS[bar][3])
            if pc not in cpc:
                # distance from nearest bar boundary
                into_bar = t % BAR
                straddles.append({"ch": ch, "note": m.note, "tick": t,
                                  "bar": bar, "into_bar": into_bar})

print(f"total out-of-chord (pitched, non-drums): {len(straddles)}")
near_start = [s for s in straddles if s["into_bar"] < 30]
print(f"  within 30 ticks after a bar line (backward straddle): {len(near_start)}")
print("  sample:", straddles[:5])
