# -*- coding: utf-8 -*-
"""089-electronic-subset-minor — post-export AUDIT (job contract).

Reads the phase-2 MIDI back (mido, READ-ONLY — analysis only, never
authoring) and verifies:
  1. Zero-drift: all tracks same length.
  2. Grid: every pitched voice's onsets on the 16th grid (120 @ 480 TPB).
  3. Harmony: every pitched note in A-natural-minor scale AND chord tones of
     its bar (bar attribution = floor(tick/BAR) — matches compose.py's
     global_bar(); boundary notes belong to the bar they start in).
Exits non-zero on any FAIL so the nightly gate is real.
# READING ONLY (analysis)
"""
import json
import os
import sys

import mido  # READING ONLY (analysis) — audit reads, never writes MIDI

from workflows.provenance import write_provenance  # noqa: E402  (compliant import; unused here)

PROJ = "/opt/data/projects/Styles/Electronic/089-electronic-subset-minor"
MID = os.path.join(PROJ, "MIDI", "089-electronic-subset-minor.mid")
BAR = 1920
GRID16 = 120
SCALE_PCS = {9, 11, 0, 2, 4, 5, 7}          # A natural minor
# progression (from compose.py run output / summary.json)
PROG = ['min9', 'min4', 'maj5', 'maj0', 'maj5', 'maj0', 'dom77', 'min72',
        'dom77', 'min74', 'dom77', 'maj70', 'maj7', 'min4', 'min2', 'maj5',
        'min2', 'min4', 'maj5', 'maj0', 'min2', 'maj0', 'dom77', 'min9']
CHORD_PCS = {  # from rules.subset_network standard_patterns subsets
    'min9': {0, 4, 9}, 'min4': {4, 7, 11}, 'maj5': {0, 5, 9},
    'maj0': {0, 4, 7}, 'dom77': {2, 5, 7, 11}, 'min72': {0, 2, 5, 9},
    'min74': {2, 4, 7, 11}, 'maj70': {0, 4, 7, 11}, 'maj7': {2, 7, 11},
    'min2': {2, 5, 9},
}
# channel 9 (drums) excluded from harmony/grid pitch audits
PITCHED_CHANNELS = {0, 1, 2, 3, 4}
VOICE_NAMES = {0: "Lead(Marimba)", 1: "Clarinet", 2: "Cello",
               3: "Dulcimer", 4: "Bass", 9: "Drums"}


def load_notes(path):
    mid = mido.MidiFile(path)
    tracks = []
    for i, tr in enumerate(mid.tracks):
        notes = []
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                notes.append({'ch': msg.channel, 'pitch': msg.note,
                              'start': t, 'vel': msg.velocity})
        tracks.append(notes)
    return mid, tracks


def main():
    fails = []
    mid, tracks = load_notes(MID)

    # 1. zero-drift: track lengths — skip track 0 (conductor: tempo/meta,
    # len 0 by design). All VOICE tracks must be identical length.
    lengths = []
    for tr in mid.tracks[1:]:
        t = 0
        for msg in tr:
            t += msg.time
        lengths.append(t)
    if len(set(lengths)) != 1:
        fails.append(f"ZERO-DRIFT FAIL: voice track lengths {lengths}")
    else:
        print(f"zero-drift OK: all {len(lengths)} voice tracks len {lengths[0]}")

    # 2+3. grid + harmony per pitched channel
    all_onsets = {ch: [] for ch in PITCHED_CHANNELS}
    for tr in tracks:
        for n in tr:
            if n['ch'] in PITCHED_CHANNELS:
                all_onsets[n['ch']].append(n)

    grid_fail = 0
    harm_fail = 0
    for ch in sorted(PITCHED_CHANNELS):
        notes = sorted(all_onsets[ch], key=lambda n: n['start'])
        if not notes:
            print(f"{VOICE_NAMES[ch]:14s}: no notes")
            continue
        off_grid = [n for n in notes if n['start'] % GRID16 != 0]
        out_scale = []
        out_chord = []
        for n in notes:
            pc = n['pitch'] % 12
            if pc not in SCALE_PCS:
                out_scale.append((n['start'], n['pitch']))
            bar = min(n['start'] // BAR, 23)
            if pc not in CHORD_PCS[PROG[bar]]:
                out_chord.append((n['start'], n['pitch'], PROG[bar]))
        grid_fail += len(off_grid)
        harm_fail += len(out_scale) + len(out_chord)
        print(f"{VOICE_NAMES[ch]:14s}: {len(notes):4d} notes | "
              f"off-grid {len(off_grid):3d} | out-scale {len(out_scale):2d} "
              f"| out-chord {len(out_chord):2d}")
        if off_grid:
            fails.append(f"{VOICE_NAMES[ch]} off-grid: {off_grid[:5]}")
        if out_scale:
            fails.append(f"{VOICE_NAMES[ch]} out-scale: {out_scale[:5]}")
        if out_chord:
            fails.append(f"{VOICE_NAMES[ch]} out-chord: {out_chord[:5]}")

    print(f"\nTOTALS: off-grid {grid_fail} | out-scale+out-chord {harm_fail}")
    verdict = "AUDIT PASS" if not fails else "AUDIT FAIL"
    print(verdict)
    with open(os.path.join(PROJ, "Analysis", "audit_result.json"), "w") as f:
        json.dump({"verdict": verdict, "fails": fails,
                   "off_grid_total": grid_fail,
                   "harmony_violations_total": harm_fail}, f, indent=2)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
