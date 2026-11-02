# -*- coding: utf-8 -*-
# READING ONLY (analysis) — read-only mido audits of the exported MIDIs.
import json
import os
import mido

PROJ = "280-ambient-pareto-variations"
BASE = "/opt/data/projects/Styles/Ambient/" + PROJ
MIDI_DIR = os.path.join(BASE, "MIDI")

KEY_PCS = {2, 4, 5, 7, 9, 10, 0}    # D Aeolian
INTERVALS = [0, 2, 3, 5, 7, 8, 10]
QUALITY = {0: (0, 3, 7), 1: (0, 3, 6), 2: (0, 4, 7), 3: (0, 3, 7),
           4: (0, 3, 7), 5: (0, 4, 7), 6: (0, 4, 7)}

SECTIONS = [
    ("Intro", 4, [0, 0, 5, 5]),
    ("Build", 8, [0, 5, 6, 5, 3, 0, 5, 6]),
    ("Rise", 8, [3, 4, 5, 6, 3, 4, 0, 6]),
    ("Peak", 8, [0, 5, 3, 4, 5, 6, 0, 0]),
    ("Bridge", 8, [5, 5, 0, 3, 5, 6, 0, 3]),
    ("Resolve", 4, [0, 0, 5, 0]),
    ("Coda", 4, [0, 0, 0, 0]),
]
BAR_DEGREES = []
for name, bars, prog in SECTIONS:
    BAR_DEGREES.extend(prog)
TOTAL_BARS = len(BAR_DEGREES)
BAR = 1920
STRONG = (0, 960)                  # beats 1 & 3


def chord_pcs(d):
    root_pc = (2 + INTERVALS[d]) % 12
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
    chord_viol = 0      # blanket per-bar chord attribution
    strong_viol = 0     # strong beats not in scale+chord
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

# zero-drift: all voice tracks equal length (both versions)
assert perf["zero_drift"], "perfect zero-drift FAILED"
assert hum["zero_drift"], "humanized zero-drift FAILED"

# perfect layer: grid-locked, key + chord clean
assert perf["off120"] == 0, f"perfect off-grid != 0 ({perf['off120']})"
assert perf["scale_violations"] == 0, "perfect scale violations != 0"
assert perf["chord_violations_blanket"] == 0, "perfect chord violations != 0"

# humanized layer: jitter ran (off-grid > 0), pitch still key-clean
assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized scale violations != 0"
assert hum["strong_beat_violations"] == 0, "humanized strong-beat violations != 0"

out = {"project": PROJ, "report": report, "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
