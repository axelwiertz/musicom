# -*- coding: utf-8 -*-
"""Read-only audit of moonlight-shadow-variant2.mid for the production job."""
import mido
from collections import defaultdict

SRC = "/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid"
mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat
print("ticks_per_beat =", tpb)
print("length_s =", round(mf.length, 2))
print("num_tracks =", len(mf.tracks))

# Gather per-track info
track_info = []
for i, tr in enumerate(mf.tracks):
    notes = []
    progs = []
    t = 0
    for m in tr:
        t += m.time
        if m.type == "program_change":
            progs.append((m.program, t))
        if m.type == "note_on" and m.velocity > 0:
            notes.append((m.note, m.velocity, t, m.channel))
    end_tick = t
    # max tick = last event time
    track_info.append({
        "idx": i, "name": tr.name, "n_notes": len(notes),
        "programs": sorted(set(p[0] for p in progs)),
        "channels": sorted(set(n[3] for n in notes)),
        "end_tick": end_tick,
        "note_min": min((n[0] for n in notes), default=None),
        "note_max": max((n[0] for n in notes), default=None),
    })
for ti in track_info:
    print(ti)

# Tempo events (track 0)
tempos = []
for tr in mf.tracks:
    t = 0
    for m in tr:
        t += m.time
        if m.type == "set_tempo":
            tempos.append((m.tempo, t))
print("tempos (microsec/beat, tick):", tempos)
if tempos:
    uspb = tempos[0][0]
    bpm = round(60_000_000 / uspb, 1)
    print("derived BPM =", bpm)

# Onset grid audit: all pitched notes (not channel 9)
GRID_8 = tpb // 2
GRID_16 = tpb // 4
off_16 = 0
off_8 = 0
total_pitched = 0
per_track_offgrid = {}
pcs = set()
for tr in mf.tracks:
    t = 0
    cnt_off16 = 0
    cnt_off8 = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            if m.channel == 9:
                continue
            total_pitched += 1
            pcs.add(m.note % 12)
            if t % GRID_16 != 0:
                off_16 += 1
                cnt_off16 += 1
            if t % GRID_8 != 0:
                off_8 += 1
                cnt_off8 += 1
    if cnt_off16 or cnt_off8:
        per_track_offgrid[tr.name or f"track{tr.name}"] = (cnt_off16, cnt_off8)

print("\n=== GRID SYNC (pitched notes only) ===")
print("total_pitched_onsets =", total_pitched)
print("off-16th (120-tick) =", off_16)
print("off-8th  (240-tick) =", off_8)
print("pitch classes used:", sorted(pcs))
print("per-track off-grid (off16, off8):", per_track_offgrid)

# Zero-drift: track end ticks
print("\n=== ZERO-DRIFT (track end ticks) ===")
ends = [ti["end_tick"] for ti in track_info]
print("end_ticks:", ends)
print("all equal:", len(set(ends)) == 1)

# Harmony: E major scale pcs = {4,6,8,9,11,1,3}
E_MAJOR = {4, 6, 8, 9, 11, 1, 3}  # E F# G# A B C# D#
out_of_scale = 0
total_pitched2 = 0
for tr in mf.tracks:
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0 and m.channel != 9:
            total_pitched2 += 1
            if m.note % 12 not in E_MAJOR:
                out_of_scale += 1
print("\n=== HARMONY (E major scale) ===")
print("total_pitched =", total_pitched2, "out_of_scale =", out_of_scale)
