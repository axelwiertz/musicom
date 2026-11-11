# -*- coding: utf-8 -*-
"""Full detail of track-1 (melody) notes in bars 10-12 and 18-20."""
import mido

SRC = "/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid"
mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
BAR = 1920

tr = mf.tracks[1]
t = 0
pending = {}
rows = []
for m in tr:
    t += m.time
    if m.type == "note_on" and m.velocity > 0:
        pending[m.note] = (t, m.velocity)
    elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
        if m.note in pending:
            st, vel = pending.pop(m.note)
            rows.append((st, t, m.note, vel))

for lo, hi in [(10 * BAR, 12 * BAR), (18 * BAR, 20 * BAR)]:
    print(f"\n=== bars {lo//BAR}-{hi//BAR} (ticks {lo}-{hi}) track1 ===")
    for st, en, note, vel in rows:
        if lo <= st < hi:
            print(f"  on={st} off={en} dur={en-st} note={note} vel={vel}")
