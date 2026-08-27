# -*- coding: utf-8 -*-
"""Read-only MIDI structure verification for 074-groove-gpc (mido allowed for analysis)."""
import mido

for name in ('MIDI/074-groove-gpc.mid', 'MIDI/074-groove-gpc-phase1.mid'):
    m = mido.MidiFile(name)
    ticks = m.length
    print(name, '| tracks:', len(m.tracks), '| dur(sec):', round(ticks, 2))
    for i, t in enumerate(m.tracks):
        n = sum(1 for msg in t if msg.type == 'note_on' and msg.velocity > 0)
        print('   track', i, 'notes:', n)
