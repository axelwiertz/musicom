# -*- coding: utf-8 -*-
"""Render + master + OGG encode for the 282 rework (perfect + humanized + phase1)."""
import os
import subprocess
import json

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Balkan/282-balkan-christoffel-variations"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
SF = discover_soundfont()
STYLE = "balkan-folk"
TARGET = target_for_style(STYLE)

BASE = "282-balkan-christoffel-variations"


def render_one(tag, midi_path, out_prefix):
    wav_raw = os.path.join(AUDIO_DIR, f"{out_prefix}.raw.wav")
    wav_master = os.path.join(AUDIO_DIR, f"{out_prefix}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{out_prefix}.ogg")

    # 1. fluidsynth render (dry, -g 1.2 to avoid tail truncation)
    r = subprocess.run([FLUIDSYNTH, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                        "-F", wav_raw, SF, midi_path],
                       capture_output=True, text=True)
    assert os.path.getsize(wav_raw) > 40, f"fluidsynth produced empty: {wav_raw}"

    # 2. master
    audio, sr = read_wav(wav_raw)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav_master, mastered, sr, normalize=False)

    # 3. silence ratio on mastered mono
    mono = mastered.mean(axis=1) if mastered.ndim > 1 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

    # 4. OGG (Opus)
    r = subprocess.run([FFMPEG, "-y", "-loglevel", "error",
                        "-i", wav_master, "-codec:a", "libopus",
                        "-application", "voip", "-b:a", "48k", ogg],
                       capture_output=True, text=True)
    assert os.path.getsize(ogg) > 40, f"ffmpeg produced empty: {ogg}"

    # drop the raw intermediate WAV (WAV cleanup rule)
    os.remove(wav_raw)

    return {
        "tag": tag, "midi": midi_path, "wav": wav_master, "ogg": ogg,
        "wav_bytes": os.path.getsize(wav_master),
        "ogg_bytes": os.path.getsize(ogg),
        "sample_rate": sr, "target_lufs": TARGET,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "silence_ratio": round(silent, 4),
        "stages": rep["stages"],
    }


if __name__ == "__main__":
    jobs = [
        ("perfect", os.path.join(MIDI_DIR, f"{BASE}-perfect.mid"), f"{BASE}-perfect"),
        ("humanized", os.path.join(MIDI_DIR, f"{BASE}-humanized.mid"), f"{BASE}-humanized"),
        ("phase1", os.path.join(MIDI_DIR, f"{BASE}-phase1.mid"), f"{BASE}-phase1"),
    ]
    out = {}
    for tag, midi, prefix in jobs:
        print(f"rendering {tag} ...", flush=True)
        out[tag] = render_one(tag, midi, prefix)
        print(f"  {tag}: LUFS={out[tag]['integrated_lufs']} "
              f"peak={out[tag]['true_peak_db']} silence={out[tag]['silence_ratio']}",
              flush=True)
    with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("DONE. render_stats.json written.")
