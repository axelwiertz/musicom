#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render + master both dual-version MIDIs -> WAV -> OGG for 250-hirajoshi-ma-rework."""
import os
import subprocess
import sys

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from utilities.env import fluidsynth_bin, soundfont_path

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SF = discover_soundfont()
FLUID = fluidsynth_bin()
FFMPEG = "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
STYLE = "classical"          # closest paradigm for japanese hogaku (sparse, ma, dynamic)
TARGET = target_for_style(STYLE)   # -18.0

BASE = "250-hirajoshi-ma-rework"
results = {}

for variant in ("perfect", "humanized"):
    midi = os.path.join(MIDI_DIR, f"{BASE}-{variant}.mid")
    wav = os.path.join(AUDIO_DIR, f"{BASE}-{variant}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{BASE}-{variant}.ogg")

    # 1. fluidsynth render
    cmd = [FLUID, "-ni", "-g", "1.2", "-F", wav, SF, midi]
    subprocess.run(cmd, check=True, capture_output=True)
    assert os.path.getsize(wav) > 40, f"{wav} empty"

    # 2. master
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    # 3. ogg (opus)
    subprocess.run([FFMPEG, "-y", "-i", wav, "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", ogg],
                   check=True, capture_output=True)
    assert os.path.getsize(ogg) > 40, f"{ogg} empty"

    # silence ratio
    mono = mastered if mastered.ndim == 1 else np.mean(mastered, axis=1)
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    peak = float(np.max(np.abs(mastered)))
    results[variant] = {
        "wav": wav, "ogg": ogg,
        "lufs": rep["integrated_lufs"], "true_peak_db": rep["true_peak_db"],
        "target_lufs": TARGET, "silence_ratio": round(silent, 4),
        "peak": round(peak, 4), "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
    }
    print(f"{variant}: LUFS={rep['integrated_lufs']} dBTP={rep['true_peak_db']} "
          f"silence={silent:.4f} peak={peak:.4f}")

print("RESULTS", results)
