#!/usr/bin/env python3
"""SP-021: Binaural Woodworth-Schlosberg spatialization (vectorized).
Applies ITD + ILD to mono WAV to create stereo binaural image.
"""
import numpy as np
import wave
import sys

def read_wav(path):
    with wave.open(path, 'rb') as wf:
        sr = wf.getframerate()
        nframes = wf.getnframes()
        data = np.frombuffer(wf.readframes(nframes), dtype=np.int16).astype(np.float32) / 32768.0
    return sr, data

def write_wav_stereo(path, sr, left, right):
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if peak > 0:
        scale = 0.891 / peak
        left = left * scale
        right = right * scale
    data = np.column_stack([left, right])
    data_int16 = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data_int16.tobytes())

def apply_binaural(sr, mono):
    """Vectorized binaural via Woodworth-Schlosberg model."""
    n = len(mono)
    t = np.arange(n, dtype=np.float64) / sr

    head_radius = 0.0875
    c = 343.0

    # Source azimuth oscillates +/-60deg over ~20s
    azimuth = 60.0 * np.sin(2 * np.pi * t / 20.0)
    azimuth_rad = np.radians(azimuth)

    # ITD (Woodworth)
    itd_seconds = (head_radius / c) * (azimuth_rad + np.sin(azimuth_rad))
    itd_samples = np.round(itd_seconds * sr).astype(int)

    # ILD (head shadow)
    ild_db = 3.0 * np.sin(azimuth_rad)
    gain_l = np.where(azimuth > 0, 10 ** (-ild_db / 20.0), 1.0)
    gain_r = np.where(azimuth > 0, 10 ** (ild_db / 20.0), 1.0)

    # Build delayed signals using integer sample delays (vectorized)
    indices = np.arange(n)
    left_src = indices - np.maximum(0, itd_samples)
    right_src = indices + np.minimum(0, itd_samples)

    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    # Left ear
    valid_l = (left_src >= 0) & (left_src < n)
    left[valid_l] = mono[left_src[valid_l]] * gain_l[valid_l]

    # Right ear
    valid_r = (right_src >= 0) & (right_src < n)
    right[valid_r] = mono[right_src[valid_r]] * gain_r[valid_r]

    return left, right

def main():
    wav_in = sys.argv[1] if len(sys.argv) > 1 else "Audio/053-euclidean-binaural.wav"
    wav_out = sys.argv[2] if len(sys.argv) > 2 else "Audio/053-euclidean-binaural_binaural.wav"

    print(f"Reading {wav_in}...")
    sr, mono = read_wav(wav_in)
    print(f"  SR={sr}, samples={len(mono)}, duration={len(mono)/sr:.1f}s")

    print("Applying binaural spatialization (SP-021)...")
    left, right = apply_binaural(sr, mono)

    print(f"Writing {wav_out}...")
    write_wav_stereo(wav_out, sr, left, right)
    print("Done.")

if __name__ == "__main__":
    main()
