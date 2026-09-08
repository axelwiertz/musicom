# -*- coding: utf-8 -*-
"""Analyze source MIDI: tracks, programs, tempo, note durations, gaps."""
import mido
from collections import Counter

path = "/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid"
mf = mido.MidiFile(path)
print(f"type={mf.type} ticks_per_beat={mf.ticks_per_beat} tracks={len(mf.tracks)}")
total = mf.length
print(f"length_sec={total:.2f}")

for ti, track in enumerate(mf.tracks):
    print(f"\n--- track {ti}: {track.name} (len={len(track)}) ---")
    programs = []
    notes = []
    t = 0
    on = {}
    for msg in track:
        t += msg.time
        if msg.type == "program_change":
            programs.append(msg.program)
        elif msg.type == "note_on" and msg.velocity > 0:
            on[msg.note] = t
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            st = on.pop(msg.note, None)
            if st is not None:
                notes.append((msg.note, st, t - st))
    if programs:
        print(f"programs={Counter(programs)}")
    if notes:
        dur = [d for _, _, d in notes]
        durs = Counter(dur)
        print(f"n_notes={len(notes)} pitch_range={min(n for n,_,_ in notes)}-{max(n for n,_,_ in notes)}")
        print(f"dur_ticks_top={durs.most_common(8)}")
        # gaps between consecutive note starts
        ons = sorted(st for _, st, _ in notes)
        gaps = [b - a for a, b in zip(ons, ons[1:])]
        print(f"onset_gap_ticks_top={Counter(gaps).most_common(8)}")
        print(f"max_dur_ticks={max(dur)}")
