# -*- coding: utf-8 -*-
"""Full distribution of picked source."""
import mido
from collections import Counter
path = "/opt/data/repos/musicom/projects/Styles/Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid"
mid = mido.MidiFile(path)
for ti, track in enumerate(mid.tracks):
    c = Counter()
    abstick = 0
    durs = []
    active = {}
    for msg in track:
        abstick += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            c[msg.note] += 1
            active[msg.note] = abstick
        elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                durs.append(abstick - active.pop(msg.note))
    print(f"track {ti} name={track.name!r} dist={dict(sorted(c.items()))}")
    if durs:
        import statistics
        print(f"  dur_ticks min={min(durs)} med={statistics.median(durs)} max={max(durs)} n={len(durs)}")
print("ticks_per_beat", mid.ticks_per_beat)
for msg in mid.tracks[0]:
    print(msg)
