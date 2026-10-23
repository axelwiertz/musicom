# -*- coding: utf-8 -*-
"""Read-only verification audit for 260-ambient-phase-drift.

mido READING ONLY (analysis). Checks: zero-drift, 16th-grid lock (perfect==0
off-grid, humanized>0), dorian scale (all pitched pcs in-scale), chord tones
(all pitched notes in their bar's chord). No swing (straight ambient) so the
grid check is plain 16ths.
# READING ONLY (analysis)
"""
import json
import os
import mido  # READING ONLY (analysis)

ROOT = "/opt/data/repos/musicom/projects/Styles/Ambient/260-ambient-phase-drift"
NAME = "260-ambient-phase-drift"
TONIC = 2
DORIAN_OFFS = [0, 2, 3, 5, 7, 9, 10]
SCALE_PCS = set((TONIC + o) % 12 for o in DORIAN_OFFS)
FORM = [("S1", 4), ("S2", 4), ("S3", 4), ("S4", 4), ("S5", 4), ("S6", 4)]
BAR = 1920
N_BARS = 24
CHORD_PCS = {
    "S1": [2, 5, 9, 0], "S2": [0, 4, 7, 11], "S3": [2, 5, 9, 0],
    "S4": [7, 11, 2], "S5": [9, 0, 4], "S6": [2, 5, 9, 0],
}


def section_of_bar(b):
    acc = 0
    for s, n in FORM:
        if acc <= b < acc + n:
            return s
        acc += n
    return FORM[-1][0]


CHORD_BY_BAR = [set(CHORD_PCS[section_of_bar(b)]) for b in range(N_BARS)]


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
                if ch is not None and ch != 9:
                    notes.append({"pitch": m.note, "start_tick": t_abs})
        if ch is not None:
            tracks.append({"channel": ch, "notes": notes, "total_ticks": t_abs})
    return mid, tracks


def audit(path):
    mid, tracks = read_tracks(path)
    lens = [t["total_ticks"] for t in tracks]
    drift_ok = len(set(lens)) == 1 and len(lens) == 5
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    pitched = 0
    for t in tracks:
        for n in t["notes"]:
            st = n["start_tick"]
            if st % 120 != 0:
                offgrid += 1
            pitched += 1
            pc = n["pitch"] % 12
            if pc not in SCALE_PCS:
                scale_viol += 1
            bar = min(st // BAR, N_BARS - 1)
            if pc not in CHORD_BY_BAR[bar]:
                chord_viol += 1
    return {"bytes": os.path.getsize(path), "voice_tracks": len(tracks),
            "voice_len": lens[0] if lens else None, "drift_ok": drift_ok,
            "pitched": pitched, "offgrid": offgrid,
            "scale_viol": scale_viol, "chord_viol": chord_viol}


results = {
    "perfect": audit(f"{ROOT}/MIDI/{NAME}-perfect.mid"),
    "humanized": audit(f"{ROOT}/MIDI/{NAME}-humanized.mid"),
}
with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag, r in results.items():
    print(f"[{tag:9}] {r}")

assert results["perfect"]["drift_ok"] and results["humanized"]["drift_ok"]
assert results["perfect"]["offgrid"] == 0, "perfect must be grid-locked"
assert results["humanized"]["offgrid"] > 0, "humanized must show jitter"
assert results["perfect"]["scale_viol"] == 0
assert results["perfect"]["chord_viol"] == 0
assert results["humanized"]["scale_viol"] == 0
print("ALL ASSERTIONS PASS")
