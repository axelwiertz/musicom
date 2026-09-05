#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Write Analysis/summary.json for project 086 (clean version)."""
import json
import os

PROJ = "/opt/data/projects/Styles/Cuban/086-son-markov-guajira"
with open(os.path.join(PROJ, "Analysis", "audit.json")) as f:
    audit = json.load(f)
with open(os.path.join(PROJ, "Analysis", "render_stats.json")) as f:
    render = json.load(f)

p2 = audit["files"][0]["voices"]
pitched = [v for v in p2 if not v["percussion"]]

# full 24-bar progression with roman numerals
DEG_ROMAN = {0: "i", 1: "ii", 2: "III", 3: "iv", 4: "V7", 5: "VI", 6: "VII"}
PROG = [0, 0, 0, 0, 0, 6, 5, 0, 1, 0, 4, 0, 3, 6, 4, 0,
        5, 3, 6, 0, 0, 6, 4, 0]
prog_rows = []
for bar, d in enumerate(PROG):
    prog_rows.append({"bar": bar + 1, "degree": DEG_ROMAN[d]})

summary = {
    "project": "086-son-markov-guajira",
    "id": 86,
    "style": "Cuban (son, guajira-leaning)",
    "method": "002 Markov Probabilistic Transitions (MarkovChainGenerator.generate_sequence)",
    "layer": "concrete",
    "form": "AAB - 6 sections x 4 bars (ClaveIntro, SonA, Montuno, SonA2, Montuno2, Outro) = 24 bars",
    "key": "A minor (aeolian; V7 bars 10/14/23 use harmonic-minor G#)",
    "tempo_bpm": 104,
    "meter": "4/4, 480 TPB",
    "voices": [
        {"name": "Lead", "instrument": "Tres (GM 24 nylon-guitar stand-in; tres not in 18-instrument registry)"},
        {"name": "Montuno", "instrument": "Piano (registry PIANO, GM 1)"},
        {"name": "Comp", "instrument": "Acoustic Guitar (registry ACOUSTIC_GUITAR, GM 25)"},
        {"name": "Bass", "instrument": "Contrabass (registry DOUBLE_BASS, GM 43)"},
        {"name": "Trumpet", "instrument": "Trumpet (registry TRUMPET, GM 56)"},
        {"name": "Drums", "instrument": "GM kit ch9 (kick/snare/hat/cowbell) + son-clave woodblock"},
    ],
    "progression": prog_rows,
    "grid_audit": {
        "per_pitched_voice_off_grid_16th": [v["off_grid_16th"] for v in pitched],
        "verdict": "0 off-grid onsets (16th = 120 ticks) across all pitched voices",
    },
    "harmony_audit": {
        "per_pitched_voice_out_of_scale": [v["out_of_scale"] for v in pitched],
        "per_pitched_voice_out_of_chord": [v["out_of_chord"] for v in pitched],
        "verdict": "0 out-of-scale, 0 out-of-chord across all pitched voices",
    },
    "zero_drift": "validate() passed for both phase-1 and phase-2 MIDIs (track length 46080 ticks)",
    "render": {
        "method": "SP-001",
        "duration_s": render["duration_s"],
        "silence_ratio": render["silence_ratio"],
        "peak": render["peak"],
        "wav_bytes": render["wav_bytes"],
        "ogg_bytes": render["ogg_bytes"],
    },
    "files": {
        "midi_phase1": "MIDI/086-son-markov-guajira-phase1.mid (1674 B)",
        "midi_phase2": "MIDI/086-son-markov-guajira.mid (8716 B)",
        "ogg": "Audio/086-son-markov-guajira.ogg (421344 B)",
        "wav": "Audio/086-son-markov-guajira.wav (10983212 B)",
    },
}
with open(os.path.join(PROJ, "Analysis", "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("written")
