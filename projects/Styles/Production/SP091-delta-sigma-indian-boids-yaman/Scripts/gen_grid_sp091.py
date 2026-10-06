# -*- coding: utf-8 -*-
"""Generate track x bar onset grid (correct program mapping) for SP-091 source."""
import mido
from pathlib import Path

SRC = "/opt/data/repos/musicom/projects/Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid"
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP091-delta-sigma-indian-boids-yaman/Analysis/grid_visualization.txt")

GM = {19: "Church_Organ", 104: "Sitar", 74: "Recorder", 0: "Drums", 73: "Flute"}

mid = mido.MidiFile(SRC)
tpb = mid.ticks_per_beat
bpb = 4
bar_ticks = tpb * bpb

track_info = {}
for i, trk in enumerate(mid.tracks):
    t = 0
    prog = None
    ons = set()
    for msg in trk:
        t += msg.time
        if msg.type == "program_change":
            prog = msg.program
        if msg.type == "note_on" and msg.velocity > 0:
            ons.add(t // bar_ticks)
    if ons:
        track_info[i] = (GM.get(prog, f"prog{prog}"), ons)

max_bar = max(max(s) for s in (v[1] for v in track_info.values()))
lines = ["SP-091 source: 212-indian-boids-yaman.mid  (90 BPM, 4/4, bars shown 0..%d)" % max_bar,
         "Legend: # = onset(s) in bar, . = rest (empty bar)", ""]
hdr = "track".ljust(16) + "".join(f"{b:>2}" for b in range(max_bar + 1))
lines.append(hdr)
for i in sorted(track_info):
    name, ons = track_info[i]
    row = "".join("#" if b in ons else "." for b in range(max_bar + 1))
    lines.append(name.ljust(16) + row)
lines += ["", f"total bars: {max_bar + 1}, duration: {mid.length:.2f}s"]
OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
