# -*- coding: utf-8 -*-
"""Pitch verification for SP-143 harmonizer output (both reference + harmonized)."""
import os
import json
import numpy as np
from sound.utils.io import read_wav

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")

A4 = 440.0


def midi_to_hz(m):
    return A4 * 2.0 ** ((m - 69) / 12.0)


# expected pitch classes for C major / C pentatonic region (120 BPM marimba ~ C4-A5)
C_DIATONIC = sorted({0, 2, 4, 5, 7, 9, 11})  # pitch classes 0..11


def analyze(path, label):
    audio, sr = read_wav(path)
    if audio.ndim > 1:
        mono = audio.mean(axis=1)
    else:
        mono = audio
    N = len(mono)
    win = int(0.5 * sr)
    hop = win
    frames = []
    hz_to_pc = lambda f: round(12 * np.log2(f / A4)) % 12 if f > 0 else None
    harmonic_energy_ratio = []
    rms_per_sec = []
    for start in range(0, N - win, win):
        seg = mono[start:start + win]
        rms = float(np.sqrt(np.mean(seg ** 2)))
        rms_per_sec.append(rms)
        if rms < 1e-4:
            frames.append((0.0, None))
            continue
        seg = seg * np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        # dominant peak in 50-1000 Hz
        band = (freqs >= 50) & (freqs <= 1000)
        if band.sum() == 0:
            frames.append((0.0, None))
            continue
        bi = np.where(band)[0]
        pk_idx = bi[np.argmax(spec[bi])]
        pk_hz = freqs[pk_idx]
        # harmonic energy: energy in first 8 harmonics of the LOWEST fundamental peak
        lo = (freqs >= 50) & (freqs <= 900)
        f0_cand = freqs[np.where(lo)[0][np.argmax(spec[lo])]]
        harm = 0.0
        tot = float(np.sum(spec[(freqs >= 50) & (freqs <= 8000)] ** 2))
        for h in range(1, 9):
            fh = f0_cand * h
            if fh > 8000:
                break
            m = np.abs(freqs - fh) < 15
            if m.any():
                harm += float(np.sum(spec[m] ** 2))
        harmonic_energy_ratio.append((harm / (tot + 1e-9)))
        frames.append((pk_hz, hz_to_pc(pk_hz)))

    voiced_frames = [(f, pc) for f, pc in frames if f > 0 and pc is not None]
    dominant_pcs = [pc for f, pc in voiced_frames]
    # fraction of voiced frames whose dominant pc is diatonic (C major) OR a
    # harmony interval of it (harmonizer stacks 3rd/5th/4th-below -> stays diatonic)
    in_c = sum(1 for pc in dominant_pcs if pc in C_DIATONIC)
    frac = (in_c / len(dominant_pcs)) if dominant_pcs else 0.0
    median_peak = float(np.median([f for f, pc in voiced_frames])) if voiced_frames else 0.0
    harm_med = float(np.median(harmonic_energy_ratio)) if harmonic_energy_ratio else 0.0
    silence = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    return {
        "label": label,
        "dur_s": round(N / sr, 2),
        "frames": len(frames),
        "voiced_frames": len(voiced_frames),
        "median_peak_hz": round(median_peak, 1),
        "dominant_pc_in_C_diatonic_frac": round(frac, 3),
        "median_harmonic_energy_ratio": round(harm_med, 3),
        "silence_ratio": round(silence, 4),
        "rms_per_sec_first_10": [round(r, 4) for r in rms_per_sec[:10]],
    }


results = {}
for name in ("full_mix", "sp143_harmonized", "sp143_tuned", "sp143_droid"):
    p = os.path.join(AUD, name + ".wav")
    if os.path.exists(p):
        results[name] = analyze(p, name)
        r = results[name]
        print(name, "-> peak", r["median_peak_hz"], "Hz | diatonic frac", r["dominant_pc_in_C_diatonic_frac"],
              "| harm-energy", r["median_harmonic_energy_ratio"], "| silence", r["silence_ratio"])

with open(os.path.join(HERE, "Analysis", "pitch_verification.json"), "w") as f:
    json.dump(results, f, indent=2)
print("wrote Analysis/pitch_verification.json")