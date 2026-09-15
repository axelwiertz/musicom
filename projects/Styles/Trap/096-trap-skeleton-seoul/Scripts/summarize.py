# -*- coding: utf-8 -*-
"""Grid visualization + Analysis/summary.json for 096-trap-skeleton-seoul."""
import json
import os

import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401  (compliant-import marker)

PROJ = "/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul"
ANALYSIS = os.path.join(PROJ, "Analysis")
MIDI = os.path.join(PROJ, "MIDI", "096-trap-skeleton-seoul.mid")
P1_MIDI = os.path.join(PROJ, "MIDI", "096-trap-skeleton-seoul-phase1.mid")
BAR = 1920
SLOT = BAR // 8

LABEL = {(12, 0): "BellLead", (40, 1): "ViolinCtr", (1, 2): "PianoStab",
         (43, 4): "Sub808", (56, 5): "BrassStab", (0, 9): "Drums"}

mid = mido.MidiFile(MIDI)
lines = ["096-trap-skeleton-seoul - grid visualization (phase-2)",
         "rows = voices, cols = 24 bars x 8 eighth-note slots",
         "bar = 1920 ticks @ 480 TPB (140 BPM half-time feel), section = 4 bars", ""]
for i, track in enumerate(mid.tracks):
    if i == 0:
        continue
    t, onsets, prog, ch = 0, [], 0, 0
    for msg in track:
        t += msg.time
        if msg.type == "program_change":
            prog, ch = msg.program, msg.channel
        elif msg.type == "note_on" and msg.velocity > 0:
            onsets.append(t)
    cells = [0] * (24 * 8)
    for st in onsets:
        bar = min(st // BAR, 23)
        slot = min((st % BAR) // SLOT, 7)
        cells[bar * 8 + slot] += 1
    chars = "".join("." if c == 0 else ("+" if c < 3 else "#") for c in cells)
    name = track.name or LABEL.get((prog, ch), "track%d" % i)
    lines.append("%-14s |%s|" % (name, chars))
    counts = [sum(cells[b * 8:(b + 1) * 8]) for b in range(24)]
    lines.append("%-14s  bar: %s" % ("", " ".join("%2d" % c for c in counts)))
lines.append("")
lines.append("Legend: . rest | + 1-2 onsets | # 3+ onsets per 8th-note slot")

with open(os.path.join(ANALYSIS, "grid_visualization.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))

concept = json.load(open(os.path.join(ANALYSIS, "concept.json")))
audit = json.load(open(os.path.join(ANALYSIS, "audit.json")))
stats = json.load(open(os.path.join(ANALYSIS, "render_stats.json")))
tonal = json.load(open(os.path.join(ANALYSIS, "tonal_check.json")))
s2 = stats["phase2"]

summary = {
    "project": "096-trap-skeleton-seoul",
    "genre": "Trap",
    "layer": "concrete",
    "method": "001 Skeleton-First Refinement",
    "method_impl": "generators.base.FunctionGenerator",
    "seed": concept["seed"],
    "key": "C phrygian",
    "bpm": concept["bpm"],
    "form": ("6 sections x 4 bars = 24 bars: Intro | VerseA | HookB | "
             "Bridge | HookB2 | Outro"),
    "skeleton": concept["skeleton"],
    "motif_steps": concept["motif_steps"],
    "progression": concept["progression"],
    "vl_flags": concept["vl_flags"],
    "vl_fixes": concept["vl_fixes"],
    "voices": [
        {"voice": "BellLead", "instrument": "Marimba", "gm": 12, "channel": 0},
        {"voice": "ViolinCtr", "instrument": "Violin", "gm": 40, "channel": 1},
        {"voice": "PianoStab", "instrument": "Piano", "gm": 1, "channel": 2},
        {"voice": "Sub808", "instrument": "Double Bass", "gm": 43, "channel": 4},
        {"voice": "BrassStab", "instrument": "Trumpet", "gm": 56, "channel": 5},
        {"voice": "Drums", "instrument": "Drum Kit", "gm": 0, "channel": 9},
    ],
    "verdict_grid": audit["verdict_grid"],
    "verdict_harmony": audit["verdict_harmony"],
    "verdict_range": audit["verdict_range"],
    "verdict_zerodrift": audit["verdict_zerodrift"],
    "verdict_tonal_phase1": tonal["verdict_phase1"],
    "verdict_tonal_phase2": tonal["verdict_phase2"],
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
    "tonal_phase1": tonal["phase1_ground_truth"],
    "tonal_phase2": tonal["phase2_polyphonic"],
    "silence_ratio": s2["silence_ratio"],
    "duration_s": s2["duration_s"],
    "peak": s2["peak"],
    "per_second_rms": s2["per_second_rms"],
    "files": {
        "midi_phase1": os.path.getsize(P1_MIDI),
        "midi_phase2": os.path.getsize(MIDI),
        "wav": s2["wav_bytes"],
        "ogg": os.path.getsize(os.path.join(
            PROJ, "Audio", "096-trap-skeleton-seoul.ogg")),
        "ogg_phase1": os.path.getsize(os.path.join(
            PROJ, "Audio", "096-trap-skeleton-seoul-phase1.ogg")),
    },
}
with open(os.path.join(ANALYSIS, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("summary.json written")
