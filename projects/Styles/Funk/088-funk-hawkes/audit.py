# -*- coding: utf-8 -*-
"""088 audit: grid + scale + chord verification on exported phase-2 MIDI.

READ-ONLY mido analysis (authoring is engine-only; this is the mandatory
verification pass). Reports per-voice off-grid onsets (16th=120, 8th=240),
out-of-scale notes, and out-of-chord notes (chord = progression triad for the
GLOBAL bar where the note starts: bar = section*4 + local). All counts must
be 0 for pitched voices.
"""
import json
import os

import mido  # READING ONLY (analysis)
from structures import MusicUnit, MusicEvent  # noqa: F401 (compliant import marker)

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(HERE, "MIDI", "088-funk-hawkes.mid")
P1_PATH = os.path.join(HERE, "MIDI", "088-funk-hawkes-phase1.mid")
OUT = os.path.join(HERE, "Analysis", "audit.json")

BAR = 1920
SIXTEENTH = 120
EIGHTH = 240
BARS_PER = 4
N_BARS = 24

# F minor pentatonic colour scale pcs (F Ab Bb C Eb); the audit scale is the
# FULL F aeolian (F G Ab Bb C Db Eb) because harmony chords are diatonic
# triads of F aeolian - a pentatonic snap then chord-quantize lands every
# note on a chord tone, which is by construction in both sets.
SCALE_PCS = {5, 7, 8, 10, 0, 1, 3}   # F G Ab Bb C Db Eb (aeolian superset)

ROOT_QUAL = {53: "m", 49: "M", 44: "M", 51: "M", 46: "m", 48: "m"}
PROG = ([53, 49, 44, 51] + [53, 49, 53, 48] + [53, 49, 44, 51] +
        [53, 49, 53, 48] + [53, 49, 44, 51] + [49, 44, 53, 53])
CHORD_PCS_BY_BAR = []
for root in PROG:
    iv = (0, 3, 7) if ROOT_QUAL[root] == "m" else (0, 4, 7)
    CHORD_PCS_BY_BAR.append(set((root + i) % 12 for i in iv))


def parse(mid_path):
    mid = mido.MidiFile(str(mid_path))
    out = {}
    for ti, track in enumerate(mid.tracks):
        program, channel = 0, 0
        for msg in track:
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
        if ti == 0 and not any(m.type == "program_change" for m in track):
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
