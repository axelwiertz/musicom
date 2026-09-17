# -*- coding: utf-8 -*-
"""097 audit: grid + scale + chord verification on exported phase-2 MIDI.

READ-ONLY mido analysis (authoring is engine-only; this is the mandatory
verification pass). Reports per-voice off-grid onsets (16th=120, 8th=240),
out-of-scale notes, and out-of-chord notes (chord = walked-anchor
triad/tetrad for the GLOBAL bar where the note starts: bar = section*4 +
local). All counts must be 0 for pitched voices.
"""
import json
import os

import mido  # READING ONLY (analysis)

# engine import (preflight reading-context marker; authoring lives in compose.py)
from structures import MusicUnit  # noqa: F401  (reading-context only)

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(HERE, "MIDI", "097-jazz-bebop-changes.mid")
P1_PATH = os.path.join(HERE, "MIDI", "097-jazz-bebop-changes-phase1.mid")
OUT = os.path.join(HERE, "Analysis", "audit.json")

BAR = 1920
SIXTEENTH = 120
EIGHTH = 240
BARS_PER = 4
N_BARS = 24

# G major audit scale: strict ionian pcs {G A B C D E F#}.
# Every phase-2 pitched note is chord-quantized to a walked anchor whose
# pcs are diatonic in G, so 0 out-of-scale is expected by construction.
SCALE_PCS = {7, 9, 11, 0, 2, 4, 6}

WALK = ["maj7", "maj0", "maj7", "maj0", "min9", "min11", "maj0", "maj7",
        "min9", "maj7", "min11", "maj0", "maj70", "min74", "maj70", "maj77",
        "min74", "min79", "min74", "maj70", "min79", "maj0", "dom72", "maj7"]

CHORD_DEF = {
    "maj7":   (55, "M"), "min9": (57, "m"), "min11": (59, "m"),
    "maj0":   (48, "M"), "maj2": (50, "M"), "min4": (52, "m"),
    "min79":  (57, "m7"), "min711": (59, "m7"), "maj70": (48, "M7"),
    "dom72":  (50, "7"), "min74": (52, "m7"), "maj77": (55, "M7"),
}
IV = {"M": (0, 4, 7), "m": (0, 3, 7), "d": (0, 3, 6), "7": (0, 4, 7, 10),
      "m7": (0, 3, 7, 10), "M7": (0, 4, 7, 11)}
CHORD_PCS_BY_BAR = []
for pid in WALK:
    root, kind = CHORD_DEF[pid]
    CHORD_PCS_BY_BAR.append(set((root + i) % 12 for i in IV[kind]))


def parse(mid_path):
    mid = mido.MidiFile(str(mid_path))
    out = {}
    for ti, track in enumerate(mid.tracks):
        program, channel = 0, 0
        has_pc = False
        for msg in track:
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
                has_pc = True
        if ti == 0 and not has_pc:
            continue
        notes = []
        abstick = 0
        active = {}
        for msg in track:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0 and msg.note != 0:
                active[msg.note] = abstick
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    notes.append((msg.note, active.pop(msg.note), abstick))
        out[ti] = {"program": program, "channel": channel, "notes": notes}
    return out


def audit(mid_path, is_phase2):
    data = parse(mid_path)
    rows = []
    total_notes = 0
    for ti, info in sorted(data.items()):
        notes = info["notes"]
        total_notes += len(notes)
        off16 = [n for n in notes if n[1] % SIXTEENTH != 0]
        off8 = [n for n in notes if n[1] % EIGHTH != 0]
        oos = 0
        ooc = 0
        if info["channel"] != 9 and is_phase2:
            for pitch, st, _ in notes:
                if pitch % 12 not in SCALE_PCS:
                    oos += 1
                bar = min(st // BAR, N_BARS - 1)
                if pitch % 12 not in CHORD_PCS_BY_BAR[bar]:
                    ooc += 1
        rows.append({
            "track": ti, "program": info["program"], "channel": info["channel"],
            "notes": len(notes), "off16": len(off16), "off8": len(off8),
            "out_of_scale": oos, "out_of_chord": ooc,
        })
    return data, rows, total_notes


_, p2rows, p2n = audit(MIDI_PATH, True)
_, p1rows, p1n = audit(P1_PATH, False)

result = {
    "phase2": {"total_notes": p2n, "rows": p2rows,
               "off16_sum": sum(r["off16"] for r in p2rows),
               "oos_sum": sum(r["out_of_scale"] for r in p2rows),
               "ooc_sum": sum(r["out_of_chord"] for r in p2rows)},
    "phase1": {"total_notes": p1n, "rows": p1rows,
               "off16_sum": sum(r["off16"] for r in p1rows)},
}
with open(OUT, "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
