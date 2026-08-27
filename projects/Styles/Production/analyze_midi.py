#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only MIDI analysis of selected composition (mido allowed for reading)."""
import mido
from mido import MidiFile
from collections import Counter

path = '/opt/data/projects/Styles/Experimental/058-markov-chorale/MIDI/058-markov-chorale.mid'
mid = MidiFile(path)
print(f'type={mid.type} ticks_per_beat={mid.ticks_per_beat} tracks={len(mid.tracks)}')
print(f'duration_seconds_est={mid.length:.2f}')
total_notes = 0
for ti, track in enumerate(mid.tracks):
    notes = []
    for msg in track:
        if msg.type == 'note_on' and msg.velocity > 0:
            notes.append((msg.note, msg.velocity, msg.time))
    total_notes += len(notes)
    programs = [m.program for m in track if m.type == 'program_change']
    print(f'track {ti}: name={track.name!r} n_notes={len(notes)} programs={Counter(programs)}')
    if notes:
        pitches = sorted(set(n[0] for n in notes))
        print(f'   pitch_range={pitches[0]}..{pitches[-1]} n_unique={len(pitches)}')
        print(f'   sample_notes={notes[:8]}')
print(f'total_notes={total_notes}')
