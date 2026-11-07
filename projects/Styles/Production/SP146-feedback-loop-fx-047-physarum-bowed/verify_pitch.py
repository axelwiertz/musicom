# -*- coding: utf-8 -*-
"""Pitch verification for SP-146 feedback-loop-fx output on 047-physarum-bowed.

Bb major / G minor: pcs {10,0,2,3,5,7,9}.  Checks: FFT dominant peak per 0.5 s
(50-1000 Hz), harmonic energy in first 8 harmonics of the lowest fundamental,
silence ratio + per-second RMS.
"""
import os
import json
import numpy as np
from sound.utils.io import read_wav

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
ANA = os.path.join(HERE, "Analysis")
os.makedirs(ANA, exist_ok=True)

A4 = 440.0
BB_MAJ = {10, 0, 2, 3, 5, 7, 9}


def analyze(path, label):
    audio, sr = read_wav(path)
    mono = audio.mean(axis=1) if audio.ndim > 1 else audio
    N = len(mono)
    win = int(0.5 * sr)
    voiced_pcs = []
    harmonic_energy = []
    peak_hz = []
    for start in range(0, N - win, win):
        seg = mono[start:start + win]
        rms = float(np.sqrt(np.mean(seg ** 2)))
        if rms < 1e-4:
            continue
        seg = seg * np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        band = (freqs >= 50) & (freqs <= 1000)
        if band.sum() == 0:
            continue
        bi = np.where(band)[0]
        pk_hz = freqs[bi[np.argmax(spec[bi])]]
        pc = round(12 * np.log2(pk_hz / A4)) % 12
        peak_hz.append(pk_hz)
        voiced_pcs.append(pc)
        lo = (freqs >= 50) & (freqs <= 900)
        f0 = freqs[np.where(lo)[0][np.argmax(spec[lo])]]
        harm = 0.0
        tot = float(np.sum(spec[(freqs >= 50) & (freqs <= 8000)] ** 2))
        for h in range(1, 9):
            fh = f0 * h
            if fh > 8000:
                break
            m = np.abs(freqs - fh) < 15
            if m.any():
                harm += float(np.sum(spec[m] ** 2))
        harmonic_energy.append(harm / (tot + 1e-9))

    in_scale = sum(1 for pc in voiced_pcs if pc in BB_MAJ)
    frac = (in_scale / len(voiced_pcs)) if voiced_pcs else 0.0
    silence = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    return {
        "label": label,
        "dur_s": round(N / sr, 2),
        "voiced_frames": len(voiced_pcs),
        "median_peak_hz": round(float(np.median(peak_hz)), 1) if peak_hz else 0.0,
        "dominant_pc_in_Bb_frac": round(frac, 3),
        "median_harmonic_energy_ratio": round(float(np.median(harmonic_energy)), 3)
        if harmonic_energy else 0.0,
        "silence_ratio": round(silence, 4),
    }


results = {}
for name in ("full_mix", "sp146_feedback", "sp146_codec"):
    p = os.path.join(AUD, name + ".wav")
    if os.path.exists(p):
        results[name] = analyze(p, name)
        r = results[name]
        print(name, "-> peak", r["median_peak_hz"], "Hz | Bb-maj frac",
              r["dominant_pc_in_Bb_frac"], "| harm-energy",
              r["median_harmonic_energy_ratio"], "| silence", r["silence_ratio"])

with open(os.path.join(ANA, "pitch_verification.json"), "w") as f:
    json.dump(results, f, indent=2)
print("wrote Analysis/pitch_verification.json")
