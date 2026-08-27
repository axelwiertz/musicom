# SP-050 — Spectral Delay Filters on 025v2 (Bollo-Koos x Indian Popular)

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
