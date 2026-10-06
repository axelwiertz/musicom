# -*- coding: utf-8 -*-
"""Recompute stats + write JSON/report for SP-091 (render already complete)."""
import json, math, wave
from pathlib import Path
import numpy as np

from sound.effects.mastering import measure_lufs

OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP091-delta-sigma-indian-boids-yaman")
ANALYSIS = OUT / "Analysis"
SR = 44100
SRC = "/opt/data/repos/musicom/projects/Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid"
final_wav = OUT / "SP091-delta-sigma-indian-boids-yaman.wav"

def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        s = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            return np.vstack([s, s]), sr
        return s.reshape(-1, nch).T, sr

audio, sr = read_wav(final_wav)
final_tm = audio.T  # (N,2)
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(audio)))
mono_mix = 0.5 * (audio[0] + audio[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
L = audio[0]; R = audio[1]
mono_corr = float(np.sum(L * R) / (math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12))

YAMAN_C_PCS = {0, 2, 4, 6, 7, 9, 11}
wl = int(0.5 * SR)
num_windows = len(mono_mix) // wl
hits = 0; valid = 0; hes = []; doms = []
for w in range(num_windows):
    seg = mono_mix[w*wl:(w+1)*wl]
    if np.max(np.abs(seg)) < 0.01:
        continue
    valid += 1
    win = np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg * win))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
    mask = (freqs >= 50.0) & (freqs <= 1000.0)
    if not np.any(mask):
        continue
    sub = spec[mask]; sf = freqs[mask]
    dom = sf[np.argmax(sub)]
    doms.append(float(dom))
    midi_val = 69.0 + 12.0 * math.log2(max(1.0, dom) / 440.0)
    rm = round(midi_val)
    tot = np.sum(spec ** 2) + 1e-12
    he = 0.0
    for h in range(1, 9):
        tf = dom * h
        hm = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
        he += np.sum(spec[hm] ** 2)
    hes.append(he / tot)
    if abs(midi_val - rm) < 0.45 and (rm % 12) in YAMAN_C_PCS:
        hits += 1

hit_rate = float(hits / max(1, valid))
mean_he = float(np.mean(hes)) if hes else 0.0
verdict = "PASS" if hit_rate >= 0.60 and mean_he >= 0.25 else "FAIL"

(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": verdict,
}, indent=2))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-091", "project": "212-indian-boids-yaman",
    "scale": "Yaman raga (C Lydian)", "pcs": sorted(YAMAN_C_PCS),
    "status": verdict, "hit_rate": hit_rate, "harmonic_energy_mean": mean_he,
    "windows_analyzed": valid,
    "median_freq_hz": float(np.median(doms)) if doms else 0.0,
}, indent=2))
provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-06", "seed": 20261006,
    "method": "SP-091",
    "method_module": "sound.effects.delta_sigma_saturator",
    "method_desc": "Physics-Based Delta-Sigma Converter Saturation & Circuit Strain (Mixland Grey Matter-style)",
    "params": {"drive_db": 4.0, "strain": 0.28, "mode": "console", "mix": 1.0, "fs": SR},
    "source_midi": SRC,
    "output_wav": str(final_wav),
    "output_ogg": str(OUT / "SP091-delta-sigma-indian-boids-yaman.ogg"),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "pitch_verdict": verdict,
    "hit_rate": hit_rate, "he_mean": mean_he,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))
(ANALYSIS / "select_20261006.json").write_text(json.dumps({
    "date": "2026-10-06", "method": "SP-091",
    "method_module": "sound.effects.delta_sigma_saturator",
    "source_midi": SRC,
    "recent_excluded": ["SP021", "SP072", "SP075", "SP079", "SP080", "SP081", "SP083", "SP086"],
    "registry_total": 40,
}, indent=2))

print(json.dumps({"lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
                  "mono_corr": mono_corr, "rms": rms, "valid": valid,
                  "hit_rate": hit_rate, "mean_he": mean_he, "verdict": verdict}, indent=2))
