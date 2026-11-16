# -*- coding: utf-8 -*-
"""Render + master + OGG-encode MIDI versions for 307-balkan-christoffel-suite."""
import os
import subprocess
import json
import numpy as np

from utilities.env import fluidsynth_bin, soundfont_path
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

PROJ = "/opt/data/projects/Styles/Balkan/307-balkan-christoffel-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

STYLE = "balkan"
SF = soundfont_path()
FLUID = fluidsynth_bin()
TARGET = target_for_style(STYLE)

print("soundfont:", SF)
print("fluidsynth:", FLUID)
print("LUFS target (%s):" % STYLE, TARGET)


def render_midi(midi_path, wav_path):
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav_path, SF, midi_path],
                   check=True, capture_output=True, text=True)
    assert os.path.getsize(wav_path) > 40, "empty wav: %s" % wav_path


def master_wav(wav_path):
    audio, sr = read_wav(wav_path)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav_path, mastered, sr, normalize=False)
    mono = mastered if mastered.ndim == 1 else mastered.mean(axis=1)
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    return rep, silent


def to_ogg(wav_path, ogg_path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    ogg_path], check=True, capture_output=True, text=True)
    assert os.path.getsize(ogg_path) > 40, "empty ogg: %s" % ogg_path


results = {}
for ver in ("phase1", "perfect", "humanized"):
    midi = os.path.join(MIDI_DIR, "307-balkan-christoffel-suite-%s.mid" % ver)
    wav = os.path.join(AUDIO_DIR, "307-balkan-christoffel-suite-%s.wav" % ver)
    ogg = os.path.join(AUDIO_DIR, "307-balkan-christoffel-suite-%s.ogg" % ver)
    print("\n=== %s ===" % ver, flush=True)
    render_midi(midi, wav)
    print("  rendered wav:", os.path.getsize(wav), "bytes", flush=True)
    rep, silent = master_wav(wav)
    print("  mastered: LUFS=%.2f dBTP=%.2f silence=%.1f%%" %
          (rep["integrated_lufs"], rep["true_peak_db"], silent * 100.0), flush=True)
    to_ogg(wav, ogg)
    print("  ogg:", os.path.getsize(ogg), "bytes", flush=True)
    results[ver] = {"wav": wav, "ogg": ogg,
                    "integrated_lufs": rep["integrated_lufs"],
                    "true_peak_db": rep["true_peak_db"],
                    "silence_ratio": silent}

with open(os.path.join(AUDIO_DIR, "master_stats.json"), "w") as f:
    json.dump({k: {kk: (vv if not isinstance(vv, float) else vv) for kk, vv in v.items()}
               for k, v in results.items()}, f, indent=2, default=str)

print("\nRESULTS:")
for ver, r in results.items():
    print("  %s: LUFS %.2f dBTP %.2f silence %.1f%%" %
          (ver, r["integrated_lufs"], r["true_peak_db"], r["silence_ratio"] * 100.0))
    print("    ogg:", r["ogg"])
print("\nDONE render.")
