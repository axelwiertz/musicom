# -*- coding: utf-8 -*-
"""Render + master + OGG encode for 283 (perfect + humanized + phase1)."""
import os
import subprocess
import json

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Baroque/283-baroque-cellular-automaton"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
SF = discover_soundfont()
STYLE = "baroque-classical"
TARGET = target_for_style(STYLE)
BASE = "283-baroque-cellular-automaton"


def render_one(tag, midi_path, out_prefix):
    wav_raw = os.path.join(AUDIO_DIR, f"{out_prefix}.raw.wav")
    wav_master = os.path.join(AUDIO_DIR, f"{out_prefix}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{out_prefix}.ogg")

    r = subprocess.run([FLUIDSYNTH, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                        "-F", wav_raw, SF, midi_path],
                       capture_output=True, text=True)
    assert os.path.getsize(wav_raw) > 40, f"fluidsynth produced empty: {wav_raw}"

    audio, sr = read_wav(wav_raw)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav_master, mastered, sr, normalize=False)

    mono = mastered.mean(axis=1) if mastered.ndim > 1 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

    # per-second RMS map (mid-track gaps > 30% silence = suspect)
    hop = sr
    nsec = len(mono) // hop
    rms_per_sec = [float(np.sqrt(np.mean(mono[i * hop:(i + 1) * hop] ** 2)))
                   for i in range(nsec)]
    mid_gap_secs = sum(1 for v in rms_per_sec[1:-1] if v < 0.005)

    r = subprocess.run([FFMPEG, "-y", "-loglevel", "error",
                        "-i", wav_master, "-codec:a", "libopus",
                        "-application", "voip", "-b:a", "48k", ogg],
                       capture_output=True, text=True)
    assert os.path.getsize(ogg) > 40, f"ffmpeg produced empty: {ogg}"

    os.remove(wav_raw)

    return {
        "tag": tag, "midi": midi_path, "wav": wav_master, "ogg": ogg,
        "wav_bytes": os.path.getsize(wav_master),
        "ogg_bytes": os.path.getsize(ogg),
        "sample_rate": sr, "target_lufs": TARGET,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "silence_ratio": round(silent, 4),
        "mid_gap_secs": mid_gap_secs,
        "duration_sec": round(len(mono) / sr, 2),
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
              f"peak={out[tag]['true_peak_db']} silence={out[tag]['silence_ratio']} "
              f"mid_gap={out[tag]['mid_gap_secs']}s", flush=True)
    with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("DONE. render_stats.json written.")
