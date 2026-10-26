# -*- coding: utf-8 -*-
"""Read-only verification for 269-techno-contour-theory. mido READING ONLY.

Checks (real numbers): zero-drift, grid audit (perfect == 0 off-grid,
humanized > 0, phase1 > 0), tiered harmony audit via audit_voice (strict chord
for BOTH perfect and humanized), and the contour-theory contract: phase-1
note pitch classes lie in the A-natural-minor scale (contour rank -> pentatonic
degree mapping).
"""
import json
import os
import mido  # READING ONLY (analysis)
from structures import MusicEvent
from workflows.pitch_audit import audit_voice

ROOT = "/opt/data/projects/Styles/Techno/269-techno-contour-theory"
NAME = "269-techno-contour-theory"
SCALE_PCS = [9, 11, 0, 2, 4, 5, 7]
BAR = 1920
STRONG_GRID = (0, 960)
CHORD_PCS = {0: [9, 0, 4], 1: [5, 9, 0], 2: [7, 11, 2], 3: [9, 0, 4]}
CHORD_BY_BAR = {b: CHORD_PCS[b % 4] for b in range(24)}


def read_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for t in mid.tracks:
        ch = None
        for m in t:
            if m.type == 'program_change':
                ch = m.channel
        if ch is None:
            ch = -1
        t_abs = 0
        onsets = []
        notes = []
        for m in t:
            t_abs += m.time
            if m.type == 'note_on' and m.velocity > 0:
                onsets.append(t_abs)
                if ch != 9:
                    notes.append(MusicEvent(pitch=m.note, volume=m.velocity,
                                            start_tick=t_abs, end_tick=t_abs))
        tracks.append({"channel": ch, "onsets": onsets, "notes": notes,
                       "total_ticks": t_abs})
    return mid, tracks


def audit(path, strict_chord):
    mid, tracks = read_tracks(path)
    voice_tracks = [t for t in tracks if t["channel"] != -1]
    lens = [t["total_ticks"] for t in voice_tracks]
    drift_ok = len(set(lens)) == 1
    offgrid = 0
    harmony = {}
    for t in voice_tracks:
        for n in t["notes"]:
            if not (n.start_tick % 120 == 0 or n.start_tick % 240 == 0):
                offgrid += 1
        r = audit_voice(t["notes"], SCALE_PCS,
                        chord_pcs_by_bar=(CHORD_BY_BAR if strict_chord else None),
                        strong_grid=STRONG_GRID, bar_ticks=BAR, grid=240)
        harmony[f"ch{t['channel']}"] = {
            "n": len(t["notes"]), "passes": r.passes,
            "untagged_out": r.untagged_out_of_scale,
            "non_resolving": r.tagged_non_resolving,
            "strong_viol": r.strong_violations, "collisions": r.collisions,
        }
    return {"bytes": os.path.getsize(path), "drift_ok": drift_ok,
            "voice_len": lens[0] if lens else None,
            "voice_tracks": len(voice_tracks),
            "offgrid": offgrid, "harmony": harmony}


# --- phase-1 contour contract: raw draft off-grid + in-scale ---------------
mid1, tr1 = read_tracks(f"{ROOT}/MIDI/{NAME}-phase1.mid")
raw_notes = [n for t in tr1 if t["channel"] != -1 for n in t["notes"]]
offgrid_p1 = sum(1 for n in raw_notes
                 if not (n.start_tick % 120 == 0 or n.start_tick % 240 == 0))
pc_in_scale = sum(1 for n in raw_notes if n.pitch % 12 in SCALE_PCS)

results = {
    "phase1": {"bytes": os.path.getsize(f"{ROOT}/MIDI/{NAME}-phase1.mid"),
               "pitched": len(raw_notes), "offgrid": offgrid_p1,
               "pc_in_scale": pc_in_scale, "pc_total": len(raw_notes)},
    "perfect": audit(f"{ROOT}/MIDI/{NAME}-perfect.mid", strict_chord=True),
    "humanized": audit(f"{ROOT}/MIDI/{NAME}-humanized.mid", strict_chord=True),
}

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag in ("phase1", "perfect", "humanized"):
    print(f"[{tag:9}] {results[tag]}")
    print()

assert results["phase1"]["bytes"] > 40
assert results["phase1"]["offgrid"] > 0, "phase1 raw must be off-grid"
assert results["phase1"]["pc_in_scale"] == results["phase1"]["pc_total"], \
    "phase1 notes must lie in the A-natural-minor scale"
assert results["perfect"]["bytes"] > 40 and results["humanized"]["bytes"] > 40
assert results["perfect"]["drift_ok"] and results["humanized"]["drift_ok"], "zero-drift"
assert results["perfect"]["offgrid"] == 0, f"perfect offgrid={results['perfect']['offgrid']}"
assert results["humanized"]["offgrid"] > 0, "humanized must show jitter"
for tag in ("perfect", "humanized"):
    for ch, h in results[tag]["harmony"].items():
        assert h["passes"], f"{tag} {ch} harmony audit failed: {h}"
        assert h["untagged_out"] == 0 and h["non_resolving"] == 0 \
            and h["strong_viol"] == 0
print("ALL ASSERTIONS PASS")
print(f"phase1 off-grid={results['phase1']['offgrid']} (>0), "
      f"in-scale={results['phase1']['pc_in_scale']}/{results['phase1']['pc_total']}")
print(f"perfect off-grid={results['perfect']['offgrid']} (0), "
      f"humanized off-grid={results['humanized']['offgrid']} (>0)")
