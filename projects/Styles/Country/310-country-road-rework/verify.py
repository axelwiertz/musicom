#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only verification for 310-country-road-rework. Reports exact counts."""
import json
import os
import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/Country/310-country-road-rework"
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}   # G major

meta = json.load(open(os.path.join(PROJ, "Analysis", "compose_meta.json")))
BAR_CHORDS = []
CHORD_PCS = {"G": {7, 11, 2}, "D": {2, 6, 9}, "Em": {4, 7, 11},
             "C": {0, 4, 7}, "Am": {9, 0, 4}}
for s in meta["sections"]:
    for b in range(s["bars"]):
        BAR_CHORDS.append(s["chords"][b % len(s["chords"])])


def audit(path):
    mid = mido.MidiFile(path)
    lengths = []
    for i, tr in enumerate(mid.tracks):
        t = 0
        for m in tr:
            t += m.time
        lengths.append(t)
    voice_lengths = lengths[1:]
    zero_drift = len(set(voice_lengths)) == 1
    offgrid = 0
    scale_viol = 0
    chord_viol = 0          # floor attribution (t // BAR)
    chord_viol_grid = 0     # nearest-16th grid attribution (recovers intended bar)
    pitched = 0
    ch9 = 0
    for tr in mid.tracks[1:]:
        t = 0
        ch = None
        for m in tr:
            t += m.time
            if m.type == "program_change":
                ch = m.channel
            if m.type == "note_on" and m.velocity > 0:
                if ch == 9:
                    ch9 += 1
                    continue
                pitched += 1
                if not (t % 120 == 0 or t % 240 == 0):
                    offgrid += 1
                pc = m.note % 12
                if pc not in KEY_PCS:
                    scale_viol += 1
                bar = min(t // 1920, len(BAR_CHORDS) - 1)
                if pc not in CHORD_PCS[BAR_CHORDS[bar]]:
                    chord_viol += 1
                bar_g = min(int(round(t / 120) * 120) // 1920, len(BAR_CHORDS) - 1)
                if pc not in CHORD_PCS[BAR_CHORDS[bar_g]]:
                    chord_viol_grid += 1
    return {
        "file": os.path.basename(path),
        "bytes": os.path.getsize(path),
        "n_tracks": len(mid.tracks),
        "voice_tracks": len(voice_lengths),
        "track_length_ticks": voice_lengths[0] if voice_lengths else 0,
        "zero_drift": zero_drift,
        "distinct_lengths": sorted(set(voice_lengths)),
        "pitched_onsets": pitched,
        "ch9_onsets": ch9,
        "offgrid": offgrid,
        "scale_violations": scale_viol,
        "chord_violations": chord_viol,
        "chord_violations_grid": chord_viol_grid,
    }


results = []
for f in ["310-country-road-rework-phase1.mid",
          "310-country-road-rework-perfect.mid",
          "310-country-road-rework-humanized.mid"]:
    p = os.path.join(PROJ, "MIDI", f)
    r = audit(p)
    results.append(r)
    print(json.dumps(r))

json.dump(results, open(os.path.join(PROJ, "Analysis", "verification.json"), "w"), indent=2)
print("wrote Analysis/verification.json")
