# -*- coding: utf-8 -*-
"""Render + master + encode for 256-tango-dorian-rework (both versions)."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from utilities.env import fluidsynth_bin, soundfont_path
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

ROOT = Path("/opt/data/projects/Styles/Tango/256-tango-dorian-rework")
NAME = "256-tango-dorian-rework"
AUDIO = ROOT / "Audio"
AUDIO.mkdir(parents=True, exist_ok=True)
SF = soundfont_path()
FLUID = fluidsynth_bin()
STYLE = "Tango"
TARGET = target_for_style(STYLE)
print(f"soundfont={SF}\nfluidsynth={FLUID}\ntarget_lufs={TARGET}")


def render_midi(midi_path, wav_path):
    cmd = [FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
           "-F", str(wav_path), SF, str(midi_path)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def master_wav(wav_path):
    audio, sr = read_wav(str(wav_path))
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(str(wav_path), mastered, sr, normalize=False)
    return rep, sr


def silence_stats(wav_path):
    audio, sr = read_wav(str(wav_path))
    mono = audio.mean(axis=1) if audio.ndim > 1 else audio
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    peak = float(np.max(np.abs(mono)))
    return {"silence_ratio": round(silent, 4), "peak": round(peak, 4),
            "duration_s": round(len(mono) / sr, 2)}


results = {}
for tag in ("perfect", "humanized"):
    midi = ROOT / "MIDI" / f"{NAME}-{tag}.mid"
    wav = AUDIO / f"{NAME}-{tag}.wav"
    ogg = AUDIO / f"{NAME}-{tag}.ogg"
    render_midi(midi, wav)
    rep, sr = master_wav(wav)
    stats = silence_stats(wav)
    stats["integrated_lufs"] = round(rep["integrated_lufs"], 2)
    stats["true_peak_db"] = round(rep["true_peak_db"], 2)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", str(wav), "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", str(ogg)],
                   check=True, capture_output=True, text=True)
    results[tag] = {
        "wav": str(wav), "ogg": str(ogg),
        "wav_bytes": wav.stat().st_size, "ogg_bytes": ogg.stat().st_size,
        **stats,
    }
    assert wav.stat().st_size > 40, f"{tag} wav empty"
    assert ogg.stat().st_size > 40, f"{tag} ogg empty"
    flag = " <-- SILENCE>30%" if stats["silence_ratio"] > 0.30 else ""
    print(f"[{tag:9}] lufs={stats['integrated_lufs']} "
          f"tp={stats['true_peak_db']} peak={stats['peak']} "
          f"silence={stats['silence_ratio']} dur={stats['duration_s']}s{flag}")
    print(f"           wav={stats['duration_s'] and wav.stat().st_size}B "
          f"ogg={ogg.stat().st_size}B")

with open(AUDIO / "render_stats.json", "w") as f:
    json.dump({"style": STYLE, "target_lufs": TARGET, "renders": results},
              f, indent=2)
print("DONE render")
