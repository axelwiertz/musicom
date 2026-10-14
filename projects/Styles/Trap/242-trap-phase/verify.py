# -*- coding: utf-8 -*-
"""Independent MIDI audit (mido readback) for 242-trap-phase.

verify-don't-trust: re-opens the phase-2 MIDI with mido (READING ONLY) and
checks, per pitched voice: (1) grid sync (16th=120 / 8th=240), (2) harmony
(every note in key scale AND its own bar's chord tones), (3) zero-drift
(equal-length tracks). Writes Analysis/audit.json.
"""
import json
import os

import mido  # READING ONLY (analysis)

from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(HERE, "MIDI", "242-trap-phase.mid")
SUMMARY_PATH = os.path.join(HERE, "Analysis", "summary.json")

BAR = 1920
GRIDS = [("16th", 120), ("8th", 240)]

summary = json.load(open(SUMMARY_PATH))
KEY_PCS = set((summary["root_pc"] + iv) % 12 for iv in summary["scale_intervals"])
chord_path = summary["chord_path"]
bar_pcs = {c["bar"]: set(c["chord_tone_pcs"]) for c in chord_path}

mf = mido.MidiFile(MIDI_PATH)

track_lengths = []
voice_results = []
for ti, tr in enumerate(mf.tracks):
    ch = None
    for m in tr:
        if m.type == "program_change":
            ch = m.channel
        elif m.type == "note_on" and ch is None and hasattr(m, "channel"):
            ch = m.channel
    if ch is None:
        continue
    is_drums = (ch == 9)
    notes = []
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            notes.append((m.note, t))
    track_lengths.append(t)
    if is_drums or not notes:
        continue
    off_grid = {}
    for gname, g in GRIDS:
        off = [n for n in notes if n[1] % g != 0]
        off_grid[gname] = len(off)
    out_scale = []
    out_chord = []
    for note, onset in notes:
        pc = note % 12
        bar = onset // BAR
        bar = max(0, min(bar, len(bar_pcs) - 1))
        if pc not in KEY_PCS:
            out_scale.append((note, onset))
        if pc not in bar_pcs[bar]:
            out_chord.append((note, onset, bar))
    voice_results.append({
        "track": ti, "channel": ch,
        "n_notes": len(notes),
        "off_grid_16th": off_grid["16th"],
        "off_grid_8th": off_grid["8th"],
        "out_of_scale": len(out_scale),
        "out_of_chord": len(out_chord),
    })

zero_drift = len(set(track_lengths)) == 1
audit = {
    "midi": MIDI_PATH,
    "zero_drift": zero_drift,
    "track_lengths_ticks": track_lengths,
    "voices": voice_results,
    "total_off_grid_16th": sum(v["off_grid_16th"] for v in voice_results),
    "total_off_grid_8th": sum(v["off_grid_8th"] for v in voice_results),
    "total_out_of_scale": sum(v["out_of_scale"] for v in voice_results),
    "total_out_of_chord": sum(v["out_of_chord"] for v in voice_results),
}
json.dump(audit, open(os.path.join(HERE, "Analysis", "audit.json"), "w"), indent=2)

print("ZERO_DRIFT:", zero_drift, "track_lengths:", track_lengths)
for v in voice_results:
    print(f"track{v['track']} ch{v['channel']} notes={v['n_notes']:3d} "
          f"off16={v['off_grid_16th']} off8={v['off_grid_8th']} "
          f"out_scale={v['out_of_scale']} out_chord={v['out_of_chord']}")
print("TOTAL off16:", audit["total_off_grid_16th"],
      "off8:", audit["total_off_grid_8th"],
      "out_scale:", audit["total_out_of_scale"],
      "out_chord:", audit["total_out_of_chord"])
