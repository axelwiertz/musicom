# -*- coding: utf-8 -*-
"""320-axel-style-study — render + master.

Chain (iteration 01, dry): FluidSynth (FluidR3_GM) -> master(-14 LUFS) -> OGG.
Both perfect and humanized renders go through the same dry chain so the A/B is
purely grid-vs-humanization. A production method (SP-*) comes in a later
iteration.
"""

import json
import os
import subprocess

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(BASE, "Audio")
ANALYSIS = os.path.join(BASE, "Analysis")
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(ANALYSIS, exist_ok=True)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF = discover_soundfont()
TARGET = target_for_style("axel")   # -14.0

report = {}
for tag in ("perfect", "humanized"):
    midi = os.path.join(BASE, "MIDI", f"320-axel-style-study-{tag}.mid")
    wav = os.path.join(AUDIO, f"320-axel-style-study-{tag}.wav")
    ogg = os.path.join(AUDIO, f"320-axel-style-study-{tag}.ogg")

    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, midi],
                   check=True, capture_output=True)
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", wav, "-codec:a", "libopus", "-b:a", "96k", ogg],
                   check=True, capture_output=True)

    assert os.path.getsize(wav) > 40, f"empty WAV: {wav}"
    assert os.path.getsize(ogg) > 40, f"empty OGG: {ogg}"
    report[tag] = {
        "target_lufs": TARGET,
        "integrated_lufs": round(rep["integrated_lufs"], 2),
        "true_peak_db": round(rep["true_peak_db"], 3),
        "duration_s": round(len(audio) / sr, 2),
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
    }
    print(tag, "->", report[tag], flush=True)

with open(os.path.join(ANALYSIS, "render_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("done")
