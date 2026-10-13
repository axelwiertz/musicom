# SP-103 Parallel Filter Bank — 048-pcfg-binaural

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-13  **Seed:** 20261013

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (45 registered) |
| Method | `SP-103` |
| Module | `sound.effects.parallel_filter_bank` |
| Description | Filtopia-style 5-Parallel SEM Filter Bank (5 parallel 12 dB/oct Oberheim SEM-inspired filters, per-filter cutoff offset/resonance, LP/BP switchable on slots 1&5) |
| Layer | ABSOLUTE — one filter-bank config applied to the whole piece |
| Recent excluded (7d) | SP-026, SP-069, SP-074, SP-085, SP-091, SP-092, SP-098 |
| Pool size | 37 |
| Well-formed candidates | 229 / 338 |

**Source composition:** `Styles/Experimental/048-pcfg-binaural/MIDI/048-pcfg-binaural.mid`
- 8-bar C Dorian, 100 BPM, 4/4, TPB 480
- Voices: Lead (Violin, prog 40 ch0), Pad (Synth Pad 89 ch1), Bass (Acoustic Bass 32 ch2)
- Methods: 034 (PCFG Recursion) + SP-021 (Binaural, original)

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Before | After | Verdict |
|---|---|---|---|
| Grid sync (8th/16th = 240/120 ticks) | 0 off-grid | 0 | PASS |
| Harmony — in scale (C Dorian) | 1 out-of-scale | 0 | PASS |
| Harmony — chord tone of bar | 56 out-of-chord | 0 | PASS |
| Zero-drift (equal track lengths) | 15360 = 15360 = 15360 | 15360 = 15360 = 15360 | PASS |

**Verdict: FAIL → reworked → PASS.** The raw PCFG lead line cycled scale
degrees independent of the harmonic context (56 non-chord tones), and bar 8's
Picardy-third pad held an E-natural (out of C Dorian).

### Rework applied (two-phase, engine-based)

- Phase-1 sidecar: `MIDI/048-pcfg-binaural-phase1.mid` (raw original preserved).
- Phase-2 (`_cron_rework_048.py`, `UnitMatrixComposer`):
  - **Lead** (51 notes snapped): each 16th-note pitch quantized to the nearest
    chord tone of its bar (register/contour preserved, ±12 st).
  - **Pad** (1 note fixed): bar 8 reharmonized C-major → Cm (E→Eb, 52→51) to
    stay inside C Dorian.
  - `validate()` → True, re-exported `048-pcfg-binaural.mid` (1400 B).

Chord-tone sets per bar: Cm7, F7, Bb, EbMaj7, Cm7, F7, Gm7, Cm.

## Method parameters (SP-103)

- Base cutoff: **1400 Hz** (keeps 65–784 Hz fundamental band inside LP slots' passband — pitch-safe).
- 5 slots:

| Slot | Mode | Offset (Hz) | Resonance | Mix |
|---|---|---|---|---|
| 1 | LP | −300 | 0.50 | 0.80 |
| 2 | BP | −100 | 0.30 | 0.60 |
| 3 | BP | 0 | 0.40 | 1.00 |
| 4 | BP | +200 | 0.30 | 0.60 |
| 5 | LP | +500 | 0.50 | 0.80 |

- Post: normalize_to_lufs(−14.0) → Limiter(−1 dBFS).

## Pitch verification (mandatory for synthesis/effects)

| Metric | Wet | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 40 | 40 |
| FFT pitch-class hit rate | **1.000** | 1.000 |
| Mean harmonic energy (8 harmonics) | 0.2994 | 0.3116 |
| HE retention | **0.961** | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40). The filter
bank is linear and preserves the fundamental; hit rate stayed at 100% and
harmonic-energy retention at 96%.

## Silence / RMS profile

- Silence ratio: **16.86%** (below the 30% suspect threshold; the gaps are the
  staccato 16th-note articulation, not mid-track holes).
- Overall RMS: 0.1253
- LUFS: −14.00  |  Peak: 0.7513 (true-peak ceiling −1 dB is a ceiling, not a target)
- Mono correlation: 0.780

## Artifacts

| File | Size |
|---|---|
| `SP103-parallel-filter-bank-048-pcfg-binaural.wav` | 4,269,612 B |
| `SP103-parallel-filter-bank-048-pcfg-binaural.ogg` | 145,799 B |
| `dry_full_mix_sp001_reference.wav` | 4,269,612 B |
| `MIDI/048-pcfg-binaural.mid` (copy of reworked source) | 1,400 B |
| `Audio/stems_dry/*.wav` (3 stems) | 3.8–4.3 MB |
| `Audio/stems_wet/*_PFB.wav` (3 stems) | 3.8–4.3 MB |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/select_20261013.json` | — |

Stem labels: `track00_Violin`, `track01_Pad_2_warm`, `track02_Acoustic_Bass`.

## Notes

- Selection script: `Production/select_job_20261013.py`.
- Source rework script: `Experimental/048-pcfg-binaural/_cron_rework_048.py`.
- Raw original preserved at `Experimental/048-pcfg-binaural/MIDI/048-pcfg-binaural-phase1.mid`.
- Trailing `shutil.copy2` SameFileError at end of produce script is cosmetic
  (script already lived in `Scripts/`); all artifacts written before it.
