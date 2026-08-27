#!/usr/bin/env python3
"""Verify generated MIDI file."""
from mido import MidiFile

mid = MidiFile('/opt/data/projects/Styles/Bluegrass/bluegrass-scruggs-daily-2026-06-23/composition.mid')
print(f'Tracks: {len(mid.tracks)}')
print(f'TPB: {mid.ticks_per_beat}')
for i, t in enumerate(mid.tracks):
    print(f'  Track {i}: {len(t)} messages')
for msg in mid.tracks[0]:
    if msg.type != 'end_of_track':
        print(f'  Meta: {msg}')
        break