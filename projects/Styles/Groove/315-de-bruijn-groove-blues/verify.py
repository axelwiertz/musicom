# -*- coding: utf-8 -*-
# READING ONLY (analysis) -- read-only mido audits of the exported MIDIs
# (315 de Bruijn groove blues). mido used for reading only, never authoring.
import json
import os
import mido

from workflows.pitch_audit import audit_voice

PROJ = "315-de-bruijn-groove-blues"
BASE = "/opt/data/projects/Styles/Groove/" + PROJ
MIDI_DIR = os.path.join(BASE, "MIDI")

TONIC_PC = 4                        # E
INTERVALS = [0, 2, 3, 5, 7, 8, 10]
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}

BAR_DEGREES = [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]
TOTAL_BARS = len(BAR_DEGREES)
BAR = 1920
STRONG = (0, 960)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


CHORD_PCS_BY_BAR = {b: chord_pcs(BAR_DEGREES[b]) for b in range(TOTAL_BARS)}


def read_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for tr in mid.tracks[1:]:
        notes = []
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                notes.append({"pitch": m.note, "start_tick": t,
                              "end_tick": t + 100, "channel": m.channel})
        tracks.append(notes)
    lengths = [sum(m.time for m in tr) for tr in mid.tracks[1:]]
    return tracks, lengths


def grid_audit(notes):
    off120 = sum(1 for n in notes if n["start_tick"] % 120 != 0)
    off240 = sum(1 for n in notes if n["start_tick"] % 240 != 0)
    return off120, off240, len(notes)


def audit(path):
    tracks, lengths = read_tracks(path)
    drift_ok = len(set(lengths)) == 1
    track_len = lengths[0] if drift_ok else lengths
    all_notes = [n for tr in tracks for n in tr]
    off120, off240, total = grid_audit(all_notes)
    voice_audits = {}
    for i, tr in enumerate(tracks):
        pitched = [n for n in tr if n["channel"] != 9]
        if not pitched:
            continue
        r = audit_voice(pitched, KEY_PCS, chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                        strong_grid=STRONG, bar_ticks=BAR, grid=240)
        voice_audits[f"voice{i}"] = {
            "notes": r.audible,
            "untagged_out_of_scale": r.untagged_out_of_scale,
            "tagged_non_resolving": r.tagged_non_resolving,
            "strong_violations": r.strong_violations,
            "passes": r.passes,
        }
    scale_viol = sum(v["untagged_out_of_scale"] for v in voice_audits.values())
    non_resolving = sum(v["tagged_non_resolving"] for v in voice_audits.values())
    strong_viol = sum(v["strong_violations"] for v in voice_audits.values())
    return {
        "tracks": len(tracks),
        "track_len": track_len,
        "zero_drift": drift_ok,
        "pitched": sum(1 for n in all_notes if n["channel"] != 9),
        "drum": sum(1 for n in all_notes if n["channel"] == 9),
        "off120": off120, "off240": off240,
        "scale_violations": scale_viol,
        "non_resolving": non_resolving,
        "strong_violations": strong_viol,
        "voice_audits": voice_audits,
    }


report = {}
for ver in ("phase1", "perfect", "humanized"):
    p = os.path.join(MIDI_DIR, PROJ + "-" + ver + ".mid")
    assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"
    report[ver] = audit(p)

perf = report["perfect"]
hum = report["humanized"]

assert perf["zero_drift"], "perfect zero-drift FAILED"
assert hum["zero_drift"], "humanized zero-drift FAILED"
assert report["phase1"]["zero_drift"], "phase1 zero-drift FAILED"

assert perf["off120"] == 0, f"perfect off-grid != 0 ({perf['off120']})"
assert perf["scale_violations"] == 0, "perfect untagged out-of-scale != 0"
assert perf["non_resolving"] == 0, "perfect non-resolving != 0"
assert perf["strong_violations"] == 0, "perfect strong violations != 0"

assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized untagged out-of-scale != 0"
assert hum["non_resolving"] == 0, "humanized non-resolving != 0"
assert hum["strong_violations"] == 0, "humanized strong violations != 0"

out = {"project": PROJ, "report": report, "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
