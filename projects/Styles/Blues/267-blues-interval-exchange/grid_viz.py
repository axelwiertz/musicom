# -*- coding: utf-8 -*-
"""ASCII rhythm-DNA grid for 267-blues-interval-exchange (from -perfect.mid)."""
import mido  # READING ONLY

ROOT = "/opt/data/projects/Styles/Blues/267-blues-interval-exchange"
NAME = "267-blues-interval-exchange"
EIGHTH = 240
N_BARS = 12
SLOTS = N_BARS * 8

mid = mido.MidiFile(f"{ROOT}/MIDI/{NAME}-perfect.mid")
# track -> channel -> name
tracks = {}
for t in mid.tracks:
    ch = None
    for m in t:
        if m.type == 'program_change':
            ch = m.channel
    if ch is not None:
        t_abs = 0
        grid = [0] * SLOTS
        for m in t:
            t_abs += m.time
            if m.type == 'note_on' and m.velocity > 0:
                s = t_abs // EIGHTH
                if 0 <= s < SLOTS:
                    grid[s] = 1
        tracks[ch] = grid

names = {0: "Harmonica", 1: "Organ", 2: "Bass", 9: "Drums"}
lines = []
lines.append(f"# {NAME} -- rhythm DNA grid (perfect, 8th-note resolution)")
lines.append(f"# 12-bar blues, Ab natural minor, 100 BPM. 1 column = 1 eighth.")
lines.append("")
bar_marks = "".join(str(b % 10) for b in range(N_BARS) for _ in range(8))
lines.append(f"bar  : {bar_marks}")
for ch in (0, 1, 2, 9):
    g = tracks.get(ch, [0] * SLOTS)
    row = "".join("#" if x else "." for x in g)
    lines.append(f"{names[ch]:9s}: {row}")
lines.append("")
lines.append("# # = onset, . = rest. Drum row shows kick/snare/hat combined.")
lines.append("# Legend: bars 0-3 i7 | 4-5 iv7 | 6-7 i7 | 8 v7 | 9 iv7 | 10-11 i7")

with open(f"{ROOT}/Analysis/grid_visualization.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
print("\nWROTE grid_visualization.txt")
