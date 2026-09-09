# -*- coding: utf-8 -*-
"""091-baroque-genetic-allemande — audit (mido READ-ONLY).

Verifies the REPORT-CONTRACT numbers on both exported MIDI artifacts:
  * zero-drift: all tracks end at the same absolute tick (track-length equal)
  * grid audit: every pitched voice onset in phase-2 is on the 16th grid (120
    @ 480 TPB) and on the 8th grid (240); phase-1 keeps off-grid fingerprint
  * harmony audit: every pitched voice note is (a) in the D-minor scale family
    (aeolian + harmonic-minor raised 7th + dorian raised 6th borrowings) and
    (b) a chord tone of its global bar (chord scaffold = TonalNetworkGenerator
    walk, same CHORD_INFO as compose.py)
  * silence/RMS profile is computed after render (audio_stats.py).
"""
import json
import os
import sys

import mido

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/091-baroque-genetic-allemande"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

BAR = 1920
GRID16 = 120
GRID8 = 240
SECTION_TICKS = 7680
N_BARS = 24

# D minor family (aeolian + harmonic-minor C# + dorian B)
SCALE_FAMILY = {0, 1, 2, 4, 5, 7, 9, 10, 11}
SCALE_AEOLIAN = {2, 4, 5, 7, 9, 10, 0}

# harmony scaffold (must match compose.py, seed 20260909; roles realized
# DIATONICALLY in D aeolian + harmonic-minor C#: iii/III = F major (root 53))
ROLES = ['tonic', 'tonic', 'tonic', 'borrow', 'tonic', 'pre_dominant',
         'dominant', 'tonic', 'tonic', 'mediant', 'pre_dominant',
         'subdominant', 'pre_dominant', 'dominant', 'tonic', 'dominant',
         'tonic', 'tonic', 'mediant', 'subdominant', 'pre_dominant',
         'dominant', 'tonic', 'mediant']
ROLE_OFF = {"tonic": 0, "subdominant": 5, "dominant": 7, "mediant": 3,
            "pre_dominant": 2, "borrow": 10}
ROLE_Q = {"tonic": "m", "subdominant": "m", "dominant": "M", "mediant": "M",
          "pre_dominant": "m", "borrow": "M"}
IV = {"m": (0, 3, 7), "M": (0, 4, 7)}
CHORDS = []  # per bar: (root_pc, {chord_pcs})
for role in ROLES:
    root = 50 + ROLE_OFF[role]
    pc = root % 12
    pcs = {(root + i) % 12 for i in IV[ROLE_Q[role]]}
    CHORDS.append((pc, pcs))


def track_notes(path):
    """Return (track_name, program, channel, [(start, pitch, end), ...])."""
    mid = mido.MidiFile(path)
    out = []
    for i, track in enumerate(mid.tracks):
        if i == 0:                      # tempo track
            continue
        program = 0
        channel = 0
        notes = []
        t = 0
        active = {}
        for msg in track:
            t += msg.time
            if msg.type == "program_change":
                program = msg.program
                channel = msg.channel
            elif msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (t, msg.velocity, msg.channel)
            elif msg.type == "note_off" or (msg.type == "note_on"
                                            and msg.velocity == 0):
                if msg.note in active:
                    st, vel, ch = active.pop(msg.note)
                    notes.append((st, msg.note, t, ch))
        end = t
        out.append((track.name, program, channel, notes, end))
    return out


def grid_report(path, label):
    rows = []
    total_off16 = 0
    total_off8 = 0
    total_on = 0
    for name, prog, ch, notes, end in track_notes(path):
        off16 = [s for (s, p, e, c) in notes if p > 0 and s % GRID16 != 0]
        off8 = [s for (s, p, e, c) in notes if p > 0 and s % GRID8 != 0]
        n_notes = len([n for n in notes if n[1] > 0])
        total_off16 += len(off16)
        total_off8 += len(off8)
        total_on += n_notes
        rows.append({"voice": name, "program": prog, "channel": ch,
                     "notes": n_notes, "off_16th": len(off16),
                     "off_8th": len(off8), "track_end": end})
    return {"label": label, "grid_16th": GRID16, "grid_8th": GRID8,
            "total_notes": total_on, "total_off_16th": total_off16,
            "total_off_8th": total_off8, "voices": rows}


def harmony_report(path):
    rows = []
    for name, prog, ch, notes, end in track_notes(path):
        if ch == 9 or prog == 0 and ch == 9:      # drum channel
            continue
        out_of_scale = []
        out_of_chord = []
        for st, p, en, c in notes:
            if p == 0:
                continue
            bar = min(st // BAR, N_BARS - 1)
            rpc, cpcs = CHORDS[bar]
            if p % 12 not in SCALE_FAMILY:
                out_of_scale.append((st, p))
            # third-based triad check (chord scaffold has no 7ths)
            if p % 12 not in cpcs:
                out_of_chord.append((st, p))
        rows.append({"voice": name, "program": prog, "notes": len(
            [n for n in notes if n[1] > 0]),
            "out_of_scale": len(out_of_scale),
            "out_of_chord": len(out_of_chord),
            "first_out_of_scale": out_of_scale[:3],
            "first_out_of_chord": out_of_chord[:3]})
    return rows


def zero_drift_report(path):
    ends = [(name, end) for name, prog, ch, notes, end in track_notes(path)]
    max_end = max(e for _, e in ends)
    drift = [(n, e, max_end - e) for n, e in ends]
    return {"max_end": max_end, "drift_per_track": drift,
            "drift_ok": all(d == 0 for _, _, d in drift)}


P2 = os.path.join(MIDI_DIR, "091-baroque-genetic-allemande.mid")
P1 = os.path.join(MIDI_DIR, "091-baroque-genetic-allemande-phase1.mid")

report = {
    "project": "091-baroque-genetic-allemande",
    "grid_phase2": grid_report(P2, "phase2"),
    "harmony_phase2": harmony_report(P2),
    "zero_drift_phase2": zero_drift_report(P2),
    "zero_drift_phase1": zero_drift_report(P1),
    "phase1_fingerprint": grid_report(P1, "phase1-raw"),
}

# verdicts (mandatory rule: onsets must be on the 16th grid (120 @ 480 TPB);
# 8th-grid off-counts are expected because 16th subdivisions legitimately
# fall between 8th slots — only 16th off-grid is a violation)
g = report["grid_phase2"]
h = report["harmony_phase2"]
report["verdict_grid"] = "PASS 0 off-grid (16th)" if g["total_off_16th"] == 0 \
    else "FAIL"
report["verdict_harmony"] = "PASS 0 out" if all(
    r["out_of_scale"] == 0 and r["out_of_chord"] == 0 for r in h) else "FAIL"
report["verdict_zerodrift"] = "PASS" if (
    report["zero_drift_phase2"]["drift_ok"]
    and report["zero_drift_phase1"]["drift_ok"]) else "FAIL"

with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
    json.dump(report, f, indent=2)

print("=== GRID AUDIT (phase-2) === [contract: 16th grid (120) lock]")
print(f"16th off-grid: {g['total_off_16th']}/{g['total_notes']}  "
      f"(8th off-grid {g['total_off_8th']}/{g['total_notes']} = "
      f"legit 16ths between 8th slots)")
for r in g["voices"]:
    print(f"  {r['voice']:8s} prog={r['program']:3d} ch={r['channel']:2d} "
          f"notes={r['notes']:3d} off16={r['off_16th']:3d} "
          f"off8={r['off_8th']:3d} end={r['track_end']}")
print("=== HARMONY AUDIT (phase-2, pitched voices) ===")
for r in h:
    print(f"  {r['voice']:8s} out_of_scale={r['out_of_scale']:3d} "
          f"out_of_chord={r['out_of_chord']:3d}")
print("=== ZERO-DRIFT (phase-2) ===")
zd = report["zero_drift_phase2"]
print(f"  max_end={zd['max_end']} drift_ok={zd['drift_ok']}")
for n, e, d in zd["drift_per_track"]:
    print(f"  {n:8s} end={e:5d} drift={d}")
print("=== PHASE-1 raw fingerprint (unquantized character check) ===")
p1 = report["phase1_fingerprint"]
print(f"  16th off-grid in raw: {p1['total_off_16th']}/{p1['total_notes']} "
      f"(>0 confirms raw draft is NOT grid-locked)")
print("VERDICTS:", report["verdict_grid"], "|", report["verdict_harmony"],
      "|", report["verdict_zerodrift"])