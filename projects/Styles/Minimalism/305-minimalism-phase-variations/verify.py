# -*- coding: utf-8 -*-
# READING ONLY (analysis) — read-only mido audits of the exported MIDIs.
import json
import os
import mido

PROJ = "305-minimalism-phase-variations"
BASE = "/opt/data/projects/Styles/Minimalism/" + PROJ
MIDI_DIR = os.path.join(BASE, "MIDI")

KEY_PCS = {0, 2, 4, 5, 7, 9, 11}    # C major
INTERVALS = [0, 2, 4, 5, 7, 9, 11]
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 7), 3: (0, 4, 7),
           4: (0, 4, 7), 5: (0, 3, 7), 6: (0, 3, 6)}

SECTIONS = [
    ("Intro", 2, [0, 0]),
    ("Phase1", 4, [0, 0, 0, 0]),
    ("Phase2", 4, [0, 3, 0, 5]),
    ("Phase3", 4, [0, 4, 0, 3]),
    ("Phase4", 4, [0, 1, 4, 0]),
    ("Phase5", 4, [5, 4, 1, 5]),
    ("Bridge", 4, [5, 1, 5, 0]),
    ("Phase6", 2, [4, 5]),
    ("Resolve", 2, [0, 0]),
    ("Coda", 2, [0, 0]),
]
BAR_DEGREES = []
for name, bars, prog in SECTIONS:
    BAR_DEGREES.extend(prog)
TOTAL_BARS = len(BAR_DEGREES)
BAR = 1920
STRONG = (0, 960)


def chord_pcs(d):
    root_pc = (0 + INTERVALS[d]) % 12
    return {((root_pc + iv) % 12) for iv in QUALITY[d]}


def audit(path):
    mid = mido.MidiFile(path)
    lengths = []
    for tr in mid.tracks[1:]:
        lengths.append(sum(m.time for m in tr))
    drift_ok = len(set(lengths)) == 1
    track_len = lengths[0] if drift_ok else lengths

    off120 = off240 = 0
    scale_viol = 0
    chord_viol = 0
    strong_viol = 0
    pitched = 0
    drum = 0
    for tr in mid.tracks[1:]:
        t = 0
        for m in tr:
            t += m.time
            if m.type != "note_on" or m.velocity == 0:
                continue
            if m.channel == 9:
                drum += 1
                continue
            pitched += 1
            if t % 120 != 0:
                off120 += 1
            if t % 240 != 0:
                off240 += 1
            pc = m.note % 12
            bar = min(t // BAR, TOTAL_BARS - 1)
            in_scale = pc in KEY_PCS
            in_chord = pc in chord_pcs(BAR_DEGREES[bar])
            if not in_scale:
                scale_viol += 1
            if not in_chord:
                chord_viol += 1
            if (t % BAR) in STRONG and not (in_scale and in_chord):
                strong_viol += 1
    return {
        "tracks": len(mid.tracks) - 1,
        "track_len": track_len,
        "zero_drift": drift_ok,
        "pitched": pitched,
        "drum": drum,
        "off120": off120,
        "off240": off240,
        "scale_violations": scale_viol,
        "chord_violations_blanket": chord_viol,
        "strong_beat_violations": strong_viol,
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

assert perf["off120"] == 0, f"perfect off-grid != 0 ({perf['off120']})"
assert perf["scale_violations"] == 0, "perfect scale violations != 0"
assert perf["chord_violations_blanket"] == 0, "perfect chord violations != 0"

assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized scale violations != 0"
assert hum["strong_beat_violations"] == 0, "humanized strong-beat violations != 0"

out = {"project": PROJ, "report": report, "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
