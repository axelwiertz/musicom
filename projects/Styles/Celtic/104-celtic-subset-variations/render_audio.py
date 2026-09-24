#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Render 104-celtic-subset-variations MIDI -> WAV (FluidSynth CLI) -> OGG (Opus)."""
import os, subprocess, json
import numpy as np
from sound.render.fluidsynth import discover_soundfont

PROJ = "/opt/data/projects/Styles/Celtic/104-celtic-subset-variations"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SF = discover_soundfont()
FLUID = os.environ.get("MUSICOM_FLUIDSYNTH", "fluidsynth")

jobs = [
    ("104-celtic-subset-variations.mid", "104-celtic-subset-variations"),
    ("104-celtic-subset-variations-phase1.mid", "104-celtic-subset-variations-phase1"),
]

stats = {}
for mid_name, base in jobs:
    mid_path = os.path.join(MIDI_DIR, mid_name)
    wav_path = os.path.join(AUDIO_DIR, base + ".wav")
    ogg_path = os.path.join(AUDIO_DIR, base + ".ogg")
    # FluidSynth CLI render
    r = subprocess.run(
        [FLUID, "-ni", "-g", "1.2", "-F", wav_path, SF, mid_path],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("fluidsynth failed: " + r.stderr[-2000:])
    # Opus encode
    r2 = subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libopus",
         "-application", "voip", "-b:a", "48k", ogg_path],
        capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError("ffmpeg failed: " + r2.stderr[-2000:])
    # silence / peak stats via numpy
    import wave
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
    mono = np.frombuffer(raw, dtype=np.int16)[::2].astype(np.float32) / 32768.0
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    # per-second RMS map (first 8 sec + min)
    seg = int(sr)
    per_sec = [float(np.sqrt(np.mean(mono[i*seg:(i+1)*seg]**2)))
               for i in range(len(mono)//seg)]
    stats[base] = {
        "wav_bytes": os.path.getsize(wav_path),
        "ogg_bytes": os.path.getsize(ogg_path),
        "silence_ratio": round(silent, 4),
        "peak": round(peak, 4),
        "rms": round(rms, 4),
        "duration_s": round(n / sr, 2),
        "min_rms_sec": round(min(per_sec), 4),
        "n_low_rms_secs": sum(1 for x in per_sec if x < 0.002),
        "soundfont": os.path.basename(SF),
    }
    print(f"{base}: wav={stats[base]['wav_bytes']} ogg={stats[base]['ogg_bytes']} "
          f"silence={stats[base]['silence_ratio']} peak={stats[base]['peak']} "
          f"dur={stats[base]['duration_s']}s")

with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(stats, f, indent=2)
print("\nRENDER DONE. Silence > 30% flags:",
      [k for k, v in stats.items() if v["silence_ratio"] > 0.30])
