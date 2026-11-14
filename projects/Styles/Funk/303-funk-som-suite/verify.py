# -*- coding: utf-8 -*-
# READING ONLY (analysis) — read-only mido audits of the exported MIDIs.
import json
import os
import mido

PROJ = "303-funk-som-suite"
BASE = "/opt/data/projects/Styles/Funk/" + PROJ
MIDI_DIR = os.path.join(BASE, "MIDI")

KEY_PCS = {5, 7, 8, 10, 0, 1, 3}      # F natural minor

PROG = [
    (5, 'm'), (5, 'm'), (10, 'm'), (0, 'm'),
    (5, 'm'), (1, 'M'), (10, 'm'), (0, 'm'),
    (5, 'm'), (8, 'M'), (3, 'M'), (10, 'm'),
    (1, 'M'), (3, 'M'), (5, 'm'), (0, 'm'),
    (10, 'm'), (5, 'm'), (1, 'M'), (0, 'm'),
    (5, 'm'), (8, 'M'), (3, 'M'), (10, 'm'),
    (1, 'M'), (3, 'M'), (5, 'm'), (5, 'm'),
    (5, 'm'), (1, 'M'), (0, 'm'), (5, 'm'),
]
TOTAL_BARS = len(PROG)
BAR = 1920
STRONG = (0, 960)


def chord_pcs(r, q):
    iv = (0, 3, 7) if q == 'm' else (0, 4, 7)
    return {(r + i) % 12 for i in iv}


BAR_PCS = [chord_pcs(r, q) for r, q in PROG]


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
            in_chord = pc in BAR_PCS[bar]
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
assert perf["strong_beat_violations"] == 0, "perfect strong-beat violations != 0"

assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized scale violations != 0 (%s)" % hum["scale_violations"]
assert hum["strong_beat_violations"] == 0, "humanized strong-beat violations != 0 (%s)" % hum["strong_beat_violations"]

out = {"project": PROJ, "report": report, "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
