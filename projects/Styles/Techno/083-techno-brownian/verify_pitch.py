# -*- coding: utf-8 -*-
"""Pitch/tonal verification for 083 renders (catches noise/silent renders).

For each WAV: FFT dominant peak per 0.5s window in 50-1000 Hz; report how many
windows have a dominant peak (tonal content). Harmonic-energy check on the
lowest fundamental's first 8 harmonics >= 30% = tonal (noise = single digits).
"""
import json
import os
import wave

import numpy as np

PROJ = "/opt/data/projects/Styles/Techno/083-techno-brownian"


def load_mono(path):
    with wave.open(path, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if wf.getnchannels() == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    return data, sr


def analyze(path):
    data, sr = load_mono(path)
    win = int(0.5 * sr)
    nwin = len(data) // win
    tonal = 0
    peaks = []
    for i in range(nwin):
        seg = data[i * win:(i + 1) * win]
        if np.max(np.abs(seg)) < 0.005:
            peaks.append(0.0)
            continue
        spectrum = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        mask = (freqs >= 50) & (freqs <= 1000)
        if not mask.any():
            peaks.append(0.0)
            continue
        sub = spectrum[mask]
        fsub = freqs[mask]
        idx = int(np.argmax(sub))
        dom = fsub[idx]
        # tonal if dominant peak energy is a clear spike relative to band mean
        band_mean = np.mean(sub)
        spike = sub[idx] / max(band_mean, 1e-9)
        peaks.append(round(float(dom), 2))
        if spike > 3.0:
            tonal += 1
    tonal_frac = tonal / max(nwin, 1)

    # harmonic energy in first 8 harmonics of lowest voiced fundamental (F2=87)
    f0 = 87.3
    spectrum = np.abs(np.fft.rfft(data[:int(0.5 * sr)]))
    freqs = np.fft.rfftfreq(int(0.5 * sr), 1.0 / sr)
    bandmask = (freqs >= 30) & (freqs <= 1000)
    band_energy = float(np.sum(spectrum[bandmask] ** 2))
    har_energy = 0.0
    for h in range(1, 9):
        f = f0 * h
        band = (freqs >= f - 15) & (freqs <= f + 15)
        if band.any():
            har_energy += float(np.sum(spectrum[band] ** 2))
    har_frac = har_energy / max(band_energy, 1e-9)
    return {
        "file": os.path.basename(path),
        "windows": nwin,
        "tonal_windows": tonal,
        "tonal_fraction": round(tonal_frac, 4),
        "harmonic_energy_first8_F2": round(har_frac, 4),
        "peak_freqs_sample": peaks[:16],
    }


out = {}
for name in ("083-techno-brownian", "083-techno-brownian-phase1"):
    p = os.path.join(PROJ, "Audio", name + ".wav")
    a = analyze(p)
    out[name] = a
    print(name, "tonal_windows", a["tonal_windows"], "/", a["windows"],
          "har_F2", a["harmonic_energy_first8_F2"], "sample_peaks", a["peak_freqs_sample"][:8])

with open(os.path.join(PROJ, "Analysis", "pitch_verification.json"), "w") as f:
    json.dump(out, f, indent=2)
print("pitch_verification.json written")
