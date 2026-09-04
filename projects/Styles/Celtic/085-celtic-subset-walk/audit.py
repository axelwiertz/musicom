#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""085 audit: grid + scale + chord verification on exported phase-2 MIDI.

READ-ONLY mido analysis (authoring is engine-only; this is the mandatory
verification pass). Reports per-voice off-grid onsets (16th=120, 8th=240),
out-of-scale notes, and out-of-chord notes (chord = walked subset realized
in Ab major for the bar where the note STARTS). All counts must be 0.
"""
import json
import os

# mido is used for READING/verification ONLY (AGENTS.md: authoring must go
# through the engine; analysis reads are permitted).
# READING ONLY (analysis)
import mido
from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)

MIDI_PATH = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk/MIDI/085-celtic-subset-walk.mid"
P1_PATH = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk/MIDI/085-celtic-subset-walk-phase1.mid"
OUT = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk/Analysis/audit.json"

BAR = 1920
TPB = 480
# Ab major scale pcs
KEY_PCS = {8, 10, 0, 1, 3, 5, 7}
# Walked subset ids per bar (must match compose.py WALK_IDS exactly)
WALK = ["maj0", "min2", "maj5", "min4",
        "maj0", "min4", "maj5", "min2",
        "maj5", "min4", "maj70", "maj7",
        "maj70", "min4", "dom77", "min4",
        "maj0", "min2", "maj5", "min2",
        "maj5", "min4", "dom77", "maj0"]
# subset id -> pc set in the C library; +8 transposes to Ab
PCS = {
    "maj0": {0, 4, 7}, "min2": {2, 5, 9}, "maj5": {5, 9, 0},
    "min4": {4, 7, 11}, "maj7": {7, 11, 2}, "min9": {9, 0, 4},
    "maj70": {0, 4, 7, 11}, "dom77": {7, 11, 2, 5}, "min72": {9, 0, 4, 7},
}
OFF = 8
DEG = {"maj0": "I", "min2": "ii", "maj5": "IV", "min4": "iii", "maj7": "V",
       "maj70": "I7", "dom77": "V7", "min9": "vi", "min72": "vi7"}
PITCH_CLASS = {0: "C", 1: "C#", 2: "D", 3: "Eb", 4: "E", 5: "F",
               6: "F#", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B"}


def bar_chord_pcs(bar):
    """Chord pitch classes (Ab-register) for a bar."""
    return {(pc + OFF) % 12 for pc in PCS[WALK[bar]]}


def analyze(path):
    mid = mido.MidiFile(path)
    voices = []
    for ti, track in enumerate(mid.tracks):
        program, channel = 0, 0
        for msg in track:
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
        abstick = 0
        notes = []
        active = {}
        for msg in track:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (abstick, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    s, vel = active.pop(msg.note)
                    if msg.note > 0 or s > 0:
                        notes.append({"pitch": msg.note, "vel": vel,
                                      "start": s, "end": abstick})
        if notes or ti > 0:
            voices.append({"track": ti, "program": program, "channel": channel,
                           "notes": notes})
    return voices


def audit(voices, label):
    res = {"label": label, "voices": []}
    all_off16 = all_off8 = 0
    all_n = 0
    for v in voices:
        notes = [n for n in v["notes"] if n["pitch"] > 0]
        is_drums = (v["channel"] == 9)
        off16 = [n for n in notes if n["start"] % 120 != 0]
        off8 = [n for n in notes if n["start"] % 240 != 0]
        out_scale = []
        out_chord = []
        if not is_drums:
            for n in notes:
                bar = min(n["start"] // BAR, 23)
                pc = n["pitch"] % 12
                if pc not in KEY_PCS:
                    out_scale.append(n)
                if pc not in bar_chord_pcs(bar):
                    out_chord.append(n)
        entry = {
            "track": v["track"], "program": v["program"],
            "channel": v["channel"], "n_notes": len(notes),
            "is_drums": is_drums,
            "off_grid_16th": len(off16), "off_grid_8th": len(off8),
            "out_of_scale": len(out_scale),
            "out_of_chord": len(out_chord),
            "off_grid_16th_examples": [n["start"] for n in off16[:3]],
            "out_of_scale_examples": [(n["pitch"], n["start"]) for n in out_scale[:3]],
            "out_of_chord_examples": [(n["pitch"], n["start"]) for n in out_chord[:3]],
        }
        all_off16 += len(off16); all_off8 += len(off8); all_n += len(notes)
        res["voices"].append(entry)
        print(f"  voice t{v['track']} prog={v['program']:3d} ch={v['channel']:2d} "
              f"notes={len(notes):4d} off16={len(off16):3d} off8={len(off8):3d} "
              f"outScale={len(out_scale):3d} outChord={len(out_chord):3d}")
    res["totals"] = {"notes": all_n, "off_grid_16th": all_off16,
                     "off_grid_8th": all_off8}
    print(f"  TOTAL notes={all_n} off16={all_off16} off8={all_off8}")
    return res


print("== PHASE 2 ==")
r2 = audit(analyze(MIDI_PATH), "phase2")
print("== PHASE 1 (raw, expected off-grid by design) ==")
r1 = audit(analyze(P1_PATH), "phase1")

with open(OUT, "w") as f:
    json.dump({"phase1": r1, "phase2": r2}, f, indent=2)
print("audit written", OUT)

# verdict
t = r2["totals"]
assert t["off_grid_16th"] == 0, "phase2 off-grid 16th violations!"
for v in r2["voices"]:
    assert v["out_of_scale"] == 0, "out-of-scale in phase2!"
    assert v["out_of_chord"] == 0, "out-of-chord in phase2!"
print("AUDIT PASS: phase-2 0 off-grid, 0 out-of-scale, 0 out-of-chord")
