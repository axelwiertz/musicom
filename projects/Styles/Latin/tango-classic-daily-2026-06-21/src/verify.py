#!/usr/bin/env python3
"""Verify MIDI file structure"""
from mido import MidiFile
m = MidiFile('/opt/data/projects/Styles/Latin/tango-classic-daily-2026-06-21/composition.mid')
print(f'Ticks per beat: {m.ticks_per_beat}')
print(f'Num tracks: {len(m.tracks)}')
for i, t in enumerate(m.tracks):
    print(f'Track {i}: {len(t)} messages')