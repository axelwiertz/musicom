# -*- coding: utf-8 -*-
"""Render + MASTER all three MIDI versions -> FluidSynth WAV -> master -> Opus OGG."""
import os
import json
import subprocess

import numpy as np

from utilities.env import fluidsynth_bin, soundfont_path
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Celtic/287-celtic-tonality-diamond"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
os.makedirs(AUDIO_DIR, exist_ok=True)

STYLE = "celtic"
TARGET = target_for_style(STYLE)
SF = soundfont_path()
FLUID = fluidsynth_bin()
assert os.path.exists(SF), SF

VERSIONS = ["phase1", "perfect", "humanized"]
BASE = "287-celtic-tonality-diamond"


def render_wav(midi_path, wav_path):
    cmd = [FLUID, "-ni", "-g", "1.2", "-F", wav_path, SF, midi_path]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def to_ogg(wav_path, ogg_path):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg_path],
        check=True, capture_output=True, text=True)


stats = {}
for v in VERSIONS:
    midi = os.path.join(MIDI_DIR, f"{BASE}-{v}.mid")
    wav = os.path.join(AUDIO_DIR, f"{BASE}-{v}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{BASE}-{v}.ogg")
    render_wav(midi, wav)
    audio, sr = read_wav(wav)
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    n = len(mono)
    silent = float(np.sum(np.abs(mono) < 0.001) / n)
    nsec = max(1, n // sr)
    rms_per_sec = [float(np.sqrt(np.mean(mono[i * sr:(i + 1) * sr] ** 2)))
                   for i in range(nsec)]
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    to_ogg(wav, ogg)
    stats[v] = {
        "midi_bytes": os.path.getsize(midi),
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
        "duration_s": round(n / sr, 2),
        "silence_ratio": round(silent, 4),
        "rms_per_sec_min": round(float(np.min(rms_per_sec)), 4),
        "rms_per_sec_max": round(float(np.max(rms_per_sec)), 4),
        "rms_per_sec_mean": round(float(np.mean(rms_per_sec)), 4),
        "target_lufs": TARGET,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
    }
    print(v, json.dumps({k: stats[v][k] for k in
                         ("wav_bytes", "ogg_bytes", "duration_s", "silence_ratio",
                          "integrated_lufs", "true_peak_db")}))

with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
    json.dump(stats, f, indent=2)
print("RENDER DONE")
