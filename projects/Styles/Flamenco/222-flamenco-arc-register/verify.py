# -*- coding: utf-8 -*-
"""Read-only verification for 222-flamenco-arc-register.

mido used READING ONLY (analysis). Verifies zero-drift, 16th-grid compliance,
scale (E flamenco composite) membership, and per-bar Andalusian-cadence chord
membership for every pitched voice.
"""
import os
import json
import mido  # READING ONLY (analysis)

# musicom engine reference — this file is a READ-ONLY audit (never authors MIDI).
from structures import MusicUnit  # noqa: F401

PROJ = "/opt/data/repos/musicom/projects/Styles/Flamenco/222-flamenco-arc-register"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

BAR = 1920
GRID16 = 120
GRID8 = 240

SCALE_PCS = {4, 5, 7, 8, 9, 11, 0, 2}   # E flamenco composite

CHORD_PCS = {
    0: {9, 0, 4},    # Am
    1: {7, 11, 2},   # G
    2: {5, 9, 0},    # F
    3: {4, 8, 11},   # E
}
SECTION_DEGREES = {
    0: [0, 1, 2, 3],  # Entrada
    1: [0, 1, 2, 3],  # Letra
    2: [0, 2, 1, 3],  # Falseta
    3: [0, 1, 0, 3],  # Cumbre
    4: [2, 1, 0, 3],  # Bajada
    5: [2, 1, 0, 3],  # Cierre
}


def chord_pcs_at(bar_idx):
    sec_idx = min(bar_idx // 4, 5)
    bar_in_sec = bar_idx % 4
    deg = SECTION_DEGREES[sec_idx][bar_in_sec]
    return CHORD_PCS[deg]


def track_channel(track):
    for m in track:
        if m.type in ("note_on", "note_off", "program_change"):
            return m.channel
    return None


def audit(mid_path):
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
                if not is_drums:
                    total_pitched += 1
                    if m.note % 12 not in SCALE_PCS:
                        out_scale += 1
                        t_oos += 1
                    bar_idx = min(abs_tick // BAR, 23)
                    if m.note % 12 not in chord_pcs_at(bar_idx):
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
    p1 = audit(os.path.join(MIDI_DIR, "222-flamenco-arc-register-phase1.mid"))
    p2 = audit(os.path.join(MIDI_DIR, "222-flamenco-arc-register.mid"))

    sizes = {}
    for p in [os.path.join(MIDI_DIR, "222-flamenco-arc-register.mid"),
              os.path.join(MIDI_DIR, "222-flamenco-arc-register-phase1.mid")]:
        sizes[os.path.basename(p)] = os.path.getsize(p)
        assert os.path.getsize(p) > 40, p
    if os.path.isdir(AUDIO_DIR):
        for f in sorted(os.listdir(AUDIO_DIR)):
            fp = os.path.join(AUDIO_DIR, f)
            if os.path.isfile(fp) and f.endswith((".wav", ".ogg")):
                sizes[f] = os.path.getsize(fp)
                assert os.path.getsize(fp) > 40, fp

    out = {"project": "222-flamenco-arc-register",
           "audit": {"phase1": p1, "phase2": p2},
           "sizes": sizes}
    with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
        json.dump(out, f, indent=2)

    print("=== PHASE 2 ===")
    print(f"tracks={p2['n_tracks']} lengths={p2['lengths']} zero_drift={p2['zero_drift']}")
    print(f"total_notes={p2['total_notes']} pitched={p2['pitched_onsets']} "
          f"off16={p2['off_grid_16']} off8={p2['off_grid_8']} "
          f"out_scale={p2['out_of_scale']} out_chord={p2['out_of_chord']}")
    for t in p2["tracks"]:
        print(f"  {t['name']} ch{t['channel']} len={t['length']} notes={t['notes']} "
              f"off16={t['off16']} off8={t['off8']} oos={t['out_of_scale']} ooc={t['out_of_chord']}")

    print("\n=== PHASE 1 (raw) ===")
    print(f"tracks={p1['n_tracks']} lengths={p1['lengths']} zero_drift={p1['zero_drift']}")
    print(f"total_notes={p1['total_notes']} off16={p1['off_grid_16']} off8={p1['off_grid_8']}")

    print("\nSIZES:", sizes)
