#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Finalize SP-050 project: OGG, README, provenance, cleanup, verify."""
import json
import os
import shutil
import subprocess
import wave
import numpy as np

OUT = "/opt/data/projects/Styles/Production/SP050-spectral-delay-indian-popular"
SRC_MIDI = "/opt/data/projects/Styles/Hybrid/025-bollo-koos-indian-unified/v2-IndianPopular/MIDI/025v2_unitmatrix.mid"

# 1. OGG conversion
wav_mix = os.path.join(OUT, "Audio", "SP050-spectral-delay-indian-popular.wav")
ogg_mix = os.path.join(OUT, "Audio", "SP050-spectral-delay-indian-popular.ogg")
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", wav_mix,
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg_mix,
], check=True)
print("ogg size:", os.path.getsize(ogg_mix))

# 2. README
readme = """# SP-050 — Spectral Delay Filters on 025v2 (Bollo-Koos x Indian Popular)

## What this is
Autonomous production pass (nightly pipeline). Random composition +
random sound-production method from methods_db.md.

- **Source composition:** `025v2_unitmatrix.mid`
  (Styles/Hybrid/025-bollo-koos-indian-unified/v2-IndianPopular)
- **Method:** SP-050 Spectral Delay Filters (SDF) — STFT-domain per-bin
  delay line + per-bin feedback (Pekonen et al. 2009; Chromax/Stroppa
  partial-template parameterization).
- **Date:** 2026-08-23 (cron production job)

## Source MIDI facts (mido analysis)
- 3 tracks, all channel 0, no program changes (GM defaults), 120 BPM
  (default tempo), 480 TPB, 7680 ticks = 4 bars / 8.0 s.
- Track 0: melody, 16 quarter notes, MIDI 60-67 (D minor-ish contour),
  vel 64 — bars 1-2 only; bars 3-4 silent.
- Track 1: bass F2 (42), 8 eighths, vel 80.
- Track 2: bass thump D2 (38), 8 hits, vel 30.
- Source MIDI copied verbatim to `MIDI/025v2_unitmatrix.mid` (no
  mutation; MIDI manipulation constraint respected).

## SP-050 implementation (per-voice mode, UnitMatrix bus)
1. **Render source to audio** (libfluidsynth ctypes, manual
   `fluid_synth_write_float`, no audio driver — CLI `fluidsynth` binary
   absent; TimGM6mb.sf2):
   - melody -> GM 104 (Sitar), bass F2 -> GM 33 (Electric Bass finger),
     thump D2 -> GM 34 (Electric Bass pick). 0.20 s release tail/note.
2. **SDF per voice** (mono STFT, Hann N=4096, H=N/4=1024):
   - **Melody template:** partial atoms f0 = 293.66 Hz (D4) + 440 Hz (A4),
     harmonic series s=1, shift=0, 8+6 partials, Gaussian atoms
     bw 45/55 Hz, harmweights 1/n. Delay tau_max = 0.75 s (hop-quantized,
     GCD: integer frame counts), feedback g_k = 0.5 + 0.3/n, cap 0.9 < 1
     (Pekonen stability).
   - **Bass template:** f0 = 87.31 (F2) + 73.42 (D2) + 261.63 (C4),
     5+5+4 partials, bw 25/25/40 Hz, tau_max = 0.75 s.
   - Per-bin delay: Y(m,k) = X(m,k) + g_k * Y(m-d_k, k), d_k =
     round(tau_k * fs / H) — feedback cycles land on frame boundaries
     (bin-synchronous, no round-off drift).
   - ISTFT: Hann, COLA normalization by window-squared sum.
3. **Mix:** melody dry 0.35 / wet 0.65, bass dry 0.9 / wet 0.5 (dry
   anchor keeps groove), peak-normalized to -1 dB (0.89).
4. **Deliverables:** full mix WAV + OGG (Opus 48k voip), per-voice stems
   WAV, source MIDI, render_stats.json, this README, provenance.json.

## What to listen for
- Bars 1-2: sitar melody + spectral-delay echo; each quarter note fans
  into a band-based arpeggio (low partials late, high early).
- Bass lock: dry electric bass keeps the groove; wet bass adds low-band
  repeats at 0.75 s (dotted-half rhythm against 4/4).
- Bars 3-4: source is silent — hear the feedback tail ring on (method
  behavior: one burst -> band arpeggio, per methods_db SP-050).
- 14 s render = 8 s loop + 3 s feedback tail + fade.

## Verified numbers (render_stats.json)
- silence fraction 0.267 (tail padding; bars 1-4 all audible)
- per-sec RMS: [0.074, 0.077, 0.029, 0.028, 0.026, 0.024, 0.025, 0.023,
  0.007, 0.005, 0.033, 0, 0, 0]
- peak 0.890 (-1 dB), sr 44100, N_FFT 4096, HOP 1024

## Files
- `MIDI/025v2_unitmatrix.mid` — source (verbatim copy)
- `Audio/SP050-spectral-delay-indian-popular.wav` — full mix
- `Audio/SP050-spectral-delay-indian-popular.ogg` — Telegram-ready Opus
- `Audio/stem_melody.wav`, `Audio/stem_bass.wav` — per-voice stems
- `Analysis/render_stats.json` — DSP + loudness stats
- `src/render_sp050.py` — full pipeline script
- `provenance.json` — job provenance
"""
with open(os.path.join(OUT, "README.md"), "w") as f:
    f.write(readme)

# 3. provenance.json
prov = {
    "job": "production-pass",
    "timestamp": "2026-08-23T00:00:00Z",
    "source_midi": SRC_MIDI,
    "source_midi_sha256": None,
    "method": "SP-050",
    "method_name": "Spectral Delay Filters (SDF)",
    "method_source": "methods_db.md#SP-050",
    "dsp": {
        "stft_fft": 4096,
        "hop": 1024,
        "window": "hann",
        "tau_max_melody_s": 0.75,
        "tau_max_bass_s": 0.75,
        "feedback_cap": 0.9,
        "gcd_quantization": "integer frame counts (hop grid)",
        "per_voice_mode": True,
    },
    "render": {
        "engine": "libfluidsynth ctypes (manual write_float, no audio driver)",
        "soundfont": "TimGM6mb.sf2",
        "sample_rate": 44100,
        "gm_programs": {"melody": 104, "bass_f2": 33, "thump_d2": 34},
        "mix_gains": {"mel_dry": 0.35, "mel_wet": 0.65, "bass_dry": 0.9, "bass_wet": 0.5},
        "peak_norm_db": -1.0,
    },
    "artifacts": [
        "Audio/SP050-spectral-delay-indian-popular.wav",
        "Audio/SP050-spectral-delay-indian-popular.ogg",
        "Audio/stem_melody.wav",
        "Audio/stem_bass.wav",
        "MIDI/025v2_unitmatrix.mid",
        "Analysis/render_stats.json",
        "README.md",
    ],
    "assistance": "AI_ASSISTED",
}
with open(os.path.join(OUT, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)

# 4. cleanup temp scripts in Production root
for tmp in ["_probe_env.py", "_step1_discover.py", "_step2_select.py",
            "_inspect_midi.py", "_dump_midi.py", "_check_render.py"]:
    p = os.path.join("/opt/data/projects/Styles/Production", tmp)
    if os.path.exists(p):
        os.remove(p)
        print("removed", tmp)

# 5. verify final outputs
print("\n== VERIFY ==")
for root, dirs, files in os.walk(OUT):
    for fn in sorted(files):
        p = os.path.join(root, fn)
        print(f"{os.path.getsize(p):>10}  {os.path.relpath(p, OUT)}")

# audio integrity: duration + peak of OGG via ffprobe
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0", ogg_mix],
                   capture_output=True, text=True)
print("ogg duration:", r.stdout.strip(), "s")

with wave.open(wav_mix, "rb") as wf:
    n = wf.getnframes()
    data = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
print("wav duration:", n / 44100, "s, peak:", float(np.max(np.abs(data))))
print("\nDONE")
