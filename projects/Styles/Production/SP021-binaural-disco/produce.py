# -*- coding: utf-8 -*-
"""
Production Pipeline: SP-021 Binaural Woodworth-Schlosberg Spatialization
Applied to: classic_disco.mid (Disco/classic/v1)

Workflow:
1. Split MIDI into per-track files (Drums, Bass, Strings, Lead)
2. Render each track to mono WAV via FluidSynth CLI
3. Apply SP-021 binaural spatialization per track with unique azimuth
4. Sum stereo, normalize, export WAV + OGG
"""

import numpy as np
import subprocess
import os
import json
import wave
import struct
import mido
from pathlib import Path

# === Configuration ===
SRC_MIDI = '/opt/data/projects/Styles/Disco/classic/v1/classic_disco.mid'
OUT_DIR = '/opt/data/projects/Styles/Production/SP021-binaural-disco'
SOUNDFONT = '/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2'
FLUIDSYNTH = '/opt/data/micromamba/envs/musicom/bin/fluidsynth'
SR = 44100

# Track azimuth assignments (radians): Drums wide, Bass center, Strings left, Lead right
TRACK_CONFIG = {
    'Drums':   {'channel': 9,  'azimuth':  0.0,   'distance': 1.5},  # center, slightly back
    'Bass':    {'channel': 0,  'azimuth':  0.0,   'distance': 1.0},  # center
    'Strings': {'channel': 1,  'azimuth': -0.8,   'distance': 1.2},  # left
    'Lead':    {'channel': 2,  'azimuth':  0.7,   'distance': 1.0},  # right
}

os.makedirs(f'{OUT_DIR}/Audio', exist_ok=True)
os.makedirs(f'{OUT_DIR}/MIDI', exist_ok=True)

# === Step 1: Split MIDI into per-track files ===
print("=== Step 1: Splitting MIDI into per-track files ===")
src_mid = mido.MidiFile(SRC_MIDI)
tempo_msg = None
for track in src_mid.tracks:
    for msg in track:
        if msg.type == 'set_tempo':
            tempo_msg = msg
            break

split_midi_paths = {}
for name, cfg in TRACK_CONFIG.items():
    ch = cfg['channel']
    new_mid = mido.MidiFile(ticks_per_beat=src_mid.ticks_per_beat)
    
    # Tempo track
    tempo_track = mido.MidiTrack()
    new_mid.tracks.append(tempo_track)
    if tempo_msg:
        tempo_track.append(mido.MetaMessage('set_tempo', tempo=tempo_msg.tempo, time=0))
    tempo_track.append(mido.MetaMessage('end_of_track', time=0))
    
    # Data track - filter messages for this channel
    data_track = mido.MidiTrack()
    new_mid.tracks.append(data_track)
    for track in src_mid.tracks:
        for msg in track:
            if hasattr(msg, 'channel') and msg.channel == ch:
                data_track.append(msg.copy())
    
    out_path = f'{OUT_DIR}/MIDI/disco_{name.lower()}.mid'
    new_mid.save(out_path)
    split_midi_paths[name] = out_path
    note_count = sum(1 for m in data_track if m.type == 'note_on' and m.velocity > 0)
    print(f"  {name} (ch{ch}): {note_count} notes -> {out_path}")

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
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"    WARNING: {result.stderr[:200]}")
    size = os.path.getsize(wav_path) if os.path.exists(wav_path) else 0
    print(f"    -> {wav_path} ({size} bytes)")
    mono_wav_paths[name] = wav_path

# === Step 3: SP-021 Binaural Woodworth-Schlosberg Spatialization ===
print("\n=== Step 3: Applying SP-021 Binaural Spatialization ===")

def first_order_lowpass(x, fc, fs):
    """First-order lowpass filter with dynamic cutoff."""
    n_samples = len(x)
    y = np.zeros(n_samples, dtype=np.float64)
    
    if np.isscalar(fc):
        fc_arr = np.full(n_samples, fc)
    else:
        fc_arr = np.asarray(fc, dtype=np.float64)
    
    alpha = (2.0 * np.pi * fc_arr / fs) / (2.0 * np.pi * fc_arr / fs + 1.0)
    alpha = np.clip(alpha, 0.0, 1.0)
    
    y_prev = 0.0
    for i in range(n_samples):
        y[i] = alpha[i] * x[i] + (1.0 - alpha[i]) * y_prev
        y_prev = y[i]
    
    return y

def linear_fractional_delay(x, delay_samples):
    """Fractional delay via linear interpolation."""
    n_samples = len(x)
    y = np.zeros(n_samples, dtype=np.float64)
    
    if np.isscalar(delay_samples):
        d_arr = np.full(n_samples, float(delay_samples))
    else:
        d_arr = np.asarray(delay_samples, dtype=np.float64)
    
    for i in range(n_samples):
        d = d_arr[i]
        d_int = int(np.floor(d))
        d_frac = d - d_int
        
        idx1 = i - d_int
        idx2 = idx1 - 1
        
        val1 = x[idx1] if 0 <= idx1 < n_samples else 0.0
        val2 = x[idx2] if 0 <= idx2 < n_samples else 0.0
        
        y[i] = (1.0 - d_frac) * val1 + d_frac * val2
    
    return y

def binaural_spatialization(x, fs, azimuth, distance=1.0, head_radius=0.0875, speed_of_sound=343.0):
    """
    SP-021: Binaural Woodworth-Schlosberg Spatialization.
    Returns stereo (n_samples, 2) array.
    """
    n_samples = len(x)
    
    # Distance attenuation
    ref_distance = 1.0
    attn = ref_distance / max(distance, ref_distance)
    x_attn = x * attn
    
    if np.isscalar(azimuth):
        az_arr = np.full(n_samples, azimuth)
    else:
        az_arr = np.asarray(azimuth)
    
    az_arr = (az_arr + np.pi) % (2 * np.pi) - np.pi
    
    # Woodworth-Schlosberg ITD
    abs_az = np.abs(az_arr)
    tau = (head_radius / speed_of_sound) * (np.sin(abs_az) + abs_az)
    tau_samples = tau * fs
    
    delay_l = np.where(az_arr >= 0.0, tau_samples, 0.0)
    delay_r = np.where(az_arr < 0.0, tau_samples, 0.0)
    
    delayed_l = linear_fractional_delay(x_attn, delay_l)
    delayed_r = linear_fractional_delay(x_attn, delay_r)
    
    # ILD via head shadowing
    f_max = 20000.0
    f_min = 1000.0
    p = 2.0
    
    fc_l = np.where(az_arr >= 0.0,
                    f_min + (f_max - f_min) * ((1.0 + np.cos(az_arr)) / 2.0)**p,
                    f_max)
    fc_r = np.where(az_arr < 0.0,
                    f_min + (f_max - f_min) * ((1.0 + np.cos(az_arr)) / 2.0)**p,
                    f_max)
    
    out_l = first_order_lowpass(delayed_l, fc_l, fs)
    out_r = first_order_lowpass(delayed_r, fc_r, fs)
    
    return np.column_stack((out_l, out_r))

def read_wav(path):
    """Read WAV file as float64 numpy array."""
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
    """Write stereo 16-bit WAV."""
    n_samples = min(len(left), len(right))
    with wave.open(path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        
        # Interleave
        stereo = np.column_stack((left[:n_samples], right[:n_samples]))
        stereo = np.clip(stereo, -1.0, 1.0)
        pcm = (stereo * 32767).astype(np.int16)
        wf.writeframes(pcm.tobytes())

# Process each track
stereo_sum_l = None
stereo_sum_r = None
max_len = 0

for name, wav_path in mono_wav_paths.items():
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
        print(f"  SKIP {name}: no valid WAV")
        continue
    
    mono_data, file_sr = read_wav(wav_path)
    print(f"  {name}: {len(mono_data)} samples ({len(mono_data)/file_sr:.1f}s)")
    
    cfg = TRACK_CONFIG[name]
    az = cfg['azimuth']
    dist = cfg['distance']
    
    # Apply SP-021 binaural spatialization
    stereo = binaural_spatialization(mono_data, file_sr, az, distance=dist)
    
    print(f"    Azimuth: {np.degrees(az):.1f} deg, Distance: {dist}m")
    print(f"    L peak: {np.max(np.abs(stereo[:,0])):.4f}, R peak: {np.max(np.abs(stereo[:,1])):.4f}")
    
    # Accumulate
    if stereo_sum_l is None:
        stereo_sum_l = stereo[:, 0].copy()
        stereo_sum_r = stereo[:, 1].copy()
    else:
        # Pad shorter to match
        target_len = max(len(stereo_sum_l), len(stereo[:, 0]))
        if len(stereo_sum_l) < target_len:
            stereo_sum_l = np.pad(stereo_sum_l, (0, target_len - len(stereo_sum_l)))
            stereo_sum_r = np.pad(stereo_sum_r, (0, target_len - len(stereo_sum_r)))
        
        sl = np.zeros(target_len)
        sr_arr = np.zeros(target_len)
        sl[:len(stereo[:, 0])] = stereo[:, 0]
        sr_arr[:len(stereo[:, 1])] = stereo[:, 1]
        
        stereo_sum_l += sl
        stereo_sum_r += sr_arr
    
    max_len = max(max_len, len(stereo[:, 0]))

# === Step 4: Normalize and export ===
print("\n=== Step 4: Normalizing and exporting ===")

# Peak normalize to -1dB (~0.89)
peak = max(np.max(np.abs(stereo_sum_l)), np.max(np.abs(stereo_sum_r)))
if peak > 0:
    target_peak = 0.89
    scale = target_peak / peak
    stereo_sum_l *= scale
    stereo_sum_r *= scale
    print(f"  Peak before norm: {peak:.4f}, scale factor: {scale:.4f}")

# Write stereo WAV
wav_out = f'{OUT_DIR}/Audio/disco_binaural_SP021.wav'
write_stereo_wav(wav_out, stereo_sum_l, stereo_sum_r, SR)
wav_size = os.path.getsize(wav_out)
print(f"  WAV: {wav_out} ({wav_size} bytes)")
assert wav_size > 1000, "WAV output too small!"

# Convert to OGG via ffmpeg
ogg_out = f'{OUT_DIR}/Audio/disco_binaural_SP021.ogg'
cmd = [
    'ffmpeg', '-y', '-i', wav_out,
    '-codec:a', 'libopus',
    '-application', 'audio',
    '-b:a', '128k',
    ogg_out
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
ogg_size = os.path.getsize(ogg_out) if os.path.exists(ogg_out) else 0
print(f"  OGG: {ogg_out} ({ogg_size} bytes)")

# Copy source MIDI
import shutil
shutil.copy2(SRC_MIDI, f'{OUT_DIR}/MIDI/classic_disco_source.mid')

print("\n=== DONE ===")
print(f"Source: {SRC_MIDI}")
print(f"Method: SP-021 Binaural Woodworth-Schlosberg Spatialization")
print(f"Output WAV: {wav_out} ({wav_size} bytes)")
print(f"Output OGG: {ogg_out} ({ogg_size} bytes)")
