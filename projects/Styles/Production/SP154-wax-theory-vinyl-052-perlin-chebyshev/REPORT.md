# SP-154 Wax Theory (Groove-Velocity Vinyl Model) — 052-perlin-chebyshev

Random-style production job (SP methods), layer-aligned, **2026-11-12**.

## Selection

| Item | Value |
|---|---|
| Seed | `20261112` |
| Registry | `workflows.musicom_workflow.SP_METHODS` (93 pickable methods) |
| Selected method | **SP-154** — `sound.effects.wax_theory_vinyl` |
| Method desc | Groove-Velocity Vinyl Model — Side control = 51→21 cm/s linear velocity driving 2nd-harmonic tracing distortion, v/(2λ) bandwidth limit, wow/flutter, LP/45/78 formats, HiFi/DJ/Worn stylus profiles, dust ticks + scratch pop + bearing rumble, platter brake (Modbap Wax Theory-style) |
| Source composition | `Experimental/052-perlin-chebyshev/MIDI/052-perlin-chebyshev.mid` |
| Pool (after exclusions) | 85 methods |
| Recent excluded (≤7 d) | SP-069, SP-097, SP-113, SP-119, SP-138, SP-143, SP-146 |
| Baseline excluded | SP-001 |
| Already on source | (none) |
| Candidates / well-formed / meaningful | 444 / 339 / 338 |

## Source composition

- **Genre**: Experimental — Perlin Noise Composition (Method 040) + Chebyshev
  Waveshaping velocity mapping (SP-019).
- **Key**: D natural minor (D E F G A Bb C = pc {2,4,5,7,9,10,0}).
- **Tempo**: 100 BPM · 4/4 · 480 ticks/beat.
- **Form**: 3 sections (A-B-C) × 4 bars = **12 bars** = 23040 ticks ≈ 28.8 s.
- **Harmony**: static **Dm7** (D F A C = pc {2,5,9,0}) across all 12 bars
  (pad = Dm7 sustains, bass = D/F/A roots).
- **Voices** (3 note tracks):
  | Track | GM | Voice |
  |---|---|---|
  | 1 | 74 Recorder/Flute | Lead — Perlin FBM pitch contour, 16 quarter-note steps/section |
  | 2 | 88 New Age Pad | Pad — Dm7 sustain per section |
  | 3 | 33 Electric Bass (finger) | Bass — one root/bar via Perlin |

## Pre-flight rules audit (BEFORE any sound change)

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **PASS** | 0 / 72 onsets off-grid (16th = 120) |
| 2. Harmony | **FAIL → FIXED** | 0 / 72 out-of-scale (D minor). **34 / 48 lead onsets off-chord** (G pc7 ×21, Bb pc10 ×5, E pc4 ×8 over static Dm7) |
| 3. Zero-drift | **PASS** | all 3 note tracks terminate at 23040 ticks (12 bars) |

### What failed and the fix

Only **Rule 2** failed. The lead melody is a Perlin-driven free wander over the
D natural-minor scale, but the accompaniment is a static **Dm7** — so the
scale's 2nd (E), 4th (G) and 6th (Bb) sit over the chord as non-chord tones
(34 of 48 lead onsets). All 34 are in-key (no out-of-scale crud), but the
strict harmony rule (chord tone of its bar) flags them.

**Rework**: chord-tone quantize the lead voice — snap each non-chord lead note
to the nearest Dm7 chord tone (minimal |semitone| move, tie → lower note):
- E (pc 4) → F (pc 5) — nearest at +1 st
- G (pc 7) → F (pc 5) — tie at ±2 st, lower wins
- Bb (pc 10) → A (pc 9) — nearest at −1 st

Pad and bass untouched (already 100% chord tones). Grid, velocities, durations,
programs, channels and terminal pads all preserved byte-exact. Re-exported via
the musicom engine (`UnitMatrixComposer`, `validate()` zero-drift gate). Raw
draft kept as `MIDI/052-perlin-chebyshev-phase1.mid` sidecar.

**Re-audit (after rework)**:
- off-grid: **0** · out-of-scale: **0** · out-of-chord: **0** (was 34)
- zero-drift: **true** (3 tracks × 23040 ticks)

## Method application — SP-154 (ABSOLUTE layer)

One vinyl playback chain applied across the whole dry mix. Parameters:

| Param | Value |
|---|---|
| format | `LP` (33⅓ rpm) |
| stylus | `HiFi` |
| side | `0.30` (mid-groove) |
| dust | `True` (surface ticks + scratch pops) |
| wear | `0.40` |
| wow_depth | `0.50` |
| platter brake | disabled (`stop_at=None`) |
| sample rate | 44100 |

**Physical state derived from `side`** (printed by the engine):
- linear velocity = **42.00 cm/s**
- tracing drive (2nd-harmonic distortion) = **0.1271**
- bandwidth (groove wavelength limit) = **8209 Hz**
- surface-noise level = **0.00311**

Per-channel application (same `WaxTheory` instance on L then R): wow/flutter is
deterministic → coherent across channels (one turntable); surface-noise RNG
advances → decorrelated L/R ticks (realistic vinyl).

Pipeline: reworked MIDI → dry FluidSynth (`-R 0 -C 0 -g 1.2`, FluidR3_GM.sf2)
→ WaxTheory vinyl → `master()` (target −14.0 LUFS, −1.0 dBTP) → WAV + Opus OGG.

## Verification

**Pitch verification** (FFT dominant peak per 0.5 s window, 50–1000 Hz, vs Dm7
chord-tone pcs {D,F,A,C}):

| Metric | Dry (reference) | Wet (SP-154) |
|---|---|---|
| Pitch-class hit rate | 0.9828 | **0.9254** |
| Mean harmonic energy (8 harmonics) | 0.6874 | **0.5952** |
| HE retention (wet/dry) | — | **0.866** |
| Verdict | — | **PASS** (hit ≥ 0.60, HE retention ≥ 0.40) |

The vinyl chain preserves pitch identity well (2nd-harmonic tracing distortion
*adds* harmonic energy at the octave; wow/flutter depth ≈ ±0.08 % — well under
one semitone, so dominant-pitch frames stay on the expected pitch class).

**Loudness / silence / RMS**:

| Metric | Value |
|---|---|
| Integrated LUFS | −14.23 (target −14.0) |
| True peak | 0.8913 (−1.00 dBTP ceiling) |
| Silence (< 0.001) | **1.49 %** |
| Overall RMS | 0.1528 |

Per-second RMS profile: music 0–28 s (0.10–0.24), then a quiet run-out tail
29–33 s (0.02–0.04) = FluidSynth pad release + vinyl surface-noise floor in the
run-out groove (not a gap — the noise floor is the effect's intended character).
No mid-track silence.

## Artifacts

| Path | Size |
|---|---|
| `SP154-wax-theory-vinyl-052-perlin-chebyshev.ogg` | 231 526 B |
| `SP154-wax-theory-vinyl-052-perlin-chebyshev.wav` | 5 984 556 B |
| `dry_full_mix_sp001_reference.wav` | 5 984 556 B |
| `MIDI/052-perlin-chebyshev.mid` (reworked, clean) | 699 B |
| `MIDI/052-perlin-chebyshev-phase1.mid` (raw) | 699 B |
| `MIDI/rework_audit.json` | 195 B |
| `Analysis/render_stats.json` | 1 174 B |
| `provenance.json` | 2 286 B |

## Decision log

- Selection via `select_job_20261112.py` (registry `SP_METHODS`, 93 methods;
  85 in pool after exclusions).
- Rework via `rework_052_20261112.py` (chord-tone quantize lead only; static
  Dm7 means one chord-tone set for all 12 bars).
- Render via `produce_sp154_cron.py` (per-channel WaxTheory, then master).
- SoundFont: `discover_soundfont()` → FluidR3_GM.sf2 (not the thin TimGM6mb).
