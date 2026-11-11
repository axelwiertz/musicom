# -*- coding: utf-8 -*-
"""Determine chord progression per bar from bass track + pad."""
import mido
from collections import Counter, defaultdict

SRC = "/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid"
mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
BAR = 1920

# track 4 = bass (program 33), track 2 = strings pad (49), track 3 = pad (88)
def get_notes(ti):
    tr = mf.tracks[ti]
    t = 0
    pending = {}
    rows = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            pending[m.note] = t
        elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
            if m.note in pending:
                st = pending.pop(m.note)
                rows.append((st, m.note))
    return rows

bass = get_notes(4)
pad = get_notes(2)

# bass root per bar = most common low note
print("=== BASS roots per bar (mode note, count) ===")
for bar in range(32):
    lo, hi = bar * BAR, (bar + 1) * BAR
    notes = [n for st, n in bass if lo <= st < hi]
    if notes:
        c = Counter(notes)
        root = c.most_common(1)[0][0]
        print(f"  bar {bar:2d}: root={root} ({root%12}) count={c[root]} notes={sorted(set(notes))}")
    else:
        print(f"  bar {bar:2d}: (no bass)")

# pad pitch-class histogram per bar (2-bar aggregation)
print("\n=== PAD (track2) pcs per bar ===")
for bar in range(32):
    lo, hi = bar * BAR, (bar + 1) * BAR
    notes = [n for st, n in pad if lo <= st < hi]
    c = Counter(n % 12 for n in notes)
    print(f"  bar {bar:2d}: {c.most_common(4)}")
