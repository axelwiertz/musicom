# -*- coding: utf-8 -*-
"""Read-only verification of the 282 rework outputs. mido = READING ONLY (analysis)."""
import os
import json
import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/Balkan/282-balkan-christoffel-variations"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

BAR_TICKS = 1320
BARS_PER_SECTION = 4
KEY_PCS = {0, 2, 4, 5, 7, 9, 10, 11}
SECTION_CHORDS = {
    0: ["Dm", "C", "Dm", "Dm"], 1: ["Dm", "C", "G", "Dm"], 2: ["F", "C", "Dm", "Am"],
    3: ["G", "F", "C", "Dm"], 4: ["Am", "Dm", "G", "C"], 5: ["C", "G", "Dm", "F"],
    6: ["G", "Dm", "C", "Dm"], 7: ["Bb", "C", "Dm", "Dm"],
}
CHORD_PCS = {"Dm": {2, 5, 9}, "C": {0, 4, 7}, "G": {7, 11, 2}, "F": {5, 9, 0},
             "Am": {9, 0, 4}, "Bb": {10, 2, 5}}


def chord_pcs_at(tick):
    bar = tick // BAR_TICKS
    sec = bar // BARS_PER_SECTION
    b = bar % BARS_PER_SECTION
    return CHORD_PCS[SECTION_CHORDS[sec][b]]


def analyze(path):
    assert os.path.getsize(path) > 40, f"too small: {path}"
    mid = mido.MidiFile(path)
    lens = []
    for tr in mid.tracks:
        t = 0
        for m in tr:
            t += m.time
        lens.append(t)
    voice_lens = lens[1:]
    zero_drift = len(set(voice_lens)) == 1

    pitched = 0
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    for tr in mid.tracks[1:]:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.channel != 9:
                pitched += 1
                if not (t % 120 == 0 or t % 240 == 0):
                    offgrid += 1
                if (m.note % 12) not in KEY_PCS:
                    scale_viol += 1
                if (m.note % 12) not in chord_pcs_at(t):
                    chord_viol += 1
    return {
        "path": path, "bytes": os.path.getsize(path),
        "ntracks": len(mid.tracks), "voice_tracks": len(voice_lens),
        "track_lengths": voice_lens, "zero_drift": zero_drift,
        "pitched_notes": pitched, "off_grid": offgrid,
        "scale_violations": scale_viol, "chord_violations": chord_viol,
    }


files = {
    "phase1": os.path.join(MIDI_DIR, "282-balkan-christoffel-variations-phase1.mid"),
    "perfect": os.path.join(MIDI_DIR, "282-balkan-christoffel-variations-perfect.mid"),
    "humanized": os.path.join(MIDI_DIR, "282-balkan-christoffel-variations-humanized.mid"),
}
report = {}
for name, path in files.items():
    r = analyze(path)
    report[name] = r
    print(f"--- {name} ---")
    print(json.dumps(r, indent=2))

out = os.path.join(ANALYSIS_DIR, "verify.json")
with open(out, "w") as f:
    json.dump(report, f, indent=2, default=str)
print("wrote", out)
