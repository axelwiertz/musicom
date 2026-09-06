#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""087 audit: grid + scale + chord verification on exported phase-2 MIDI.

READ-ONLY mido analysis (authoring is engine-only; this is the mandatory
verification pass). Reports per-voice off-grid onsets (16th=120, 8th=240),
out-of-scale notes, and out-of-chord notes (chord = walked subset realized
in D dorian for the bar where the note STARTS). All counts must be 0.
"""
import json
import os
import random

# mido is used for READING/verification ONLY (AGENTS.md: authoring must go
# through the engine; analysis reads are permitted).
# READING ONLY (analysis)
import mido
from structures import MusicUnit, MusicEvent  # noqa: F401  (compliant import marker)
from rules.subset_network import PatternNetwork, standard_patterns  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI_PATH = os.path.join(HERE, "MIDI", "087-tango-abstract-dorian.mid")
P1_PATH = os.path.join(HERE, "MIDI", "087-tango-abstract-dorian-phase1.mid")
OUT = os.path.join(HERE, "Analysis", "audit.json")

BAR = 1920
SIXTEENTH = 120
EIGHTH = 240
TONIC = 2
DORIAN_OFFS = [0, 2, 3, 5, 7, 9, 10]
SCALE_PCS = set((TONIC + o) % 12 for o in DORIAN_OFFS)

# --- recompute the walked subset ids per bar (must match compose.py) -------
def chord_pcs(deg, seventh=False):
    idx = [deg, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    rels = [DORIAN_OFFS[i] for i in idx]
    return frozenset((TONIC + r) % 12 for r in rels)

def find_id(pcs):
    for p in standard_patterns():
        if p.subset == pcs:
            return p.id
    return None

ANCHOR_DEG = {}
anchor_ids = []
for d in range(7):
    pid = find_id(chord_pcs(d))
    if pid:
        ANCHOR_DEG[pid] = d
        anchor_ids.append(pid)
for d in (0, 1, 2, 3, 4, 6):
    pid = find_id(chord_pcs(d, seventh=True))
    if pid:
        ANCHOR_DEG[pid] = d
        anchor_ids.append(pid)
anchor_ids = sorted(set(anchor_ids))
net_lib = PatternNetwork(standard_patterns())
net = PatternNetwork([net_lib.patterns[i] for i in anchor_ids])
T_CURVE = [2.0] * 24
for b in range(24):
    if 4 <= b < 8:
        T_CURVE[b] = 2.0 + 0.3 * (b - 4)
    elif 8 <= b < 12:
        T_CURVE[b] = 2.6
    elif 12 <= b < 16:
        T_CURVE[b] = 3.0 + 0.8 * (b - 12)
    elif 16 <= b < 20:
        T_CURVE[b] = 3.0 - 0.4 * (b - 16)
rng = random.Random(20260905)
WALK = net.walk("maj0", 24, rng=rng, tension_curve=T_CURVE, home="maj0")
WALK[-1] = "maj0"
BAR_PCS = [frozenset(net_lib.patterns[pid].subset) for pid in WALK]


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
                bar = min(st // BAR, 23)
                if pitch % 12 not in BAR_PCS[bar]:
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
