# -*- coding: utf-8 -*-
"""Render + master the dual-version MIDI to OGG (FluidSynth -> master -> Opus)."""
import os
import subprocess

import numpy as np

from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
NAME = "293-steel-guitar-rework"
STYLE = "country"
SF = discover_soundfont()
FLUID = os.environ.get("MUSICOM_FLUIDSYNTH") or "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = os.environ.get("FFMPEG") or "ffmpeg"
TARGET = target_for_style(STYLE)

os.makedirs(AUDIO_DIR, exist_ok=True)


def render_and_master(tag):
    mid = os.path.join(MIDI_DIR, f"{NAME}-{tag}.mid")
    wav = os.path.join(AUDIO_DIR, f"{NAME}-{tag}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{NAME}-{tag}.ogg")

    # 1. FluidSynth render (-R no -C no = dry, real silence gaps; -g 1.2 no tail cut)
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                    "-F", wav, SF, mid], check=True, capture_output=True)
    assert os.path.getsize(wav) > 100000, f"{tag} WAV too small"

    # 2. master to genre LUFS target, -1 dBTP ceiling
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    # 3. silence + peak metrics
    mono = mastered.mean(axis=1) if mastered.ndim > 1 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    peak = float(np.max(np.abs(mastered)))

    # 4. Opus OGG
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-b:a", "96k", ogg], check=True)
    assert os.path.getsize(ogg) > 10000, f"{tag} OGG too small"

    # 5. WAV cleanup (keep only compressed OGG)
    os.remove(wav)

    return {"tag": tag, "lufs": round(rep["integrated_lufs"], 2),
            "true_peak_db": round(rep["true_peak_db"], 2),
            "silence_ratio": round(silent, 4), "peak": round(peak, 3),
            "ogg_bytes": os.path.getsize(ogg)}


def main():
    results = []
    for tag in ("perfect", "humanized"):
        r = render_and_master(tag)
        results.append(r)
        print(tag, r)
    print("SF", SF, "TARGET", TARGET)
    print("DONE")


if __name__ == "__main__":
    main()
