# -*- coding: utf-8 -*-
"""Read-only verification audit for 262-harmonic-chorale-variations.

mido READING ONLY (analysis). Checks: zero-drift (all tracks equal length),
16th-grid lock (perfect == 0 off-grid, humanized > 0, phase1 raw), scale
discipline (0 out-of-scale, skip ch9), chord discipline (per-bar chord, floor
t//BAR, 0 violations, skip ch9).
"""
import json
import os
import mido  # READING ONLY (analysis)

ROOT = "/opt/data/projects/Styles/Experimental/262-harmonic-chorale-variations"
NAME = "262-harmonic-chorale-variations"
TONIC = 5
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
SCALE_PCS = set((TONIC + o) % 12 for o in SCALE_INTERVALS)
BAR = 1920
N_BARS = 24
GRID = 120

# form degrees (must match compose.py)
FORM_DEGREES = [
    ("A Theme", [0, 5, 3, 4]), ("B Retrograde", [4, 3, 5, 0]),
    ("C Transposed", [4, 0, 1, 4]), ("D Inversion", [3, 1, 4, 0]),
    ("E Diminution", [0, 3, 1, 4]), ("F Coda Augm", [3, 4, 0, 0]),
]
CHORD_DEGREE_BY_BAR = [d for _, dg in FORM_DEGREES for d in dg]
KEY_ROOT_MIDI = 53


def diatonic(deg):
    oct_shift = deg // 7
    step = deg % 7
    return KEY_ROOT_MIDI + oct_shift * 12 + SCALE_INTERVALS[step]


def chord_pcs(deg):
    return {diatonic(deg) % 12, diatonic(deg + 2) % 12, diatonic(deg + 4) % 12}


def read_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for t in mid.tracks:
        ch = None
        for m in t:
            if m.type == "program_change":
                ch = m.channel
        t_abs = 0
        notes = []
        for m in t:
            t_abs += m.time
            if m.type == "note_on" and m.velocity > 0:
                notes.append({"pitch": m.note, "start_tick": t_abs,
                              "channel": ch})
        if ch is not None:
            tracks.append({"channel": ch, "notes": notes, "total_ticks": t_abs})
    return mid, tracks


def audit(path):
    mid, tracks = read_tracks(path)
    lens = [t["total_ticks"] for t in tracks]
    drift_ok = len(lens) > 0 and len(set(lens)) == 1
    pitched = [n for t in tracks if t["channel"] != 9 for n in t["notes"]]
    offgrid = sum(1 for n in pitched if not (n["start_tick"] % 120 == 0
                                             or n["start_tick"] % 240 == 0))
    scale_viol = sum(1 for n in pitched if n["pitch"] % 12 not in SCALE_PCS)
    chord_viol = sum(1 for n in pitched
                     if n["pitch"] % 12
                     not in chord_pcs(CHORD_DEGREE_BY_BAR[n["start_tick"] // BAR]))
    return {"bytes": os.path.getsize(path), "voice_tracks": len(tracks),
            "voice_len": lens[0] if lens else None, "drift_ok": drift_ok,
            "pitched_notes": len(pitched), "offgrid_pitched": offgrid,
            "scale_viol": scale_viol, "chord_viol": chord_viol}


results = {tag: audit(f"{ROOT}/MIDI/{NAME}-{tag}.mid")
           for tag in ("perfect", "humanized", "phase1")}

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag, r in results.items():
    print(f"[{tag:9}] {r}")

for tag in ("perfect", "humanized", "phase1"):
    assert results[tag]["drift_ok"], f"{tag} drift"
assert results["perfect"]["offgrid_pitched"] == 0, "perfect must be grid-locked"
assert results["humanized"]["offgrid_pitched"] > 0, "humanized must show jitter"
assert results["phase1"]["offgrid_pitched"] > 0, "phase1 raw must be off-grid"
# perfect layer: authoritative scale + chord gate (floor t//BAR)
assert results["perfect"]["scale_viol"] == 0, "perfect scale violations"
assert results["perfect"]["chord_viol"] == 0, "perfect chord violations"
# humanized: pitch untouched by humanizer -> scale must stay 0; chord attribution
# via floor t//BAR is intentionally NOT asserted (jittered onsets near bar
# boundaries legitimately cross the floor, matching the 261 reference).
assert results["humanized"]["scale_viol"] == 0, "humanized scale violations"
print("ALL ASSERTIONS PASS")
