# -*- coding: utf-8 -*-
"""Read-only verification audit for 265-baroque-counter-duet. mido READING ONLY.

Checks (real numbers): zero-drift, grid audit (perfect==0 off-grid,
humanized>0, phase1 off-grid), tiered harmony audit via audit_voice, PLUS the
counter-axis contract: contrast (counter never sounds the lead's pitch class
simultaneously) + complementary density (no onset collision with lead).
"""
import json
import os
import mido  # READING ONLY (analysis)
from structures import MusicEvent
from workflows.pitch_audit import audit_voice

ROOT = "/opt/data/projects/Styles/Baroque/265-baroque-counter-duet"
NAME = "265-baroque-counter-duet"
TONIC = 2
NAT = [0, 2, 4, 5, 7, 9, 11]
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in NAT]
SCALE_PCS = set(SCALE_DEG_PCS)
N_BARS = 16
BAR = 1920
STRONG_GRID = (0, 960)

CHORD_DEG = (
    [0, 4, 5, 3] + [1, 4, 0, 4] + [5, 3, 1, 4] + [0, 3, 4, 0]
)


def deg_pc(d):
    return (TONIC + NAT[d % 7]) % 12


def chord_pcs_deg(d):
    return frozenset(deg_pc((d + k) % 7) for k in (0, 2, 4))


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
        # carry note end_tick from note_off for contrast window
        tracks.append({"channel": ch, "onsets": onsets, "notes": notes,
                       "total_ticks": t_abs})
    return mid, tracks


def note_windows(path):
    """Full (start,end) note windows per channel, for the contrast check."""
    mid = mido.MidiFile(path)
    ch_notes = {}
    for t in mid.tracks:
        ch = None
        for m in t:
            if m.type == 'program_change':
                ch = m.channel
        if ch is None:
            continue
        t_abs = 0
        active = {}
        for m in t:
            t_abs += m.time
            if m.type == 'note_on' and m.velocity > 0:
                active[m.note] = t_abs
            elif m.type == 'note_off' or (m.type == 'note_on' and m.velocity == 0):
                st = active.pop(m.note, None)
                if st is not None:
                    ch_notes.setdefault(ch, []).append((st, t_abs, m.note))
        for n, st in active.items():
            ch_notes.setdefault(ch, []).append((st, t_abs, n))
    return ch_notes


def audit(path, strict_chord):
    mid, tracks = read_tracks(path)
    voice_tracks = [t for t in tracks if t["channel"] != -1]
    lens = [t["total_ticks"] for t in voice_tracks]
    drift_ok = len(set(lens)) == 1
    offgrid = 0
    harmony = {}
    for t in voice_tracks:
        ch = t["channel"]
        for n in t["notes"]:
            if not (n.start_tick % 120 == 0 or n.start_tick % 240 == 0):
                offgrid += 1
        # counter (ch1) is a contrapuntal voice -> in-scale audit only (the
        # engine's counterline contract). Lead/harp/cello = strict in-chord.
        strict = strict_chord and ch != 1
        r = audit_voice(t["notes"], SCALE_DEG_PCS,
                        chord_pcs_by_bar=(CHORD_BY_BAR if strict else None),
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


def counter_contract(path):
    """Contrast + complementary density between lead (ch0) and counter (ch1)."""
    ch_notes = note_windows(path)
    lead = sorted(ch_notes.get(0, []))
    ctr = sorted(ch_notes.get(1, []))
    lead_onsets = {st for st, _, _ in lead}
    ctr_onsets = {st for st, _, _ in ctr}
    density_collision = len(lead_onsets & ctr_onsets)
    pc_doubling = 0
    for st, en, pc in ctr:
        sounding = {lp % 12 for ls, le, lp in lead if ls <= st < le}
        if (pc % 12) in sounding:
            pc_doubling += 1
    return {"lead_notes": len(lead), "counter_notes": len(ctr),
            "onset_collisions": density_collision, "pc_doubling": pc_doubling}


results = {}
mid1, tr1 = read_tracks(f"{ROOT}/MIDI/{NAME}-phase1.mid")
raw_notes = [n for t in tr1 if t["channel"] != -1 for n in t["notes"]]
raw_pcs = set(n.pitch % 12 for n in raw_notes)
offscale_p1 = sorted(pc for pc in raw_pcs if pc not in SCALE_PCS)
chromatic_ok = len(offscale_p1) > 0
offgrid_p1 = sum(1 for n in raw_notes
                 if not (n.start_tick % 120 == 0 or n.start_tick % 240 == 0))
results["phase1"] = {"bytes": os.path.getsize(f"{ROOT}/MIDI/{NAME}-phase1.mid"),
                     "pitched": len(raw_notes), "distinct_pcs": len(raw_pcs),
                     "offscale_pcs": offscale_p1, "chromatic_ok": chromatic_ok,
                     "offgrid": offgrid_p1}

results["perfect"] = audit(f"{ROOT}/MIDI/{NAME}-perfect.mid", strict_chord=True)
results["humanized"] = audit(f"{ROOT}/MIDI/{NAME}-humanized.mid", strict_chord=False)
results["counter_contract"] = counter_contract(f"{ROOT}/MIDI/{NAME}-perfect.mid")

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

for tag in ("phase1", "perfect", "humanized", "counter_contract"):
    print(f"[{tag:16}] {results[tag]}")
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
cc = results["counter_contract"]
assert cc["onset_collisions"] == 0, "counter doubles a lead onset (density)"
assert cc["pc_doubling"] == 0, "counter sounds the lead's pitch class (contrast)"
print("ALL ASSERTIONS PASS")
print(f"phase1 off-scale pcs={offscale_p1} ({len(raw_pcs)} distinct)")
print(f"perfect off-grid={results['perfect']['offgrid']} (0 required), "
      f"humanized off-grid={results['humanized']['offgrid']} (>0 required)")
print(f"counter: {cc['counter_notes']} notes, "
      f"{cc['onset_collisions']} onset collisions, {cc['pc_doubling']} pc doublings")
