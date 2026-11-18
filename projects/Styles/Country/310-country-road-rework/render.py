#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render + master 310-country-road-rework. Usage: render.py [phase1|perfect|humanized ...]"""
import json
import os
import subprocess
import sys

import numpy as np

from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont

PROJ = "/opt/data/projects/Styles/Country/310-country-road-rework"
STYLE = "country"
SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SR = 22050  # halved to keep master() (4x true-peak oversample) under the ~1.7 GB cgroup limit

TARGETS = {
    "phase1": "310-country-road-rework-phase1.mid",
    "perfect": "310-country-road-rework-perfect.mid",
    "humanized": "310-country-road-rework-humanized.mid",
}

STATS_PATH = os.path.join(PROJ, "Analysis", "render_stats.json")
stats = {}
if os.path.exists(STATS_PATH):
    stats = json.load(open(STATS_PATH))


def render_one(key):
    mid = os.path.join(PROJ, "MIDI", TARGETS[key])
    wav = os.path.join(PROJ, "Audio", f"310-country-road-rework-{key}.wav")
    ogg = os.path.join(PROJ, "Audio", f"310-country-road-rework-{key}.ogg")
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-r", str(SR), "-F", wav, SF, mid],
                   check=True, capture_output=True)
    print(f"{key}: fluidsynth done, mastering...", flush=True)
    audio, sr = read_wav(wav)
    target = target_for_style(STYLE)
    mastered, rep = master(audio, target_lufs=target, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    print(f"{key}: master done (LUFS {rep.get('integrated_lufs')}), ogg...", flush=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", wav, "-codec:a", "libopus", "-b:a", "96k", ogg],
                   check=True)
    mono = mastered[:, 0] if mastered.ndim == 2 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    return {
        "midi": mid,
        "wav": wav,
        "ogg": ogg,
        "soundfont": SF,
        "target_lufs": target,
        "integrated_lufs": rep.get("integrated_lufs"),
        "true_peak_db": rep.get("true_peak_db"),
        "silence_ratio": round(silent, 4),
        "bytes_wav": os.path.getsize(wav),
        "bytes_ogg": os.path.getsize(ogg),
    }


keys = sys.argv[1:] or list(TARGETS)
for key in keys:
    if key not in TARGETS:
        print(f"unknown target {key}", file=sys.stderr)
        continue
    r = render_one(key)
    stats[key] = r
    json.dump(stats, open(STATS_PATH, "w"), indent=2)
    print(json.dumps(r), flush=True)
print("done")
