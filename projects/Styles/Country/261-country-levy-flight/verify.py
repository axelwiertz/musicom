# -*- coding: utf-8 -*-
"""Read-only verification audit for 261-country-levy-flight.

mido READING ONLY (analysis). Checks: zero-drift (all tracks equal length),
16th-grid lock (perfect == 0 off-grid, humanized > 0, phase1 raw), naive
in-scale count (perfect: only the tagged lead ornaments are chromatic — the
authoritative tiered gate is Analysis/pitch_audit.json from compose.py).
"""
import json
import os
import mido  # READING ONLY (analysis)

ROOT = "/opt/data/repos/musicom/projects/Styles/Country/261-country-levy-flight"
NAME = "261-country-levy-flight"
TONIC = 7
SCALE_PCS = set((TONIC + o) % 12 for o in [0, 2, 4, 5, 7, 9, 11])
BAR = 1920
N_BARS = 16
GRID = 120


def read_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for t in mid.tracks:
        ch = None
        for m in t:
            if m.type == "program_change":
                ch = m.channel
        t_abs = 0
        notes = []
        for m in t:
            t_abs += m.time
            if m.type == "note_on" and m.velocity > 0:
                notes.append({"pitch": m.note, "start_tick": t_abs,
                              "channel": ch})
        if ch is not None:
            tracks.append({"channel": ch, "notes": notes, "total_ticks": t_abs})
    return mid, tracks


def audit(path):
    mid, tracks = read_tracks(path)
    lens = [t["total_ticks"] for t in tracks]
    drift_ok = len(lens) > 0 and len(set(lens)) == 1
    pitched_tracks = [t for t in tracks if t["channel"] != 9]
    pitched_onsets = [n["start_tick"] for t in pitched_tracks for n in t["notes"]]
    drum_onsets = [n["start_tick"] for t in tracks if t["channel"] == 9
                   for n in t["notes"]]
    offgrid_pitched = sum(1 for o in pitched_onsets if o % GRID != 0)
    offgrid_drums = sum(1 for o in drum_onsets if o % GRID != 0)
    scale_viol = sum(1 for n in
                     [n for t in pitched_tracks for n in t["notes"]]
                     if n["pitch"] % 12 not in SCALE_PCS)
    return {"bytes": os.path.getsize(path), "voice_tracks": len(tracks),
            "voice_len": lens[0] if lens else None, "drift_ok": drift_ok,
            "pitched_notes": len(pitched_onsets), "drum_notes": len(drum_onsets),
            "offgrid_pitched": offgrid_pitched, "offgrid_drums": offgrid_drums,
            "offgrid_total": offgrid_pitched + offgrid_drums,
            "scale_viol_naive": scale_viol}


results = {tag: audit(f"{ROOT}/MIDI/{NAME}-{tag}.mid")
           for tag in ("perfect", "humanized", "phase1")}

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag, r in results.items():
    print(f"[{tag:9}] {r}")

# authoritative tiered audit (from compose.py) — must be all-passes
with open(f"{ROOT}/Analysis/pitch_audit.json") as f:
    pa = json.load(f)
ornament_count = pa["Lead"]["tagged_ornaments"]
print("tiered pitch audit (authoritative):", {k: (v.get("passes"),
      v["untagged_out_of_scale"], v["tagged_non_resolving"], v["strong_violations"])
      for k, v in pa.items() if isinstance(v, dict) and "passes" in v})

for tag in ("perfect", "humanized", "phase1"):
    assert results[tag]["drift_ok"], f"{tag} drift"
assert results["perfect"]["offgrid_total"] == 0, "perfect must be grid-locked"
assert results["humanized"]["offgrid_total"] > 0, "humanized must show jitter"
# perfect: only the tagged lead ornaments are chromatic (naive scale count)
assert results["perfect"]["scale_viol_naive"] == ornament_count, \
    f"perfect naive scale viol {results['perfect']['scale_viol_naive']} != ornaments {ornament_count}"
# tiered gate: all voices pass
for v, d in pa.items():
    if isinstance(d, dict) and "passes" in d:
        assert d["passes"], f"tiered pitch audit failed for {v}"
print("ALL ASSERTIONS PASS")
