# -*- coding: utf-8 -*-
"""SP-107 BitCrusher absolute-layer production: crush + master + verify (2026-11-18)."""
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from sound.effects.bit_crusher import BitCrusher
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP107-bitcrusher-212-indian-boids-yaman")
AUD = OUT / "Audio"
AUD.mkdir(parents=True, exist_ok=True)
dry_wav = OUT / "dry_full_mix_sp001_reference.wav"

SR = 44100
SEED = 20261118
STYLE = "IndianClassical"
TARGET_LUFS = target_for_style(STYLE)   # -18.0
CEILING_DB = -1.0
# Raga Yaman on C pcs
YAMAN_PCS = {0, 2, 4, 6, 7, 9, 11}

# ---- SP-107 params (fidelity coordinate) ----
FIDELITY = 0.42
MODE = "worn"
RING = 0.2
MIX = 1.0

t0 = time.time()
audio, sr = read_wav(str(dry_wav))
if audio.ndim == 1:
    audio = np.column_stack([audio, audio])
audio = np.asarray(audio, dtype=np.float32)
assert sr == SR, "unexpected sr %r" % sr
print("dry shape", audio.shape, "peak", float(np.max(np.abs(audio))),
      flush=True)

# per-channel instances -> no cross-channel filter-state leakage
crL = BitCrusher(sample_rate=SR)
crR = BitCrusher(sample_rate=SR)
for c in (crL, crR):
    c.fidelity = FIDELITY
    c.config.mode = MODE
    c.config.ring = RING
    c.config.mix = MIX
print("SP-107 config: sr=%.0f Hz, bits=%d, mode=%s, ring=%.2f, mix=%.2f"
      % (crL.config.sample_rate_hz, crL.config.bit_depth,
         crL.config.mode, crL.config.ring, crL.config.mix), flush=True)

t_crush = time.time()
wetL = crL.process(audio[:, 0])
wetR = crR.process(audio[:, 1])
wet = np.column_stack([wetL, wetR]).astype(np.float32)
print("bit-crush done in %.1f s; wet peak %.4f"
      % (time.time() - t_crush, float(np.max(np.abs(wet)))), flush=True)

# ---- master ----
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB), flush=True)
mastered, rep = master(wet, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))),
      flush=True)

final_wav = OUT / "SP107-bitcrusher-212-indian-boids-yaman.wav"
final_ogg = OUT / "SP107-bitcrusher-212-indian-boids-yaman.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV %d B, OGG %d B" % (final_wav.stat().st_size, final_ogg.stat().st_size), flush=True)

# ---- verification ----
meas_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono = 0.5 * (mastered[:, 0] + mastered[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]


def pitch_verify(audio_tm, pcs):
    wl = int(0.5 * SR)
    nw = len(audio_tm) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = audio_tm[w * wl:(w + 1) * wl]
        if seg.ndim > 1:
            seg = 0.5 * (seg[:, 0] + seg[:, 1])
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub = spec[mask]
        subf = freqs[mask]
        dom = subf[np.argmax(sub)]
        midi_val = 69.0 + 12.0 * np.log2(max(1.0, dom) / 440.0)
        pc = round(midi_val) % 12
        if pc in pcs:
            hits += 1
        tot = np.sum(spec ** 2) + 1e-12
        he = 0.0
        for h in range(1, 9):
            tf = dom * h
            hband = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
            he += np.sum(spec[hband] ** 2)
        he_list.append(float(he / tot))
    hit_rate = hits / max(1, valid)
    he_mean = float(np.mean(he_list)) if he_list else 0.0
    return hit_rate, he_mean, valid


wet_hit, wet_he, wet_valid = pitch_verify(mastered, YAMAN_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(audio, YAMAN_PCS)
he_retention = wet_he / dry_he if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (wet_hit >= 0.60 and he_retention >= 0.40) else "FAIL"
print("pitch verify: wet hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | "
      "HE retention=%.3f -> %s"
      % (wet_hit, wet_he, dry_hit, dry_he, he_retention, pitch_verdict), flush=True)
print("silence=%.2f%% rms=%.4f LUFS=%.2f peak=%.4f"
      % (silence_pct, rms, meas_lufs, peak_val), flush=True)

cfg = {"fidelity": FIDELITY, "mode": MODE, "ring": RING, "mix": MIX,
       "sample_rate_hz": crL.config.sample_rate_hz, "bit_depth": crL.config.bit_depth}

(OUT / "Analysis" / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "wet_hit_rate": wet_hit, "wet_mean_harmonic_energy": wet_he,
    "dry_hit_rate": dry_hit, "dry_mean_harmonic_energy": dry_he,
    "he_retention": he_retention,
    "valid_windows": wet_valid, "pitch_verdict": pitch_verdict,
    "target_lufs": TARGET_LUFS, "crush_params": cfg,
    "wall_seconds": round(time.time() - t0, 1),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-18", "seed": SEED,
    "method": "SP-107", "method_module": "sound.effects.bit_crusher",
    "method_desc": "Bit Crusher / Fidelity Reducer — linked sample-rate/bit-depth macro, Iron/Worn character voicing, aliasing foldover emphasis (Modbap Fidelity Theory-style)",
    "layer": "ABSOLUTE - one bit-crusher chain applied to the whole dry mix (per-channel instances)",
    "params": cfg, "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "source_midi": str(OUT / "MIDI" / "212-indian-boids-yaman.mid"),
    "phase1_midi": str(OUT / "MIDI" / "212-indian-boids-yaman-phase1.mid"),
    "source_bpm": 90, "source_key": "Raga Yaman on C",
    "source_pitch_classes": sorted(YAMAN_PCS),
    "source_form": "alap->gat->jhala->alap, 32 bars (8 sections x 4), monophonic raga over Sa+Pa drone",
    "output_wav": str(final_wav), "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict,
    "wet_hit_rate": wet_hit, "wet_he": wet_he,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
print("DONE in %.1f s" % (time.time() - t0), flush=True)
