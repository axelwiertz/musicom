# -*- coding: utf-8 -*-
"""Dump out-of-chord notes per track for 047-physarum-bowed.mid."""
import mido

SRC = ("/opt/data/repos/musicom/projects/Styles/Experimental/"
       "047-physarum-bowed/MIDI/047-physarum-bowed.mid")
BAR = 1920
CHORD_TONES = [
    {3, 7, 10}, {3, 7, 10},
    {5, 9, 0}, {5, 9, 0},
    {7, 10, 2}, {7, 10, 2},
    {10, 2, 5}, {10, 2, 5},
]
CHORD_NAMES = ["Eb", "Eb", "F", "F", "Gm", "Gm", "Bb", "Bb"]

mf = mido.MidiFile(SRC)
for ti, tr in enumerate(mf.tracks):
    t = 0
    notes = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            notes.append({"note": m.note, "on": t})
        elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
            for n in reversed(notes):
                if n["note"] == m.note and "off" not in n:
                    n["off"] = t
                    break
    ooc = []
    for n in notes:
        pc = n["note"] % 12
        bar = min(n["on"] // BAR, 7)
        if pc not in CHORD_TONES[bar]:
            ooc.append((n["note"], pc, bar, CHORD_NAMES[bar], n["on"]))
    if ooc:
        print(f"track {ti}: {len(ooc)} out-of-chord")
        for nn, pc, bar, cn, on in ooc[:60]:
            print(f"   note={nn} pc={pc} bar={bar}({cn}) on={on}")
