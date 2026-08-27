#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only MIDI verification for project 059 (mido analysis only, no authoring)."""
import mido

mid = mido.MidiFile("/opt/data/projects/Styles/Experimental/059-genetic-chorale/MIDI/059-genetic-chorale.mid")
print(f"Ticks per beat: {mid.ticks_per_beat}")
print(f"Tracks: {len(mid.tracks)}")

track_ends = []
for ti, track in enumerate(mid.tracks):
    abs_time = 0
    notes = []
    max_time = 0
    for msg in track:
        abs_time += msg.time
        max_time = max(max_time, abs_time)
        if msg.type == 'note_on' and msg.velocity > 0:
            notes.append((msg.note, abs_time))
    track_ends.append(max_time)
    prog = next((m.program for m in track if m.type == 'program_change'), None)
    print(f"  Track {ti}: program={prog}, end_tick={max_time}, notes={len(notes)}")
    print(f"    note sequence: {[n for n, _ in sorted(notes, key=lambda x: x[1])]}")

print(f"\nTrack end ticks: {track_ends}")
print(f"Zero-drift (all equal): {len(set(track_ends)) == 1}")
