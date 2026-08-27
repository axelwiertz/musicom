# -*- coding: utf-8 -*-
"""Verify percussion onsets align exactly with the 16th-note beat grid."""
import mido
import os

MIDI = "/opt/data/projects/Styles/Pop/pop-5part-methods/MIDI/pop_5part_methods.mid"
BAR = 1920
STEP16 = 120

mid = mido.MidiFile(MIDI)

def extract_on_offs(track):
    """Return {note: set of onset ticks} with absolute time."""
    onsets = {}
    t = 0
    active = {}
    for msg in track:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            if msg.note not in active:
                active[msg.note] = t
            else:
                active[msg.note] = t
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            n = msg.note
            if n in active:
                onsets.setdefault(n, set()).add(active.pop(n))
    for n, t in active.items():
        onsets.setdefault(n, set()).add(t)
    return onsets

# Inspect tracks: find drum channel (ch9)
for idx, track in enumerate(mid.tracks):
    ch = None
    for msg in track:
        if msg.type == 'program_change':
            ch = msg.channel
            break
    label = f"track{idx}"
    if ch == 9:
        label = "DRUMS"
    print(f"=== {label} (ch {ch}) ===")
    if ch == 9:
        ons = extract_on_offs(track)
        # percussion notes 36 kick, 38 snare, 42 hat
        for note in (36, 38, 42):
            if note in ons:
                ticks = sorted(ons[note])
                # check all on grid
                off_grid = [x for x in ticks if x % STEP16 != 0]
                print(f"  note {note}: {len(ticks)} onsets, off-grid: {off_grid[:5]}")
                print(f"    first 12: {ticks[:12]}")
            else:
                print(f"  note {note}: none")