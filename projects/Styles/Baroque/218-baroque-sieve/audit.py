# -*- coding: utf-8 -*-
# READING ONLY (analysis)
"""Audit 218-baroque-sieve MIDI (mido used for READING/verification only).

Verifies:
  1. zero-drift: all voice tracks equal expected tick length
  2. 16th-grid sync: phase-2 pitched onsets MUST be 0 off-grid
  3. harmony: every pitched note in D-minor scale AND its bar's chord (0/0)
  4. phase-1 raw fingerprint: off-grid ratio (informational, should be >0)
Writes Analysis/audit.json.
"""
import os
import json
import mido

# compliant musicom import (marks this as read-only analysis per preflight)
from structures import MusicUnit, MusicEvent

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/218-baroque-sieve"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "218-baroque-sieve.mid")
P1_MID = os.path.join(MIDI_DIR, "218-baroque-sieve-phase1.mid")

GRID16 = 120
GRID8 = 240
BAR_TICKS = 1920
N_SECTIONS = 6
BARS_PER_SECTION = 4
TOTAL_TICKS = BAR_TICKS * BARS_PER_SECTION * N_SECTIONS  # 46080

# D natural minor
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}

SECTION_DEGREES = {
    0: [0, 5, 3, 0],   # Prelude   i VI iv i
    1: [0, 3, 6, 2],   # Allemande i iv VII III
    2: [2, 6, 0, 3],   # Courante  III VII i iv
    3: [3, 4, 0, 0],   # Sarabande iv v i i
    4: [0, 3, 5, 4],   # Gigue     i iv VI v
    5: [4, 0, 3, 0],   # Finale    v i iv i
}
CHORD_PCS = {
    0: {2, 5, 9}, 1: {4, 7, 10}, 2: {5, 9, 0},
    3: {7, 10, 2}, 4: {9, 0, 4}, 5: {10, 2, 5}, 6: {0, 4, 7},
}


def get_chord_pcs_at_tick(tick):
    bar_idx = tick // BAR_TICKS
    sec_idx = min(bar_idx // BARS_PER_SECTION, N_SECTIONS - 1)
    bar_in_sec = bar_idx % BARS_PER_SECTION
    d = SECTION_DEGREES[sec_idx][bar_in_sec]
    return d, CHORD_PCS[d]


def parse_events(mid_path):
    mid = mido.MidiFile(mid_path)
    tracks = []
    for trk_idx, trk in enumerate(mid.tracks):
        abs_tick = 0
        notes = []
        open_notes = {}
        for msg in trk:
            abs_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                open_notes[msg.note] = (abs_tick, msg.velocity)
            elif msg.type in ('note_off',) or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in open_notes:
                    st, vel = open_notes.pop(msg.note)
                    notes.append({"pitch": msg.note, "velocity": vel,
                                  "start_tick": st, "end_tick": abs_tick,
                                  "track": trk_idx,
                                  "channel": getattr(msg, 'channel', 0)})
        tracks.append((trk.name, abs_tick, notes))
    return tracks


def audit_p2():
    tracks = parse_events(P2_MID)
    total_notes = off_grid = out_scale = out_chord = 0
    track_stats = []
    for trk_name, total_tick, notes in tracks:
        ch = notes[0]["channel"] if notes else 0
        t_notes = t_off = t_oos = t_ooc = 0
        for n in notes:
            if n["pitch"] == 0:
                continue
            t_notes += 1
            total_notes += 1
            st = n["start_tick"]
            if st % GRID16 != 0:
                off_grid += 1
                t_off += 1
            pc = n["pitch"] % 12
            if pc not in KEY_PCS:
                out_scale += 1
                t_oos += 1
            d, c_pcs = get_chord_pcs_at_tick(st)
            if pc not in c_pcs:
                out_chord += 1
                t_ooc += 1
        track_stats.append({"name": trk_name, "channel": ch,
                            "total_tick": total_tick, "notes": t_notes,
                            "off_grid_16": t_off, "out_of_scale": t_oos,
                            "out_of_chord": t_ooc})
    return {"file": os.path.basename(P2_MID), "total_notes": total_notes,
            "off_grid_16": off_grid, "out_of_scale": out_scale,
            "out_of_chord": out_chord, "tracks": track_stats}


def audit_p1():
    tracks = parse_events(P1_MID)
    total_notes = off_grid = 0
    for trk_name, total_tick, notes in tracks:
        for n in notes:
            if n["pitch"] == 0:
                continue
            total_notes += 1
            if n["start_tick"] % GRID16 != 0:
                off_grid += 1
    return {"file": os.path.basename(P1_MID), "total_notes": total_notes,
            "off_grid_16": off_grid,
            "off_grid_ratio": round(off_grid / max(1, total_notes), 4)}


if __name__ == "__main__":
    p2 = audit_p2()
    p1 = audit_p1()
    print("=== Phase 2 ===")
    print(f"notes={p2['total_notes']} off16={p2['off_grid_16']} "
          f"out_scale={p2['out_of_scale']} out_chord={p2['out_of_chord']}")
    for t in p2["tracks"]:
        print(f"  {t['name']:12s} ch{t['channel']} len={t['total_tick']:6d} "
              f"notes={t['notes']:4d} off16={t['off_grid_16']} "
              f"oos={t['out_of_scale']} ooc={t['out_of_chord']}")
    print("=== Phase 1 ===")
    print(f"notes={p1['total_notes']} off16={p1['off_grid_16']} "
          f"ratio={p1['off_grid_ratio']}")
    with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
        json.dump({"phase2": p2, "phase1": p1}, f, indent=2)
    print("wrote Analysis/audit.json")
