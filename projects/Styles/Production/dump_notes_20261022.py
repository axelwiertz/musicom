# -*- coding: utf-8 -*-
"""Detailed note dump of source MIDI (2026-10-22)."""
import mido
from collections import Counter

SRC = "/opt/data/repos/musicom/projects/Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-v5.mid"
mf = mido.MidiFile(SRC)
tr = mf.tracks[0]

t = 0
events = []
pending = {}
for m in tr:
    t += m.time
    if m.type == "note_on" and m.velocity > 0:
        pending.setdefault(m.note, []).append((t, m.velocity))
    elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
        if m.note in pending and pending[m.note]:
            s, vel = pending[m.note].pop(0)
            events.append((s, t, m.note, vel))

events.sort()
print("total notes:", len(events))
print("first 40 (start, end, note, vel):")
for e in events[:40]:
    print(f"  {e[0]:6d} {e[1]:6d}  n={e[2]:3d} v={e[3]}")

# durations histogram
durs = Counter(e[1] - e[0] for e in events)
print("\nduration histogram (ticks:count):")
for d in sorted(durs):
    print(f"  {d}: {durs[d]}")

# start tick deltas
starts = [e[0] for e in events]
deltas = Counter(starts[i+1] - starts[i] for i in range(len(starts)-1))
print("\ninter-onset deltas (ticks:count):")
for d in sorted(deltas):
    print(f"  {d}: {deltas[d]}")

# grid check at 120 (16th)
off_grid = [s for s in starts if s % 120 != 0]
print("\noff-16th-grid onsets:", len(off_grid), off_grid[:10])
# grid check at 240 (8th)
off_grid8 = [s for s in starts if s % 240 != 0]
print("off-8th-grid onsets:", len(off_grid8))
# grid check at 480 (quarter)
off_grid4 = [s for s in starts if s % 480 != 0]
print("off-quarter-grid onsets:", len(off_grid4))
