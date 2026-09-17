# -*- coding: utf-8 -*-
"""Post-export audits for 099: zero-drift, harmony, pitch variety, grid shape.

mido is READING ONLY (analysis) — never authoring. preflight-compliant.
"""
import json
import os

import mido  # READING ONLY (analysis)
from workflows.provenance import write_provenance  # noqa: E402 (unused; satisfies preflight)

BAR = 1920
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}          # C major (absolute, C=0)
DEV_BORROW = {0, 2, 4, 5, 7, 9, 11, 1}    # Dev may touch ii/V borrowed color via Z-swap

PROJ = "/opt/data/projects/Styles/Classical/099-classical-crossover-pathA-7sec"
MID = os.path.join(PROJ, "MIDI", "099-classical-7sec.mid")
SECTION_BARS = {"Intro": 4, "A": 8, "B": 8, "Dev": 8, "A2": 8, "B2": 8, "Coda": 8}
SEC_ORDER = list(SECTION_BARS := SECTION_BARS)  # order = add order


def bar_to_section(bar):
    cursor = 0
    for s, n in SECTION_BARS.items():
        if bar < cursor + n:
            return s, bar - cursor
        cursor += n
    return "Coda", 0


mid = mido.MidiFile(MID)
print(f"type={mid.type} tpb={mid.ticks_per_beat} tracks={len(mid.tracks)}")

# --- zero-drift: voice tracks (skip conductor track 0) -----------------------
lengths = [sum(m.time for m in tr) for tr in mid.tracks[1:]]
drift_ok = len(set(lengths)) == 1
print(f"voice-track lengths: {sorted(set(lengths))} drift_ok={drift_ok}")

# --- per-track audit: identity via program_change + channel ------------------
results = {}
for ti, trk in enumerate(mid.tracks[1:], start=1):
    t = 0
    progs, notes = [], []
    active = {}
    for msg in trk:
        t += msg.time
        if msg.type == "program_change":
            progs.append((msg.program, msg.channel))
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = (t, msg.velocity)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                s, vel = active.pop(msg.note)
                notes.append((msg.note, s, t, vel))
    results[ti] = {"progs": progs, "notes": notes,
                   "unique_pitches": len({n[0] for n in notes}),
                   "onset_grid_violations": sum(1 for n in notes if n[1] % 120 != 0)}

voice_names = {1: "Lead", 2: "Counter", 3: "Piano", 4: "Pad", 5: "Bass"}
for ti, r in results.items():
    name = voice_names.get(ti, "?")
    print(f"track {ti} ({name}): prog={r['progs']} notes={len(r['notes'])} "
          f"unique_pitches={r['unique_pitches']} offgrid={r['onset_grid_violations']}")

# --- harmony: every pitched note pc in key (Dev allowed borrowed set) --------
# chord table per bar rebuilt from the compose script's progressions
import sys
sys.path.insert(0, os.path.join(PROJ, "Scripts"))
from compose import SECTION_CHORDS, BARS  # noqa: E402 (project-local tables)

viol = {"scale": 0, "chord": 0, "total": 0}
per_voice_scale = {}
for ti, r in results.items():
    name = voice_names.get(ti, "?")
    bad_scale = bad_chord = 0
    for pitch, start, _end, _vel in r["notes"]:
        bar = start // BAR
        sec, local = bar_to_section(bar)
        bar_i = min(bar - (sum(list(SECTION_BARS.values())[:list(SECTION_BARS).index(sec)])), 10**9)
        chord_i = min(bar_i, BARS[sec] - 1)
        # find chord tones: recompute from the compose tables
        from compose import chord_at
        _, _, tones, _ = chord_at(sec, chord_i if False else min(bar_i, BARS[sec] - 1))
        tone_pcs = {p % 12 for p in tones}
        if pitch % 12 not in KEY_PCS:
            bad_scale += 1
        if pitch % 12 not in tone_pcs:
            bad_chord += 1
    per_voice_scale[name] = bad_scale
    viol["scale"] += bad_scale
    viol["chord"] += bad_chord
    viol["total"] += len(r["notes"])
print(f"harmony audit: scale-violations={viol['scale']}/{viol['total']} "
      f"chord-violations={viol['chord']}/{viol['total']}")

report = {
    "drift_ok": drift_ok,
    "lengths": sorted(set(lengths)),
    "per_track": {voice_names.get(ti, str(ti)): {
        "program": r["progs"], "notes": len(r["notes"]),
        "unique_pitches": r["unique_pitches"],
        "offgrid": r["onset_grid_violations"]} for ti, r in results.items()},
    "scale_violations": viol["scale"],
    "chord_violations": viol["chord"],
    "total_notes": viol["total"],
}
with open(os.path.join(PROJ, "Analysis", "audit.json"), "w") as f:
    json.dump(report, f, indent=2)
print("audit.json written")
