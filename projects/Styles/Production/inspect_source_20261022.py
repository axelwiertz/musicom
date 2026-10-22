# -*- coding: utf-8 -*-
"""Inspect source MIDI for SP-101 BLOT job (2026-10-22)."""
import mido
from collections import Counter

SRC = "/opt/data/repos/musicom/projects/Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-v5.mid"

mf = mido.MidiFile(SRC)
print("TPB", mf.ticks_per_beat, "length(s)", round(mf.length, 3), "tracks", len(mf.tracks))

tempo = None
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            tempo = m.tempo
print("bpm", round(mido.tempo2bpm(tempo), 2) if tempo else None)

all_pcs = Counter()
track_info = []
for i, tr in enumerate(mf.tracks):
    t = 0
    prog = None
    notes = []
    chans = set()
    for m in tr:
        t += m.time
        if m.type == "program_change":
            prog = m.program
        if m.type == "note_on" and m.velocity > 0:
            notes.append((m.note, m.velocity, t, m.channel))
            chans.add(m.channel)
            all_pcs[m.note % 12] += 1
    if notes:
        lows = min(n[0] for n in notes)
        highs = max(n[0] for n in notes)
        # durations
        durs = []
        for tr2 in [tr]:
            t2 = 0
            pending = {}
            for m in tr2:
                t2 += m.time
                if m.type == "note_on" and m.velocity > 0:
                    pending[m.note] = t2
                elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                    if m.note in pending:
                        durs.append(t2 - pending.pop(m.note))
        durset = sorted(set(durs))[:8]
        track_info.append((i, prog, len(notes), lows, highs, sorted(chans), durset))
    print(f"track{i}: end_tick={t} prog={prog} notes={len(notes)} range=({min(n[0] for n in notes) if notes else '-'},{max(n[0] for n in notes) if notes else '-'}) chans={sorted(chans)}")

print("\nPitch class histogram (pc:count):")
for pc in sorted(all_pcs):
    print(f"  {pc}: {all_pcs[pc]}")

print("\nDistinct pitch classes present:", sorted(all_pcs))
print("Total note-ons:", sum(all_pcs.values()))
