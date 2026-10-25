# -*- coding: utf-8 -*-
"""Read-only verification for 266-pop-subset-walker. mido READING ONLY.

Checks (real numbers): zero-drift, grid audit (perfect==0 off-grid,
humanized>0, phase1 off-grid), tiered harmony audit via audit_voice, AND the
abstract-layer contract: phase-1 note pcs lie inside the walked subset of their
bar (the ABS-002 walk is directly audible as harmony colour) + walk validity
(starts/ends on tonic, contains the V7->I cadence).
"""
import json
import os
import mido  # READING ONLY (analysis)
from structures import MusicEvent
from workflows.pitch_audit import audit_voice

ROOT = "/opt/data/projects/Styles/Pop/266-pop-subset-walker"
NAME = "266-pop-subset-walker"
TONIC = 0
SCALE_PCS = [0, 2, 4, 5, 7, 9, 11]
N_BARS = 24
BAR = 1920
STRONG_GRID = (0, 960)

summary = json.load(open(f"{ROOT}/Analysis/summary.json"))
WALK = summary["walk"]
CHORD_BY_BAR = {i: d["pcs"] for i, d in enumerate(summary["walk_detail"])}


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


# --- abstract-layer contract: phase-1 pcs inside walked subset --------------
mid1, tr1 = read_tracks(f"{ROOT}/MIDI/{NAME}-phase1.mid")
raw_notes = [n for t in tr1 if t["channel"] != -1 for n in t["notes"]]
offgrid_p1 = sum(1 for n in raw_notes
                 if not (n.start_tick % 120 == 0 or n.start_tick % 240 == 0))
pc_in_subset = 0
pc_total = 0
for n in raw_notes:
    bar = min(n.start_tick // BAR, N_BARS - 1)
    subset_pcs = set(CHORD_BY_BAR[bar])
    pc_total += 1
    if n.pitch % 12 in subset_pcs:
        pc_in_subset += 1


# walk validity
walk_ok = (WALK[0] == "maj0" and WALK[-1] == "maj0"
           and WALK[-2:] == ["dom77", "maj0"] and len(WALK) == N_BARS)

results = {
    "phase1": {"bytes": os.path.getsize(f"{ROOT}/MIDI/{NAME}-phase1.mid"),
               "pitched": len(raw_notes), "offgrid": offgrid_p1,
               "pc_in_subset": pc_in_subset, "pc_total": pc_total,
               "pc_in_subset_ratio": round(pc_in_subset / max(pc_total, 1), 4)},
    "walk": {"walk": WALK, "walk_ok": walk_ok,
             "n_bars": len(WALK), "cadence": WALK[-2:]},
    "perfect": audit(f"{ROOT}/MIDI/{NAME}-perfect.mid", strict_chord=True),
    "humanized": audit(f"{ROOT}/MIDI/{NAME}-humanized.mid", strict_chord=False),
}

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag in ("phase1", "walk", "perfect", "humanized"):
    print(f"[{tag:9}] {results[tag]}")
    print()

assert results["phase1"]["bytes"] > 40
assert results["perfect"]["bytes"] > 40 and results["humanized"]["bytes"] > 40
assert results["phase1"]["offgrid"] > 0, "phase1 raw must be off-grid"
assert results["phase1"]["pc_in_subset_ratio"] > 0.99, \
    "phase1 notes must lie in the walked subset"
assert results["walk"]["walk_ok"], "walk must start/end tonic + V7->I cadence"
assert results["perfect"]["drift_ok"] and results["humanized"]["drift_ok"], "zero-drift"
assert results["perfect"]["offgrid"] == 0, f"perfect offgrid={results['perfect']['offgrid']}"
assert results["humanized"]["offgrid"] > 0, "humanized must show jitter"
for ch, h in results["perfect"]["harmony"].items():
    assert h["passes"], f"perfect {ch} harmony audit failed: {h}"
    assert h["untagged_out"] == 0 and h["non_resolving"] == 0 and h["strong_viol"] == 0
for ch, h in results["humanized"]["harmony"].items():
    assert h["passes"], f"humanized {ch} harmony audit failed: {h}"
    assert h["untagged_out"] == 0 and h["non_resolving"] == 0
print("ALL ASSERTIONS PASS")
print(f"walk: {' '.join(WALK)}")
print(f"phase1 off-grid={results['phase1']['offgrid']} (>0 required), "
      f"pc-in-subset={results['phase1']['pc_in_subset_ratio']}")
print(f"perfect off-grid={results['perfect']['offgrid']} (0 required), "
      f"humanized off-grid={results['humanized']['offgrid']} (>0 required)")
