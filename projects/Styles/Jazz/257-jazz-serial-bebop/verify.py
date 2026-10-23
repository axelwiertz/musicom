# -*- coding: utf-8 -*-
"""Read-only verification audit for 257-jazz-serial-bebop. mido READING ONLY.

Checks (real numbers): zero-drift, grid audit (perfect==0 off-grid,
humanized>0), tiered harmony audit via workflows.pitch_audit.audit_voice
(perfect: in-scale+in-chord strict; humanized: in-scale), phase-1 serial
fingerprint (all 12 pitch classes), humanization off-grid proof.
"""
import json
import os
import mido  # READING ONLY (analysis)
from workflows.pitch_audit import audit_voice

ROOT = "/opt/data/projects/Styles/Jazz/257-jazz-serial-bebop"
NAME = "257-jazz-serial-bebop"
TONIC = 5
MAJOR_OFFS = [0, 2, 4, 5, 7, 9, 11]
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in MAJOR_OFFS]
SCALE_PCS = set(SCALE_DEG_PCS)
FORM = [("Intro", 4), ("A1", 8), ("A2", 8), ("B", 8), ("A3", 8)]
N_BARS = 36
BAR = 1920
STRONG_GRID = (0, 960)


def on_grid(st):
    """On-grid for a swing tune: 16th grid (0/120/240/360) OR the swung 8th
    off-beat (320). The ride swings 2:1, so pitched voices that swing land on
    320, not the straight 240."""
    pos = st % 480
    return (pos % 120 == 0) or (pos == 320)


def section_of_bar(b):
    acc = 0
    for sname, nbars in FORM:
        if acc <= b < acc + nbars:
            return sname
        acc += nbars
    return FORM[-1][0]


def chord_pcs(deg, seventh=True):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    return frozenset((TONIC + MAJOR_OFFS[i]) % 12 for i in idx)


# reconstruct CHORD_SPECS (deterministic, no RNG)
CHORD_SPECS = []
SECTION_TICKS = {}
_tick = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _tick)
    _tick += b * BAR
for b in range(N_BARS):
    s = section_of_bar(b)
    bi = b - SECTION_TICKS[s][1] // BAR
    if s == "Intro":
        spec = [0, 5, 1, 4][bi]
    elif s in ("A1", "A2", "A3"):
        spec = [1, 4, 0, 5, 1, 4, 0, 0][bi]
    else:
        spec = [2, 5, 1, 4, 2, 5, 1, 4][bi]
    CHORD_SPECS.append((spec, True))
BAR_PCS = [chord_pcs(*CHORD_SPECS[b]) for b in range(N_BARS)]
CHORD_BY_BAR = {b: sorted(BAR_PCS[b]) for b in range(N_BARS)}


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
        notes = []          # (pitch, start_tick) for pitched voices
        for m in t:
            t_abs += m.time
            if m.type == 'note_on' and m.velocity > 0:
                onsets.append(t_abs)
                if ch != 9:
                    notes.append({"pitch": m.note, "start_tick": t_abs})
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
            st = n["start_tick"]
            if not on_grid(st):
                offgrid += 1
        r = audit_voice(t["notes"], SCALE_DEG_PCS,
                        chord_pcs_by_bar=(CHORD_BY_BAR if strict_chord else None),
                        strong_grid=STRONG_GRID, bar_ticks=BAR, grid=240)
        harmony[f"ch{t['channel']}"] = {
            "audible": r.audible, "strong_ok": r.strong_ok,
            "weak_in_scale": r.weak_in_scale, "tagged": r.tagged_ornaments,
            "untagged_out": r.untagged_out_of_scale,
            "non_resolving": r.tagged_non_resolving,
            "strong_viol": r.strong_violations, "passes": r.passes,
        }
    return {"bytes": os.path.getsize(path), "n_tracks": len(mid.tracks),
            "voice_tracks": len(voice_tracks),
            "voice_len": lens[0] if lens else None,
            "drift_ok": drift_ok, "total_notes": total, "pitched": pitched,
            "offgrid": offgrid, "harmony": harmony}


results = {}
# phase1: raw serial draft — off-grid, chromatic fingerprint (all 12 pcs)
mid1, tr1 = read_tracks(f"{ROOT}/MIDI/{NAME}-phase1.mid")
raw_notes = [n for t in tr1 if t["channel"] != 9 for n in t["notes"]]
raw_pcs = set(n["pitch"] % 12 for n in raw_notes)
serial_ok = raw_pcs == set(range(12))
offgrid_p1 = sum(1 for n in raw_notes
                 if not (n["start_tick"] % 120 == 0 or n["start_tick"] % 240 == 0))
results["phase1"] = {
    "bytes": os.path.getsize(f"{ROOT}/MIDI/{NAME}-phase1.mid"),
    "serial_all_12_pcs": serial_ok, "serial_ok": serial_ok,
    "raw_pc_count": len(raw_pcs),
    "offgrid": offgrid_p1, "pitched": len(raw_notes),
}
results["perfect"] = audit(f"{ROOT}/MIDI/{NAME}-perfect.mid", strict_chord=True)
results["humanized"] = audit(f"{ROOT}/MIDI/{NAME}-humanized.mid", strict_chord=False)

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag in ("phase1", "perfect", "humanized"):
    r = results[tag]
    print(f"[{tag:9}] {r}")
    print()

# assertions
assert results["phase1"]["bytes"] > 40
assert results["perfect"]["bytes"] > 40 and results["humanized"]["bytes"] > 40
assert results["phase1"]["serial_ok"], "phase1 must contain all 12 pitch classes"
assert results["phase1"]["offgrid"] > 0, "phase1 raw must be off-grid"
assert results["perfect"]["drift_ok"] and results["humanized"]["drift_ok"]
assert results["perfect"]["offgrid"] == 0, "perfect offgrid must be 0"
assert results["humanized"]["offgrid"] > 0, "humanized must show jitter"
for ch, h in results["perfect"]["harmony"].items():
    assert h["passes"], f"perfect {ch} harmony audit failed: {h}"
    assert h["untagged_out"] == 0 and h["non_resolving"] == 0 and h["strong_viol"] == 0
for ch, h in results["humanized"]["harmony"].items():
    assert h["passes"], f"humanized {ch} harmony audit failed: {h}"
    assert h["untagged_out"] == 0 and h["non_resolving"] == 0
print("ALL ASSERTIONS PASS")
print(f"serial fingerprint: phase1 all-12-pcs={serial_ok} ({len(raw_pcs)} pcs)")
print(f"perfect off-grid={results['perfect']['offgrid']} (0 required), "
      f"humanized off-grid={results['humanized']['offgrid']} (>0 required)")
