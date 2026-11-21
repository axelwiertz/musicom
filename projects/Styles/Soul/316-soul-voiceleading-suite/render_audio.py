# -*- coding: utf-8 -*-
"""Render + master + encode 316-soul-voiceleading-suite (-perfect and -humanized)."""
import os
import subprocess
import json

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Soul/316-soul-voiceleading-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
STYLE = "soul"
TARGET = target_for_style(STYLE)

results = {}
for tag in ("perfect", "humanized"):
    mid = os.path.join(MIDI_DIR, f"316-soul-voiceleading-suite-{tag}.mid")
    wav_raw = os.path.join(AUDIO_DIR, f"316-soul-voiceleading-suite-{tag}.raw.wav")
    wav_master = os.path.join(AUDIO_DIR, f"316-soul-voiceleading-suite-{tag}.wav")
    ogg = os.path.join(AUDIO_DIR, f"316-soul-voiceleading-suite-{tag}.ogg")

    # 1. FluidSynth render (dry: -R no -C no keeps decay tight)
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                    "-F", wav_raw, SF, mid], check=True, capture_output=True)
    assert os.path.getsize(wav_raw) > 40, "render empty: " + wav_raw

    # 2. master to genre LUFS target, -1 dBTP ceiling
    audio, sr = read_wav(wav_raw)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav_master, mastered, sr, normalize=False)

    mono = mastered.mean(axis=1) if mastered.ndim == 2 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

    # 3. Opus OGG encode of MASTERED wav
    subprocess.run([FFMPEG, "-y", "-loglevel", "error",
                    "-i", wav_master, "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", ogg], check=True)
    assert os.path.getsize(ogg) > 40, "ogg empty: " + ogg

    # cleanup raw wav (keep mastered wav + ogg)
    os.remove(wav_raw)

    results[tag] = {
        "target_lufs": TARGET,
        "integrated_lufs": rep.get("integrated_lufs"),
        "true_peak_db": rep.get("true_peak_db"),
        "silence_ratio": silent,
        "wav": os.path.basename(wav_master),
        "ogg": os.path.basename(ogg),
        "duration_s": len(mono) / sr,
    }
    print(tag, json.dumps(results[tag], default=str), flush=True)

with open(os.path.join(AUDIO_DIR, "render_report.json"), "w") as f:
    json.dump(results, f, indent=2, default=str)
print("DONE", flush=True)
