# -*- coding: utf-8 -*-
"""090 audit: grid + scale + chord verification on exported phase-2 MIDI.

READ-ONLY mido analysis (authoring is engine-only; this is the mandatory
verification pass). Reports per-voice off-grid onsets (16th=120, 8th=240),
out-of-scale notes, and out-of-chord notes (chord = subset-walk realization
triad/tetrad for the GLOBAL bar where the note starts: bar = section*4 +
local). All counts must be 0 for pitched voices.
"""
import json
import os

import mido  # READING ONLY (analysis)

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(HERE, "MIDI", "090-celtic-subset-walk.mid")
P1_PATH = os.path.join(HERE, "MIDI", "090-celtic-subset-walk-phase1.mid")
OUT = os.path.join(HERE, "Analysis", "audit.json")

BAR = 1920
SIXTEENTH = 120
EIGHTH = 240
BARS_PER = 4
N_BARS = 24

# D minor audit scale: aeolian + harmonic-minor raised 7th (C#, in A7 V7 and
# C#dim vii*) + dorian raised 6th (B natural, in G7 bVII7) — the abstract
# layer walk's idiomatic modal borrowings (same superset pattern as project
# 088's F-aeolian audit). Every note is chord-quantized so this superset is
# the piece's actual pitch universe.
# pcs: D E F G A Bb B C C#
SCALE_PCS = {2, 4, 5, 7, 9, 10, 11, 0, 1}

WALK = ["min2", "maj5", "min2", "min9", "min2", "maj5", "min70", "maj75",
        "min70", "maj75", "dom79", "dom77", "dim1", "dom79", "maj75",
        "dom79", "dim1", "dom77", "min2", "maj5", "min2", "min9", "dom79",
        "min2"]

CHORD_DEF = {
    "min2":   (50, "m"), "maj5": (53, "M"), "min9": (57, "m"),
    "maj0":   (48, "M"), "maj10": (46, "M"), "min7": (55, "m"),
    "dom79":  (57, "7"), "dim1": (49, "d"), "min70": (50, "m7"),
    "dom77":  (55, "7"), "maj75": (53, "M7"), "min4": (52, "m"),
}
IV = {"m": (0, 3, 7), "M": (0, 4, 7), "d": (0, 3, 6), "7": (0, 4, 7, 10),
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
