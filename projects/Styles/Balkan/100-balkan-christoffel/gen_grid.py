# -*- coding: utf-8 -*-
"""Generate grid visualization for 100-balkan-christoffel.
# READING ONLY (analysis)
"""
import os
import mido

from structures import MusicUnit


PROJ = "/opt/data/repos/musicom/projects/Styles/Balkan/100-balkan-christoffel"
MIDI_PATH = os.path.join(PROJ, "MIDI", "100-balkan-christoffel.mid")
OUT_TXT = os.path.join(PROJ, "Analysis", "grid_visualization.txt")

mid = mido.MidiFile(MIDI_PATH)
GRID = 120  # 16th grid
TOTAL_SLOTS = 31680 // GRID  # 264 slots

voice_grids = {}

for trk in mid.tracks:
    if not trk.name:
        # Check track notes
        has_notes = any(m.type == 'note_on' and m.velocity > 0 for m in trk)
        if not has_notes:
            continue
    t_name = trk.name or "Voice"
    abs_t = 0
    slots = ["░"] * TOTAL_SLOTS
    for msg in trk:
        abs_t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0 and msg.note > 0:
            idx = abs_t // GRID
            if 0 <= idx < TOTAL_SLOTS:
                slots[idx] = "█"
    voice_grids[t_name] = slots

with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("=== 100-balkan-christoffel: Kopanitsa 11/8 Grid Visualization ===\n")
    f.write(f"Grid unit: 16th note = 120 ticks. Bar = 11 sixteenths = 1320 ticks.\n")
    f.write("Sections (4 bars each): Intro | Tema_A | Tema_B | Razvivka | Tema_A_Var | Zavurshek\n\n")
    
    # Print bar by bar
    for b in range(24):
        sec_name = ["Intro", "Tema_A", "Tema_B", "Razvivka", "Tema_A_Var", "Zavurshek"][b // 4]
        f.write(f"--- Bar {b+1:02d} ({sec_name}) ---\n")
        st_slot = b * 11
        end_slot = st_slot + 11
        f.write("Beat:  1 . 2 . 3 . . 4 . 5 .\n")
        for v_idx, (v_name, slots) in enumerate(voice_grids.items()):
            bar_str = " ".join(slots[st_slot:end_slot])
            f.write(f"V{v_idx:02d}:  {bar_str}  ({v_name})\n")
        f.write("\n")

print(f"Grid visualization written to {OUT_TXT}")
