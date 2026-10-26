# -*- coding: utf-8 -*-
"""True track-end audit (note-off inclusive) + terminal landmark check."""
import mido
from pathlib import Path

SRC = Path("/opt/data/repos/musicom/projects/Styles/Balkan/"
           "252-balkan-spectral-extended/MIDI/252-balkan-spectral-extended-perfect.mid")
mf = mido.MidiFile(str(SRC))
TPB = mf.ticks_per_beat

for ti, tr in enumerate(mf.tracks):
    t = 0
    max_any = 0       # any event (incl note_off)
    max_noteon = 0
    last_noteoff = 0
    n_on = 0
    n_off = 0
    progs = [m.program for m in tr if m.type == "program_change"]
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            n_on += 1
            max_noteon = max(max_noteon, t)
        if m.type in ("note_off",):
            n_off += 1
            last_noteoff = max(last_noteoff, t)
        elif m.type == "note_on" and m.velocity == 0:
            n_off += 1
            last_noteoff = max(last_noteoff, t)
        max_any = max(max_any, t)
    print("track %d progs=%s note_on=%d note_off=%d last_noteoff=%d max_any=%d"
          % (ti, progs, n_on, n_off, last_noteoff, max_any))

# print last few raw events of each track to see terminal landmark
print("\n--- tail of each track ---")
for ti, tr in enumerate(mf.tracks):
    t = 0
    evs = []
    for m in tr:
        t += m.time
        evs.append((t, m.type, getattr(m, "note", None), getattr(m, "velocity", None)))
    print("track", ti, "->", evs[-6:])
