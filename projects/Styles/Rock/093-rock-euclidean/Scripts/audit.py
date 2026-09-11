# -*- coding: utf-8 -*-
"""093-rock-euclidean - audit (mido READ - analysis only).

READING ONLY (analysis): verifies the REPORT-CONTRACT numbers on both exported
MIDI artifacts:
  * zero-drift: every track ends at the same absolute tick
  * grid audit: every pitched voice onset in phase 2 is locked to the 16th grid
    (120 @ 480 TPB); phase 1 keeps its off-grid raw fingerprint
  * harmony audit: every pitched voice note is in the E-aeolian scale AND a
    chord tone of its bar (same degree table as compose.py)
  * range audit: every pitch inside its instrument registry range
"""
import json
import os
import sys

import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401  (compliant-import marker)

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    FIDDLE, ACOUSTIC_GUITAR, PIANO, ORGAN, DOUBLE_BASS,
)

PROJ = "/opt/data/repos/musicom/projects/Styles/Rock/093-rock-euclidean"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

BAR = 1920
GRID16 = 120
GRID8 = 240
N_BARS = 24

KEY_ROOT = 64
AEOLIAN = [0, 2, 3, 5, 7, 8, 10]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in AEOLIAN}

PROG_DEG = ([0, 0, 5, 6] + [0, 5, 2, 6] + [5, 6, 0, 0] +
            [3, 5, 2, 6] + [5, 6, 0, 0] + [0, 0, 5, 0])


def _deg_note(d):
    oct_shift = d // 7
    return KEY_ROOT + oct_shift * 12 + AEOLIAN[d % 7]


CHORD_PCS = [{_deg_note(deg + k) % 12 for k in (0, 2, 4)} for deg in PROG_DEG]

LABEL = {(110, 0): "Lead(fiddle)", (25, 1): "Guitar", (1, 2): "Piano",
         (19, 3): "Organ", (43, 4): "Bass", (0, 9): "Drums"}
INST = {110: FIDDLE, 25: ACOUSTIC_GUITAR, 1: PIANO, 19: ORGAN,
        43: DOUBLE_BASS}


def track_notes(path):
    mid = mido.MidiFile(path)
    out = []
    for i, track in enumerate(mid.tracks):
        if i == 0:
            continue
        program, channel = 0, 0
        notes, t, active = [], 0, {}
        for msg in track:
            t += msg.time
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
            elif msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (t, msg.velocity, msg.channel)
            elif msg.type == "note_off" or (msg.type == "note_on"
                                            and msg.velocity == 0):
                if msg.note in active:
                    st, vel, ch = active.pop(msg.note)
                    notes.append((st, msg.note, t, ch))
        out.append((track.name or LABEL.get((program, channel), "track%d" % i),
                    program, channel, notes, t))
    return out


def grid_report(path, label):
    rows, off16, off8, total = [], 0, 0, 0
    for name, prog, ch, notes, end in track_notes(path):
        o16 = [s for (s, p, e, c) in notes if p > 0 and s % GRID16 != 0]
        o8 = [s for (s, p, e, c) in notes if p > 0 and s % GRID8 != 0]
        n = len([x for x in notes if x[1] > 0])
        off16 += len(o16)
        off8 += len(o8)
        total += n
        rows.append({"voice": name, "program": prog, "channel": ch, "notes": n,
                     "off_16th": len(o16), "off_8th": len(o8),
                     "first_off_16th": o16[:4], "track_end": end})
    return {"label": label, "grid_16th": GRID16, "grid_8th": GRID8,
            "total_notes": total, "total_off_16th": off16,
            "total_off_8th": off8, "voices": rows}


def harmony_report(path):
    rows = []
    for name, prog, ch, notes, end in track_notes(path):
        if ch == 9:
            continue
        out_scale, out_chord = [], []
        for st, p, en, c in notes:
            if p == 0:
                continue
            bar = min(st // BAR, N_BARS - 1)
            if p % 12 not in SCALE_PCS:
                out_scale.append((st, p))
            if p % 12 not in CHORD_PCS[bar]:
                out_chord.append((st, p))
        rows.append({"voice": name, "program": prog,
                     "notes": len([x for x in notes if x[1] > 0]),
                     "out_of_scale": len(out_scale),
                     "out_of_chord": len(out_chord),
                     "first_out_of_scale": out_scale[:3],
                     "first_out_of_chord": out_chord[:3]})
    return rows


def range_report(path):
    rows = []
    for name, prog, ch, notes, end in track_notes(path):
        ps = [p for (s, p, e, c) in notes if p > 0]
        if ch == 9 or not ps:
            continue
        inst = INST.get(prog)
        rows.append({"voice": name, "instrument":
                     inst.gm_name if inst else str(prog),
                     "min": min(ps), "max": max(ps),
                     "range": [inst.range_min, inst.range_max] if inst else None,
                     "in_range": all(inst.in_range(p) for p in ps)
                     if inst else None})
    return rows


def zero_drift_report(path):
    ends = [(name, end) for name, prog, ch, notes, end in track_notes(path)]
    max_end = max(e for _, e in ends)
    drift = [(n, e, max_end - e) for n, e in ends]
    return {"max_end": max_end, "drift_per_track": drift,
            "drift_ok": all(d == 0 for _, _, d in drift)}


P2 = os.path.join(MIDI_DIR, "093-rock-euclidean.mid")
P1 = os.path.join(MIDI_DIR, "093-rock-euclidean-phase1.mid")

report = {
    "project": "093-rock-euclidean",
    "grid_phase2": grid_report(P2, "phase2"),
    "harmony_phase2": harmony_report(P2),
    "range_phase2": range_report(P2),
    "zero_drift_phase2": zero_drift_report(P2),
    "zero_drift_phase1": zero_drift_report(P1),
    "phase1_fingerprint": grid_report(P1, "phase1-raw"),
}

g, h = report["grid_phase2"], report["harmony_phase2"]
report["verdict_grid"] = ("PASS 0 off-grid (16th)"
                          if g["total_off_16th"] == 0 else "FAIL")
report["verdict_harmony"] = ("PASS 0 out"
                             if all(r["out_of_scale"] == 0
                                    and r["out_of_chord"] == 0 for r in h)
                             else "FAIL")
report["verdict_range"] = ("PASS"
                           if all(r["in_range"] for r in report["range_phase2"])
                           else "FAIL")
report["verdict_zerodrift"] = ("PASS" if (
    report["zero_drift_phase2"]["drift_ok"]
    and report["zero_drift_phase1"]["drift_ok"]) else "FAIL")

with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
    json.dump(report, f, indent=2)

print("=== GRID AUDIT (phase-2) === [contract: 16th grid (120) lock]")
print("16th off-grid: %d/%d  (8th off-grid %d/%d = legit 16ths)"
      % (g["total_off_16th"], g["total_notes"], g["total_off_8th"],
         g["total_notes"]))
for r in g["voices"]:
    print("  %-14s prog=%3d ch=%2d notes=%3d off16=%3d off8=%3d end=%d"
          % (r["voice"], r["program"], r["channel"], r["notes"],
             r["off_16th"], r["off_8th"], r["track_end"]))
print("=== HARMONY AUDIT (phase-2, pitched voices) ===")
for r in h:
    print("  %-14s out_of_scale=%3d out_of_chord=%3d"
          % (r["voice"], r["out_of_scale"], r["out_of_chord"]))
print("=== RANGE AUDIT (phase-2, instrument registry) ===")
for r in report["range_phase2"]:
    print("  %-14s %-24s min=%d max=%d range=%s in_range=%s"
          % (r["voice"], r["instrument"], r["min"], r["max"], r["range"],
             r["in_range"]))
print("=== ZERO-DRIFT ===")
for lbl, key in (("phase-2", "zero_drift_phase2"),
                 ("phase-1", "zero_drift_phase1")):
    zd = report[key]
    print("  %s: max_end=%d drift_ok=%s" % (lbl, zd["max_end"],
                                            zd["drift_ok"]))
print("=== PHASE-1 raw fingerprint ===")
p1 = report["phase1_fingerprint"]
print("  16th off-grid in raw: %d/%d (>0 confirms raw draft is NOT grid-locked)"
      % (p1["total_off_16th"], p1["total_notes"]))
print("VERDICTS:", report["verdict_grid"], "|", report["verdict_harmony"],
      "|", report["verdict_range"], "|", report["verdict_zerodrift"])
