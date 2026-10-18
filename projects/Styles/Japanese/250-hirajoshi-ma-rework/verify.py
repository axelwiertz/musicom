#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent read-only verification of 250-hirajoshi-ma-rework MIDI artifacts."""
import os
import sys
import mido  # READING ONLY (analysis)

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJ, "MIDI")

TPB = 480
BAR = TPB * 4
S = TPB // 4          # 120
E = TPB // 2          # 240

KEY_PCS = {0, 2, 3, 7, 8}   # D hirajoshi pitch classes
HIRA_IVLS = [0, 1, 5, 6, 10]

SECTIONS = [
    ("Jo",      [0, 0, 4, 4]),
    ("Ha",      [0, 2, 4, 0]),
    ("Ha2",     [3, 2, 0, 4]),
    ("Kyu",     [4, 3, 2, 1]),
    ("Bridge",  [1, 2, 3, 4]),
    ("Kyu2",    [4, 3, 2, 1]),
    ("Develop", [2, 1, 4, 3]),
    ("Jo2",     [0, 0, 0, 0]),
]
GLOBAL_DEG = []
for _n, degs in SECTIONS:
    GLOBAL_DEG.extend(degs)
assert len(GLOBAL_DEG) == 32


def chord_pcs(deg):
    def sp(d):
        return 50 + (d // 5) * 12 + HIRA_IVLS[d % 5]
    return {sp(deg) % 12, sp(deg + 2) % 12, sp(deg + 4) % 12}


def audit(path, check_grid=True, check_harmony=True):
    assert os.path.getsize(path) > 40, f"{path} too small"
    mid = mido.MidiFile(path)
    tracks = mid.tracks[1:]
    lens = []
    for t in tracks:
        ln = 0
        for m in t:
            ln += m.time
        lens.append(ln)
    zero_drift = len(set(lens)) == 1
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    pitched_onsets = 0
    for t in tracks:
        ch = None
        for m in t:
            if m.type == "note_on" and m.velocity > 0:
                ch = m.channel
                break
        abs_t = 0
        for m in t:
            abs_t += m.time
            if m.type != "note_on" or m.velocity == 0:
                continue
            if m.channel == 9:
                continue
            pitched_onsets += 1
            if check_grid and not (abs_t % S == 0 or abs_t % E == 0):
                offgrid += 1
            if check_harmony:
                if m.note % 12 not in KEY_PCS:
                    scale_viol += 1
                bar = abs_t // BAR
                if bar < len(GLOBAL_DEG) and m.note % 12 not in chord_pcs(GLOBAL_DEG[bar]):
                    chord_viol += 1
    return {
        "size": os.path.getsize(path), "n_voice_tracks": len(tracks),
        "track_lens": lens, "zero_drift": zero_drift,
        "offgrid": offgrid, "scale_viol": scale_viol,
        "chord_viol": chord_viol, "pitched_onsets": pitched_onsets,
    }


for name in ["250-hirajoshi-ma-rework-phase1",
             "250-hirajoshi-ma-rework-perfect",
             "250-hirajoshi-ma-rework-humanized"]:
    p = os.path.join(MIDI_DIR, name + ".mid")
    if name.endswith("phase1"):
        r = audit(p, check_grid=False, check_harmony=False)
        r["note"] = "raw draft: grid/harmony checks intentionally skipped"
    else:
        r = audit(p)
    print(name, "->", r)
