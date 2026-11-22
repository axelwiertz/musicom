# -*- coding: utf-8 -*-
"""318-sinterklaaslied — render + master (perfect + humanized).

FluidSynth (FluidR3_GM) -> WAV -> master() to style LUFS (-16) -> Opus OGG.
Writes Audio/render_report.json with integrated LUFS + true-peak + sizes.
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
TARGET = target_for_style("sinterklaas")   # -16.0

report = {}
for tag in ("perfect", "humanized"):
    midi = os.path.join(BASE, "MIDI", f"318-sinterklaaslied-{tag}.mid")
    wav = os.path.join(AUDIO, f"318-sinterklaaslied-{tag}.wav")
    ogg = os.path.join(AUDIO, f"318-sinterklaaslied-{tag}.ogg")

    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, midi],
                   check=True, capture_output=True)

    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", wav, "-codec:a", "libopus", "-b:a", "96k", ogg],
                   check=True, capture_output=True)

    report[tag] = {
        "soundfont": os.path.basename(SF),
        "target_lufs": TARGET,
        "integrated_lufs": round(rep["integrated_lufs"], 2),
        "true_peak_db": round(rep["true_peak_db"], 3),
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
    }
    assert os.path.getsize(wav) > 40, f"empty WAV: {wav}"
    assert os.path.getsize(ogg) > 40, f"empty OGG: {ogg}"
    print(tag, "->", report[tag])

with open(os.path.join(ANALYSIS, "render_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("done")
