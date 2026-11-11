# -*- coding: utf-8 -*-
"""Inspect the off-grid melody notes: what are their note-off ticks?"""
import mido

SRC = "/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid"
mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat

# Track 1 = flute/melody
tr = mf.tracks[1]
t = 0
pending = {}
print("track1 events around bar seams (tick 23040 and 38400):")
for m in tr:
    t += m.time
    if m.type == "note_on" and m.velocity > 0:
        pending[m.note] = (t, m.velocity)
    elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
        if m.note in pending:
            st = pending.pop(m.note)[0]
            dur = t - st
            if st in (23039, 38399) or (22900 <= st <= 23100) or (38200 <= st <= 38500):
                print(f"  on@{st} off@{t} dur={dur} note={m.note}")

# Also list all note durations for track 1 to understand clamps
print("\ntrack1 note start-tick distribution (last 3 digits / 120):")
from collections import Counter
c = Counter()
t = 0
for m in tr:
    t += m.time
    if m.type == "note_on" and m.velocity > 0:
        c[t % 1920] += 1
for r in sorted(c):
    print(f"  bar-relative {r}: {c[r]}")
