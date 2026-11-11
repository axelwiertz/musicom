# -*- coding: utf-8 -*-
"""Surgical rework of moonlight-shadow-variant2.mid.

Removes the 59 one-tick stub notes that sit 1 tick BEFORE each bar seam
(note_on at t % 1920 == 1919, note_off 1 tick later). These break grid sync
(59 off-grid onsets). Everything else is preserved byte-exact: pitches,
velocities, durations, cross-bar sustains, programs, channels, terminal pads.

Rationale for surgical (not UnitMatrixComposer) rework: the source has ~150
sustained notes that ring across BAR boundaries within multi-bar sections
(Intro 4 / Verse 8 / Chorus 8 / Verse2 8 / Outro 4). A 1-bar-per-section
matrix reconstruction clamps those sustains at every bar line (audible
fidelity loss). The surgical edit preserves them and only deletes the stubs.
"""
import os
import json
import shutil

import mido

SRC = ("/opt/data/repos/musicom/projects/Styles/Pop/moonlight-shadow/"
       "MIDI/moonlight-shadow-variant2.mid")

OUT_DIR = ("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP069-topology-distortion-moonlight-shadow")
MID = os.path.join(OUT_DIR, "MIDI")
os.makedirs(MID, exist_ok=True)

BAR = 1920
GRID = 120

mf = mido.MidiFile(SRC)
tpb = mf.ticks_per_beat

new_mf = mido.MidiFile(ticks_per_beat=tpb)
# track 0 = conductor/tempo, keep byte-identical
new_mf.tracks.append(mf.tracks[0])

removed = 0
for ti, tr in enumerate(mf.tracks[1:], start=1):
    new_tr = mido.MidiTrack()
    t = 0
    stub_offs = []          # (note, channel, abs_tick) of note_offs to skip
    kept = []               # (abs_tick, msg)
    for msg in tr:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0 and (t % BAR) == BAR - 1:
            stub_offs.append((msg.note, msg.channel, t + 1))
            removed += 1
            continue
        if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            key = (msg.note, msg.channel, t)
            if key in stub_offs:
                stub_offs.remove(key)
                continue
        kept.append((t, msg))
    last = 0
    for abs_t, msg in kept:
        m2 = msg.copy()
        m2.time = abs_t - last
        last = abs_t
        new_tr.append(m2)
    new_mf.tracks.append(new_tr)

print("removed stub notes:", removed)
assert removed == 59, f"expected 59, got {removed}"

clean = os.path.join(MID, "moonlight-shadow-clean.mid")
new_mf.save(clean)
print("clean MIDI:", clean, os.path.getsize(clean), "bytes")

# phase1 sidecar = original raw
phase1 = os.path.join(MID, "moonlight-shadow-variant2-phase1.mid")
shutil.copyfile(SRC, phase1)
print("phase1 sidecar:", phase1)

# ---- re-audit the clean MIDI (3 rules) ----
mf2 = mido.MidiFile(clean)

E_MAJOR = {4, 6, 8, 9, 11, 1, 3}
off_grid = 0
out_scale = 0
total = 0
end_ticks = []

for tr in mf2.tracks:
    t = 0
    for msg in tr:
        t += msg.time
    end_ticks.append(t)

for tr in mf2.tracks:
    t = 0
    for msg in tr:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            if msg.channel == 9:
                continue
            total += 1
            if t % GRID != 0:
                off_grid += 1
            if msg.note % 12 not in E_MAJOR:
                out_scale += 1

note_end = end_ticks[1:]  # skip conductor
print("track end ticks:", end_ticks)
print("zero-drift (all note tracks equal):", len(set(note_end)) == 1)

audit = {
    "off_grid": off_grid,
    "out_scale": out_scale,
    "total_pitched_onsets": total,
    "track_end_ticks": end_ticks,
    "zero_drift": len(set(note_end)) == 1,
    "removed_stub_notes": removed,
}
print("re-audit:", json.dumps(audit, indent=2))

with open(os.path.join(MID, "rework_audit.json"), "w") as f:
    json.dump(audit, f, indent=2)

assert off_grid == 0, "grid rework did not reach 0"
assert out_scale == 0, "scale rework did not reach 0"
assert len(set(note_end)) == 1, "zero-drift violated"
print("CLEAN: 0 off-grid, 0 out-of-scale, zero-drift intact")
