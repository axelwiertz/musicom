# -*- coding: utf-8 -*-
# READING ONLY (analysis)
"""Audits MIDI for 103-japanese-kojo-koto (READING ONLY).

Verifies:
1. Zero-drift (track tick lengths equal)
2. Grid compliance (16th=120 ticks) for Phase 2 -> must be 0 off-grid
3. Harmony compliance (scale + palette) for Phase 2 -> 0 out-of-scale, 0 out-of-chord
4. Phase 1 raw unquantized fingerprint
"""
import os
import json
import mido

from structures import MusicUnit, MusicEvent

PROJ = "/opt/data/repos/musicom/projects/Styles/Japanese/103-japanese-kojo-koto"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "103-japanese-kojo-koto.mid")
P1_MID = os.path.join(MIDI_DIR, "103-japanese-kojo-koto-phase1.mid")

GRID16 = 120
GRID8 = 240
BAR_TICKS = 1920
TOTAL_TICKS = 46080

# A hirajoshi pentatonic
SCALE_PCS = {9, 10, 2, 4, 7}

PALETTES = {
    "A":  {9, 10, 2, 4},
    "G":  {9, 10, 2, 7},
    "Bb": {10, 2, 4, 7},
    "E":  {9, 10, 4, 7},
}
SECTION_PALETTES = {
    0: ["A", "A", "G", "A"],
    1: ["A", "G", "Bb", "A"],
    2: ["Bb", "G", "E", "Bb"],
    3: ["E", "Bb", "A", "E"],
    4: ["A", "G", "Bb", "A"],
    5: ["A", "E", "A", "A"],
}

def get_palette_at_tick(tick):
    bar_idx = min(tick // BAR_TICKS, 23)
    sec_idx = bar_idx // 4
    bar_in_sec = bar_idx % 4
    pal = SECTION_PALETTES[sec_idx][bar_in_sec]
    return pal, PALETTES[pal]

def parse_events(mid_path):
    mid = mido.MidiFile(mid_path)
    tracks_events = []
    for trk in mid.tracks:
        abs_tick = 0
        notes = []
        open_notes = {}
        for msg in trk:
            abs_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                open_notes[msg.note] = (abs_tick, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in open_notes:
                    st, vel = open_notes.pop(msg.note)
                    notes.append({
                        "pitch": msg.note, "velocity": vel,
                        "start_tick": st, "end_tick": abs_tick,
                        "channel": getattr(msg, 'channel', 0)
                    })
        tracks_events.append((trk.name, abs_tick, notes))
    return tracks_events

def audit_p2():
    tracks = parse_events(P2_MID)
    total_notes = off_grid = out_of_scale = out_of_chord = 0
    track_stats = []

    for trk_name, total_tick, notes in tracks:
        ch = notes[0]["channel"] if notes else -1
        is_drum = (ch == 9)
        t_n = t_off = t_oos = t_ooc = 0
        for n in notes:
            if n["pitch"] == 0:
                continue
            t_n += 1
            total_notes += 1
            st = n["start_tick"]
            if st % GRID16 != 0:
                off_grid += 1
                t_off += 1
            if not is_drum:
                pc = n["pitch"] % 12
                if pc not in SCALE_PCS:
                    out_of_scale += 1
                    t_oos += 1
                _, pal_pcs = get_palette_at_tick(st)
                if pc not in pal_pcs:
                    out_of_chord += 1
                    t_ooc += 1
        track_stats.append({
            "name": trk_name, "channel": ch, "total_tick": total_tick,
            "notes": t_n, "off_grid_16": t_off,
            "out_of_scale": t_oos, "out_of_chord": t_ooc
        })

    return {
        "file": os.path.basename(P2_MID),
        "total_notes": total_notes,
        "off_grid_16": off_grid,
        "out_of_scale": out_of_scale,
        "out_of_chord": out_of_chord,
        "tracks": track_stats,
    }

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
    return {
        "file": os.path.basename(P1_MID),
        "total_notes": total_notes,
        "off_grid_16": off_grid,
        "off_grid_ratio": round(off_grid / max(1, total_notes), 4),
    }

if __name__ == "__main__":
    p2 = audit_p2()
    p1 = audit_p1()

    print("=== Phase 2 Audit ===")
    print(f"Total notes: {p2['total_notes']}")
    print(f"Off 16th-grid: {p2['off_grid_16']}")
    print(f"Out of scale:  {p2['out_of_scale']}")
    print(f"Out of chord:  {p2['out_of_chord']}")
    for t in p2["tracks"]:
        print(f"  {t['name']} (ch{t['channel']}): {t['notes']} notes | "
              f"len={t['total_tick']} | off16={t['off_grid_16']} | "
              f"oos={t['out_of_scale']} | ooc={t['out_of_chord']}")

    print("\n=== Phase 1 Audit ===")
    print(f"Total notes: {p1['total_notes']}")
    print(f"Off 16th-grid: {p1['off_grid_16']} / {p1['total_notes']} "
          f"({p1['off_grid_ratio']*100:.1f}% raw)")

    with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
        json.dump({"phase2": p2, "phase1": p1}, f, indent=2)
    print("\nAudit saved to Analysis/audit.json")
