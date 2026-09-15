# -*- coding: utf-8 -*-
"""Analyze picked source MIDI for SP-074 job."""
import mido
from collections import Counter

path = "/opt/data/repos/musicom/projects/Styles/Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid"
mid = mido.MidiFile(path)
print(f"type={mid.type} tpb={mid.ticks_per_beat} tracks={len(mid.tracks)} len={mid.length:.2f}s")

# tempo map
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        print(f"tempo={msg.tempo} bpm={round(60000000/msg.tempo,2)}")
    if msg.type == "time_signature":
        print(f"timesig={msg.numerator}/{msg.denominator}")

total = 0
for ti, track in enumerate(mid.tracks):
    notes = []
    abstick = 0
    for msg in track:
        abstick += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            notes.append((abstick, msg.note, msg.velocity, msg.channel if hasattr(msg, "channel") else -1))
    progs = [(m.program, m.channel) for m in track if m.type == "program_change"]
    print(f"track {ti}: name={track.name!r} n_notes={len(notes)} progs={progs}")
    if notes:
        pitches = sorted(set(n[1] for n in notes))
        print(f"  pitch_range={pitches[0]}..{pitches[-1]} nunique={len(pitches)}")
        for n in notes[:16]:
            print(f"    tick={n[0]} pitch={n[1]} vel={n[2]} ch={n[3]}")
        # tick extents
        print(f"  last_tick={notes[-1][0]}")
    total += len(notes)
print(f"total_notes={total}")

# file size
import os
print(f"size={os.path.getsize(path)}")
