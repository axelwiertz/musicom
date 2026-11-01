# -*- coding: utf-8 -*-
"""render_audio.py - render + master perfect & humanized MIDI -> WAV -> OGG.

FluidSynth CLI render, then master() to genre LUFS target (-1 dBTP ceiling),
then Opus OGG. Reports LUFS / true-peak / silence ratio.
"""
import os
import subprocess
import numpy as np

from workflows.provenance import write_provenance, AI_ASSISTED
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Funk/278-funk-contour-groove-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
STYLE = "funk"
SR = 44100
TARGET = target_for_style("Funk")


def render_wav(midi_path, wav_path):
    cmd = [FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
           "-F", wav_path, SF, midi_path]
    subprocess.run(cmd, check=True, capture_output=True)
    assert os.path.getsize(wav_path) > 40, f"empty {wav_path}"


def silence_ratio(audio):
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    return float(np.sum(np.abs(mono) < 0.001) / len(mono))


def process(name):
    midi = os.path.join(MIDI_DIR, f"{name}.mid")
    wav = os.path.join(AUDIO_DIR, f"{name}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{name}.ogg")
    render_wav(midi, wav)

    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    sil = silence_ratio(mastered)

    subprocess.run([FFMPEG, "-y", "-loglevel", "error",
                    "-i", wav, "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", ogg], check=True)

    stats = {
        "name": name,
        "style": STYLE,
        "target_lufs": round(TARGET, 1),
        "integrated_lufs": round(float(rep.get("integrated_lufs", 0)), 3),
        "true_peak_db": round(float(rep.get("true_peak_db", 0)), 3),
        "silence_ratio": round(sil, 4),
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
    }
    write_provenance(wav, classification=AI_ASSISTED,
                     generator="fluidsynth CLI + sound.effects.mastering",
                     parameters={**stats, "project": "278-funk-contour-groove-suite"})
    write_provenance(ogg, classification=AI_ASSISTED,
                     generator="ffmpeg Opus",
                     parameters={**stats, "project": "278-funk-contour-groove-suite"})
    print(stats)
    return stats


if __name__ == "__main__":
    import json
    print("SoundFont:", SF)
    out = {}
    for name in ["278-funk-contour-groove-suite-perfect",
                 "278-funk-contour-groove-suite-humanized"]:
        out[name] = process(name)
    with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("render_stats.json written")