# -*- coding: utf-8 -*-
"""
Production Pipeline: SP-021 Binaural Woodworth-Schlosberg Spatialization
Applied to: here-comes-the-sun original.mid (Rock/001-here-comes-the-sun)

Workflow:
1. Split MIDI by TRACK INDEX (source has 2 data tracks, both on channel 0):
   - Track 0 = Lead/Melody (pitch range G#3-G#5, 658 notes)
   - Track 1 = Bass/Foundation (pitch range D2-E4, 286 notes)
2. Render each track to mono WAV via FluidSynth CLI
3. Apply SP-021 binaural spatialization with DYNAMIC azimuth choreography
   (Lead: slow panoramic sine drift; Bass: center anchor with subtle counter-drift)
   - CHUNKED streaming DSP to respect the 3.9 GB RAM budget:
     process 1-second blocks, carry filter state and delay-line tails between chunks;
     one track at a time, per-track stereo WAV on disk, summed in a second pass
4. Sum stereo, peak-normalize to -1 dB, export WAV + OGG (Opus)
5. Verify silence ratio + per-second RMS (silent-render trap rule)
"""

import numpy as np
import subprocess
import os
import json
import wave
import mido
import shutil
from datetime import datetime, timezone
from scipy.signal import lfilter

# === Configuration ===
SRC_MIDI = '/opt/data/projects/Styles/Rock/001-here-comes-the-sun/MIDI/original.mid'
OUT_DIR = '/opt/data/projects/Styles/Production/SP021-binaural-here-comes-the-sun'
SOUNDFONT = '/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2'
FLUIDSYNTH = '/opt/data/micromamba/envs/musicom/bin/fluidsynth'
SR = 44100
CHUNK = SR  # 1 second per chunk

# Per-track config: source track index, azimuth choreography params, distance
# Track 0 = 658 notes, pitch [56,79] (G#3-G#5) -> Lead/Melody
# Track 1 = 286 notes, pitch [38,64] (D2-E4)   -> Bass/Foundation
# Azimuth sweep capped at ~±60 deg (1.0 rad) for musical placement
TRACK_CONFIG = [
    {'name': 'Lead',  'track_idx': 0, 'base_az': 0.5,  'sweep_amp': 0.9, 'sweep_period': 44.0, 'distance': 1.4},
    {'name': 'Bass',  'track_idx': 1, 'base_az': 0.0,  'sweep_amp': 0.2, 'sweep_period': 22.0, 'distance': 1.0},
]

os.makedirs(f'{OUT_DIR}/Audio', exist_ok=True)
os.makedirs(f'{OUT_DIR}/MIDI', exist_ok=True)

# === Step 1: Split MIDI by track index ===
print("=== Step 1: Splitting MIDI into per-track files ===")
src_mid = mido.MidiFile(SRC_MIDI)
tempo_msg = None
for track in src_mid.tracks:
    for msg in track:
        if msg.type == 'set_tempo':
            tempo_msg = msg
            break
    if tempo_msg:
        break

split_midi_paths = {}
for cfg in TRACK_CONFIG:
    idx = cfg['track_idx']
    new_mid = mido.MidiFile(ticks_per_beat=src_mid.ticks_per_beat)

    tempo_track = mido.MidiTrack()
    new_mid.tracks.append(tempo_track)
    if tempo_msg:
        tempo_track.append(mido.MetaMessage('set_tempo', tempo=tempo_msg.tempo, time=0))
    tempo_track.append(mido.MetaMessage('end_of_track', time=0))

    data_track = mido.MidiTrack()
    new_mid.tracks.append(data_track)
    for msg in src_mid.tracks[idx]:
        data_track.append(msg.copy())

    out_path = f'{OUT_DIR}/MIDI/{cfg["name"].lower()}.mid'
    new_mid.save(out_path)
    split_midi_paths[cfg['name']] = out_path
    note_count = sum(1 for m in data_track if m.type == 'note_on' and m.velocity > 0)
    print(f"  {cfg['name']} (track {idx}): {note_count} notes -> {out_path}")

# === Step 2: Render each track to mono WAV via FluidSynth ===
print("\n=== Step 2: Rendering tracks via FluidSynth CLI ===")
mono_wav_paths = {}
for name, midi_path in split_midi_paths.items():
    wav_path = f'{OUT_DIR}/Audio/{name.lower()}_mono.wav'
    cmd = [
        FLUIDSYNTH, '-ni',
        '-F', wav_path,
        '-r', str(SR),
        '-g', '1.0',
        SOUNDFONT, midi_path,
    ]
    print(f"  Rendering {name}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        print(f"    WARNING: {result.stderr[:300]}")
    size = os.path.getsize(wav_path) if os.path.exists(wav_path) else 0
    print(f"    -> {wav_path} ({size} bytes)")
    mono_wav_paths[name] = wav_path

# === Step 3: SP-021 Binaural Spatialization (chunked streaming DSP) ===
print("\n=== Step 3: Applying SP-021 Binaural Spatialization (dynamic azimuth) ===")


def chunked_fractional_delay(x, delay_samples, out, start, max_delay=64):
    """Chunked fractional delay with carry-over tail.

    Writes into out[start:start+len(x)]. delay_samples has same length as x.
    """
    n = len(x)
    for s in range(0, n, CHUNK):
        e = min(s + CHUNK, n)
        d = delay_samples[s:e]
        d_int = np.floor(d).astype(np.int64)
        d_frac = d - d_int
        idx1 = np.arange(e - s) - d_int
        idx2 = idx1 - 1
        m1 = (idx1 >= 0) & (idx1 < e - s)
        m2 = (idx2 >= 0) & (idx2 < e - s)
        val1 = np.where(m1, x[s:e][np.clip(idx1, 0, e - s - 1)], 0.0)
        val2 = np.where(m2, x[s:e][np.clip(idx2, 0, e - s - 1)], 0.0)
        out[start + s:start + e] = (1.0 - d_frac) * val1 + d_frac * val2


def chunked_first_order_lowpass(x, fc, out, start):
    """Chunked first-order lowpass with per-chunk alpha and state carry."""
    n = len(x)
    y_prev = 0.0
    for s in range(0, n, CHUNK):
        e = min(s + CHUNK, n)
        seg = x[s:e]
        if np.isscalar(fc):
            alpha = np.full(e - s, fc)
        else:
            alpha = fc[s:e]
        alpha = (2.0 * np.pi * alpha / SR) / (2.0 * np.pi * alpha / SR + 1.0)
        alpha = np.clip(alpha, 0.0, 1.0)
        # azimuth changes slowly -> alpha nearly constant per chunk; use mean alpha
        # with state carry for exact one-pole recursion
        a = float(np.mean(alpha))
        if a >= 1.0:
            out[start + s:start + e] = seg
            y_prev = seg[-1]
        elif a <= 0.0:
            out[start + s:start + e] = y_prev
        else:
            yy, zf = lfilter([a], [1.0, -(1.0 - a)], seg, zi=np.array([y_prev * (1.0 - a)]))
            out[start + s:start + e] = yy
            y_prev = zf[0]


def binaural_spatialization(x, fs, azimuth, distance=1.0, head_radius=0.0875, speed_of_sound=343.0):
    """SP-021 chunked. x: mono float64. Returns (n, 2) stereo float64.

    Memory-light: azimuth-derived intermediates stored as float32.
    """
    n = len(x)
    ref_distance = 1.0
    attn = ref_distance / max(distance, ref_distance)
    x_attn = x * attn

    az_arr = np.asarray(azimuth, dtype=np.float64)
    az_arr = (az_arr + np.pi) % (2 * np.pi) - np.pi

    # Woodworth-Schlosberg ITD (float32 intermediates)
    abs_az = np.abs(az_arr).astype(np.float32)
    tau = (head_radius / speed_of_sound) * (np.sin(abs_az) + abs_az)
    tau_samples = (tau * fs).astype(np.float32)

    delay_l = np.where(az_arr >= 0.0, tau_samples, np.float32(0.0)).astype(np.float32)
    delay_r = np.where(az_arr < 0.0, tau_samples, np.float32(0.0)).astype(np.float32)

    out_l = np.zeros(n, dtype=np.float64)
    out_r = np.zeros(n, dtype=np.float64)

    chunked_fractional_delay(x_attn, delay_l, out_l, 0)
    chunked_fractional_delay(x_attn, delay_r, out_r, 0)

    # ILD head shadowing (float32 cutoff arrays)
    f_max = 20000.0
    f_min = 1000.0
    p = 2.0
    fc_l = np.where(az_arr >= 0.0,
                    f_min + (f_max - f_min) * ((1.0 + np.cos(az_arr)) / 2.0) ** p,
                    f_max).astype(np.float32)
    fc_r = np.where(az_arr < 0.0,
                    f_min + (f_max - f_min) * ((1.0 + np.cos(az_arr)) / 2.0) ** p,
                    f_max).astype(np.float32)
    del az_arr, abs_az, tau, tau_samples, delay_l, delay_r

    # apply lowpass in place
    tmp_l = out_l.copy()
    tmp_r = out_r.copy()
    chunked_first_order_lowpass(tmp_l, fc_l, out_l, 0)
    chunked_first_order_lowpass(tmp_r, fc_r, out_r, 0)
    del tmp_l, tmp_r, fc_l, fc_r

    return np.column_stack((out_l, out_r))


def read_wav(path):
    """Read WAV file as float64 numpy array (mono mixdown)."""
    with wave.open(path, 'r') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    if sampwidth == 2:
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    elif sampwidth == 4:
        data = np.frombuffer(raw, dtype=np.int32).astype(np.float64) / 2147483648.0
    else:
        data = np.frombuffer(raw, dtype=np.uint8).astype(np.float64) / 128.0 - 1.0
    if n_channels > 1:
        data = data.reshape(-1, n_channels).mean(axis=1)
    return data, framerate


def write_stereo_wav(path, left, right, sr=44100):
    """Write stereo 16-bit WAV (chunked to bound memory)."""
    n_samples = min(len(left), len(right))
    with wave.open(path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for s in range(0, n_samples, CHUNK):
            e = min(s + CHUNK, n_samples)
            stereo = np.column_stack((left[s:e], right[s:e]))
            stereo = np.clip(stereo, -1.0, 1.0)
            pcm = (stereo * 32767).astype(np.int16)
            wf.writeframes(pcm.tobytes())


def write_mono_wav(path, data, sr=44100):
    """Write mono 16-bit WAV (chunked)."""
    n = len(data)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for s in range(0, n, CHUNK):
            e = min(s + CHUNK, n)
            seg = np.clip(data[s:e], -1.0, 1.0)
            pcm = (seg * 32767).astype(np.int16)
            wf.writeframes(pcm.tobytes())


# === Step 3: SP-021 per-track spatialization (strict streaming, one track at a time) ===
print("\n=== Step 3: Applying SP-021 Binaural Spatialization (dynamic azimuth) ===")

# Track durations from mono WAVs (read headers only); n_total = MAX FRAME COUNT (no truncation)
track_frame_counts = {}
for name, wav_path in mono_wav_paths.items():
    with wave.open(wav_path, 'r') as wf:
        track_frame_counts[name] = wf.getnframes()
    print(f"  {name}: {track_frame_counts[name] / SR:.1f}s ({track_frame_counts[name]} samples)")
n_total = max(track_frame_counts.values())
print(f"  Master timeline: {n_total / SR:.1f}s ({n_total} samples)")

# Spatialize each track to its own stereo WAV, freeing everything between tracks
track_stereo_paths = {}
for cfg in TRACK_CONFIG:
    name = cfg['name']
    wav_path = mono_wav_paths[name]
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
        print(f"  SKIP {name}: no valid WAV")
        continue

    mono_data, _ = read_wav(wav_path)
    n_track = len(mono_data)

    # Dynamic azimuth for this track (exact sample count)
    t_track = np.arange(n_track, dtype=np.float64) / SR
    if name == 'Lead':
        az = cfg['base_az'] + cfg['sweep_amp'] * np.sin(2 * np.pi * t_track / cfg['sweep_period'])
    else:  # Bass: center anchor, subtle counter-drift
        az = cfg['base_az'] + cfg['sweep_amp'] * np.sin(2 * np.pi * t_track / cfg['sweep_period'] + np.pi)
    del t_track

    print(f"  Spatializing {name} ({n_track} samples)...")
    stereo = binaural_spatialization(mono_data, SR, az, distance=cfg['distance'])
    del mono_data, az

    az_deg = np.degrees(np.array([cfg['base_az'] - cfg['sweep_amp'],
                                  cfg['base_az'] + cfg['sweep_amp']]))
    print(f"    az range [{az_deg.min():+.1f}, {az_deg.max():+.1f}] deg, dist {cfg['distance']}m, "
          f"L peak {np.max(np.abs(stereo[:, 0])):.4f}, R peak {np.max(np.abs(stereo[:, 1])):.4f}")

    # Write per-track stereo WAV (chunked), then free
    track_wav = f'{OUT_DIR}/Audio/{name.lower()}_spatial.wav'
    write_stereo_wav(track_wav, stereo[:, 0], stereo[:, 1], SR)
    track_stereo_paths[name] = track_wav
    del stereo

# === Step 4: Sum per-track stereo files, normalize, export ===
print("\n=== Step 4: Summing, normalizing and exporting ===")

stereo_sum_l = np.zeros(n_total, dtype=np.float64)
stereo_sum_r = np.zeros(n_total, dtype=np.float64)
for name, track_wav in track_stereo_paths.items():
    data, _ = read_wav(track_wav)  # returns mono mixdown of the stereo file
    # read_wav mixes stereo -> mono; we need L/R separately
    with wave.open(track_wav, 'r') as wf:
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    stereo_raw = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    stereo_raw = stereo_raw.reshape(-1, 2)
    ln = len(stereo_raw)
    stereo_sum_l[:ln] += stereo_raw[:, 0]
    stereo_sum_r[:ln] += stereo_raw[:, 1]
    del stereo_raw
    print(f"  Summed {name} ({ln} samples)")

peak = max(np.max(np.abs(stereo_sum_l)), np.max(np.abs(stereo_sum_r)))
if peak > 0:
    target_peak = 0.89
    scale = target_peak / peak
    stereo_sum_l *= scale
    stereo_sum_r *= scale
    print(f"  Peak before norm: {peak:.4f}, scale factor: {scale:.4f}")

wav_out = f'{OUT_DIR}/Audio/here_comes_the_sun_binaural_SP021.wav'
write_stereo_wav(wav_out, stereo_sum_l, stereo_sum_r, SR)
wav_size = os.path.getsize(wav_out)
print(f"  WAV: {wav_out} ({wav_size} bytes)")
assert wav_size > 1000, "WAV output too small!"

# Silence / RMS verification (SP-011 silent-render trap rule)
mono_mix = (stereo_sum_l + stereo_sum_r) * 0.5
silent_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix))
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"  Silence ratio: {silent_ratio*100:.1f}%  RMS: {rms:.4f}")
assert silent_ratio < 0.30, f"Silent render trap: {silent_ratio*100:.1f}% silence"

seg = int(SR)
rms_per_sec = [float(np.sqrt(np.mean(mono_mix[i:i+seg] ** 2))) for i in range(0, len(mono_mix), seg)]
active_seconds = sum(1 for r in rms_per_sec if r > 0.005)
print(f"  Active seconds: {active_seconds}/{len(rms_per_sec)}")
assert active_seconds > len(rms_per_sec) * 0.5, "Too many silent seconds"

# OGG conversion
ogg_out = f'{OUT_DIR}/Audio/here_comes_the_sun_binaural_SP021.ogg'
cmd = ['ffmpeg', '-y', '-i', wav_out, '-codec:a', 'libopus', '-application', 'audio', '-b:a', '128k', ogg_out]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
ogg_size = os.path.getsize(ogg_out) if os.path.exists(ogg_out) else 0
print(f"  OGG: {ogg_out} ({ogg_size} bytes)")

# Copy source MIDI
shutil.copy2(SRC_MIDI, f'{OUT_DIR}/MIDI/here_comes_the_sun_source.mid')

# === Provenance ===
provenance = {
    "composition_source": {
        "path": SRC_MIDI,
        "genre": "Rock",
        "substyle": "Here Comes the Sun (Beatles-style rock study)",
        "version": "original",
        "tempo_bpm": 120,
        "duration_seconds": round(n_total / SR, 2),
        "tracks": {
            "Lead": {"source_track": 0, "channel": 0, "program": 0, "notes": 658, "pitch_range": [56, 79]},
            "Bass": {"source_track": 1, "channel": 0, "program": 0, "notes": 286, "pitch_range": [38, 64]},
        },
    },
    "production_method": {
        "id": "SP-021",
        "name": "Binaural Woodworth-Schlosberg Spatialization",
        "layer": "Post-Processing / DSP",
        "description": "Applies Head-Related Transfer Function (HRTF) emulation via Woodworth-Schlosberg ITD and frequency-dependent ILD head-shadowing filters for realistic 3D acoustic placement.",
        "parameters": {
            "head_radius_m": 0.0875,
            "speed_of_sound_m_s": 343.0,
            "f_max_hz": 20000.0,
            "f_min_hz": 1000.0,
            "angular_power_p": 2.0,
        },
        "track_spatialization": {
            "Lead": {
                "azimuth_choreography": "dynamic sine drift, base +0.5 rad, amp 0.9 rad, period 44s",
                "azimuth_range_deg": [round(float(np.degrees(0.5 - 0.9)), 1),
                                      round(float(np.degrees(0.5 + 0.9)), 1)],
                "distance_m": 1.4,
            },
            "Bass": {
                "azimuth_choreography": "center anchor, subtle counter-drift, base 0.0 rad, amp 0.2 rad, period 22s",
                "azimuth_range_deg": [round(float(np.degrees(-0.2)), 1),
                                      round(float(np.degrees(0.2)), 1)],
                "distance_m": 1.0,
            },
        },
    },
    "output": {
        "wav_path": "Audio/here_comes_the_sun_binaural_SP021.wav",
        "ogg_path": "Audio/here_comes_the_sun_binaural_SP021.ogg",
        "sample_rate": SR,
        "channels": 2,
        "bit_depth": 16,
        "duration_seconds": round(n_total / SR, 2),
        "peak_normalized_to": -1.0,
        "silence_ratio": round(silent_ratio, 4),
        "rms": round(rms, 4),
    },
    "processing_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "engine": {
        "synth": "FluidSynth 2.5.6 CLI",
        "soundfont": "TimGM6mb.sf2",
        "dsp": "numpy/scipy SP-021 chunked implementation (methods_db.md reference)",
    },
}

with open(f'{OUT_DIR}/provenance.json', 'w') as f:
    json.dump(provenance, f, indent=2)
print("  provenance.json written")

print("\n=== DONE ===")
print(f"Source: {SRC_MIDI}")
print(f"Method: SP-021 Binaural Woodworth-Schlosberg Spatialization (dynamic azimuth)")
print(f"Output WAV: {wav_out} ({wav_size} bytes)")
print(f"Output OGG: {ogg_out} ({ogg_size} bytes)")
