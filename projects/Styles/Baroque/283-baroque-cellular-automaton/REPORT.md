# REPORT — 283-baroque-cellular-automaton

**Nightly composition job · 2026-11-03 · seed 20261103**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Baroque** (random from genre folders; `target_for_style("baroque-classical")` → −18 LUFS classical target) |
| Method | **021 — Cellular Automata Grid Evolution (CAGE)** |
| Layer | **concrete** (emits `MusicEvent`s that fill UnitMatrix cells directly; no abstract design stage) |
| Paradigm | Rules-Based · Grid-Locked · Meso/Cell |
| Form | **aba** (da capo ternary) — A1 (8) · B (8) · A2 (8) = **24 bars**. Baroque has no FORM_PALETTE style-hint, so mapped to the classical hint family {aba, rondo, through-composed}; `aba` selected (Minuet/da-capo idiom). |
| Key | **D minor** — harmonic/melodic-mixture: `KEY_PCS = {0,1,2,4,5,7,9,10}` (D E F G A Bb C C#; b7 **and** leading tone both declared) |
| Meter / tempo | 4/4 · **96 BPM** · 480 TPB (BAR = 1920, SECTION = 15360, TOTAL = 46080 ticks ≈ 60 s) |

## 2. Method realization (two-phase)

**Phase 1 — raw generative draft.** A 1D elementary cellular automaton (Rule 30,
width 24, seeded `SEED`, evolved 192 steps = one step per 8th slot) produces an
unquantized single-voice walk: a cursor cell's live/dead state steps the pitch
up/down by fractional semitones, onsets are jittered off the grid, no harmony.
Exported as `-phase1.mid` with its own zero-drift gate.

**Phase 2 — musicom rules post-process.** Re-deriving the same CA grid:
- **Tiered pitch snap** — `classify_weight(onset, STRONG_GRID['4/4'], bar_ticks=1920)`
  gives strong (beats 1 & 3) vs weak; strong notes snap to the bar's **chord**
  tones (in-scale AND in-chord), weak notes snap to the **scale** (KEY_PCS).
  Implemented as `tiered_snap()` — the weight-aware mirror of `ScaleQuantizer.tiered_quantize`,
  but against the harmonic-minor key set (the fixed `'minor'` mode lacks the C# leading tone).
- **Rhythm-grid snap** — every onset snapped to the 8th grid (240 ticks).
- **Register/range enforcement** — per-voice ranges; `dedup_keep_longest` collision collapse.
- **Full 5-voice Baroque texture** (below), terminal landmark at every section seam.

### CA → music mapping
- Violin (lead): cursor cell live ⇒ +2 semitones, dead ⇒ −2, walking an 8th-note
  line whose contour arcs follow the CA's live/dead runs.
- Oboe (counter): inverted contour (live ⇒ −2), quarter/half-note grid, echoing the lead.
- Harpsichord (continuo): block chord on beat 1 + broken-chord (root-5th-3rd-5th)
  figuration whose density is **gated by the CA row's alive-count** (sparse rows thin the figuration).
- Viola (inner pedal): sustained whole-note chord tone, nearest-tone voice leading.
- Cello (ground bass): root/fifth quarter-note dance lock.

## 3. Voices & instruments (registry source of truth)

| Voice | Program | GM | Register | humanize_dna (timing, vel, layback, dur) |
|---|---|---|---|---|
| Violin | 40 | Violin | 62–86 | (None, 6.0, None, 0.03) |
| Oboe | 68 | Oboe | 60–81 | (None, 7.0, None, 0.02) |
| Harpsichord | 6 | Harpsichord | 55–72 | (None, 5.0, None, 0.015) |
| Viola | 41 | Viola | 57–69 | (None, 6.0, None, 0.03) |
| Cello | 42 | Cello | 40–55 | (10.0, 6.0, 8.0, 0.03) — DOUBLE_BASS override for bass layback |

## 4. Harmonic ground (D minor)

| Section | Bars 1–8 |
|---|---|
| A1 | Dm · C · Bb · A · Dm · Gm · A · Dm |
| B | F · C · Dm · A · Bb · Gm · A · Dm |
| A2 | Dm · C · Bb · A · Dm · Gm · A · Dm |

Chord PCS: Dm {2,5,9} · C {0,4,7} · Bb {10,2,5} · A {9,1,4} (A-major, C# leading tone) · Gm {7,10,2} · F {5,9,0}.

## 5. Grid audit (per voice, exported MIDI)

| Version | off-8th | off-16th | verdict |
|---|---|---|---|
| perfect | **0 / 0 / 0 / 0 / 0** (Violin/Oboe/Harpsichord/Viola/Cello) | 0 | **grid-locked** |
| humanized | 170 / 89 / 209 / 20 / 94 (total **582**) | 582 | **humanizer ran** |
| phase1 | 185 (single raw voice) | 185 | unquantized by design |

## 6. Harmony audit (tiered, `workflows.pitch_audit.audit_voice`, perfect MIDI)

All 5 voices **PASS** — every pitched note is in-scale AND (on strong beats) in-chord:

| Voice | audible | strong_ok | weak_in_scale | untagged_out | tagged_non_resolving | strong_viol | collisions |
|---|---|---|---|---|---|---|---|
| Violin | 192 | 48 | 144 | 0 | 0 | 0 | 0 |
| Oboe | 96 | 48 | 48 | 0 | 0 | 0 | 0 |
| Harpsichord | 240 | 96 | 144 | 0 | 0 | 0 | 0 |
| Viola | 24 | 24 | 0 | 0 | 0 | 0 | 0 |
| Cello | 96 | 48 | 48 | 0 | 0 | 0 | 0 |

Lead/counter carry **zero** tagged chromatic ornaments (the harmonic-minor leading
tone C# is in the declared key, so it needs no exemption). Bass/pad/harmony/rhythm
are chromatic-free as required.

## 7. Humanization (always-on, style-derived, seeded)

`export_dual(...)` validated + exported the grid-locked `-perfect` MIDI FIRST,
then humanized in place and re-validated + exported `-humanized` (zero-drift gate on BOTH).

- Style profile **baroque-classical** → `HumanizeProfile(timing_sigma_ms=7.0, velocity_sigma=5–7/voice, layback_ms=1.0, phrase_corr=0.6)`.
- Master seed **20261103**; per-voice child seed = `seed*101 + row`.

| Voice | seed | mean_abs_shift (ticks) | max_abs_shift | mean_abs_vel_delta |
|---|---|---|---|---|
| Violin | 2046371403 | 3.838 | 12 | 4.537 |
| Oboe | 2046371404 | 3.948 | 13 | 5.385 |
| Harpsichord | 2046371405 | 4.158 | 13 | 3.996 |
| Viola | 2046371406 | 3.375 | 12 | 5.042 |
| Cello (bass) | 2046371407 | 7.823 | 25 | 4.219 |

Cello lays back (10 ms timing + 8 ms layback) → the largest mean shift, as expected for the bass role.

## 8. Zero-drift

- perfect: 5 voice tracks all **46080** ticks (equal) → zero-drift **PASS**.
- humanized: 5 voice tracks all **46080** ticks → zero-drift **PASS**.
- phase1: 1 voice track **46080** ticks → PASS.

## 9. Render + master (FluidSynth → `master()` → Opus OGG)

SoundFont `discover_soundfont()` (FluidR3_GM), dry render (`-R no -C no`, `-g 1.2`).
Style target **−18.0 LUFS** (classical), ceiling −1 dBTP.

| Version | integrated LUFS | true peak (dBTP) | silence ratio | mid-track gaps | WAV | OGG |
|---|---|---|---|---|---|---|
| perfect | −18.0 | −6.35 | 4.98% | 0 s | 11.07 MB | 450 KB |
| humanized | −18.0 | −6.55 | 4.99% | 0 s | 11.07 MB | 455 KB |
| phase1 | −18.0 | −3.14 | 5.48% | 0 s | 11.04 MB | 503 KB |

True peak sits below the −1 dB ceiling (dynamic Baroque material at −18 LUFS →
~11.7 LU of headroom) — correct behaviour; `master()` true-peak is a ceiling, not a target.

## 10. Files

| Path | Bytes |
|---|---|
| MIDI/283-baroque-cellular-automaton-phase1.mid | 1664 |
| MIDI/283-baroque-cellular-automaton-perfect.mid | 5852 |
| MIDI/283-baroque-cellular-automaton-humanized.mid | 5594 |
| Audio/*-perfect.wav / .ogg | 11069996 / 450757 |
| Audio/*-humanized.wav / .ogg | 11068460 / 455420 |
| Audio/*-phase1.wav / .ogg | 11041068 / 503488 |
| Analysis/grid_visualization.txt | 6509 |
| Analysis/verify.json | 5717 |
| Analysis/render_stats.json | 2002 |
| Analysis/summary.json | (see below) |

Provenance sidecars: `*.mid.provenance.json` per artifact (phase1 = phase 1,
perfect = phase 2 grid-locked, humanized = phase 2 humanized) + root `provenance.json`.

## 11. Fixes applied / notes

- No violations required a fix on the first pass (grid 0 off, harmony 0/0/0, zero-drift clean).
- Harmonic-minor leading tone: `ScaleQuantizer`'s fixed `'minor'` mode lacks C#, so
  tiered snapping was implemented against the declared `KEY_PCS` (harmonic/melodic
  mixture) using the engine's `classify_weight` — no custom modulo wrappers.
