# -*- coding: utf-8 -*-
"""SP-157 Whole-Tone Filter Bank production pass (2026-11-19).

Source: Styles/Metal/247-metal-fourier-spectrum (Method 113 Pitch-Class Fourier
Spectrum Composition). E minor, 140 BPM, 4/4, 480 TPB, 32 bars (4 sections x 8)
= 61440 ticks ~ 54.86 s. 4 voices: Lead guitar (29/ch0), Rhythm guitar (29/ch1),
Bass (33/ch2), Drums (ch9). Section pools: Head1/Head2 E natural minor,
Solo1 E harmonic minor, Solo2 E half-whole octatonic.

PRE-FLIGHT: source .mid is the composition job's HUMANIZED export (1826/1984
pitched onsets off-grid -> rule 1 grid-sync FAIL). Harmony 0 out-of-scale /
0 out-of-chord, zero-drift OK. Rework: snap onsets to 16th grid (round/120),
preserve durations -> 0 off-grid / 0 / 0 / zero-drift (rework_247.py).

SP-157 -> sound.effects.whole_tone_filterbank (AudioThing/Hainbach "Seconds"
48-band whole-tone filter bank). ABSOLUTE layer: one resonant 48-band bank
across the whole mix. Spectral freeze of the dry mix sets the band-gain profile
(0.15 floor), resonance 0.25, odd/even pan spread 0.40; ring mod OFF to keep
the render tonal (ring mod adds inharmonic sidebands -> would break pitch
verification).

Pipeline: reworked MIDI -> dry FluidSynth (FX off) -> SP-157 whole-tone bank ->
master() (-14 LUFS, -1 dBTP) -> WAV + Opus OGG -> pitch/silence/RMS
verification -> provenance + REPORT.
"""
import json
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import mido

from sound.effects.whole_tone_filterbank import WholeToneFilterbank
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP157-whole-tone-filterbank-247-metal-fourier-spectrum")
SRC_PROJ = Path("/opt/data/repos/musicom/projects/Styles/Metal/"
                "247-metal-fourier-spectrum")
SRC_MID = SRC_PROJ / "MIDI" / "247-metal-fourier-spectrum.mid"
SRC_PHASE1 = SRC_PROJ / "MIDI" / "247-metal-fourier-spectrum-phase1.mid"

AUD = OUT / "Audio"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261119
DATE = "2026-11-19"
STYLE = "Metal"
TARGET_LUFS = target_for_style(STYLE)   # -14.0 (no 'metal' key -> fallback)
CEILING_DB = -1.0
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"

REWORKED = MIDIDIR / "247-metal-fourier-spectrum.mid"   # grid-quantized (clean)
HUMANIZED = MIDIDIR / "247-metal-fourier-spectrum-humanized.mid"
PHASE1 = MIDIDIR / "247-metal-fourier-spectrum-phase1.mid"

# ---- copy sidecars into output record ----
shutil.copy2(str(SRC_MID), str(HUMANIZED))
if SRC_PHASE1.exists():
    shutil.copy2(str(SRC_PHASE1), str(PHASE1))
print("reworked MIDI:", REWORKED.stat().st_size, "B")
print("humanized sidecar:", HUMANIZED.stat().st_size, "B")
print("phase1 sidecar:", PHASE1.stat().st_size, "B")

# ---- 1. dry FluidSynth render (FX off) from the clean reworked MIDI ----
dry_wav = OUT / "dry_full_mix_sp001_reference.wav"
t0 = time.time()
r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                    "-F", str(dry_wav), SF, str(REWORKED)],
                   capture_output=True, text=True, timeout=900)
if r.returncode != 0 or not dry_wav.exists() or dry_wav.stat().st_size < 1000:
    raise RuntimeError("FluidSynth dry render failed: %s" % r.stderr[-500:])
print("dry WAV:", dry_wav.stat().st_size, "B  (%.1f s)" % (time.time() - t0))

# ---- 2. SP-157 whole-tone filter bank ----
audio, sr = read_wav(str(dry_wav))
if audio.ndim == 1:
    audio = np.column_stack([audio, audio])
audio = np.asarray(audio, dtype=np.float32)
assert sr == SR
mono = 0.5 * (audio[:, 0] + audio[:, 1])
print("dry shape", audio.shape, "peak", float(np.max(np.abs(audio))), flush=True)

RESONANCE = 0.25
PAN_SPREAD = 0.40
RING_MOD = 0.0
FLOOR = 0.15

fb = WholeToneFilterbank(sr=SR, resonance=RESONANCE)
profile = fb.freeze(mono)               # spectral freeze: FFT band-energy profile
fb.gains = FLOOR + (1.0 - FLOOR) * profile   # floor keeps broadband content
strong = int((fb.gains > 0.5).sum())
print("SP-157: bands=%d f0=%.1f Hz f_last=%.1f Hz resonance=%.2f "
      "pan_spread=%.2f ring_mod=%.2f | %d strong bands"
      % (fb.n_bands, fb.freqs[0], fb.freqs[-1], RESONANCE,
         PAN_SPREAD, RING_MOD, strong), flush=True)

t_157 = time.time()
wet = fb.process(mono, ring_mod=RING_MOD, pan_spread=PAN_SPREAD)
wet = np.asarray(wet, dtype=np.float32)
print("SP-157 done in %.1f s; wet shape %s peak %.4f"
      % (time.time() - t_157, wet.shape, float(np.max(np.abs(wet)))), flush=True)

# ---- 3. master ----
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB), flush=True)
mastered, rep = master(wet, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))),
      flush=True)

final_wav = OUT / "SP157-whole-tone-filterbank-247-metal-fourier-spectrum.wav"
final_ogg = OUT / "SP157-whole-tone-filterbank-247-metal-fourier-spectrum.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV %d B, OGG %d B" % (final_wav.stat().st_size, final_ogg.stat().st_size), flush=True)

# ---- 4. verification ----
meas_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono_out = 0.5 * (mastered[:, 0] + mastered[:, 1])
silence_pct = float(np.sum(np.abs(mono_out) < 0.001) / len(mono_out)) * 100.0
rms = float(np.sqrt(np.mean(mono_out ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono_out[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono_out), SR)]

# section pools by time (bar = 60/140*4 = 1.7142857 s; 8 bars = 13.7142857 s)
BAR_S = 60.0 / 140.0 * 4.0
SEC_S = BAR_S * 8.0
POOLS = [
    (0.0, SEC_S, {0, 2, 4, 6, 7, 9, 11}),         # Head1
    (SEC_S, 2 * SEC_S, {0, 3, 4, 6, 7, 9, 11}),   # Solo1
    (2 * SEC_S, 3 * SEC_S, {1, 2, 4, 5, 7, 8, 10, 11}),  # Solo2
    (3 * SEC_S, 4 * SEC_S, {0, 2, 4, 6, 7, 9, 11}),      # Head2
]


def pool_for(t):
    for lo, hi, p in POOLS:
        if lo <= t < hi:
            return p
    return POOLS[-1][2]


def pitch_verify(audio_tm):
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
        tsec = (w + 0.5) * 0.5
        if pc in pool_for(tsec):
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


wet_hit, wet_he, wet_valid = pitch_verify(mastered)
dry_hit, dry_he, dry_valid = pitch_verify(audio)
he_retention = wet_he / dry_he if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (wet_hit >= 0.60 and he_retention >= 0.40) else "FAIL"
print("pitch verify: wet hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | "
      "HE retention=%.3f -> %s"
      % (wet_hit, wet_he, dry_hit, dry_he, he_retention, pitch_verdict), flush=True)
print("silence=%.2f%% rms=%.4f LUFS=%.2f peak=%.4f"
      % (silence_pct, rms, meas_lufs, peak_val), flush=True)

cfg = {"resonance": RESONANCE, "pan_spread": PAN_SPREAD, "ring_mod": RING_MOD,
       "gain_floor": FLOOR, "n_bands": fb.n_bands,
       "f_low_hz": round(float(fb.freqs[0]), 1),
       "f_high_hz": round(float(fb.freqs[-1]), 1),
       "strong_bands": strong, "freeze": "dry-mix spectral profile"}

(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "wet_hit_rate": wet_hit, "wet_mean_harmonic_energy": wet_he,
    "dry_hit_rate": dry_hit, "dry_mean_harmonic_energy": dry_he,
    "he_retention": he_retention,
    "valid_windows": wet_valid, "pitch_verdict": pitch_verdict,
    "target_lufs": TARGET_LUFS, "sp157_params": cfg,
    "wall_seconds": round(time.time() - t0, 1),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": DATE, "seed": SEED,
    "method": "SP-157", "method_module": "sound.effects.whole_tone_filterbank",
    "method_desc": "48-Band Whole-Tone Filter Bank — 48 RBJ bandpass bands spaced in whole tones over 8 octaves, per-band resonance, spectral freeze, odd/even panning (AudioThing/Hainbach Seconds-style)",
    "layer": "ABSOLUTE - one resonant 48-band whole-tone bank applied to the whole dry mix (freeze-gain profile + odd/even pan spread)",
    "params": cfg, "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "source_midi": str(REWORKED),
    "humanized_midi": str(HUMANIZED),
    "phase1_midi": str(PHASE1),
    "source_bpm": 140, "source_key": "E minor",
    "source_pitch_classes": "Head/Solo pools: nat minor {0,2,4,6,7,9,11} / harmonic minor {0,3,4,6,7,9,11} / octatonic {1,2,4,5,7,8,10,11}",
    "source_form": "head-solos-head, 32 bars (4 x 8), 140 BPM",
    "preflight": {"grid_off": 0, "out_scale": 0, "out_chord": 0,
                  "zero_drift": True, "note": "humanized source de-humanized (onsets snapped to 16th grid)"},
    "output_wav": str(final_wav), "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict,
    "wet_hit_rate": wet_hit, "wet_he": wet_he,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
print("DONE in %.1f s" % (time.time() - t0), flush=True)
