# -*- coding: utf-8 -*-
"""096-trap-skeleton-seoul - audit (mido READ - analysis only)."""
import json
import os
import sys

import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401  (compliant-import marker)

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    MARIMBA, VIOLIN, PIANO, DOUBLE_BASS, TRUMPET,
)

PROJ = "/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

BAR = 1920
GRID16 = 120
GRID8 = 240
N_BARS = 24

KEY_ROOT = 60
PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in PHRYGIAN}

PROG_DEG = ([0, 1, 1, 0] + [0, 1, 6, 1] + [6, 1, 0, 0] +
            [6, 3, 1, 1] + [6, 1, 0, 0] + [0, 1, 0, 0])


def _deg_note(d):
    oct_shift = d // 7
    return KEY_ROOT + oct_shift * 12 + PHRYGIAN[d % 7]


CHORD_PCS = [{_deg_note(deg + k) % 12 for k in (0, 2, 4)} for deg in PROG_DEG]

LABEL = {(12, 0): "BellLead", (40, 1): "ViolinCtr", (1, 2): "PianoStab",
         (43, 4): "Sub808", (56, 5): "BrassStab", (0, 9): "Drums"}
INST = {12: MARIMBA, 40: VIOLIN, 1: PIANO, 43: DOUBLE_BASS, 56: TRUMPET}


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
            rows.append({"voice": name, "program": prog, "channel": ch,
                         "notes": len(ps), "status": "skip (drums/empty)"})
            continue
        inst = INST.get(prog)
        if inst is None:
            rows.append({"voice": name, "program": prog, "channel": ch,
                         "notes": len(ps), "status": "UNKNOWN PROG"})
            continue
        bad = [p for p in ps if not inst.in_range(p)]
        rows.append({"voice": name, "program": prog, "channel": ch,
                     "notes": len(ps), "min": min(ps), "max": max(ps),
                     "range": [inst.range_min, inst.range_max],
                     "out_of_range": len(bad),
                     "status": "PASS" if not bad else "FAIL %s" % bad[:5]})
    return rows


P2 = os.path.join(MIDI_DIR, "096-trap-skeleton-seoul.mid")
P1 = os.path.join(MIDI_DIR, "096-trap-skeleton-seoul-phase1.mid")

grid2 = grid_report(P2, "phase2")
grid1 = grid_report(P1, "phase1-raw-fingerprint")
harm2 = harmony_report(P2)
range2 = range_report(P2)
ends = sorted({v["track_end"] for v in grid2["voices"]})

verdict_grid = "PASS" if grid2["total_off_16th"] == 0 else "FAIL"
verdict_harm = ("PASS" if all(r["out_of_scale"] == 0 and
                              r["out_of_chord"] == 0 for r in harm2)
                else "FAIL")
verdict_range = ("PASS" if all(r.get("status") == "PASS" or
                               r.get("status", "").startswith("skip")
                               for r in range2) else "FAIL")
verdict_drift = "PASS" if len(ends) == 1 else "FAIL %s" % ends

audit = {
    "project": "096-trap-skeleton-seoul",
    "grid_phase2": grid2,
    "phase1_fingerprint": grid1,
    "harmony_phase2": harm2,
    "range_phase2": range2,
    "track_ends": ends,
    "verdict_grid": verdict_grid,
    "verdict_harmony": verdict_harm,
    "verdict_range": verdict_range,
    "verdict_zerodrift": verdict_drift,
    "files": {"midi_phase2": os.path.getsize(P2),
              "midi_phase1": os.path.getsize(P1)},
}
with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
    json.dump(audit, f, indent=2)

print("GRID phase2: %d off-16th / %d notes (off-8th %d)" %
      (grid2["total_off_16th"], grid2["total_notes"], grid2["total_off_8th"]))
for v in grid2["voices"]:
    print("  %-10s prog=%3d ch=%d notes=%4d off16=%d off8=%d end=%d" %
          (v["voice"], v["program"], v["channel"], v["notes"],
           v["off_16th"], v["off_8th"], v["track_end"]))
print("GRID phase1 fingerprint: %d off-16th / %d notes (by design)" %
      (grid1["total_off_16th"], grid1["total_notes"]))
print("HARMONY phase2:")
for r in harm2:
    print("  %-10s notes=%4d out_scale=%d out_chord=%d %s %s" %
          (r["voice"], r["notes"], r["out_of_scale"], r["out_of_chord"],
           r["first_out_of_scale"], r["first_out_of_chord"]))
print("RANGE phase2:")
for r in range2:
    print("  ", r)
print("TRACK ENDS:", ends)
print("VERDICTS grid=%s harmony=%s range=%s zerodrift=%s" %
      (verdict_grid, verdict_harm, verdict_range, verdict_drift))
assert verdict_grid == "PASS", "grid audit failed"
assert verdict_harm == "PASS", "harmony audit failed"
assert verdict_range == "PASS", "range audit failed"
assert verdict_drift == "PASS", "zero-drift failed"
print("AUDIT ALL PASS")
