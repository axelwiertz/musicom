# -*- coding: utf-8 -*-
"""Render + master the 252 rework (phase1 raw, perfect + humanized mastered).

FluidSynth CLI -> WAV -> master to target_for_style(style) -> Opus OGG + WAV.
Reports LUFS / true-peak / silence ratio per render (real numbers).
"""
import json
import os
import subprocess

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJECT_DIR = "/opt/data/projects/Styles/Balkan/252-balkan-spectral-extended"
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
STYLE = "folk"
TARGET = target_for_style(STYLE)   # -16.0

os.makedirs(AUDIO_DIR, exist_ok=True)
SF = discover_soundfont()

NAME = "252-balkan-spectral-extended"


def render_wav(midi_path, wav_path):
    cmd = [FLUID, "-ni", "-g", "1.2", "-F", wav_path, SF, midi_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return wav_path


def master_to_lufs(wav_path, out_wav_path):
    audio, sr = read_wav(wav_path)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(out_wav_path, mastered, sr, normalize=False)
    return mastered, sr, rep


def silence_ratio(audio):
    if audio.ndim == 2:
        mono = audio.mean(axis=1)
    else:
        mono = audio
    return float(np.sum(np.abs(mono) < 0.001) / len(mono))


def encode_ogg(wav_path, ogg_path):
    cmd = ["ffmpeg", "-y", "-i", wav_path,
           "-codec:a", "libopus", "-b:a", "48k", ogg_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return ogg_path


def main():
    jobs = [
        # (label, midi_stem, master?)
        ("phase1", f"{NAME}-phase1.mid", False),
        ("perfect", f"{NAME}-perfect.mid", True),
        ("humanized", f"{NAME}-humanized.mid", True),
    ]
    stats = {}
    for label, midi_stem, do_master in jobs:
        midi = os.path.join(MIDI_DIR, midi_stem)
        raw_wav = os.path.join(AUDIO_DIR, f"{NAME}-{label}-raw.wav")
        final_wav = os.path.join(AUDIO_DIR, f"{NAME}-{label}.wav")
        ogg = os.path.join(AUDIO_DIR, f"{NAME}-{label}.ogg")

        render_wav(midi, raw_wav)
        rec = {"raw_wav_bytes": os.path.getsize(raw_wav)}
        if do_master:
            audio, sr, rep = master_to_lufs(raw_wav, final_wav)
        else:
            audio, sr = read_wav(raw_wav)
            final_wav = raw_wav
            rep = {"integrated_lufs": None, "true_peak_db": None}
        rec.update({
            "target_lufs": TARGET if do_master else None,
            "integrated_lufs": rep.get("integrated_lufs"),
            "true_peak_db": rep.get("true_peak_db"),
            "silence_ratio": round(silence_ratio(audio), 4),
            "sample_rate": sr,
        })
        encode_ogg(final_wav, ogg)
        rec["wav_bytes"] = os.path.getsize(final_wav)
        rec["ogg_bytes"] = os.path.getsize(ogg)
        assert os.path.getsize(ogg) > 40
        assert os.path.getsize(midi) > 40
        # clean raw wav if it differs from final
        if do_master and os.path.exists(raw_wav) and raw_wav != final_wav:
            os.remove(raw_wav)
        stats[label] = rec
        print(f"[{label}] LUFS={rec['integrated_lufs']} "
              f"peak={rec['true_peak_db']} "
              f"silence={rec['silence_ratio']} "
              f"ogg={rec['ogg_bytes']}B")

    with open(os.path.join(PROJECT_DIR, "Analysis", "render_stats.json"), "w") as f:
        json.dump({"style": STYLE, "target_lufs": TARGET, "render": stats},
                  f, indent=2)
    print("DONE", os.path.join(PROJECT_DIR, "Analysis", "render_stats.json"))


if __name__ == "__main__":
    main()