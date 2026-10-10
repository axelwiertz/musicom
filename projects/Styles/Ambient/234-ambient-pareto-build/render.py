# -*- coding: utf-8 -*-
"""Render phase1 + phase2 MIDI -> WAV (FluidSynth) -> OGG (Opus) + silence/RMS profile."""
import json
import os
import subprocess
import sys

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "Audio")
ANALYSIS_DIR = os.path.join(BASE_DIR, "Analysis")
os.makedirs(AUDIO_DIR, exist_ok=True)

BASE = "234-ambient-pareto-build"
MIDI2 = os.path.join(BASE_DIR, "MIDI", BASE + ".mid")
MIDI1 = os.path.join(BASE_DIR, "MIDI", BASE + "-phase1.mid")

FLUIDSYNTH = os.environ.get("MUSICOM_FLUIDSYNTH") or "fluidsynth"


def discover_soundfont():
    try:
        from sound.render.fluidsynth import discover_soundfont as _d
        return _d()
    except Exception:
        pass
    for cand in [
        os.environ.get("MUSICOM_SOUNDFONT"),
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/share/sounds/sf3/FluidR3_GM.sf3",
        "/usr/share/sounds/sf2/TimGM6mb.sf2",
    ]:
        if cand and os.path.exists(cand):
            return cand
    raise RuntimeError("no soundfont found")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd)}\n{r.stderr}")
    return r


def render(midi, wav):
    run([FLUIDSYNTH, "-ni", "-g", "1.2", "-F", wav, sf2, midi])


def to_ogg(wav, ogg):
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg])


def profile(wav):
    # read WAV as int16 mono mix
    import wave
    with wave.open(wav, "rb") as w:
        nch = w.getnchannels()
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        a = a.reshape(-1, nch).mean(axis=1)
    silence = float(np.mean(np.abs(a) < 0.001))
    peak = float(np.abs(a).max())
    rms = float(np.sqrt(np.mean(a ** 2)))
    # per-second RMS map
    sec = max(1, int(len(a) / sr))
    per_sec = [float(np.sqrt(np.mean(a[i * sr:(i + 1) * sr] ** 2))) for i in range(sec)]
    return {"sr": sr, "samples": len(a), "seconds": round(len(a) / sr, 2),
            "silence_ratio": round(silence, 4), "peak": round(peak, 4),
            "rms_mean": round(rms, 4), "per_sec_rms": [round(x, 4) for x in per_sec],
            "mid_gaps": sum(1 for x in per_sec[1:-1] if x < 0.005)}


sf2 = discover_soundfont()
print("soundfont:", sf2)

out = {}
for tag, midi in [("phase2", MIDI2), ("phase1", MIDI1)]:
    wav = os.path.join(AUDIO_DIR, BASE + ("" if tag == "phase2" else "-phase1") + ".wav")
    ogg = os.path.join(AUDIO_DIR, BASE + ("" if tag == "phase2" else "-phase1") + ".ogg")
    render(midi, wav)
    to_ogg(wav, ogg)
    p = profile(wav)
    out[tag] = {"wav": wav, "ogg": ogg, "wav_size": os.path.getsize(wav),
                "ogg_size": os.path.getsize(ogg), "profile": p}
    print(f"[{tag}] wav={os.path.getsize(wav)}B ogg={os.path.getsize(ogg)}B "
          f"silence={p['silence_ratio']} peak={p['peak']} rms={p['rms_mean']} "
          f"mid_gaps={p['mid_gaps']}")

with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
    json.dump(out, f, indent=2)
print("wrote Analysis/render_stats.json")
