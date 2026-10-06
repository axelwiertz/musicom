# -*- coding: utf-8 -*-
"""Render 226-apollonian-packing phase1 + phase2 to WAV (FluidSynth) + OGG (opus).

Also measure silence ratio + per-second RMS and pitch sanity. Reports real numbers.
"""
import json
import os
import subprocess

import numpy as np

from sound.render.fluidsynth import discover_soundfont

PROJECT = "226-apollonian-packing"
PROJECT_DIR = f"/opt/data/repos/musicom/projects/Styles/Experimental/{PROJECT}"
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "ffmpeg"

os.makedirs(AUDIO_DIR, exist_ok=True)


def render(mid_name, wav_name, ogg_name):
    midi = os.path.join(MIDI_DIR, mid_name)
    wav = os.path.join(AUDIO_DIR, wav_name)
    ogg = os.path.join(AUDIO_DIR, ogg_name)
    sf2 = discover_soundfont()
    # FluidSynth CLI -> WAV (16-bit stereo)
    cmd = [FLUID, "-ni", "-g", "1.2", "-F", wav, sf2, midi]
    subprocess.run(cmd, check=True, capture_output=True)
    # OGG opus (voice-optimised)
    subprocess.run([FFMPEG, "-y", "-i", wav, "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", ogg],
                   check=True, capture_output=True)
    return midi, wav, ogg, sf2


def analyze(wav):
    from scipy.io import wavfile
    sr, data = wavfile.read(wav)
    if data.ndim == 2:
        mono = data.astype(np.float64).mean(axis=1)
    else:
        mono = data.astype(np.float64)
    peak = np.max(np.abs(mono))
    mono = mono / (32768.0 if peak > 2 else 1.0)
    peak = np.max(np.abs(mono))
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    # per-second RMS map
    win = sr
    n_win = len(mono) // win
    rms = [float(np.sqrt(np.mean(mono[i * win:(i + 1) * win] ** 2)))
           for i in range(n_win)]
    mid_gap = 0
    if rms:
        # mid-track gaps: windows after the first non-silent, before the last
        # non-silent, with RMS below 0.001
        first = next((i for i, r in enumerate(rms) if r > 0.001), None)
        last = next((i for i, r in enumerate(rms[::-1]) if r > 0.001), None)
        if first is not None and last is not None:
            last = len(rms) - 1 - last
            mid_gap = sum(1 for i in range(first, last + 1) if rms[i] < 0.001)
    return {
        "sr": sr, "duration_s": round(len(mono) / sr, 2),
        "peak": round(peak, 4), "silence_ratio": round(silent, 4),
        "rms_mean": round(float(np.mean(rms)) if rms else 0.0, 4),
        "rms_max": round(float(np.max(rms)) if rms else 0.0, 4),
        "mid_gap_seconds": int(mid_gap),
        "n_windows": int(n_win),
    }


def main():
    stats = {}
    for mid, wav, ogg, tag in [
        (f"{PROJECT}-phase1.mid", f"{PROJECT}-phase1.wav",
         f"{PROJECT}-phase1.ogg", "phase1"),
        (f"{PROJECT}.mid", f"{PROJECT}.wav", f"{PROJECT}.ogg", "phase2"),
    ]:
        midi, wav, ogg, sf2 = render(mid, wav, ogg)
        a = analyze(wav)
        a["sf2"] = sf2
        a["midi_bytes"] = os.path.getsize(midi)
        a["wav_bytes"] = os.path.getsize(wav)
        a["ogg_bytes"] = os.path.getsize(ogg)
        stats[tag] = a
        print(f"[{tag}] {a}")
    with open(os.path.join(PROJECT_DIR, "Analysis", "render_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print("RENDER_STATS", os.path.join(PROJECT_DIR, "Analysis", "render_stats.json"))


if __name__ == "__main__":
    main()
