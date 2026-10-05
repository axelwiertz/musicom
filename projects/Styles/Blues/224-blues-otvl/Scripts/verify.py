# -*- coding: utf-8 -*-
"""Read-only verification for 224-blues-otvl.

mido used READING ONLY (analysis). Verifies zero-drift, 16th/8th-grid
compliance, E-blues scale membership, and per-bar 12-bar-blues chord membership
for every pitched voice. Drums (channel 9) are excluded from harmony checks.
"""
import os
import json
import mido  # READING ONLY (analysis)

# musicom engine reference — this file is a READ-ONLY audit (never authors MIDI).
from structures import MusicUnit  # noqa: F401

PROJ = "/opt/data/repos/musicom/projects/Styles/Blues/224-blues-otvl"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

BAR = 1920
GRID16 = 120
GRID8 = 240
N_BARS = 24

SCALE_PCS = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11}   # E blues tonality (excludes C, F)

CHORD_PCS = {
    0: {4, 8, 11, 2, 7, 10},    # I7  E7
    1: {9, 1, 4, 7, 3},         # IV7 A7
    2: {11, 3, 6, 9, 2},        # V7  B7
}
# 12-bar blues x2:  I I I I | IV IV I I | V IV I I
PROG_DEG = [0, 0, 0, 0, 1, 1, 0, 0, 2, 1, 0, 0,
            0, 0, 0, 0, 1, 1, 0, 0, 2, 1, 0, 0]


def chord_pcs_at(bar_idx):
    return CHORD_PCS[PROG_DEG[min(bar_idx, N_BARS - 1)]]


def track_channel(track):
    for m in track:
        if m.type in ("note_on", "note_off", "program_change"):
            return m.channel
    return None


def audit(mid_path, check_harmony=True):
    mid = mido.MidiFile(mid_path)
    voice_tracks = mid.tracks[1:]
    lengths = [sum(m.time for m in t) for t in voice_tracks]
    zero_drift = len(set(lengths)) == 1
    channels = [track_channel(t) for t in voice_tracks]

    total_pitched = 0
    off16 = 0
    off8 = 0
    out_scale = 0
    out_chord = 0
    per_track = []

    for ti, t in enumerate(voice_tracks):
        is_drums = channels[ti] == 9
        abs_tick = 0
        t_notes = 0
        t_off16 = 0
        t_off8 = 0
        t_oos = 0
        t_ooc = 0
        for m in t:
            abs_tick += m.time
            if m.type == "note_on" and m.velocity > 0:
                if m.note == 0:
                    continue
                t_notes += 1
                if abs_tick % GRID16 != 0:
                    off16 += 1
                    t_off16 += 1
                if abs_tick % GRID8 != 0:
                    off8 += 1
                    t_off8 += 1
                if not is_drums and check_harmony:
                    total_pitched += 1
                    if m.note % 12 not in SCALE_PCS:
                        out_scale += 1
                        t_oos += 1
                    if m.note % 12 not in chord_pcs_at(abs_tick // BAR):
                        out_chord += 1
                        t_ooc += 1
        per_track.append({
            "name": t.name or f"track{ti}",
            "channel": channels[ti],
            "length": lengths[ti],
            "notes": t_notes,
            "off16": t_off16,
            "off8": t_off8,
            "out_of_scale": t_oos,
            "out_of_chord": t_ooc,
        })

    return {
        "n_tracks": len(voice_tracks),
        "lengths": lengths,
        "zero_drift": zero_drift,
        "total_notes": sum(p["notes"] for p in per_track),
        "pitched_onsets": total_pitched,
        "off_grid_16": off16,
        "off_grid_8": off8,
        "out_of_scale": out_scale,
        "out_of_chord": out_chord,
        "tracks": per_track,
    }


if __name__ == "__main__":
    p2 = audit(os.path.join(MIDI_DIR, "224-blues-otvl.mid"))
    p1 = audit(os.path.join(MIDI_DIR, "224-blues-otvl-phase1.mid"), check_harmony=False)

    sizes = {}
    for f in os.listdir(MIDI_DIR):
        fp = os.path.join(MIDI_DIR, f)
        if os.path.isfile(fp) and f.endswith(".mid"):
            sizes[f] = os.path.getsize(fp)
            assert os.path.getsize(fp) > 40, fp

    out = {"project": "224-blues-otvl",
           "audit": {"phase1": p1, "phase2": p2},
           "sizes": sizes}
    with open(os.path.join(ANALYSIS_DIR, "verify.json"), "w") as f:
        json.dump(out, f, indent=2)

    print("=== PHASE 2 ===")
    print(f"tracks={p2['n_tracks']} lengths={p2['lengths']} zero_drift={p2['zero_drift']}")
    print(f"total_notes={p2['total_notes']} pitched={p2['pitched_onsets']} "
          f"off16={p2['off_grid_16']} off8={p2['off_grid_8']} "
          f"out_scale={p2['out_of_scale']} out_chord={p2['out_of_chord']}")
    for t in p2["tracks"]:
        print(f"  {t['name']:8s} ch{t['channel']} len={t['length']} notes={t['notes']} "
              f"off16={t['off16']} off8={t['off8']} oos={t['out_of_scale']} ooc={t['out_of_chord']}")

    print("\n=== PHASE 1 (raw) ===")
    print(f"tracks={p1['n_tracks']} lengths={p1['lengths']} zero_drift={p1['zero_drift']}")
    print(f"total_notes={p1['total_notes']} off16={p1['off_grid_16']} off8={p1['off_grid_8']}")

    print("\nSIZES:", sizes)

    # Gate assertions
    assert p2["zero_drift"], "phase2 zero-drift FAIL"
    assert p1["zero_drift"], "phase1 zero-drift FAIL"
    assert p2["off_grid_16"] == 0 and p2["off_grid_8"] == 0, "phase2 off-grid FAIL"
    assert p2["out_of_scale"] == 0, "phase2 out-of-scale FAIL"
    assert p2["out_of_chord"] == 0, "phase2 out-of-chord FAIL"
    print("\nALL GATES PASS")
