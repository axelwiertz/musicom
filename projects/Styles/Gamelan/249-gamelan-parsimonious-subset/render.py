# -*- coding: utf-8 -*-
"""249 render + master: fluidsynth -> WAV -> master(LUFS) -> Opus OGG.

Renders phase1 + perfect + humanized. Each: FluidSynth (discover_soundfont)
-> WAV, then master() to the style's LUFS target, then ffmpeg Opus OGG.
Reports integrated LUFS / true-peak / silence ratio / per-second RMS gap.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import numpy as np  # noqa: E402

from utilities.env import fluidsynth_bin  # noqa: E402
from sound.render.fluidsynth import discover_soundfont  # noqa: E402
from sound.effects.mastering import master, target_for_style  # noqa: E402
from sound.utils.io import read_wav, write_wav  # noqa: E402

AUDIO_DIR = C.AUDIO_DIR
BASE = C.BASE
SF = discover_soundfont()
FLUID = fluidsynth_bin()


def silence_profile(audio):
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    # per-second RMS map
    sr = 44100
    rms = []
    for s in range(0, len(mono) - sr, sr):
        seg = mono[s:s + sr]
        rms.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
    gap_count = sum(1 for r in rms if r < 0.005)
    return {"silence_ratio": round(silent, 4),
            "per_second_rms": rms,
            "low_rms_seconds": gap_count,
            "n_seconds": len(rms)}


def render_and_master(midi_path, label):
    wav_path = os.path.join(AUDIO_DIR, f"{BASE}-{label}.wav")
    ogg_path = os.path.join(AUDIO_DIR, f"{BASE}-{label}.ogg")
    r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav_path, SF, midi_path],
                       capture_output=True, text=True)
    if r.returncode != 0 or os.path.getsize(wav_path) < 1000:
        raise RuntimeError(f"fluidsynth failed for {label}: {r.stderr[-500:]}")

    audio, sr = read_wav(wav_path)
    target = target_for_style(C.STYLE)          # 'gamelan' -> fallback -14.0
    mastered, rep = master(audio, target_lufs=target, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav_path, mastered, sr, normalize=False)

    prof = silence_profile(mastered)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                    "-codec:a", "libopus", "-b:a", "128k", ogg_path],
                   capture_output=True, text=True)
    return {
        "label": label,
        "midi": midi_path,
        "wav": wav_path,
        "ogg": ogg_path,
        "soundfont": SF,
        "target_lufs": target,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "wav_bytes": os.path.getsize(wav_path),
        "ogg_bytes": os.path.getsize(ogg_path),
        "sr": sr,
        "duration_s": round(len(mastered) / sr, 2),
        "silence_ratio": prof["silence_ratio"],
        "low_rms_seconds": prof["low_rms_seconds"],
        "n_seconds": prof["n_seconds"],
    }


def main():
    print("soundfont:", SF)
    print("fluidsynth:", FLUID)
    results = []
    for label, midi in [("phase1", C.PHASE1_PATH),
                        ("perfect", C.PERFECT_PATH),
                        ("humanized", C.HUMANIZED_PATH)]:
        res = render_and_master(midi, label)
        results.append(res)
        print(f"[{label}] target={res['target_lufs']} -> "
              f"LUFS={res['integrated_lufs']} dBTP={res['true_peak_db']} "
              f"dur={res['duration_s']}s silence={res['silence_ratio']} "
              f"low_rms_sec={res['low_rms_seconds']}/{res['n_seconds']}")
        print(f"        wav={res['wav_bytes']}B ogg={res['ogg_bytes']}B")
    with open(os.path.join(C.ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("wrote Analysis/render_stats.json")
    print("DONE")


if __name__ == "__main__":
    main()
