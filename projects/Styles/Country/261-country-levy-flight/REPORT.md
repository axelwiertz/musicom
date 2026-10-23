# REPORT — 261-country-levy-flight

**Date:** 2026-10-23 · **Job:** musicom nightly composition (ID 1fc3fd65d359) · **Status:** complete + verified

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| **Project** | `Styles/Country/261-country-levy-flight/` |
| **Style** | **Country** — random draw from 48 genre folders (seed 20261023) |
| **Method** | **053 — Lévy Flight Composition (LFC)** |
| **Layer** | **concrete** (Stochastic · Nature-Led) — emits `MusicEvent` stream, feeds `generators/` |
| **Form** | **aabb** — `pick_form(style)` style-weighted (country hint → aabb); A1(4) A2(4) B1(4) B2(4) = **16 bars** |
| **Key / meter** | G major · 4/4 · 112 BPM |
| **Selection rule** | ~6/7 concrete (this night = concrete branch); method 053 not in the last-7-days exclusion set (006, 026, 043, 051, 065, 075, 082, 098, 104, 111, 113, ABS-001/002). |

## 2. Method mechanics (concrete → engine)

**Phase 1 — raw Lévy-flight draft.** Heavy-tailed random walk in pitch space:
~85% of steps are small (±1..3 semitones → stepwise *motifs*), ~15% are large
jumps (±4..14 semitones → *leaps* / section pivots). Pitch is a continuous
float, onsets are off-grid floats. Result: **100 raw events**, single voice,
**34 chromatic** (out-of-scale), **39 off-grid** — the unquantized generative
character preserved, exported as `-phase1.mid` with its own zero-drift gate.

**Phase 2 — musicom rules post-processing (tiered pitch discipline):**
- Onsets snapped to the **16th grid (120 ticks)**; rhythm-grid sync enforced.
- Weight-aware pitch snap via `ScaleQuantizer.tiered_quantize`:
  **strong** (beat 1/3) → scale THEN chord tone (hard in-scale + in-chord);
  **weak** (off-beat) → scale tone only.
- **Tagged chromatic ornaments** on the lead (`rules.ornament.approach_note`):
  3 chromatic approach tones, each `weight="weak"`, `ornament="approach"`,
  `resolve_pitch=<next chord tone>` — legal only because tagged + resolves by
  step within 1 grid step.
- Full texture: fiddle lead + steel-acoustic guitar strum + double-bass
  root-fifth + train-beat drums.

## 3. Voices + instruments (registry = source of truth)

| Voice | Instrument | Program | Channel | humanize_dna (timing, vel, layback, dur) |
|---|---|---|---|---|
| Lead | Fiddle | 110 | 0 | (None, 6.0, None, 0.02) |
| Guitar | Steel Acoustic | 25 | 1 | (None, 6.0, None, 0.02) |
| Bass | Double Bass | 43 | 2 | (10.0, 6.0, 8.0, 0.03) |
| Drums | Drum Kit | 0 | 9 | (2.0, 4.0, 0.0, 0.008) |

## 4. Harmony — full progression (G major)

`G G C G | G G C D | D C G G | D C D G` (A = I–IV–I, B = V–IV–I–V turn)

Chord pcs: G = {7,11,2} · C = {0,4,7} · D = {2,6,9} · scale pcs = {7,9,11,0,2,4,6}

## 5. Grid audit (16th = 120 ticks) — readback, real numbers

| Version | pitched off-grid | drums off-grid | total off-grid | verdict |
|---|---|---|---|---|
| **perfect** | 0 / 294 | 0 / 192 | **0** | grid-locked ✓ |
| **humanized** | 275 / 294 | 140 / 192 | **415** | jitter present ✓ |
| **phase1** (raw) | 39 / 100 | — | 39 | intentionally unquantized |

## 6. Harmony audit — `workflows.pitch_audit.audit_voice` (tiered, authoritative)

| Voice | notes | strong_ok | weak_in_scale | tagged ornaments (resolving) | untagged_out | non_resolving | strong_viol | **passes** |
|---|---|---|---|---|---|---|---|---|
| Lead | 102 | 14 | 85 | 3 (3) | 0 | 0 | 0 | ✅ |
| Guitar | 128 | 32 | 96 | 0 | 0 | 0 | 0 | ✅ |
| Bass | 64 | 32 | 32 | 0 | 0 | 0 | 0 | ✅ |

Drums = channel 9 (unpitched), excluded from the pitch audit by role. All
pitched voices: **0 un-tagged out-of-scale / 0 non-resolving / 0 strong
violations** — the hard gate is satisfied. Naive readback (perfect) counts
exactly 3 chromatic pitches = the 3 tagged ornaments, nothing else.

## 7. Humanization (always-on, style-derived, seeded) + dual-version export

`export_dual()` via `workflows.humanize`; style profile = `STYLE_HUMANIZE["country"]`
(timing 9.0 ms, vel 6.5, phrase_corr 0.5, layback 2.0 ms); **hz_seed = 20261024**.
Per-voice instrument DNA overrides as listed above.

| Voice | child seed | timing σ (ms) | layback (ms) | mean shift (ticks) | max shift | mean vel Δ |
|---|---|---|---|---|---|---|
| Lead | 2046363424 | 9.0 | 2.0 | 5.657 | 21 | 5.245 |
| Guitar | 2046363425 | 9.0 | 2.0 | 6.562 | 25 | 5.094 |
| Bass | 2046363426 | 10.0 | 8.0 | 8.499 | 27 | 4.891 |
| Drums | 2046363427 | 2.0 | 0.0 | 1.156 | 4 | 3.422 |

Rhythm-section roles hold their DNA: **drums tightest** (2 ms / 0 layback),
**bass lays back** (8 ms) — as intended. Melodic voices style-governed (9 ms).

## 8. Zero-drift status

`validate()` passed on **all three** exports. Readback: perfect/humanized =
4 tracks × 30720 ticks (equal); phase1 = 1 track × 30720 ticks. No drift.

## 9. Render + master (both versions + phase1)

FluidSynth (FluidR3_GM.sf2, `-R no -C no`) → WAV → `master()` to
`target_for_style("Country")` = **−14 LUFS**, ceiling −1 dBTP → Opus OGG.

| Version | LUFS | dBTP | peak | silence | duration | wav | ogg |
|---|---|---|---|---|---|---|---|
| perfect | −14.02 | −1.00 | 0.861 | 13.2% | 40.1 s | 7.08 MB | 279 KB |
| humanized | −14.06 | −1.00 | 0.833 | 15.2% | 41.5 s | 7.33 MB | 288 KB |
| phase1 | −14.00 | −4.13 | 0.543 | 7.4% | 36.5 s | 6.44 MB | 283 KB |

phase1 dBTP −4.13 is correct: true-peak is a *ceiling*, not a target — the
single-voice raw draft never reaches −1 dB and is not pushed up. Silence all
< 30% (tail padding only, no mid-track gaps). Post-master LUFS ≈ −14 target.

## 10. Files

```
MIDI/261-country-levy-flight-phase1.mid     (939 B, raw draft)
MIDI/261-country-levy-flight-perfect.mid    (3997 B, grid-locked)
MIDI/261-country-levy-flight-humanized.mid  (3993 B)
MIDI/*.provenance.json                       (3 sidecars)
Audio/261-country-levy-flight-{perfect,humanized,phase1}.ogg/.wav
Audio/render_stats.json
Analysis/grid_visualization.txt
Analysis/summary.json
Analysis/pitch_audit.json
Analysis/verify.json
compose.py · render.py · verify.py
```

## 11. Fixes applied this session

1. `fill()` now builds **non-mutating copies** of `MusicEvent`s when rebasing
   section-local ticks — the in-place rebase previously corrupted the
   absolute-tick source, so the accompaniment pitch audit read section-local
   ticks and reported phantom strong_violations/collisions.
2. Ornament slot check corrected from `% BAR == BEAT` (beat 2) to
   `% BAR == 2*BEAT` (beat 3 = 960) — otherwise no strong note ever matched
   and 0 ornaments were placed.
