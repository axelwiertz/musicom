# -*- coding: utf-8 -*-
"""Render + master + Opus-encode both perfect and humanized MIDI."""
import os, subprocess, sys, json
import numpy as np

from utilities.env import soundfont_path, fluidsynth_bin
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(PROJ, "MIDI")
AUDIO = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO, exist_ok=True)
BASE = "272-indie-pop-sunset-rework"
SF = soundfont_path()
FLUID = fluidsynth_bin()
STYLE = "pop"
TARGET = target_for_style(STYLE)

report = {}
for variant in ["perfect", "humanized"]:
    mid = os.path.join(MIDI, f"{BASE}-{variant}.mid")
    wav = os.path.join(AUDIO, f"{BASE}-{variant}.wav")
    ogg = os.path.join(AUDIO, f"{BASE}-{variant}.ogg")

    # 1. FluidSynth render
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, mid],
                   check=True, capture_output=True)

    # 2. master to genre target (pop = -9 LUFS, -1 dBTP ceiling)
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    # 3. Opus encode
    r = subprocess.run(["ffmpeg", "-y", "-i", wav,
                        "-codec:a", "libopus", "-b:a", "48k", ogg],
                       capture_output=True, text=True)

    # 4. silence ratio
    mono = mastered.mean(axis=-1) if mastered.ndim > 1 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

    report[variant] = {
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
        "lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "silence_ratio": round(silent, 4),
        "sr": sr,
        "target_lufs": TARGET,
    }
    print(variant, json.dumps(report[variant]))

with open(os.path.join(PROJ, "Analysis", "render.json"), "w") as f:
    json.dump(report, f, indent=2)
print("render.json written")
print("DONE")