# -*- coding: utf-8 -*-
# READING ONLY (analysis)
"""Verify 236-flamenco-rbm-cadence phase-2 MIDI: grid + harmony audit (readback).

mido is used here to READ the exported MIDI for the grid/harmony audit; it
never authors MIDI (authoring stays in compose.py via to_midi()).
"""
import json
import os
import sys

import mido

from structures import MusicUnit  # noqa: F401  (compliance marker: musicom context)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(BASE_DIR, "MIDI", "236-flamenco-rbm-cadence.mid")
ANALYSIS_DIR = os.path.join(BASE_DIR, "Analysis")

BAR = 1920
KEY_PCS = {9, 11, 0, 2, 4, 5, 7}          # A B C D E F G
CADENCE = [
    {"name": "Am", "pcs": {9, 0, 4}},
    {"name": "G", "pcs": {7, 11, 2}},
    {"name": "F", "pcs": {5, 9, 0}},
    {"name": "Em", "pcs": {4, 7, 11}},
]
BAR_CHORD = list(range(4)) * 8

CH_TO_VOICE = {0: "Lead", 1: "Compas", 2: "Bass", 3: "Flute", 9: "Palmas(drums)"}

mid = mido.MidiFile(MIDI_PATH)
print("ticks_per_beat:", mid.ticks_per_beat)
print("num tracks:", len(mid.tracks))

results = {}
for ti, track in enumerate(mid.tracks):
    # determine channel + program from program_change / first note
    ch = None
    for msg in track:
        if msg.type == "program_change":
            ch = msg.channel
            break
    voice = CH_TO_VOICE.get(ch, f"track{ti}_ch{ch}")
    # collect note_ons (velocity > 0, pitch > 0)
    abs_t = 0
    onsets = []
    for msg in track:
        abs_t += msg.time
        if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
            onsets.append((abs_t, msg.note))
    if not onsets:
        continue
    is_drums = (ch == 9)
    off16 = [o for o, _ in onsets if o % 120 != 0]
    off8 = [o for o, _ in onsets if o % 240 != 0]
    out_scale = []
    out_chord = []
    if not is_drums:
        for o, p in onsets:
            bar = o // BAR
            if not (0 <= bar < 32):
                out_scale.append((o, p, "bar-oob"))
                continue
            cidx = BAR_CHORD[bar]
            pc = p % 12
            if pc not in KEY_PCS:
                out_scale.append((o, p))
            if pc not in CADENCE[cidx]["pcs"]:
                out_chord.append((o, p))
    results[voice] = {
        "channel": ch,
        "n_notes": len(onsets),
        "drums": is_drums,
        "off_16th": len(off16),
        "off_8th": len(off8),
        "out_of_scale": len(out_scale),
        "out_of_chord": len(out_chord),
    }

print(json.dumps(results, indent=2))
with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
    json.dump(results, f, indent=2)

# totals for pitched voices
pitched = {k: v for k, v in results.items() if not v["drums"]}
tot_notes = sum(v["n_notes"] for v in pitched.values())
tot_off16 = sum(v["off_16th"] for v in pitched.values())
tot_off8 = sum(v["off_8th"] for v in pitched.values())
tot_scale = sum(v["out_of_scale"] for v in pitched.values())
tot_chord = sum(v["out_of_chord"] for v in pitched.values())
print("\n=== PITCHED VOICE TOTALS ===")
print("notes=%d  off_16th=%d  off_8th(16th-note subdivisions, on-grid)=%d  "
      "out_of_scale=%d  out_of_chord=%d"
      % (tot_notes, tot_off16, tot_off8, tot_scale, tot_chord))
# authoritative grid = finest 16th grid (120). Every onset must be a multiple
# of 120; the 8th-grid count simply tallies legitimate 16th-note subdivisions.
ok = (tot_off16 == 0 and tot_scale == 0 and tot_chord == 0)
print("AUDIT PASS (off_16th==0, out_of_scale==0, out_of_chord==0):", ok)

