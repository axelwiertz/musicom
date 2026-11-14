# REPORT — 304-trap-bibd-suite

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-14 · Method 132 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Trap** (44 candidate genre folders) |
| Method | **132 — Balanced Incomplete Block Design Composition (BIBDC)** (Rules-Based) |
| **Layer** | **concrete** (weekly abstract cadence not due — last abstract composition was 300 on 11-12, two days ago) |
| Form | **strophic** → sections `Verse1·Verse2·Verse3·Verse4`, bars `[8,8,8,8]` = **32 bars** (from `pick_form("trap")`; trap matches no style hint → full non-loop palette → strophic) |
| Seed | 20261114 · humanize seed 263394786 · form seed 202611147 |

Method pool: concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134,139}, the AI-Driven methods
{42,46,47,54,57,60,62,63,72,74,85,100,101,103,106,108,110,118,140,142}, and the
last-7-days methods {1,7,13,15,23,31,32,41,45,53,75,120,134} → 100 candidates.

## 2. Method 132 — Balanced Incomplete Block Design Composition

The ensemble schedule *is* the composition. A **BIBD(v=4, k=3, λ=2, b=4, r=3)**
over the four pitched voices: 4 points (voices), 4 blocks (verses), 3 active
voices per verse (one rotating tacet), every voice plays r=3 verses, every
voice-pair co-occurs in exactly λ=2 verses. Drums are a constant layer OUTSIDE
the design (trap groove backbone, not a BIBD point).

| Verse | Block (active) | Tacet | Role |
|---|---|---|---|
| Verse1 | Lead · Pluck · Pad | Bass | atmospheric (no 808) |
| Verse2 | Lead · Pluck · Bass | Pad | 808 enters |
| Verse3 | Lead · Pad · Bass | Pluck | fullest (lead octave-up) |
| Verse4 | Pluck · Pad · Bass | Lead | outro texture |

**Pair-novelty curve** (new voice-pairs introduced per verse) = **3 → 2 → 1 → 0**
(sum 6 = C(4,2)) — a provable, order-independent monotone-decreasing tension
curve. Verified on the exported MIDI: 0 schedule violations (tacet voices have
exactly 0 notes in their rest verse; active voices > 0).

## 3. Key, tempo, instruments

- **Key**: E natural minor, `{4,6,7,9,11,0,2}` = E F# G A B C D. Tonic E3 (52).
- **Tempo**: 140 BPM, 4/4, TPB 480 (BAR = 1920). Half-time trap feel.

| Voice | Instrument | GM | Channel | Role |
|---|---|---|---|---|
| Lead | Kalimba | 108 | 0 | sparse pluck lead (raw-walk quantized) |
| Pluck | Music Box | 10 | 1 | syncopated 16th counterline |
| Pad | Warm Pad | 89 | 2 | sustained triads |
| Bass | Synth Bass 1 | 38 | 3 | 808 sub (root + octave) |
| Drums | Drum Kit | 0 | 9 | half-time kick/snare/clap + rolling 16th hats |

All from `projects/Instruments/instrument_registry.py` (source of truth).

## 4. Harmony — i · VI · III · VII (Em · C · G · D)

Classic trap minor loop, repeated 2× per verse (8 bars), consistent across all
four verses (loop-based strophic form; contrast comes from the BIBD ensemble +
register variation, not harmonic change).

| Verse | Progression |
|---|---|
| Verse1–4 | Em Em C G D Em C G D (per 8 bars: i·VI·III·VII ×2) |

## 5. Two-phase pipeline

**Phase 1** (raw): single Kalimba voice, stochastic melodic walk (mostly
conjunct, off-grid onset jitter ±18 ticks, unquantized chromatic pitch), no
harmony, no schedule. Exported `304-trap-bibd-suite-phase1.mid` (own zero-drift
gate). **158 notes, 150 off-grid onsets, 72 out-of-scale, 123 out-of-chord, 1
strong-beat violation** — deliberately imperfect pre-rules material. Per-section
mean pitch: 68.93 / 78.00 / 72.05 / 68.87.

**Phase 2** (rules): 16th-grid lock → tiered snap (`ScaleQuantizer` root E +
`classify_weight`: strong beat → bar chord tone, weak → E-minor scale tone) →
BIBD ensemble schedule → full trap texture (lead/pluck/pad/808/drums) →
landmark → `validate()`. Exported via `export_dual` → `-perfect.mid` +
`-humanized.mid`.

## 6. Grid audit (pre-humanization, phase 2)

| Voice | 16th off-grid | 8th off-grid |
|---|---|---|
| Lead | 0/119 | 60/119 |
| Pluck | 0/96 | 24/96 |
| Pad | 0/132 | 0/132 |
| Bass | 0/48 | 0/48 |

**Perfect layer: 0 off-grid on every pitched voice at the 16th grid** ✓ (the
Lead/Pluck 8th-grid offsets are legitimate 16th-note syncopation; every onset is
16th-aligned).

## 7. Harmony audit (tiered pitch discipline)

`workflows.pitch_audit.audit_voice` per pitched voice (strong_grid = 4/4 beats
1&3, bar 1920, grid 240):

| Voice | total | strong_ok | weak_in_scale | untagged_out | non_resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|
| Lead | 119 | 22 | 97 | 0 | 0 | 0 | ✓ |
| Pluck | 96 | 0 | 96 | 0 | 0 | 0 | ✓ |
| Pad | 132 | 132 | 0 | 0 | 0 | 0 | ✓ |
| Bass | 48 | 24 | 24 | 0 | 0 | 0 | ✓ |

All voices: **0 untagged out-of-scale, 0 non-resolving ornaments, 0 strong
violations** ✓. No chromatic ornaments used (trap is chromatic-free; the lead's
raw chromatic walk is fully snapped to scale/chord tones).

## 8. Humanization (always-on, seeded, dual-version)

`export_dual(style="trap", seed=263394786)` — per-voice instrument DNA from the
registry; trap profile governs melodic timing (4.0 ms, layback 6 ms):

| Voice | timing σ ms | vel σ | layback ms | mean\|shift\| (ticks) | max\|shift\| | mean\|velΔ\| |
|---|---|---|---|---|---|---|---|
| Lead | 4.0 | 6.0 | 6.0 | 6.823 | 14 | 5.412 |
| Pluck | 4.0 | 5.0 | 6.0 | 6.490 | 15 | 4.198 |
| Pad | 4.0 | 4.0 | 6.0 | 8.879 | 17 | 2.780 |
| Bass | 5.0 | 4.0 | 8.0 | 8.396 | 19 | 3.771 |
| Drums | 2.0 | 4.0 | 0.0 | 1.503 | 6 | 3.170 |

Drums anchor (2 ms / 0 layback, tightest at 1.503 ticks), bass lays back
(+8 ms), all within profile bounds. Deterministic per seed (per-voice child
seed = 263394786·101 + row).

**Dual-version readback** (mido, read-only):

| Version | off-grid 16th | note-ons | scale viol | strong viol |
|---|---|---|---|---|
| perfect | **0** | 395 | 0 | 0 |
| humanized | **386** | 395 | 0 | 0 |

Perfect == 0 off-grid, humanized > 0 — proves the humanizer ran.

## 9. Zero-drift

`validate()` OK on both phases. Exported readback: all tracks = **61440 ticks**
(32 bars × 1920), identical length across 1 (phase1) / 5 (phase2) tracks. ✓

## 10. Render + master (all three)

FluidSynth (`FluidR3_GM.sf2`, `-g 1.2 -R no -C no`) → `master()` → Opus OGG.
Style target `target_for_style("trap")` = **−8.0 LUFS**, −1 dBTP ceiling.

| Version | target LUFS | measured LUFS | true peak dBTP | silence | OGG bytes |
|---|---|---|---|---|---|
| perfect | −8.0 | −10.02 | −1.00 | 12.1% | 430751 |
| humanized | −8.0 | −10.10 | −1.00 | 12.0% | 431628 |
| phase1 | −8.0 | −11.47 | −1.00 | 8.1% | 516646 |

Measured LUFS sits below target because the −1 dBTP true-peak ceiling is binding
(dense kick + layered clap) — the documented "true-peak is a ceiling, not a
target" behaviour, correct for a percussion-heavy piece. Silence is tail
padding after the last note (music fills ~55 s, then decay to ~0; no mid-track
gaps — the BIBD schedule guarantees at least 3 voices sound every bar).

## 11. Files

| Path | Size |
|---|---|
| `MIDI/304-trap-bibd-suite-phase1.mid` | 1462 B |
| `MIDI/304-trap-bibd-suite-perfect.mid` | 8615 B |
| `MIDI/304-trap-bibd-suite-humanized.mid` | 8617 B |
| `Audio/304-trap-bibd-suite-perfect.wav` | 11231276 B |
| `Audio/304-trap-bibd-suite-humanized.wav` | 11231532 B |
| `Audio/304-trap-bibd-suite-phase1.wav` | 10691116 B |
| `Audio/304-trap-bibd-suite-perfect.ogg` | 430751 B |
| `Audio/304-trap-bibd-suite-humanized.ogg` | 431628 B |
| `Audio/304-trap-bibd-suite-phase1.ogg` | 516646 B |

Plus `.mid.provenance.json` sidecars, `Analysis/grid_visualization.txt`,
`Analysis/manifest.json`, `Analysis/verification.json`, `Audio/master_stats.json`,
`README.md`, `compose.py` / `render.py` / `verify.py`.

## 12. Fixes applied

One: the read-only `verify.py` originally asserted `chord_violations_blanket == 0`,
but under the tiered pitch discipline weak notes legitimately snap to scale-only
(60 weak notes are in-scale-but-not-chord — legal). Corrected the gate to the
tiered invariants (0 scale violations + 0 strong-beat violations), which hold.
No other fixes — first-pass clean. All gates green: validate, grid audit, tiered
harmony audit, BIBD schedule audit, zero-drift readback, humanization DNA,
master loudness.
