# -*- coding: utf-8 -*-
# READING ONLY (analysis) — read-only mido audits of the exported MIDIs.
import json
import os
import mido

PROJ = "301-country-hope-rework"
BASE = "/opt/data/projects/Styles/Country/" + PROJ
MIDI_DIR = os.path.join(BASE, "MIDI")

KEY_PCS = {7, 9, 11, 0, 2, 4, 6}      # G major

CHORD_PCS = {
    "G":  {7, 11, 2},
    "C":  {0, 4, 7},
    "D":  {2, 6, 9},
    "Em": {4, 7, 11},
    "Am": {9, 0, 4},
}

SECTIONS = [
    ("Intro",   2, ["G", "C"]),
    ("Verse",   4, ["G", "C", "G", "D"]),
    ("Chorus",  4, ["C", "G", "D", "G"]),
    ("Verse2",  4, ["Em", "Em", "C", "D"]),
    ("Bridge",  4, ["C", "Am", "D", "G"]),
    ("Outro",   2, ["D", "G"]),
]
BAR_KEYS = []
for name, bars, prog in SECTIONS:
    for b in range(bars):
        BAR_KEYS.append(prog[b])
TOTAL_BARS = len(BAR_KEYS)
BAR = 1920
STRONG = (0, 960)


def audit(path):
    mid = mido.MidiFile(path)
    lengths = []
    for tr in mid.tracks[1:]:
        lengths.append(sum(m.time for m in tr if not m.is_meta))
    drift_ok = len(set(lengths)) == 1
    track_len = lengths[0] if drift_ok else lengths

    off120 = 0
    scale_viol = 0
    chord_viol = 0
    strong_viol = 0
    pitched = 0
    drum = 0
    for tr in mid.tracks[1:]:
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
            if m.type != "note_on" or m.velocity == 0:
                continue
            if m.channel == 9:
                drum += 1
                continue
            pitched += 1
            if t % 120 != 0:
                off120 += 1
            pc = m.note % 12
            bar = min(t // BAR, TOTAL_BARS - 1)
            in_scale = pc in KEY_PCS
            in_chord = pc in CHORD_PCS[BAR_KEYS[bar]]
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
        "scale_violations": scale_viol,
        "chord_violations_blanket": chord_viol,
        "strong_beat_violations": strong_viol,
    }


report = {}
for ver in ("phase1", "perfect", "humanized"):
    p = os.path.join(MIDI_DIR, PROJ + "-" + ver + ".mid")
    assert os.path.getsize(p) > 40, "empty/corrupt: %s" % p
    report[ver] = audit(p)

perf = report["perfect"]
hum = report["humanized"]

assert perf["zero_drift"], "perfect zero-drift FAILED"
assert hum["zero_drift"], "humanized zero-drift FAILED"

assert perf["off120"] == 0, "perfect off-grid != 0 (%s)" % perf["off120"]
assert perf["scale_violations"] == 0, "perfect scale violations != 0 (%s)" % perf["scale_violations"]
assert perf["chord_violations_blanket"] == 0, "perfect chord violations != 0 (%s)" % perf["chord_violations_blanket"]

assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized scale violations != 0 (%s)" % hum["scale_violations"]
assert hum["strong_beat_violations"] == 0, "humanized strong-beat violations != 0 (%s)" % hum["strong_beat_violations"]

out = {"project": PROJ, "report": report, "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
