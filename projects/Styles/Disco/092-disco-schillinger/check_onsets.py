# -*- coding: utf-8 -*-
"""Quick onset-position sanity check for the exported phase-2 MIDI."""
import os
import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401

MIDI = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger/MIDI/092-disco-schillinger.mid")
mid = mido.MidiFile(MIDI)
for i, track in enumerate(mid.tracks):
    if i == 0:
        continue
    t, prog, ch, onsets = 0, 0, 0, []
    for msg in track:
        t += msg.time
        if msg.type == "program_change":
            prog, ch = msg.program, msg.channel
        elif msg.type == "note_on" and msg.velocity > 0:
            onsets.append(t)
    print("track", i, "prog", prog, "ch", ch, "n_on", len(onsets))
    print("   first 16 onsets:", onsets[:16])
    print("   mod1920 first 16:", [o % 1920 for o in onsets[:16]])
