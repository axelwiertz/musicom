# -*- coding: utf-8 -*-
"""Render + master + OGG encode for 290-funk-hawkes-suite (perfect + humanized)."""
import os
import shutil
import subprocess

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Funk/290-funk-hawkes-suite"
AUDIO = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO, exist_ok=True)

SF = discover_soundfont()
FLUID = os.environ.get("MUSICOM_FLUIDSYNTH") or shutil.which("fluidsynth") \
    or "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = shutil.which("ffmpeg") or "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
print("SF:", SF)
print("FLUID:", FLUID)

results = {}
for name in ["perfect", "humanized"]:
    mid = os.path.join(PROJ, "MIDI", f"290-funk-hawkes-suite-{name}.mid")
    wav = os.path.join(AUDIO, f"290-funk-hawkes-suite-{name}.wav")
    ogg = os.path.join(AUDIO, f"290-funk-hawkes-suite-{name}.ogg")

    r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, mid],
                       capture_output=True, text=True)
    assert os.path.getsize(wav) > 40, "render empty"
    print(f"[{name}] fluidsynth render OK, wav={os.path.getsize(wav)} B")

    audio, sr = read_wav(wav)
    target = target_for_style("funk")
    mastered, rep = master(audio, target_lufs=target, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    mono = np.abs(mastered).mean(axis=1) if mastered.ndim == 2 else np.abs(mastered)
    silent = float(np.sum(mono < 0.001) / len(mono))

    r2 = subprocess.run([FFMPEG, "-y", "-i", wav, "-codec:a", "libopus",
                         "-application", "voip", "-b:a", "48k", ogg],
                        capture_output=True, text=True)
    assert os.path.getsize(ogg) > 40, "ogg empty"
    print(f"[{name}] mastered LUFS={rep.get('integrated_lufs')} "
          f"true_peak={rep.get('true_peak_db')} silence={silent:.4f} "
          f"ogg={os.path.getsize(ogg)} B")
    results[name] = {
        "target_lufs": target,
        "integrated_lufs": rep.get("integrated_lufs"),
        "true_peak_db": rep.get("true_peak_db"),
        "silence_ratio": silent,
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
    }

import json
with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(results, f, indent=2)
print("DONE render")
