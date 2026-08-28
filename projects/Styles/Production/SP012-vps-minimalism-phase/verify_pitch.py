#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose harmonic structure of the SP-012 VPS mix.

Checks:
  1. Full-mix harmonic energy over the WHOLE piece (not 4s window).
  2. Fundamental PRESENCE for C2 (bass) and a mid marimba note (presence, not argmax).
  3. Spectral flatness measure (noise proxy).
  4. Per-stem harmonic energy of that stem's lowest fundamental.
"""
import json
import wave
import sys
import os
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_sp012 import SR, OUT_ROOT, NAME, midi_to_freq

OUT = OUT_ROOT


def load_mono(path):
    wf = wave.open(str(path), "rb")
    sr = wf.getframerate()
    n_ch = wf.getnchannels()
    data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    wf.close()
    if n_ch > 1:
        data = data.reshape(-1, n_ch).mean(axis=1)
    return data.astype(np.float64) / 32768.0


def spectral_energy(x, sr, t0, t1, f0=None, n_harm=8, harm_bw=20.0,
                    band=(30.0, 8000.0)):
    seg = x[int(t0 * sr):int(t1 * sr)]
    seg = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    total_mask = (freqs >= band[0]) & (freqs <= band[1])
    total = np.sum(spec[total_mask] ** 2) + 1e-12
    if f0 is None:
        return None, None, spec, freqs
    harm = 0.0
    for h in range(1, n_harm + 1):
        fc = f0 * h
        m = (freqs >= fc - harm_bw) & (freqs <= fc + harm_bw)
        harm += np.sum(spec[m] ** 2)
    return harm / total, harm, spec, freqs


def fundamental_presence(spec, freqs, f0, bw=15.0, rel=0.01):
    """Is there a spectral peak near f0 at least `rel` of global max?"""
    m = (freqs >= f0 - bw) & (freqs <= f0 + bw)
    if m.sum() == 0:
        return False
    peak = np.max(spec[m])
    return peak > rel * np.max(spec)


def main():
    mix = load_mono(OUT / "Audio" / f"{NAME}.wav")
    results = {}

    # 1. whole-piece harmonic energy of C2 (bass pedal, always present)
    f_c2 = midi_to_freq(36)
    frac_full, _, spec, freqs = spectral_energy(mix, SR, 0.0, len(mix) / SR, f0=f_c2, n_harm=8)
    print(f"[full mix 0-{len(mix)/SR:.0f}s] C2 harmonic energy: {frac_full*100:.1f}%")
    results["full_mix_C2_harmonic_energy"] = round(float(frac_full), 4)

    # 2. fundamental presence checks
    c2_pres = fundamental_presence(spec, freqs, f_c2)
    print(f"C2 fundamental present (>=1% of global peak): {c2_pres}")
    results["C2_fundamental_present"] = bool(c2_pres)
    c4 = midi_to_freq(60)
    c4_pres = fundamental_presence(spec, freqs, c4)
    print(f"C4 fundamental present (>=1% of global peak): {c4_pres}")
    results["C4_fundamental_present"] = bool(c4_pres)

    # 3. spectral flatness (noise proxy) — geometric/arithmetic mean in 200-2000 Hz
    m = (freqs >= 200) & (freqs <= 2000)
    p = spec[m] ** 2 + 1e-15
    flat = np.exp(np.mean(np.log(p))) / (np.mean(p) + 1e-15)
    print(f"spectral flatness 200-2000 Hz: {flat:.5f} (0=tone, 1=white noise)")
    results["spectral_flatness_200_2000"] = round(float(flat), 5)

    # 4. per-stem harmonic energy of that stem's lowest fundamental
    for label, midi_note in [("marimba", 62), ("pad", 60), ("bass", 36), ("kick", 36)]:
        stem_path = OUT / "Audio" / "stems" / f"stem_{label}.wav"
        if not stem_path.exists():
            continue
        stem = load_mono(stem_path)
        f0 = midi_to_freq(midi_note)
        frac_s, _, _, _ = spectral_energy(stem, SR, 0.0, len(stem) / SR, f0=f0, n_harm=8)
        print(f"stem {label}: {f0:.1f} Hz harmonic energy: {frac_s*100:.1f}%")
        results[f"stem_{label}_harmonic_energy"] = round(float(frac_s), 4)

    (OUT / "Analysis" / "pitch_verification.json").write_text(json.dumps(results, indent=2))
    print("saved Analysis/pitch_verification.json")
    print("DONE")


if __name__ == "__main__":
    main()
