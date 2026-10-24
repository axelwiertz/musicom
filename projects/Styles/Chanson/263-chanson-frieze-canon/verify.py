# -*- coding: utf-8 -*-
"""Read-only verification audit for 263-chanson-frieze-canon. mido READING ONLY.

Checks (real numbers): zero-drift, grid audit (perfect==0 off-grid,
humanized>0, phase1 off-grid), tiered harmony audit via
workflows.pitch_audit.audit_voice (perfect: in-scale + in-chord strict;
humanized: in-scale), phase-1 chromatic fingerprint (off-scale pcs present),
humanization off-grid proof.
"""
import json
import os
import mido  # READING ONLY (analysis)
from structures import MusicEvent
from workflows.pitch_audit import audit_voice

ROOT = "/opt/data/projects/Styles/Chanson/263-chanson-frieze-canon"
NAME = "263-chanson-frieze-canon"
TONIC = 2
NAT = [0, 2, 4, 5, 7, 9, 11]
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in NAT]
SCALE_PCS = set(SCALE_DEG_PCS)
FORM = [("Intro", 4), ("Verse", 8), ("Chorus", 8),
        ("Verse2", 8), ("Chorus2", 8), ("Outro", 4)]
N_BARS = 40
BAR = 1920
STRONG_GRID = (0, 960)

CHORD_DEG = (
    [0, 3, 1, 4]
    + [0, 5, 3, 4, 0, 5, 1, 4]
    + [3, 4, 0, 5, 3, 4, 0, 0]
    + [0, 5, 3, 4, 0, 5, 1, 4]
    + [3, 4, 0, 5, 3, 4, 0, 0]
    + [3, 4, 0, 0]
)


def deg_pc(d):
    return (TONIC + NAT[d % 7]) % 12


def chord_pcs_deg(d):
    return frozenset(deg_pc((d + k) % 7) for k in (0, 2, 4, 6))


CHORD_BY_BAR = {b: sorted(chord_pcs_deg(CHORD_DEG[b])) for b in range(N_BARS)}


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
    pitched = 0
    total = 0
    harmony = {}
    for t in voice_tracks:
        if t["channel"] == 9:
            total += len(t["onsets"])
            continue
        total += len(t["onsets"])
        pitched += len(t["notes"])
        for n in t["notes"]:
            st = n.start_tick
            if not (st % 120 == 0 or st % 240 == 0):
                offgrid += 1
        r = audit_voice(t["notes"], SCALE_DEG_PCS,
                        chord_pcs_by_bar=(CHORD_BY_BAR if strict_chord else None),
                        strong_grid=STRONG_GRID, bar_ticks=BAR, grid=240)
        harmony[f"ch{t['channel']}"] = {
            "audible": r.audible, "strong_ok": r.strong_ok,
            "weak_in_scale": r.weak_in_scale, "tagged": r.tagged_ornaments,
            "untagged_out": r.untagged_out_of_scale,
            "non_resolving": r.tagged_non_resolving,
            "strong_viol": r.strong_violations, "collisions": r.collisions,
            "passes": r.passes,
        }
    return {"bytes": os.path.getsize(path), "n_tracks": len(mid.tracks),
            "voice_tracks": len(voice_tracks),
            "voice_len": lens[0] if lens else None,
            "drift_ok": drift_ok, "total_notes": total, "pitched": pitched,
            "offgrid": offgrid, "harmony": harmony}


results = {}
mid1, tr1 = read_tracks(f"{ROOT}/MIDI/{NAME}-phase1.mid")
raw_notes = [n for t in tr1 if t["channel"] != 9 for n in t["notes"]]
raw_pcs = set(n.pitch % 12 for n in raw_notes)
offscale_p1 = sorted(pc for pc in raw_pcs if pc not in SCALE_PCS)
chromatic_ok = len(offscale_p1) > 0
offgrid_p1 = sum(1 for n in raw_notes
                 if not (n.start_tick % 120 == 0 or n.start_tick % 240 == 0))
results["phase1"] = {
    "bytes": os.path.getsize(f"{ROOT}/MIDI/{NAME}-phase1.mid"),
    "pitched": len(raw_notes),
    "distinct_pcs": len(raw_pcs),
    "offscale_pcs": offscale_p1,
    "chromatic_ok": chromatic_ok,
    "offgrid": offgrid_p1,
}
results["perfect"] = audit(f"{ROOT}/MIDI/{NAME}-perfect.mid", strict_chord=True)
results["humanized"] = audit(f"{ROOT}/MIDI/{NAME}-humanized.mid", strict_chord=False)

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag in ("phase1", "perfect", "humanized"):
    print(f"[{tag:9}] {results[tag]}")
    print()

assert results["phase1"]["bytes"] > 40
assert results["perfect"]["bytes"] > 40 and results["humanized"]["bytes"] > 40
assert results["phase1"]["offgrid"] > 0, "phase1 raw must be off-grid"
assert results["phase1"]["chromatic_ok"], "phase1 must contain off-scale pcs"
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
print(f"phase1 off-scale pcs={offscale_p1} ({len(raw_pcs)} distinct pcs)")
print(f"perfect off-grid={results['perfect']['offgrid']} (0 required), "
      f"humanized off-grid={results['humanized']['offgrid']} (>0 required)")
