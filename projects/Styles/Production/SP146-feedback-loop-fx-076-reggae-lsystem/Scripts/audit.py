# -*- coding: utf-8 -*-
"""Reusable 3-rule audit for A-aeolian reggae MIDI (takes MIDI path as argv)."""
import json
import sys
from collections import defaultdict

import mido

MIDI = sys.argv[1] if len(sys.argv) > 1 else (
    "/opt/data/repos/musicom/projects/Styles/Reggae/076-reggae-lsystem/"
    "MIDI/076-reggae-lsystem.mid")

SCALE_PCS = {9, 11, 0, 2, 4, 5, 7}  # A aeolian
DEGREES = [0, 6, 0, 5] * 6           # i bVII i bVI per bar
CHORD_PCS = {0: {9, 0, 4}, 6: {7, 11, 2}, 5: {5, 9, 0}}
BAR_TICKS = 1920
GRID = 120

mf = mido.MidiFile(MIDI)
track_meta = []
for i, tr in enumerate(mf.tracks):
    channels = set()
    notes = []
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            channels.add(m.channel)
            notes.append((m.note, m.velocity, t))
    track_meta.append({"idx": i, "name": tr.name, "channels": sorted(channels),
                       "drum": 9 in channels, "notes": notes})

track_last_event = []
for tr in mf.tracks:
    t = 0
    last = 0
    for m in tr:
        t += m.time
        last = t
    track_last_event.append(last)
note_idx = [i for i, tm in enumerate(track_meta) if tm["notes"]]
lengths = [track_last_event[i] for i in note_idx]

off_grid = out_scale = out_chord = total = 0
per_voice = defaultdict(lambda: {"off_grid": 0, "out_scale": 0, "out_chord": 0, "n": 0})
for tm in track_meta:
    if tm["drum"]:
        continue
    for note, vel, t in tm["notes"]:
        total += 1
        bar = min(t // BAR_TICKS, len(DEGREES) - 1)
        deg = DEGREES[bar]
        pc = note % 12
        v = tm["name"] or ("track%d" % tm["idx"])
        per_voice[v]["n"] += 1
        if t % GRID != 0:
            off_grid += 1
            per_voice[v]["off_grid"] += 1
        if pc not in SCALE_PCS:
            out_scale += 1
            per_voice[v]["out_scale"] += 1
        if pc not in CHORD_PCS[deg]:
            out_chord += 1
            per_voice[v]["out_chord"] += 1

print("AUDIT:", MIDI)
print("note-track last-event ticks:", lengths, "equal:", len(set(lengths)) == 1)
print("total pitched:", total)
print("off_grid:", off_grid, " out_scale:", out_scale, " out_chord:", out_chord)
for v, d in sorted(per_voice.items()):
    print("  %-12s n=%-4d off_grid=%d out_scale=%d out_chord=%d"
          % (v, d["n"], d["off_grid"], d["out_scale"], d["out_chord"]))
verdict = (off_grid == 0 and out_scale == 0 and out_chord == 0
           and len(set(lengths)) == 1)
print("VERDICT:", "PASS" if verdict else "FAIL")
