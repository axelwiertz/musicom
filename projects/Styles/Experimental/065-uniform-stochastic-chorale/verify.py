# -*- coding: utf-8 -*-
"""Verify 065 artifacts: track structure, pitch content, zero-drift check."""
import mido
import os

BASE = "/opt/data/projects/Styles/Experimental/065-uniform-stochastic-chorale"
P1 = os.path.join(BASE, "MIDI/065-uniform-stochastic-chorale-phase1.mid")
P2 = os.path.join(BASE, "MIDI/065-uniform-stochastic-chorale.mid")

for label, path in [("PHASE1(raw)", P1), ("PHASE2(rules)", P2)]:
    m = mido.MidiFile(path)
    print(f"=== {label}: {os.path.basename(path)} ({os.path.getsize(path)} B) ===")
    print(f"  tracks: {len(m.tracks)}, length ticks: {m.length}")
    for i, t in enumerate(m.tracks):
        notes = [msg for msg in t if msg.type == "note_on" and msg.velocity > 0]
        pitches = sorted(set(n.note for n in notes))
        print(f"  track{i}: {len(notes)} notes, pitch range {min(pitches) if pitches else '-'}..{max(pitches) if pitches else '-'}, "
              f"unique={pitches[:14]}")
    # zero-drift: all tracks same length
    lens = []
    for t in m.tracks:
        ticks = 0
        for msg in t:
            ticks += msg.time
        lens.append(ticks)
    print(f"  track end ticks: {lens}  -> equal-length: {len(set(lens)) == 1}")
    print()