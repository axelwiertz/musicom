# -*- coding: utf-8 -*-
"""Render Audio for 101-folk-sieve.
Uses FluidSynth CLI with auto-discovered SoundFont (FluidR3_GM.sf2).
Converts to .ogg (Opus) via ffmpeg.
Computes silence ratio and per-second RMS profile.
"""
import os
import subprocess
import json
import wave
import numpy as np

from sound.render.fluidsynth import discover_soundfont

PROJ = "/opt/data/repos/musicom/projects/Styles/Folk/101-folk-sieve"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "101-folk-sieve.mid")
P1_MID = os.path.join(MIDI_DIR, "101-folk-sieve-phase1.mid")

P2_WAV = os.path.join(AUDIO_DIR, "101-folk-sieve.wav")
P2_OGG = os.path.join(AUDIO_DIR, "101-folk-sieve.ogg")
P1_WAV = os.path.join(AUDIO_DIR, "101-folk-sieve-phase1.wav")
P1_OGG = os.path.join(AUDIO_DIR, "101-folk-sieve-phase1.ogg")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

def render_midi(mid_path, wav_path, ogg_path):
    sf2 = discover_soundfont()
    print(f"Using SoundFont: {sf2}")
    
    # 1. Render WAV with FluidSynth CLI
    cmd = [
        FLUIDSYNTH,
        "-ni",
        "-g", "1.2",
        "-F", wav_path,
        sf2,
        mid_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FluidSynth error:", res.stderr)
        raise RuntimeError("FluidSynth failed")
        
    wav_size = os.path.getsize(wav_path)
    print(f"Rendered WAV: {wav_path} ({wav_size} bytes)")
    assert wav_size > 40, "WAV too small"
    
    # 2. Convert to Opus OGG with ffmpeg
    ff_cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-codec:a", "libopus",
        "-b:a", "128k",
        "-v", "error",
        ogg_path
    ]
    subprocess.run(ff_cmd, check=True)
    ogg_size = os.path.getsize(ogg_path)
    print(f"Rendered OGG: {ogg_path} ({ogg_size} bytes)")
    assert ogg_size > 40, "OGG too small"

def analyze_wav(wav_path):
    with wave.open(wav_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)
        
    samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)
        
    duration = len(samples) / sr
    # Silence ratio: samples with abs < 0.001
    silence_ratio = float(np.mean(np.abs(samples) < 0.001))
    
    # Per-second RMS profile
    sec_frames = sr
    rms_per_sec = []
    n_sec = int(np.ceil(duration))
    for s in range(n_sec):
        seg = samples[s * sec_frames : (s + 1) * sec_frames]
        if len(seg) > 0:
            rms = float(np.sqrt(np.mean(seg ** 2)))
            rms_per_sec.append(round(rms, 4))
        else:
            rms_per_sec.append(0.0)
            
    # FFT pitch check: check dominant frequency in 0.5s chunks between 50 and 1000 Hz
    chunk_frames = int(0.5 * sr)
    n_chunks = len(samples) // chunk_frames
    tonal_peaks = 0
    for c in range(n_chunks):
        seg = samples[c * chunk_frames : (c + 1) * chunk_frames]
        w = np.hanning(len(seg))
        fft_vals = np.abs(np.fft.rfft(seg * w))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        
        band = (freqs >= 50) & (freqs <= 1000)
        if np.any(band) and np.max(fft_vals[band]) > 0.01:
            tonal_peaks += 1
            
    tonal_ratio = float(tonal_peaks / max(1, n_chunks))
    
    return {
        "duration_sec": round(duration, 2),
        "silence_ratio": round(silence_ratio, 4),
        "tonal_frames_detected": f"{tonal_peaks} / {n_chunks}",
        "tonal_ratio": round(tonal_ratio, 4),
        "rms_per_sec": rms_per_sec
    }

if __name__ == "__main__":
    print("--- Rendering Phase 2 ---")
    render_midi(P2_MID, P2_WAV, P2_OGG)
    p2_analysis = analyze_wav(P2_WAV)
    print("Phase 2 Analysis:", {k: v for k, v in p2_analysis.items() if k != "rms_per_sec"})
    
    print("\n--- Rendering Phase 1 ---")
    render_midi(P1_MID, P1_WAV, P1_OGG)
    p1_analysis = analyze_wav(P1_WAV)
    print("Phase 1 Analysis:", {k: v for k, v in p1_analysis.items() if k != "rms_per_sec"})
    
    stats = {
        "phase2": p2_analysis,
        "phase1": p1_analysis
    }
    stats_path = os.path.join(ANALYSIS_DIR, "render_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nRender stats written to {stats_path}")
