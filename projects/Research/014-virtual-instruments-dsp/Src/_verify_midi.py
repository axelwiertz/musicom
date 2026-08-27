#!/usr/bin/env python3
"""Verify MIDI output."""
from mido import MidiFile
mid = MidiFile('/opt/data/projects/Research/014-virtual-instruments-dsp/MIDI/steel_guitar_2026-06-24.mid')
for i, track in enumerate(mid.tracks):
    print(f'Track {i}: {len(track)} messages')
    for msg in track:
        print(f'  {msg}')
print(f'Ticks per beat: {mid.ticks_per_beat}')