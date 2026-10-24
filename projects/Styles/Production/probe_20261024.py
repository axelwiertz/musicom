# -*- coding: utf-8 -*-
"""Quick env/import probe + source drift analysis."""
import mido
from pathlib import Path

p = Path("/opt/data/repos/musicom/projects/Styles/Gamelan/017-gamelan-central-java/MIDI/gamelan_live_render.mid")
mf = mido.MidiFile(str(p))

print("=== per-track detail ===")
for i, tr in enumerate(mf.tracks):
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    t = 0
    last_off = 0
    n_on = 0
    noteoffs = []
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            n_on += 1
        if m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            noteoffs.append(t)
    print(f"track {i}: chans={chans} n_on={n_on} final_time={t} last_noteoff={noteoffs[-1] if noteoffs else None}")

print("\n=== env import probe ===")
try:
    from sound.generators.polymetric_grid import PolymetricGrid, eulerian_mask
    from sound.effects.mastering import master, target_for_style, measure_lufs
    from sound.render.fluidsynth import discover_soundfont
    print("imports OK")
    print("sf =", discover_soundfont())
    for s in ("gamelan", "pop", "folk", "classical"):
        print(f"  target_for_style({s!r}) =", target_for_style(s))
except Exception as e:
    import traceback; traceback.print_exc()
