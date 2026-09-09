# -*- coding: utf-8 -*-
import json
import os

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/091-baroque-genetic-allemande"
MIDI = os.path.join(PROJ, "MIDI", "091-baroque-genetic-allemande.mid")
P1_MIDI = os.path.join(PROJ, "MIDI", "091-baroque-genetic-allemande-phase1.mid")
ANALYSIS = os.path.join(PROJ, "Analysis")

# grid visualization (mido READ-ONLY — the sanctioned audit pattern)
import mido  # noqa: E402

mid = mido.MidiFile(MIDI)
lines = []
lines.append("091-baroque-genetic-allemande — grid visualization (phase-2)")
lines.append("rows = voices, cols = 24 bars (bar = 1920 ticks @ 480 TPB)")
lines.append("")

# per-voice onset density rows: bar -> count of onsets (16th cells)
BAR = 1920
HALF = BAR // 2  # 8 slots per bar for compact view
for i, track in enumerate(mid.tracks):
    if i == 0:
        continue
    t = 0
    active = {}
    onsets = []
    for msg in track:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            active.setdefault(msg.note, []).append(t)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if active.get(msg.note):
                st = active[msg.note].pop(0)
                onsets.append(st)
    cells = [0] * (24 * 8)
    for st in onsets:
        bar = min(st // BAR, 23)
        slot = (st % BAR) // HALF
        if slot >= 8:
            slot = 7
        cells[bar * 8 + slot] += 1
    chars = []
    for c in cells:
        chars.append("." if c == 0 else ("+" if c < 3 else "#"))
    lines.append(f"{track.name or f'track{i}':12s} |{''.join(chars)}|")
    # counts per bar
    bar_counts = [sum(cells[b * 8:(b + 1) * 8]) for b in range(24)]
    lines.append(f"{'':12s}  bar: " + " ".join(f"{c:2d}" for c in bar_counts))

with open(os.path.join(ANALYSIS, "grid_visualization.txt"), "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))

# summary.json (aggregate the contract numbers)
audit = json.load(open(os.path.join(ANALYSIS, "audit.json")))
stats = json.load(open(os.path.join(ANALYSIS, "render_stats.json")))
summary = {
    "project": "091-baroque-genetic-allemande",
    "genre": "Baroque",
    "method": "003 Genetic Genome Selection",
    "layer": "concrete",
    "key": "D aeolian (+ harmonic-minor C#, dorian B)",
    "bpm": 92,
    "form": "6 sections x 4 bars = 24 bars: Intro | AllemandeA | AllemandeB | Lift | AllemandeA2 | Outro",
    "voices": [
        {"voice": "Lead", "instrument": "Violin", "gm": 40},
        {"voice": "Oboe", "instrument": "Oboe", "gm": 68},
        {"voice": "Cello", "instrument": "Cello", "gm": 42},
        {"voice": "Piano", "instrument": "Acoustic Grand Piano", "gm": 1},
        {"voice": "Viola", "instrument": "Viola", "gm": 41},
        {"voice": "Bass", "instrument": "Double Bass", "gm": 43},
        {"voice": "Drums", "instrument": "Drum Kit", "gm": 0, "channel": 9},
    ],
    "verdict_grid": audit["verdict_grid"],
    "verdict_harmony": audit["verdict_harmony"],
    "verdict_zerodrift": audit["verdict_zerodrift"],
    "verdict_silence": stats["verdict_silence"],
    "grid": {
        "16th_off": audit["grid_phase2"]["total_off_16th"],
        "notes": audit["grid_phase2"]["total_notes"],
    },
    "harmony": {
        "out_of_scale": sum(r["out_of_scale"] for r in audit["harmony_phase2"]),
        "out_of_chord": sum(r["out_of_chord"] for r in audit["harmony_phase2"]),
    },
    "silence_ratio": stats["silence_ratio"],
    "duration_s": stats["duration_s"],
    "files": {
        "midi_phase1": os.path.getsize(P1_MIDI),
        "midi_phase2": os.path.getsize(MIDI),
        "wav": stats["wav_bytes"],
        "ogg": os.path.getsize(os.path.join(PROJ, "Audio", "091-baroque-genetic-allemande.ogg")),
    },
}
with open(os.path.join(ANALYSIS, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("summary.json written")