# SP-028 LPC Synthesis — 083-techno-brownian

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-14  **Seed:** 20261014

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (45 registered) |
| Method | `SP-028` |
| Module | `sound.effects.lpc_synth` |
| Description | Linear Predictive Coding Synthesis — source-filter model (autocorrelation + Levinson-Durbin all-pole formants; re-excitation with glottal impulse train / noise) |
| Layer | ABSOLUTE — one LPC vocode config applied to the whole piece |
| Recent excluded (7d) | SP-026, SP-069, SP-074, SP-085, SP-092, SP-098, SP-103 |
| Already on source | SP-071 (2026-09-12 severance pass) |
| Pool size | 36 |
| Well-formed candidates | 231 / 340 |

**Source composition:** `Styles/Techno/083-techno-brownian/MIDI/083-techno-brownian.mid`
- 24-bar F natural minor, 128 BPM, 4/4, TPB 480 (BAR = 1920 ticks)
- Composition method 048 — Reflected Brownian Motion Pitch Diffusion (RBMPD)
- Voices: Lead (Church Organ GM19 ch0), Cello (GM42 ch1), Piano (GM1 ch2),
  Violin (GM40 ch3), Double Bass (GM43 ch4), Drums (ch9)
- Note counts: 174 / 72 / 192 / 192 / 137 pitched + 372 drum onsets

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Before | After | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks @ 480 TPB) | 0 off-grid | 0 | PASS |
| Harmony — in scale (F natural minor) | 0 out-of-scale | 0 | PASS |
| Harmony — chord tone of bar | 0 out-of-chord | 0 | PASS |
| Zero-drift (equal track lengths) | 46080 = 46080 = 46080 = 46080 = 46080 = 46080 | unchanged | PASS |

**Verdict: PASS — no rework needed.** The source is already a clean phase-2
rules-processed composition (16th-grid locked, F-minor scale + per-bar
chord-tone quantized, voice-leading checked, zero-drift `validate()` OK from
its own compose run). All three rules read 0 before any SP work. (280 pitched
onsets sit on 16th-but-not-8th positions — offbeat 16ths are allowed by the
grid rule; only off-16th would fail.)

Chord-tone sets per bar follow the source's 24-bar F-minor progression:
i–VI–III–VII | i–iv–v–i | VI–III–VII–i | i–VI–III–VII | i–iv–v–i | VI–III–i–i.

## Method parameters (SP-028 — absolute layer)

| Param | Value |
|---|---|
| order (all-pole) | 16 |
| frame_ms / hop_ms | 30 / 10 (Hamming window, pre-emphasis α=0.97) |
| pitch_shift | 1.0 (formant-preserving resynthesis — no pitch change) |
| voiced_gain / unvoiced_gain | 1.0 / 0.15 |
| wet / dry blend | 0.60 LPC / 0.40 dry (transient support for the 4-on-floor grid) |
| fs | 44100 |

Chain: dry FluidSynth render (FX off) → per-channel LPC analyze + re-excite →
0.6/0.4 wet-dry blend → `normalize_to_lufs(−14)` → `Limiter(−1 dBFS)`.

## Pitch verification (mandatory) — PASS

| Metric | Wet | Dry (SP-001 ref) | Gate |
|---|---|---|---|
| Valid 0.5 s windows | 91 | 91 | — |
| FFT pitch-class hit rate | **1.000** | 1.000 | ≥ 0.60 |
| Mean harmonic energy (8 harmonics) | **0.3908** | 0.4736 | ≥ 0.30 |
| HE retention | **0.825** | — | ≥ 0.40 |

**Pitch verdict: PASS.** LPC with `pitch_shift=1.0` preserves the detected
pitch period exactly (impulse-train re-excitation at the residual's fundamental),
so every 0.5 s window still lands on an F-minor pitch class. Harmonic energy
drops from 0.474 → 0.391 (the all-pole filter + noise excitation for unvoiced
drums softens upper harmonics) but stays 82% retained — far above the 0.40 gate.

## Silence / RMS profile

- Silence ratio: **6.45%** (below the 30% suspect threshold; natural tail
  + staccato 16th articulation gaps, no mid-track holes).
- Overall RMS: 0.1201
- LUFS: −14.20  |  Peak: 0.8913 (true-peak ceiling −1 dB is a ceiling, not a target)
- Mono correlation: 0.471 (LPC per-channel processing decorrelates L/R from the dry's 0.67)

## Artifacts

| File | Size |
|---|---|
| `SP028-lpc-synth-083-techno-brownian.wav` | 8,505,132 B |
| `SP028-lpc-synth-083-techno-brownian.ogg` | 270,874 B |
| `dry_full_mix_sp001_reference.wav` | 8,505,132 B |
| `MIDI/083-techno-brownian.mid` (source copy) | 9,620 B |
| `Audio/stems_dry/*.wav` (6 stems) | 8.36–8.51 MB |
| `Audio/stems_wet/*_LPC.wav` (6 stems) | 8.36–8.51 MB |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/select_20261014.json` | — |

Stem labels: `track00_Church_Organ`, `track01_Cello`,
`track02_Bright_Acoustic_Piano`, `track03_Violin`, `track04_Contrabass`,
`track05_Drums`.

## Notes

- Selection script: `Production/select_job_20261014.py` (record in `.selection_cron.json`).
- Production script: `Scripts/produce_sp028_cron.py`.
- LPC resynth length is `(n_frames−1)·H + L`, 211 samples shorter than the
  48.22 s source — each channel/stem is zero-padded back to the dry length
  before blend (fix applied this run; first attempt crashed on the broadcast
  mismatch, no artifacts were left inconsistent).
- `pitch_shift=1.0` was chosen (not a formant-preserving pitch shift) to keep
  the render pitch-safe for the verification gate; a β>1 pitch-shift variant
  is a trivial follow-up on the same dry render.
