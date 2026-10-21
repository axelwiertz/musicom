# SP-090 Orbital Stereo Sculptor / AutoPanner — 012-country-country-uke

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-21  **Seed:** 20261021

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (54 registered) — the **implemented** dict, NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-090` |
| Module | `sound.effects.orbit_sculptor` → `OrbitalStereoSculptor` (`LinkwitzRiley4Crossover`, `OrbitalBandProcessor`, `ModulatorConfig`) |
| Description | 3-Band Orbital Stereo Sculptor / AutoPanner — LR4 24 dB/oct crossover into Low/Mid/High; per-band pan (constant-power law), stereo width (mid/side), gain, and LFO modulators (sine/tri/square/random/env, tempo-synced or free Hz) |
| Layer | ABSOLUTE — the WHOLE dry FluidSynth mix is fed as one buffer; one band config applied to the whole piece |
| Recent excluded (7d) | SP-006, SP-028, SP-032, SP-092, SP-099, SP-105, SP-108, SP-111 |
| Already on source | (none) |
| Baseline excluded | SP-001 |
| Pool size | 46 |
| Well-formed candidates | 249 / 361 |

**Source composition:** `Styles/Country/012-country-country-uke/MIDI/v2_country_unitmatrix.mid`
- Country-pop road song, **G major**, **96 BPM**, 4/4, TPB 480 (bar = 1920), **48 bars** (120.3 s); type-1 MIDI, 9 tracks.
- 8 voices: Lead Vocal (ch0, prog 53), Harmony Vox (ch1, prog 52), Acoustic Guitar (ch2, prog 24), Electric Guitar (ch3, prog 29), Bass (ch4, prog 33), Drums (ch9), Fiddle (ch5, prog 40), Pedal Steel (ch6, prog 48).
- Chord progression (per bar): Intro G·D·Em·C; Verse/Chorus ×2 G·D·Em·C·G·D·C·D; Bridge Em·C·G·D; Final Chorus G·D·C·D; Outro G·C·G·G.
- 1960 total notes (1608 pitched + 352 drums). Fully diatonic G major (0 out-of-scale in source).

## PRE-FLIGHT AUDIT (3-rule gate) — FAILED on 3 of 4

| Rule | Before | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | 192 off-grid | **FAIL** |
| Harmony — in scale (G major {7,9,11,0,2,4,6}) | 0 out-of-scale | PASS |
| Harmony — chord tone (per-bar G/D/Em/C) | 576 out-of-chord | **FAIL** |
| Zero-drift (note tracks equal length) | 8 distinct ends [91564…92400] | **FAIL** |

**Findings:**
- **Grid (192):** the acoustic-guitar strums are authored as 3-note rolls at
  14/28-tick micro-offsets from the 0/960/1920 grid base (e.g. onsets 0·14·28,
  960·974·988). Deliberate strum articulation in the May-2026 source, but the
  current standard requires grid-locked onsets.
- **Chord-tone (576):** lead/harmony/e-guitar/fiddle/pedal-steel melodies carry
  diatonic *passing tones* (scale degrees 2 and 6) that are in the G-major scale
  but not chord tones of their bar (e.g. A=69 over a G chord {G,B,D}). Fully
  diatonic (0 out-of-scale), but the nightly-composition standard is
  chord-tone-clean, so these are non-compliant.
- **Zero-drift:** final-note durations differ by voice, so note tracks end at 8
  distinct ticks (91564…92400).

## REWORK (two-phase, source preserved)

`Scripts/rework_20261021.py` — repairs the source into a rule-clean copy in the
production folder; the source MIDI is **never modified** (byte copy kept as
`MIDI/source_original.mid`).

1. **Grid snap** — every note onset snapped to nearest 16th (×120). Strum rolls
   collapse to block chords (0·14·28 → 0·0·0). Duration preserved
   (`end = snapped_start + orig_dur`).
2. **Chord-tone quantize** — every pitched note not a chord tone of its bar is
   snapped to the nearest chord tone (signed circular semitone delta, tie →
   downward resolution). Passing tones resolve (A→G over G/D/Em/C, E→D, F#→G).
3. **Zero-drift** — all note ends clamped to 48 bars (92160), every note track
   padded to 92160 (terminal landmark).

**Re-audit after rework — CLEAN:**

| Rule | After | Verdict |
|---|---|---|
| Grid sync | 0 off-grid | PASS |
| In-scale | 0 out-of-scale | PASS |
| Chord-tone | 0 out-of-chord | PASS |
| Zero-drift | 8 tracks × 92160 | PASS |

grid snaps applied: 192 · chord snaps applied: 576 · notes preserved: 1960.

## Layer discipline (absolute)

SP-090 is an **absolute-layer stereo effect**: the dry FluidSynth mix (FX off)
is the single source; `OrbitalStereoSculptor` splits it into Low/Mid/High via
LR4 crossover and applies per-band pan/width/gain + tempo-synced LFO autopan.

Pipeline: dry FluidSynth (`-R 0 -C 0`, `-g 1.2`) → `OrbitalStereoSculptor`
(whole mix) → `master()` (country −14 LUFS, −1 dBTP) → WAV + Opus OGG. Dry
per-track stems via `RenderPipeline.render_stems` as DAW-import artifacts.

| Param | Value |
|---|---|
| `low_mid_cross` / `mid_high_cross` | 250 Hz / 3500 Hz (LR4 24 dB/oct) |
| Low band | pan 0.0, width 0.0 (bass centered mono), gain 0 dB |
| Mid band | pan 0.0, width 1.15, gain 0 dB, `pan_mod` sine · tempo-sync 1/2 · depth 0.45 |
| High band | pan 0.0, width 1.5, gain 0 dB, `pan_mod` sine · tempo-sync 1/8 · depth 0.35 |
| Mastering | `master()` → LUFS −14.0 (`target_for_style("country")`), ceiling −1 dBTP |

The low end stays centered/mono (standard practice — no bass wandering); the
mid band sweeps at half-note rate, the high band at eighth-note rate for a
gentle country "orbital" motion without destabilising the groove.

## Pitch / tonal-content verification — PASS

| Metric | Wet (SP-090) | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 241 | 241 |
| FFT pitch-class hit rate | **1.0000** | 1.0000 |
| Mean harmonic energy (8 harmonics) | 0.5137 | 0.4904 |
| HE retention | 1.048 | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40). The orbit
sculptor is a pure stereo panner (pan/width/gain only — **no pitch shift**), so
pitch-class content is fully preserved (hit 1.0). Harmonic energy is essentially
unchanged (retention 1.048, within measurement noise from constant-power pan
law). No 0-Hz frames, no noise signature.

## Silence / RMS profile

- Silence ratio: **3.69%** (clean — no mid-track gaps; the 124.3 s dry render is
  music end-to-end, the only silence is the natural attack gaps between notes).
- Overall RMS: **0.1339**
- LUFS: **−14.02**  |  Peak: **0.8913** (−1.0 dBTP ceiling)
- Mono correlation: **0.631** — the tempo-synced mid/high autopan decorrelates
  the L/R channels from ~1.0 (dry center-panned) into a moving stereo image;
  still strongly correlated (the lows stay centered/mono, and only the mid/high
  bands pan), so mono-downmix compatibility is preserved.

## Artifacts

| File | Size |
|---|---|
| `SP090-orbit-sculptor-012-country-uke.wav` | 21,932,588 B (124.3 s) |
| `SP090-orbit-sculptor-012-country-uke.ogg` | 906,787 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 21,932,588 B |
| `Audio/stems_dry/track00_Voice_Oohs.wav` | 21,658,924 B |
| `Audio/stems_dry/track01_Choir_Aahs.wav` | 21,865,516 B |
| `Audio/stems_dry/track02_Acoustic_Guitar_nylon.wav` | 21,521,196 B |
| `Audio/stems_dry/track03_Overdriven_Guitar.wav` | 21,533,740 B |
| `Audio/stems_dry/track04_Electric_Bass_finger.wav` | 21,521,196 B |
| `Audio/stems_dry/track05_Drums.wav` | 21,536,812 B |
| `Audio/stems_dry/track06_Violin.wav` | 21,600,044 B |
| `Audio/stems_dry/track07_String_Ensemble_1.wav` | 21,932,588 B |
| `MIDI/composition.mid` (reworked, zero-drift/grid/chord clean) | 17,653 B |
| `MIDI/source_original.mid` (byte copy of source) | 17,650 B |
| `provenance.json` | 1,876 B |
| `Analysis/render_stats.json`, `Analysis/select_20261021.json` | — |
| `Scripts/` — select / audit / rework / produce (4 files) | — |

Stem labels use GM program names (not `add_voice()` names): prog 53 → `Voice_Oohs`,
52 → `Choir_Aahs`, 24 → `Acoustic_Guitar_nylon`, 29 → `Overdriven_Guitar` (the
known off-by-one label quirk for program 29), 33 → `Electric_Bass_finger`,
40 → `Violin`, 48 → `String_Ensemble_1`, ch9 → `Drums`.

## Notes

- **Source MIDI was NOT modified in place** — the rework is a rule-clean copy in
  the production folder's `MIDI/composition.mid`; `MIDI/source_original.mid` is a
  byte copy of the original. Grid snap (192) and chord-tone quantize (576) are
  applied only to the copy.
- The pre-flight gate caught a legacy May-2026 composition that predates the
  strict grid/chord/zero-drift standards. The rework is the two-phase fix the
  gate prescribes: quantize onsets → chord-tone quantize → zero-drift pad →
  re-audit to 0/0/0 → then apply the SP method.
- `master()` landed at −14.02 LUFS (target −14) with peak at the −1 dBTP
  ceiling — correct ceiling behaviour (the limiter is a ceiling, not a target).
- Selection script: `Production/select_job_20261021.py` (writes
  `.selection_cron.json`). Audit: `Scripts/audit_source_20261021.py`. Rework:
  `Scripts/rework_20261021.py`. Produce: `Scripts/produce_sp090_cron.py`.
- WAVs are `.gitignore`d; tracked deliverables = OGG + MIDI + REPORT +
  provenance + Scripts + Analysis. Commit/push handled by the nightly auto-sync.
