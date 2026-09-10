# -*- coding: utf-8 -*-
"""Grid visualization + Analysis/summary.json for 092-disco-schillinger.

READING ONLY (analysis) for the 8-slot-per-bar onset density map; the canonical
visualization helper writes the UnitMatrix-level high-contrast grid render.
"""
import json
import os

PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger")
ANALYSIS = os.path.join(PROJ, "Analysis")
MIDI = os.path.join(PROJ, "MIDI", "092-disco-schillinger.mid")
P1_MIDI = os.path.join(PROJ, "MIDI", "092-disco-schillinger-phase1.mid")
BAR = 1920
HALF = BAR // 2

import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401

LABEL = {(56, 0): "Lead(trp)", (65, 1): "Sax", (1, 2): "Piano",
         (19, 3): "Organ", (25, 4): "Guitar", (43, 5): "Bass", (0, 9): "Drums"}

mid = mido.MidiFile(MIDI)
lines = ["092-disco-schillinger - grid visualization (phase-2)",
         "rows = voices, cols = 24 bars x 8 half-beat slots",
         "bar = 1920 ticks @ 480 TPB (118 BPM), section = 4 bars", ""]
for i, track in enumerate(mid.tracks):
    if i == 0:
        continue
    t, active, onsets, prog, ch = 0, {}, [], 0, 0
    for msg in track:
        t += msg.time
        if msg.type == "program_change":
            prog, ch = msg.program, msg.channel
        elif msg.type == "note_on" and msg.velocity > 0:
            active.setdefault(msg.note, []).append(t)
            onsets.append(t)
    cells = [0] * (24 * 8)
    for st in onsets:
        bar = min(st // BAR, 23)
        slot = min((st % BAR) // HALF, 7)
        cells[bar * 8 + slot] += 1
    chars = "".join("." if c == 0 else ("+" if c < 3 else "#") for c in cells)
    name = track.name or LABEL.get((prog, ch), "track%d" % i)
    lines.append("%-10s |%s|" % (name, chars))
    counts = [sum(cells[b * 8:(b + 1) * 8]) for b in range(24)]
    lines.append("%-10s  bar: %s" % ("", " ".join("%2d" % c for c in counts)))
lines.append("")
lines.append("Legend: . rest | + 1-2 onsets | # 3+ onsets per half-beat slot")

with open(os.path.join(ANALYSIS, "grid_visualization.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))

concept = json.load(open(os.path.join(ANALYSIS, "concept.json")))
audit = json.load(open(os.path.join(ANALYSIS, "audit.json")))
stats = json.load(open(os.path.join(ANALYSIS, "render_stats.json")))
s2 = stats["phase2"]

summary = {
    "project": "092-disco-schillinger",
    "genre": "Disco",
    "layer": "concrete",
    "method": "018 Schillinger System of Musical Design",
    "seed": concept["seed"],
    "key": "Eb major",
    "bpm": concept["bpm"],
    "form": ("6 sections x 4 bars = 24 bars: Intro | Verse | Chorus | Break | "
             "Chorus2 | Outro"),
    "schillinger_resultant": concept["schillinger"],
    "progression": concept["progression"],
    "voices": [
        {"voice": "Lead", "instrument": "Trumpet", "gm": 56},
        {"voice": "Sax", "instrument": "Saxophone", "gm": 65},
        {"voice": "Piano", "instrument": "Acoustic Grand Piano", "gm": 1},
        {"voice": "Organ", "instrument": "Church Organ", "gm": 19},
        {"voice": "Guitar", "instrument": "Acoustic Guitar (nylon)", "gm": 25},
        {"voice": "Bass", "instrument": "Double Bass", "gm": 43},
        {"voice": "Drums", "instrument": "Drum Kit", "gm": 0, "channel": 9},
    ],
    "verdict_grid": audit["verdict_grid"],
    "verdict_harmony": audit["verdict_harmony"],
    "verdict_zerodrift": audit["verdict_zerodrift"],
    "verdict_silence": s2["verdict_silence"],
    "grid": {"off_16th": audit["grid_phase2"]["total_off_16th"],
             "notes": audit["grid_phase2"]["total_notes"],
             "off_8th": audit["grid_phase2"]["total_off_8th"]},
    "harmony": {"out_of_scale": sum(r["out_of_scale"]
                                    for r in audit["harmony_phase2"]),
                "out_of_chord": sum(r["out_of_chord"]
                                    for r in audit["harmony_phase2"])},
    "phase1_fingerprint": {
        "off_16th": audit["phase1_fingerprint"]["total_off_16th"],
        "notes": audit["phase1_fingerprint"]["total_notes"]},
    "silence_ratio": s2["silence_ratio"],
    "duration_s": s2["duration_s"],
    "peak": s2["peak"],
    "per_second_rms": s2["per_second_rms"],
    "files": {
        "midi_phase1": os.path.getsize(P1_MIDI),
        "midi_phase2": os.path.getsize(MIDI),
        "wav": s2["wav_bytes"],
        "ogg": os.path.getsize(os.path.join(
            PROJ, "Audio", "092-disco-schillinger.ogg")),
        "ogg_phase1": os.path.getsize(os.path.join(
            PROJ, "Audio", "092-disco-schillinger-phase1.ogg")),
    },
}
with open(os.path.join(ANALYSIS, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("summary.json written")
