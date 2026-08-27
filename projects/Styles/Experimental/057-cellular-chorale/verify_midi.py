#!/usr/bin/env python3
import mido

mid = mido.MidiFile('/opt/data/projects/Styles/Experimental/057-cellular-chorale/MIDI/057-cellular-chorale.mid')
print(f'Tracks: {len(mid.tracks)}')
print(f'Ticks/beat: {mid.ticks_per_beat}')
for i, track in enumerate(mid.tracks):
    notes = [m for m in track if m.type in ('note_on', 'note_off')]
    print(f'  Track {i}: {len(track)} messages, {len(notes)} note events')
    for m in notes[:4]:
        print(f'    {m}')
