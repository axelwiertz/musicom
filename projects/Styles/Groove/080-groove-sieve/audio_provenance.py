# -*- coding: utf-8 -*-
"""080-groove-sieve: provenance for audio artifacts + README/REPORT check."""
import os
import json
import subprocess

PROJ = "/opt/data/projects/Styles/Groove/080-groove-sieve"
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

BASE_PARAMS = {
    "bpm": 110, "key": "G natural minor", "sections": 6, "bars": 24,
    "seed": 20260828,
    "sieve_A": {"mod": 8, "res": [0, 2, 5]},
    "sieve_B": {"mod": 7, "res": [0, 1, 4]},
    "progression": ["i", "III", "iv", "V", "i", "III", "iv", "V",
                    "i", "iv", "V", "i", "i", "V", "i", "VI",
                    "i", "III", "iv", "V", "i", "V", "iv", "i"],
}

for name, note in (
    ("080-groove-sieve.wav", "FluidSynth full-mix render (TimGM6mb.sf2, gain 1.2) of phase-2 MIDI"),
    ("080-groove-sieve.ogg", "Opus 48k voip delivery render of phase-2 full mix"),
    ("080-groove-sieve-phase1.wav", "FluidSynth full-mix render of phase-1 raw sieve draft"),
    ("080-groove-sieve-phase1.ogg", "Opus 48k voip delivery render of phase-1 draft"),
):
    p = os.path.join(AUDIO_DIR, name)
    if os.path.exists(p):
        write_provenance(
            p, AI_GENERATED,
            "Xenakis Sieve Theory (Method 025, sieve C = A ∩ B, lcm 56)",
            parameters=dict(BASE_PARAMS, artifact=name),
            notes=note)
        print("provenance:", name)

# ---- preflight check ----
r = subprocess.run(
    ["/opt/data/micromamba/envs/musicom/bin/python",
     "/opt/data/projects/Research/preflight_check.py", PROJ],
    capture_output=True, text=True, timeout=120)
print("PREFLIGHT exit:", r.returncode)
print(r.stdout[-2000:])
if r.stderr:
    print("STDERR:", r.stderr[-1000:])
