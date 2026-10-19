# -*- coding: utf-8 -*-
"""251 render — FluidSynth -> WAV -> MASTER (LUFS) -> Opus OGG.

Renders all three MIDIs (phase1 / perfect / humanized), masters each to the
style's genre LUFS target (target_for_style), encodes Opus OGG, and writes
render stats + per-artifact audio provenance.
"""
import json
import os
import subprocess

import numpy as np

from utilities.env import fluidsynth_bin, soundfont_path
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from workflows.provenance import write_provenance, AI_ASSISTED

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
BASE = "251-japanese-christoffel"
SR = 44100

STYLE = "japanese"
TARGET = target_for_style(STYLE)     # -14.0 (fallback; 'japanese' not in map)

FLUID = fluidsynth_bin()
SF = soundfont_path()


def silence_and_rms(audio):
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    secs = len(mono) / SR
    n_sec = max(1, int(secs))
    rms_map = []
    for i in range(n_sec):
        seg = mono[i * SR:(i + 1) * SR]
        rms_map.append(round(float(np.sqrt(np.mean(seg ** 2) + 1e-12)), 4))
    return silent, rms_map


def render_one(tag, midi_path):
    wav_path = os.path.join(AUDIO_DIR, f"{BASE}-{tag}.wav")
    ogg_path = os.path.join(AUDIO_DIR, f"{BASE}-{tag}.ogg")
    # 1. FluidSynth -> WAV
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav_path, SF, midi_path],
                   capture_output=True, text=True, check=True)
    # 2. master
    audio, sr = read_wav(wav_path)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav_path, mastered, sr, normalize=False)
    # 3. OGG (Opus)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    ogg_path], capture_output=True, text=True, check=True)
    silent, rms_map = silence_and_rms(mastered)
    return {
        "tag": tag,
        "wav": wav_path,
        "ogg": ogg_path,
        "wav_bytes": os.path.getsize(wav_path),
        "ogg_bytes": os.path.getsize(ogg_path),
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "silence_ratio": silent,
        "rms_per_sec": rms_map,
        "sample_rate": sr,
        "duration_s": round(len(mastered) / sr, 2),
    }


if __name__ == "__main__":
    os.makedirs(AUDIO_DIR, exist_ok=True)
    jobs = [
        ("phase1", os.path.join(MIDI_DIR, BASE + "-phase1.mid")),
        ("perfect", os.path.join(MIDI_DIR, BASE + "-perfect.mid")),
        ("humanized", os.path.join(MIDI_DIR, BASE + "-humanized.mid")),
    ]
    stats = {}
    for tag, mp in jobs:
        print(f"[render] {tag} -> fluidsynth ...", flush=True)
        r = render_one(tag, mp)
        stats[tag] = r
        print(f"[ok] {tag}: LUFS={r['integrated_lufs']} dBTP={r['true_peak_db']} "
              f"silence={r['silence_ratio']:.3f} dur={r['duration_s']}s "
              f"wav={r['wav_bytes']}B ogg={r['ogg_bytes']}B", flush=True)
        write_provenance(
            r["wav"], classification=AI_ASSISTED,
            generator=f"FluidSynth + master(target={TARGET} LUFS) - 251 CWCC",
            parameters={"tag": tag, "style": STYLE, "target_lufs": TARGET,
                        "integrated_lufs": r["integrated_lufs"],
                        "true_peak_db": r["true_peak_db"],
                        "soundfont": os.path.basename(SF)},
            notes=f"Mastered render of {tag} (SoundFont render, LUFS-normalized, "
                  "-1 dBTP ceiling).")
    stats["target_lufs"] = TARGET
    stats["soundfont"] = SF
    stats["style"] = STYLE
    with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print("[OK] render_stats.json written.")
