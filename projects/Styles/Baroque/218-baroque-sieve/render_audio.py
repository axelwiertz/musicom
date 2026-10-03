# -*- coding: utf-8 -*-
"""Render 218-baroque-sieve MIDI -> WAV -> OGG (Opus).
FluidSynth CLI + discover_soundfont(). Computes silence ratio + per-second RMS.
Writes Analysis/render_stats.json.
"""
import os
import subprocess
import json
import wave
import numpy as np

from sound.render.fluidsynth import discover_soundfont

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/218-baroque-sieve"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "218-baroque-sieve.mid")
P2_WAV = os.path.join(AUDIO_DIR, "218-baroque-sieve.wav")
P2_OGG = os.path.join(AUDIO_DIR, "218-baroque-sieve.ogg")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def render(mid_path, wav_path, ogg_path):
    sf2 = discover_soundfont()
    print("SoundFont:", sf2)
    cmd = [FLUIDSYNTH, "-ni", "-g", "1.2", "-F", wav_path, sf2, mid_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FluidSynth stderr:", r.stderr[-2000:])
        raise RuntimeError("FluidSynth failed")
    assert os.path.getsize(wav_path) > 40, "WAV empty"
    ff = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libopus",
          "-b:a", "128k", "-v", "error", ogg_path]
    subprocess.run(ff, check=True)
    assert os.path.getsize(ogg_path) > 40, "OGG empty"
    print("WAV", os.path.getsize(wav_path), "bytes; OGG", os.path.getsize(ogg_path), "bytes")


def analyze(wav_path):
    with wave.open(wav_path, 'rb') as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        nf = wf.getnframes()
        raw = wf.readframes(nf)
    s = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        s = s.reshape(-1, nch).mean(axis=1)
    dur = len(s) / sr
    silence = float(np.mean(np.abs(s) < 0.001))
    peak = float(np.max(np.abs(s))) if len(s) else 0.0
    rms_per_sec = []
    for k in range(int(np.ceil(dur))):
        seg = s[k * sr:(k + 1) * sr]
        rms_per_sec.append(round(float(np.sqrt(np.mean(seg ** 2))), 4) if len(seg) else 0.0)
    return {"duration_sec": round(dur, 2), "silence_ratio": round(silence, 4),
            "peak": round(peak, 4), "rms_per_sec": rms_per_sec}


if __name__ == "__main__":
    os.makedirs(AUDIO_DIR, exist_ok=True)
    render(P2_MID, P2_WAV, P2_OGG)
    stats = analyze(P2_WAV)
    print("Analysis:", {k: v for k, v in stats.items() if k != "rms_per_sec"})
    with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print("wrote Analysis/render_stats.json")
