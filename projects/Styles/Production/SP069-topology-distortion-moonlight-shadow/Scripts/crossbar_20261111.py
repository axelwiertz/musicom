# -*- coding: utf-8 -*-
"""Check cross-bar notes in the ORIGINAL moonlight-shadow-variant2.mid."""
import mido

SRC = "/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid"
mf = mido.MidiFile(SRC)
BAR = 1920

for ti in range(1, 7):
    tr = mf.tracks[ti]
    t = 0
    open_notes = []
    crossing = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            open_notes.append({"note": m.note, "on": t})
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            for i in range(len(open_notes) - 1, -1, -1):
                if open_notes[i]["note"] == m.note:
                    n = open_notes.pop(i)
                    if n["on"] // BAR != t // BAR:
                        crossing.append((n["note"], n["on"], t, t - n["on"]))
                    break
    print(f"track {ti}: {len(crossing)} cross-bar notes")
    for c in crossing[:15]:
        print(f"    note={c[0]} on={c[1]} off={c[2]} dur={c[3]}")
