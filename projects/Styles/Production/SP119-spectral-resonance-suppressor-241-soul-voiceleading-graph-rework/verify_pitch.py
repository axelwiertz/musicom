# -*- coding: utf-8 -*-
"""Pitch verification for SP-119 spectral resonance suppressor (soul, D minor).

Mandatory checks: FFT dominant peak per 0.5s window (50-1000 Hz), harmonic
energy in first 8 harmonics of the lowest fundamental, silence ratio, per-sec
RMS. D-aeolian pitch classes {0,2,4,5,7,9,10}.
"""
import os
import json
import numpy as np
from sound.utils.io import read_wav

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")

A4 = 440.0
D_AEOLIAN = {0, 2, 4, 5, 7, 9, 10}


def midi_to_hz(m):
    return A4 * 2.0 ** ((m - 69) / 12.0)


def analyze(path, label):
    audio, sr = read_wav(path)
    mono = audio.mean(axis=1) if audio.ndim > 1 else audio
    N = len(mono)
    win = int(0.5 * sr)
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
        band = (freqs >= 50) & (freqs <= 1000)
        bi = np.where(band)[0]
        if len(bi) == 0:
            frames.append((0.0, None))
            continue
        pk_idx = bi[np.argmax(spec[bi])]
        pk_hz = freqs[pk_idx]
        lo = (freqs >= 50) & (freqs <= 900)
        lbi = np.where(lo)[0]
        f0_cand = freqs[lbi[np.argmax(spec[lbi])]] if len(lbi) else pk_hz
        harm = 0.0
        tot = float(np.sum(spec[(freqs >= 50) & (freqs <= 8000)] ** 2))
        for h in range(1, 9):
            fh = f0_cand * h
            if fh > 8000:
                break
            m = np.abs(freqs - fh) < 15
            if m.any():
                harm += float(np.sum(spec[m] ** 2))
        harmonic_energy_ratio.append(harm / (tot + 1e-9))
        frames.append((pk_hz, hz_to_pc(pk_hz)))

    voiced = [(f, pc) for f, pc in frames if f > 0 and pc is not None]
    dominant_pcs = [pc for f, pc in voiced]
    in_key = sum(1 for pc in dominant_pcs if pc in D_AEOLIAN)
    frac = (in_key / len(dominant_pcs)) if dominant_pcs else 0.0
    median_peak = float(np.median([f for f, pc in voiced])) if voiced else 0.0
    harm_med = float(np.median(harmonic_energy_ratio)) if harmonic_energy_ratio else 0.0
    silence = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    return {
        "label": label,
        "dur_s": round(N / sr, 2),
        "frames": len(frames),
        "voiced_frames": len(voiced),
        "median_peak_hz": round(median_peak, 1),
        "dominant_pc_in_D_aeolian_frac": round(frac, 3),
        "median_harmonic_energy_ratio": round(harm_med, 3),
        "silence_ratio": round(silence, 4),
        "rms_per_sec_first_10": [round(r, 4) for r in rms_per_sec[:10]],
        "rms_per_sec_last_5": [round(r, 4) for r in rms_per_sec[-5:]],
    }


results = {}
for name in ("full_mix", "sp119_suppressed"):
    p = os.path.join(AUD, name + ".wav")
    if os.path.exists(p):
        results[name] = analyze(p, name)
        r = results[name]
        print(name, "-> peak", r["median_peak_hz"], "Hz | D-aeol frac",
              r["dominant_pc_in_D_aeolian_frac"], "| harm-energy",
              r["median_harmonic_energy_ratio"], "| silence", r["silence_ratio"])

with open(os.path.join(HERE, "Analysis", "pitch_verification.json"), "w") as f:
    json.dump(results, f, indent=2)
print("wrote Analysis/pitch_verification.json")
