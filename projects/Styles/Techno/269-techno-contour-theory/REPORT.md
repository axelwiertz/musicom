# 269-techno-contour-theory — Report

**Date:** 2026-10-26 · **Project:** 269 · **Genre:** Techno

## Selection

| Field | Value |
|---|---|
| Style | **Techno** (random from `/projects/Styles/` genre folders) |
| Method | **095 Contour Theory Composition (CTC)** — **layer: abstract** (→ concrete interpretation) |
| Form | **intro-break-drop-outro** (24 bars) |
| Key | **A natural minor** (aeolian) |
| BPM / meter | 128 / 4/4 (480 TPB, BAR = 1920) |
| Seed | 20261026 (humanize 20261027) |

> Form note: `pick_form("Techno")` first rolled the occasional loop form
> (`loop4`, ~1/7). For a full-length nightly deliverable this was re-resolved
> to the style-hinted canonical techno form `intro-break-drop-outro`
> (Intro 4 · Break 8 · Drop 8 · Outro 4 = 24 bars), matching the palette's
> techno→intro-break-drop hint.

## Method — 095 Contour Theory Composition (abstract layer)

A melodic contour (CSEG) is the *shape* of a melody — an ordered sequence of
pitch positions described by up/down/same relations, independent of exact
pitch. The abstract layer holds a 4-member **contour class** (ContourNetwork),
the concrete layer maps each **rank** → scale degree.

```
BASE (P)  = [0, 3, 1, 2, 4, 1]    CAS = [+, -, +, +, -]
I         = [4, 1, 3, 2, 0, 3]    CAS = [-, +, -, -, +]
R         = [1, 4, 2, 1, 3, 0]    CAS = [+, -, -, +, -]
RI        = [3, 0, 2, 3, 1, 4]    CAS = [-, +, +, -, +]
```

rank 0..4 → A3 C4 D4 E4 G4 (A-natural-minor pentatonic degrees).
Section traversal: Intro=P, Break=P·I·R·RI (×2), Drop=RI·R·I·P (octave +1),
Outro=I·P.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw contour draft — single Clavi voice, 109
  notes, **off-grid onsets** (8th-slot ±40-tick jitter) + octave register
  drift, **no harmony**. The abstract generative layer.
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): grid-lock to 16ths,
  **tiered weight-aware snap** (`ScaleQuantizer.tiered_quantize` +
  `classify_weight`): strong beats (1 & 3) → in-scale AND in-chord; weak → in-
  scale only. Full techno texture. Dual export via `export_dual`.

## Voices (instrument registry)

| Voice | Instrument | GM program | Channel | Notes |
|---|---|---|---|---|
| Lead  | Clavi        | 7   | 0 | contour melody (144) |
| Pad   | Pad 1 (new age) | 88 | 1 | sustained triad (72) |
| Bass  | Synth Bass 1  | 38  | 2 | techno pump (176) |
| Drums | Drum Kit     | 0   | 9 | 4-on-floor (percussion) |

## Harmony

4-bar cycle **i — bVI — bVII — i** (Am — F — G — Am) repeated across 24 bars.

| degree | chord | pcs | bass root MIDI |
|---|---|---|---|
| i   | Am | 9 0 4   | 45 (A2) |
| bVI | F  | 5 9 0   | 41 (F2) |
| bVII| G  | 7 11 2  | 43 (G2) |
| i   | Am | 9 0 4   | 45 (A2) |

## Grid audit (off-grid onsets)

| version | off-grid | verdict |
|---|---|---|
| phase1    | 107 / 109 | > 0 (raw draft — expected) |
| perfect   | **0** | all voices on 16th grid ✓ |
| humanized | 326 | > 0 (proves humanizer ran) ✓ |

## Harmony audit (tiered pitch discipline)

`audit_voice(..., chord_pcs_by_bar=CHORD_BY_BAR, strong_grid=(0,960))`.
Every pitched note must be in-scale AND in-chord, or a tagged resolving
ornament. **All voices: 0 untagged_out_of_scale / 0 tagged_non_resolving /
0 strong_violations.**

| voice | notes | passes | untagged | non-resolving | strong viol |
|---|---|---|---|---|---|
| Lead (ch0)  | 144 | ✓ | 0 | 0 | 0 |
| Pad (ch1)   | 72  | ✓ | 0 | 0 | 0 |
| Bass (ch2)  | 176 | ✓ | 0 | 0 | 0 |
| Drums (ch9) | 0 (perc) | ✓ | 0 | 0 | 0 |

No chromatic ornaments were used (lead carried only scale/chord tones).

## Zero-drift

All 4 voice tracks equal length = **46080 ticks** (24 bars) for both perfect
and humanized. `validate()` passed for phase-1, phase-2-perfect, and
phase-2-humanized.

## Humanization (seed 20261027, style "Techno")

Style profile: timing 2.0 ms (tight), phrase_corr 0.1. Per-voice DNA from the
instrument registry; drums anchor (2 ms / 0 layback), bass lays back (8 ms).

| voice | timing ms | vel σ | layback ms | mean shift (ticks) | max shift | vel Δ |
|---|---|---|---|---|---|---|
| Lead  | 2.0 | 5.0 | 0.0 | 1.354 | 5  | 3.806 |
| Pad   | 2.0 | 4.0 | 0.0 | 1.389 | 5  | 3.389 |
| Bass  | 5.0 | 4.0 | **8.0** | **7.665** | 20 | 2.949 |
| Drums | 2.0 | 4.0 | 0.0 | **1.381** | 5  | 3.383 |

Confirms DNA: drums tightest (1.38), bass lays back most (7.67), all within
profile bounds.

## Render + master (FluidSynth → master() → Opus OGG)

Genre target: **techno → −10 LUFS**, ceiling −1 dBTP. FluidR3_GM.sf2,
`fluidsynth -ni -g 1.2 -R no -C no`.

| version | LUFS (target −10) | true peak | peak | silence | dur |
|---|---|---|---|---|---|
| perfect   | −10.93 | −1.00 dBTP | 0.889 | 11.91% | 52.25 s |
| humanized | −10.89 | −1.00 dBTP | 0.891 | 11.91% | 52.27 s |
| phase1    | −11.04 | −1.00 dBTP | 0.891 | 39.58% | 47.0 s |

phase1 silence 39.58% is **expected**: it is a single-voice sparse raw contour
draft (18% note-drop + rest slots + ~7 s tail), not a full mix. The full mixes
(perfect/humanized) sit at a healthy 11.9% silence.

## Files (all > 40 bytes)

| artifact | bytes |
|---|---|
| MIDI/…-phase1.mid | 1072 |
| MIDI/…-perfect.mid | 6560 |
| MIDI/…-humanized.mid | 6560 |
| Audio/…-perfect.wav / .ogg | 9217068 / 362106 |
| Audio/…-humanized.wav / .ogg | 9220140 / 363018 |
| Audio/…-phase1.wav / .ogg | 8291116 / 333902 |

Each MIDI carries a provenance sidecar; `Analysis/` holds
`grid_visualization.txt`, `summary.json`, `verify.json`.

## Verification summary

- Grid: perfect **0** off-grid · humanized **326** (>0) · phase1 **107** (>0) ✓
- Harmony: 0 un-tagged / 0 non-resolving / 0 strong violations (all voices) ✓
- Zero-drift: 46080 ticks equal across tracks ✓
- Humanization: drums tightest, bass lays back (8 ms) ✓
- Master: −10.9 LUFS ≈ −10 target, true peak −1.0 dBTP ≤ −1 ✓
- Phase-1 contract: 109/109 notes in-scale (contour rank → pentatonic) ✓

## Fixes applied

- Form re-resolved from the occasional `loop4` roll to `intro-break-drop-outro`
  (full-length deliverable; techno-canonical).
- `chord_tones_midi` helper simplified to take the pitch-class list directly
  (avoided a dead-code branch from the first draft).
