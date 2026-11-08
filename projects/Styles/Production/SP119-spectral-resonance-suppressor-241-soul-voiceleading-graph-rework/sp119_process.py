# -*- coding: utf-8 -*-
"""SP-119 Spectral Resonance Suppressor (Fixate:Midrange-style) — 241 soul.

Absolute-layer method: render the full soul mix, run the STFT de-resonator
across the WHOLE piece (per-channel midrange suppression), then master to the
soul loudness target.

Source: Soul/241-soul-voiceleading-graph-rework — D minor (aeolian), 92 BPM,
32 bars, TenorSax/Rhodes/Violin/Guitar/Bass/Drums (6 voices, 7 MIDI tracks).
"""
import json
import os
import subprocess

import numpy as np

from sound.effects.spectral_resonance_suppressor import SpectralResonanceSuppressor
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
MID = os.path.join(HERE, "MIDI")
ANA = os.path.join(HERE, "Analysis")
for d in (AUD, MID, ANA):
    os.makedirs(d, exist_ok=True)

SRC_MIDI = ("/opt/data/repos/musicom/projects/Styles/Soul/"
            "241-soul-voiceleading-graph-rework/MIDI/"
            "241-soul-voiceleading-graph-rework.mid")
SF = discover_soundfont()
FLUID = fluidsynth_bin()
STYLE = "soul"
BPM = 92.0

SP119 = {
    "amount": 0.7,
    "threshold_db": 5.0,
    "width_bins": 24,
    "min_freq": 200.0,
    "max_freq": 6000.0,
    "attack": 0.05,
    "release": 0.3,
}

# ---- 1. render full mix ------------------------------------------------
mix_path = os.path.join(AUD, "full_mix.wav")
if not os.path.exists(mix_path):
    r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", mix_path, SF, SRC_MIDI],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]
audio, sr = read_wav(mix_path)          # (N, 2) time-major float32
N = len(audio)
dur = N / sr
print("full_mix:", audio.shape, "sr", sr, "dur_s", round(dur, 2))


# ---- helper: harmonic energy (first 8 harmonics of lowest fundamental) ---
def harmonic_energy(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    seg = mono * np.hanning(len(mono))
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(mono), 1 / sr)
    lo = (fr >= 50) & (fr <= 900)
    lbi = np.where(lo)[0]
    f0 = fr[lbi[np.argmax(spec[lbi])]] if len(lbi) else 294.0
    tot = float(np.sum(spec[(fr >= 50) & (fr <= 8000)] ** 2))
    harm = 0.0
    for h in range(1, 9):
        fh = f0 * h
        if fh > 8000:
            break
        m = np.abs(fr - fh) < 15
        if m.any():
            harm += float(np.sum(spec[m] ** 2))
    return harm / (tot + 1e-9)


def crest(x, lo=200.0, hi=6000.0):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    w = np.hanning(len(mono))
    Y = np.abs(np.fft.rfft(mono * w))
    fr = np.fft.rfftfreq(len(mono), 1 / sr)
    m = (fr >= lo) & (fr <= hi)
    with np.errstate(divide="ignore"):
        db = 20.0 * np.log10(Y[m] + 1e-12)
    return float(db.max() - db.mean())


he_before = harmonic_energy(audio)
crest_before = crest(audio)
print("BEFORE harm_energy:", round(he_before, 3), "crest_db:", round(crest_before, 2))

# ---- 2. SP-119 per channel --------------------------------------------
rs = SpectralResonanceSuppressor(sample_rate=sr)
out = np.empty_like(audio)
for ch in range(audio.shape[1]):
    out[:, ch] = rs.process(audio[:, ch], **SP119)
suppressed = out.astype(np.float32)

diff = np.abs(suppressed.astype(np.float64) - audio.astype(np.float64))
rms_diff = float(np.sqrt(np.mean(diff ** 2)))
max_diff = float(diff.max())
he_after = harmonic_energy(suppressed)
crest_after = crest(suppressed)
print("AFTER  harm_energy:", round(he_after, 3), "crest_db:", round(crest_after, 2))
print("rms_diff:", round(rms_diff, 4), "max_abs_diff:", round(max_diff, 4))

# ---- 3. master ---------------------------------------------------------
target = target_for_style(STYLE)
mastered, rep = master(suppressed, target_lufs=target, ceiling_db=-1.0,
                       sample_rate=sr)
write_wav(os.path.join(AUD, "sp119_suppressed.wav"), mastered, sr,
          normalize=False)
print("MASTER:", STYLE, "target", target,
      "integrated_lufs", round(rep["integrated_lufs"], 2),
      "true_peak_db", round(rep["true_peak_db"], 2))

# ---- 4. silence profile ------------------------------------------------
def silence_profile(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [round(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))), 4)
           for s in range(0, len(mono) - sr, sr)]
    gaps = sum(1 for r in rms if r < 0.005)
    return {"silence_ratio": round(silent, 4), "low_rms_seconds": gaps,
            "n_seconds": len(rms), "per_second_rms": rms}


prof = silence_profile(mastered)
print("SILENCE:", prof["silence_ratio"], "low_rms_sec",
      prof["low_rms_seconds"], "/", prof["n_seconds"])

# ---- 5. Opus OGG -------------------------------------------------------
for name in ("full_mix", "sp119_suppressed"):
    wav = os.path.join(AUD, name + ".wav")
    ogg = os.path.join(AUD, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-b:a", "128k", ogg],
                   capture_output=True, text=True)
    print(name, "ogg", os.path.getsize(ogg), "B")

# ---- 6. sidecars -------------------------------------------------------
with open(os.path.join(AUD, "silence_profile.json"), "w") as f:
    json.dump(prof, f, indent=2)

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-08",
    "method": "SP-119",
    "method_module": "sound.effects.spectral_resonance_suppressor",
    "method_desc": "Spectral Resonance Suppressor (Newfangled Fixate:Midrange-style)",
    "source_midi": SRC_MIDI,
    "source_project": "Soul/241-soul-voiceleading-graph-rework",
    "style": STYLE,
    "bpm": BPM,
    "key": "D minor (aeolian)",
    "sp119_params": SP119,
    "sample_rate": sr,
    "duration_s": round(dur, 2),
    "harmonic_energy_before": round(he_before, 3),
    "harmonic_energy_after": round(he_after, 3),
    "midrange_crest_before_db": round(crest_before, 2),
    "midrange_crest_after_db": round(crest_after, 2),
    "waveform_rms_diff": round(rms_diff, 4),
    "waveform_max_abs_diff": round(max_diff, 4),
    "master_target_lufs": target,
    "master_integrated_lufs": round(rep["integrated_lufs"], 2),
    "master_true_peak_db": round(rep["true_peak_db"], 2),
}
with open(os.path.join(AUD, "provenance.json"), "w") as f:
    json.dump(provenance, f, indent=2)

# remove stale normalized intermediate (superseded by clean in-memory metrics)
for stale in ("sp119_suppressed_raw.wav",):
    p = os.path.join(AUD, stale)
    if os.path.exists(p):
        os.remove(p)
        print("removed", stale)

print("DONE. outputs in", AUD)
