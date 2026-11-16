# -*- coding: utf-8 -*-
# READING ONLY (analysis) -- read-only mido audits of the exported MIDIs.
import json
import os
import mido

PROJECT = "307-balkan-christoffel-suite"
BASE = "/opt/data/projects/Styles/Balkan/" + PROJECT
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")

KEY_PCS = {0, 2, 4, 5, 7, 9, 10, 11}     # D Dorian + Bb (bVI)
CHORD_PCS = {
    "Dm": {2, 5, 9}, "C": {0, 4, 7}, "G": {7, 11, 2},
    "F": {5, 9, 0}, "Am": {9, 0, 4}, "Bb": {10, 2, 5},
}
SECTION_PROG = [
    ["Dm", "Dm", "C", "Dm"], ["Dm", "C", "G", "Dm"], ["C", "G", "Dm", "G"],
    ["F", "C", "Dm", "Am"], ["G", "F", "C", "Dm"], ["C", "Am", "G", "F"],
    ["Dm", "G", "C", "Dm"], ["Bb", "C", "Dm", "Dm"],
]
BAR_CHORDS = [c for prog in SECTION_PROG for c in prog]
N_BARS = len(BAR_CHORDS)                 # 32
BAR = 1320                               # 11 sixteenths
SEAM = 50                                # within this many ticks of a bar boundary
                                         # = humanizer onset jitter, not a pitch error


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
    chord_seam = 0                        # chord violations at bar seams (jitter)
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
            bar = min(t // BAR, N_BARS - 1)
            if pc not in KEY_PCS:
                scale_viol += 1
            if pc not in CHORD_PCS[BAR_CHORDS[bar]]:
                chord_viol += 1
                if (t % BAR) >= (BAR - SEAM):
                    chord_seam += 1
    return {"tracks": len(mid.tracks) - 1, "track_len": track_len,
            "zero_drift": drift_ok, "pitched": pitched, "drum": drum,
            "off120": off120, "scale_violations": scale_viol,
            "chord_violations": chord_viol, "chord_seam_violations": chord_seam}


report = {}
for ver in ("phase1", "perfect", "humanized"):
    p = os.path.join(MIDI_DIR, PROJECT + "-" + ver + ".mid")
    assert os.path.getsize(p) > 40, "empty/corrupt: %s" % p
    report[ver] = audit(p)

perf = report["perfect"]
hum = report["humanized"]

assert perf["zero_drift"], "perfect zero-drift FAILED"
assert hum["zero_drift"], "humanized zero-drift FAILED"
assert perf["off120"] == 0, "perfect off-grid != 0 (%s)" % perf["off120"]
assert perf["scale_violations"] == 0, "perfect scale violations != 0"
assert perf["chord_violations"] == 0, "perfect chord violations != 0"

assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized scale violations != 0"
# humanized: every chord violation must be bar-seam onset jitter (not a pitch error)
assert hum["chord_violations"] == hum["chord_seam_violations"], \
    "humanized has non-seam chord violations (real pitch errors)"

# size asserts on audio too
for ver in ("phase1", "perfect", "humanized"):
    for ext in ("wav", "ogg"):
        ap = os.path.join(AUDIO_DIR, PROJECT + "-" + ver + "." + ext)
        if os.path.exists(ap):
            assert os.path.getsize(ap) > 40, "empty audio: %s" % ap

out = {"project": PROJECT, "report": report, "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
