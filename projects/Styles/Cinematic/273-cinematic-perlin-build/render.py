# -*- coding: utf-8 -*-
"""Render + master all three MIDIs (phase1, perfect, humanized) -> OGG."""
import os, subprocess, json, shutil
import numpy as np
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "273-cinematic-perlin-build"
BASE = "/opt/data/projects/Styles/Cinematic/" + PROJ
SF = discover_soundfont()
FLUID = shutil.which("fluidsynth") or "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = shutil.which("ffmpeg") or "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
STYLE = "cinematic"
TARGET = target_for_style(STYLE)


def render_midi_to_wav(mid, wav):
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, mid],
                   check=True, capture_output=True)


def silence_ratio(wav):
    a, sr = read_wav(wav)
    mono = a if a.ndim == 1 else a.mean(axis=1)
    return float(np.sum(np.abs(mono) < 0.001) / len(mono))


def per_second_rms(wav):
    a, sr = read_wav(wav)
    mono = a if a.ndim == 1 else a.mean(axis=1)
    n = len(mono) // sr
    return [float(np.sqrt(np.mean(mono[i * sr:(i + 1) * sr] ** 2))) for i in range(n)]


report = {}
for ver in ("phase1", "perfect", "humanized"):
    mid = f"{BASE}/MIDI/{PROJ}-{ver}.mid"
    wav = f"{BASE}/Audio/{PROJ}-{ver}.wav"
    ogg = f"{BASE}/Audio/{PROJ}-{ver}.ogg"
    render_midi_to_wav(mid, wav)
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "48k", ogg], check=True)
    sil = silence_ratio(wav)
    rms = per_second_rms(wav)
    report[ver] = {
        "lufs": rep["integrated_lufs"], "true_peak_db": rep["true_peak_db"],
        "target_lufs": TARGET, "silence_ratio": round(sil, 4),
        "rms_mean": round(float(np.mean(rms)), 4),
        "rms_max": round(float(np.max(rms)), 4),
        "wav_bytes": os.path.getsize(wav), "ogg_bytes": os.path.getsize(ogg),
        "wav": wav, "ogg": ogg,
    }
    for p in (wav, ogg):
        assert os.path.getsize(p) > 40, f"empty output: {p}"

print(json.dumps(report, indent=2))
with open(f"{BASE}/Analysis/render_report.json", "w") as f:
    json.dump({"soundfont": SF, "style": STYLE, "target_lufs": TARGET,
               **report}, f, indent=2)
print("RENDER_OK")