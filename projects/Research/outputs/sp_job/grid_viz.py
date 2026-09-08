#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write grid visualization for the source MIDI (provenance pass)."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom")
import mido

SRC = "/opt/data/projects/Styles/Tango/dramatic/v1/tango_dramatic.mid"
OUT = "/opt/data/projects/Styles/Production/SP035-shimmer-tango-dramatic/Analysis"

mid = mido.MidiFile(SRC)
ppq = mid.ticks_per_beat
total = 0
for trk in mid.tracks:
    t = 0
    for msg in trk:
        t += msg.time
    total = max(total, t)
print("tracks:", len(mid.tracks), "ppq:", ppq, "max_tick:", total, "dur_s:",
      total / ppq / 2.0 if False else total / (ppq * 2.0))

# parse notes per channel
from collections import defaultdict
evs = defaultdict(list)
for trk in mid.tracks:
    t = 0
    for msg in trk:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            evs[msg.channel].append((t, msg.note))
channels = sorted(evs)
print("channels:", {c: len(evs[c]) for c in channels})

# density grid: 16 rows (channels) x cols (bars). bar = ppq*4
BPB = 4
bar = ppq * BPB
n_bars = total // bar + 1
n_ch = len(channels)
grid = [["."] * n_bars for _ in range(n_ch)]
for i, ch in enumerate(channels):
    for t, n in evs[ch]:
        b = t // bar
        if b < n_bars:
            grid[i][b] = "#"
lines = []
lines.append("SP-035 Shimmer Tango Dramatic — source MIDI density grid")
lines.append(f"tracks={len(mid.tracks)} channels={n_ch} bars={n_bars} ({BPB} beats/bar)")
lines.append("rows = MIDI channels (0=Bandoneon,1=Piano,2=Bass,9=Perc)")
lines.append("cols = bars; # = any onset in bar")
lines.append("")
for i, ch in enumerate(channels):
    label = {0: "Bandoneon", 1: "Piano", 2: "Bass", 9: "Perc"}.get(ch, f"ch{ch}")
    lines.append(f"{label:10s} " + "".join(grid[i]))
with open(OUT + "/grid_visualization.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
