# -*- coding: utf-8 -*-
"""Render audio for 105-african-contour via FluidSynth CLI + ffmpeg OGG.

Also computes silence ratio, per-second RMS, and a tonal-content (FFT) check
for both phases, and writes provenance sidecars for the audio artifacts.
"""
import os
import subprocess
import json
import wave
import numpy as np

from sound.render.fluidsynth import discover_soundfont
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/repos/musicom/projects/Styles/African/105-african-contour"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "105-african-contour.mid")
P1_MID = os.path.join(MIDI_DIR, "105-african-contour-phase1.mid")
P2_WAV = os.path.join(AUDIO_DIR, "105-african-contour.wav")
P2_OGG = os.path.join(AUDIO_DIR, "105-african-contour.ogg")
P1_WAV = os.path.join(AUDIO_DIR, "105-african-contour-phase1.wav")
P1_OGG = os.path.join(AUDIO_DIR, "105-african-contour-phase1.ogg")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def render_midi(mid_path, wav_path, ogg_path):
    sf2 = discover_soundfont()
    print(f"SoundFont: {sf2}")
    cmd = [FLUIDSYNTH, "-ni", "-g", "1.2", "-F", wav_path, sf2, mid_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FluidSynth error:", res.stderr)
        raise RuntimeError("FluidSynth failed")
    wav_size = os.path.getsize(wav_path)
    print(f"WAV: {wav_path} ({wav_size} bytes)")
    assert wav_size > 40, "WAV too small"

    ff_cmd = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libopus",
              "-b:a", "128k", "-v", "error", ogg_path]
    subprocess.run(ff_cmd, check=True)
    ogg_size = os.path.getsize(ogg_path)
    print(f"OGG: {ogg_path} ({ogg_size} bytes)")
    assert ogg_size > 40, "OGG too small"

    write_provenance(
        wav_path, classification=AI_ASSISTED,
        generator="musicom.sound.render.fluidsynth",
        parameters={"project": "105-african-contour", "format": "wav",
                    "soundfont": os.path.basename(sf2), "source_midi": os.path.basename(mid_path)})
    write_provenance(
        ogg_path, classification=AI_ASSISTED,
        generator="ffmpeg libopus",
        parameters={"project": "105-african-contour", "format": "ogg",
                    "codec": "libopus", "bitrate": "128k",
                    "source_midi": os.path.basename(mid_path)})


def analyze_wav(wav_path):
    with wave.open(wav_path, "rb") as wf:
        n_ch = wf.getnchannels()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if n_ch > 1:
        samples = samples.reshape(-1, n_ch).mean(axis=1)
    duration = len(samples) / sr
    silence_ratio = float(np.mean(np.abs(samples) < 0.001))
    peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
    rms_per_sec = []
    n_sec = int(np.ceil(duration))
    for s in range(n_sec):
        seg = samples[s * sr:(s + 1) * sr]
        rms_per_sec.append(round(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0, 4))

    # FFT tonal check in 50-1000 Hz per 0.5s window
    chunk = int(0.5 * sr)
    n_chunks = len(samples) // chunk
    tonal = 0
    for c in range(n_chunks):
        seg = samples[c * chunk:(c + 1) * chunk]
        w = np.hanning(len(seg))
        fft = np.abs(np.fft.rfft(seg * w))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        band = (freqs >= 50) & (freqs <= 1000)
        if np.any(band) and np.max(fft[band]) > 0.01:
            tonal += 1
    return {
        "duration_sec": round(duration, 2),
        "silence_ratio": round(silence_ratio, 4),
        "peak": round(peak, 4),
        "tonal_frames": f"{tonal}/{n_chunks}",
        "tonal_ratio": round(tonal / max(1, n_chunks), 4),
        "rms_per_sec": rms_per_sec,
    }


if __name__ == "__main__":
    print("--- Phase 2 ---")
    render_midi(P2_MID, P2_WAV, P2_OGG)
    p2 = analyze_wav(P2_WAV)
    print("Phase 2:", {k: v for k, v in p2.items() if k != "rms_per_sec"})

    print("\n--- Phase 1 ---")
    render_midi(P1_MID, P1_WAV, P1_OGG)
    p1 = analyze_wav(P1_WAV)
    print("Phase 1:", {k: v for k, v in p1.items() if k != "rms_per_sec"})

    with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump({"phase2": p2, "phase1": p1}, f, indent=2)
    print("\nRender stats -> Analysis/render_stats.json")
