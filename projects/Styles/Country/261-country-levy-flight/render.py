# -*- coding: utf-8 -*-
"""Render + master + encode for 261-country-levy-flight (perfect/humanized/phase1)."""
import json
import subprocess
from pathlib import Path

import numpy as np

from utilities.env import fluidsynth_bin, soundfont_path
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

ROOT = Path("/opt/data/repos/musicom/projects/Styles/Country/261-country-levy-flight")
NAME = "261-country-levy-flight"
AUDIO = ROOT / "Audio"
AUDIO.mkdir(parents=True, exist_ok=True)
SF = soundfont_path()
FLUID = fluidsynth_bin()
STYLE = "Country"
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
    return rep


def stats_of(wav_path):
    audio, sr = read_wav(str(wav_path))
    mono = audio.mean(axis=1) if audio.ndim > 1 else audio
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    peak = float(np.max(np.abs(mono)))
    # per-second RMS map (mid-track gap detection)
    sec = sr
    n_sec = len(mono) // sec
    rms_per_sec = [float(np.sqrt(np.mean(mono[i*sec:(i+1)*sec]**2)))
                   for i in range(n_sec)]
    return {"silence_ratio": round(silent, 4), "peak": round(peak, 4),
            "duration_s": round(len(mono) / sr, 2),
            "rms_per_sec": [round(x, 4) for x in rms_per_sec]}


results = {}
for tag in ("perfect", "humanized", "phase1"):
    midi = ROOT / "MIDI" / f"{NAME}-{tag}.mid"
    wav = AUDIO / f"{NAME}-{tag}.wav"
    ogg = AUDIO / f"{NAME}-{tag}.ogg"
    render_midi(midi, wav)
    rep = master_wav(wav)
    st = stats_of(wav)
    st["integrated_lufs"] = round(rep["integrated_lufs"], 2)
    st["true_peak_db"] = round(rep["true_peak_db"], 2)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", str(wav), "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", str(ogg)],
                   check=True, capture_output=True, text=True)
    results[tag] = {"wav": str(wav), "ogg": str(ogg),
                    "wav_bytes": wav.stat().st_size, "ogg_bytes": ogg.stat().st_size,
                    **st}
    assert wav.stat().st_size > 40, f"{tag} wav empty"
    assert ogg.stat().st_size > 40, f"{tag} ogg empty"
    print(f"[{tag:9}] lufs={st['integrated_lufs']} tp={st['true_peak_db']} "
          f"peak={st['peak']} silence={st['silence_ratio']} dur={st['duration_s']}s")
    print(f"           wav={wav.stat().st_size}B ogg={ogg.stat().st_size}B")

with open(AUDIO / "render_stats.json", "w") as f:
    json.dump({"style": STYLE, "target_lufs": TARGET, "renders": results}, f, indent=2)
print("DONE render")
