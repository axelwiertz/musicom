# REPORT — 315-de-bruijn-groove-blues

**Nightly composition job · 2026-11-20.**

| Field | Value |
|---|---|
| **Project** | `315-de-bruijn-groove-blues` (next ID after 314) |
| **Genre / Style** | Groove |
| **Method** | 077 — De Bruijn Universal Cycle Composition (DBUC) |
| **Layer** | **concrete** (Rules-Based, exhaustive cycle over a k-symbol alphabet) |
| **Form** | `blues-12` — 12-bar blues (single `Blues` section) |
| **Key** | E minor (aeolian) — pcs `{E,F#,G,A,B,C,D}` = `{4,6,7,9,11,0,2}` |
| **Tempo / Meter** | 104 BPM · 4/4 · 480 TPB (BAR = 1920) |
| **Voices** | Lead=Clavinet(7) · Guitar=Muted Guitar(28) · Rhodes(4) · Bass=Electric Bass(33) · Drums(ch9) |
| **Seeds** | raw `20261120` · humanize `29275` |

## 1. Selection

Seeded (`20261120`) random selection per the LAYERED METHODOLOGY:
- **Style**: Groove (random over 47 genre folders).
- **Method**: 077 DBUC (random over 123 concrete methods, excluding 12 used
  in the last 7 days: 012, 019, 023, 025, 026, 035, 036, 069, 075, 126, 132, 139).
  ~6/7 concrete weighting → concrete chosen.
- **Form**: `pick_form("groove")` → `blues-12` (12-bar blues).

## 2. Method — De Bruijn Universal Cycle (077 DBUC)

A de Bruijn sequence `B(k,n)` is a cyclic word of length `n^k` whose every
length-`n` window over a `k`-symbol alphabet appears exactly once — an
exhaustive, non-repeating generator.

| Sequence | Value | Role |
|---|---|---|
| `PITCH_SEQ = B(7,2)` | 49 symbols over 7 diatonic degrees | melodic pitch DNA |
| `RHYTHM_SEQ = B(2,3)` | `00010111` (8 binary symbols) | onset gate (1=hit, 0=rest) |

`PITCH_SEQ = [0,0,1,0,2,0,3,0,4,0,5,0,6,1,1,2,1,3,1,4,1,5,1,6,2,2,3,2,4,2,5,2,6,3,3,4,3,5,3,6,4,4,5,4,6,5,5,6,6]`
(0=E, 1=F#, 2=G, 3=A, 4=B, 5=C, 6=D). Both sequences verified: every
length-2 degree pair and every length-3 binary window appears exactly once
(`verify_de_bruijn` assertion).

The lead walks `PITCH_SEQ` across the piece's 8th-note grid (96 slots =
12 bars × 8 eighths), gated by `RHYTHM_SEQ` (period 8 = one bar). The 12-bar
blues progression supplies the harmonic regions (macro-form) that the
chord-tone snap quantizes against.

## 3. Form & harmonic regions

12-bar blues, E natural minor (diatonic, all triads in-scale):

| Bars | 1-4 | 5-6 | 7-8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|
| Degree | i | iv | i | v | iv | i | v |
| Chord | Em | Am | Em | Bm | Am | Em | Bm |

`BLUES_DEGREES = [1,1,1,1, 4,4,1,1, 5,4,1,5]`. Per-bar harmonic regions (not a
single tonic region) → no bar-0 tonic collapse.

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw de Bruijn walk, single Clavinet voice.
  48 events = the 96 slots gated by `RHYTHM_SEQ` (4 hits/bar), float pitch +
  chromatic jitter (±1 semitone), off-grid onsets (±40 ticks), no harmony.
  Own `validate()` gate: PASS (23040 ticks). Scale violations = 19 (expected —
  raw draft is pre-rules, deliberately imperfect).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): STRICT chord discipline
  (every note snaps to its own bar's chord tone → in-scale AND in-chord),
  16th-grid snap, 5-voice Groove texture.

## 5. Humanization (dual-version, style-derived, seeded)

`hz_seed = 29275`. Style `groove` profile + per-instrument DNA. The phase-2
composer uses 1-bar sections so the humanizer's boundary clamp == bar boundary
(no jittered note crosses a bar line → per-bar chord violations stay 0).

Per-voice DNA (mean/max abs shift in ticks; 1 tick ≈ 1.2 ms @ 104 BPM):

| Voice | seed | n | mean shift | max shift | vel Δ | sigma |
|---|---|---|---|---|---|---|
| Lead (Clavinet) | 2956775 | 48 | 2.13 | 6 | 3.98 | 2.50 |
| Guitar (Muted) | 2956776 | 180 | 1.82 | 6 | 4.62 | 2.50 |
| Rhodes | 2956777 | 72 | 2.22 | 5 | 3.51 | 2.50 |
| Bass (Elec) | 2956778 | 48 | 6.94 | 17 | 3.31 | 4.16 |
| Drums | 2956779 | 156 | 0.97 | 4 | 2.97 | 1.66 |

Drums anchor (tightest, 0.97 ticks ≈ 1.2 ms); bass lays back (6.94 ticks ≈
8.3 ms, the +8 ms layback); melodic voices governed by the style profile.
Phase-1 raw draft stays un-humanized.

## 6. Verification (read-only mido)

| Artifact | tracks | tick len | pitched | drums | off-grid | untagged out-of-scale | non-resolving | strong viol |
|---|---|---|---|---|---|---|---|---|
| phase1 | 1 | 23040 | 48 | 0 | 47 (raw) | 19 (raw) | 0 | 0 |
| **perfect** | 5 | 23040 | 348 | 156 | **0** | **0** | **0** | **0** |
| **humanized** | 5 | 23040 | 348 | 156 | 407 (>0, jitter ran) | **0** | **0** | **0** |

- **Zero-drift**: all voice tracks equal length (23040) in all three artifacts.
- **Grid**: perfect off-grid == 0; humanized off-grid > 0 (humanizer ran).
- **Tiered harmony** (`workflows.pitch_audit.audit_voice`, per pitched voice):
  all PASS — 0 un-tagged out-of-scale, 0 non-resolving ornaments, 0 strong
  violations. STRICT discipline makes every note in-scale AND in-chord.

Per-voice tiered audit (perfect layer):

| Voice | audible | strong_ok | weak_in_scale | result |
|---|---|---|---|---|
| Lead | 48 | 0 | 48 | PASS |
| Guitar | 180 | 72 | 108 | PASS |
| Rhodes | 72 | 0 | 72 | PASS |
| Bass | 48 | 24 | 24 | PASS |

## 7. Render + master

`target_for_style("groove")` = **−14.0 LUFS**, ceiling **−1 dBTP**.
SoundFont `FluidR3_GM.sf2`.

| Artifact | LUFS | true peak | silence | RMS mean | OGG bytes |
|---|---|---|---|---|---|
| Phase 1 (raw) | -14.11 | -1.00 | 49.0% | 0.130 | 195,789 |
| Perfect | -14.03 | -1.00 | 14.3% | 0.131 | 213,002 |
| Humanized | -14.06 | -1.00 | 14.4% | 0.131 | 212,331 |

Phase-1 silence (49%) is the raw single-voice gated draft (4 hits/bar, no
accompaniment) — expected, not a render bug. Perfect/humanized at ~14% are
healthy full-texture renders.

## 8. Files

- `MIDI/315-de-bruijn-groove-blues-{phase1,perfect,humanized}.mid` (+ provenance sidecars)
- `Audio/315-de-bruijn-groove-blues-{phase1,perfect,humanized}.ogg`
- `provenance.json` (root) · `index.html` · `README.md` · `REPORT.md`
- `Analysis/grid_visualization*.txt` · `compose_summary.json` · `verification.json` · `render_report.json`
- `compose.py` · `render.py` · `verify.py`

## 9. Fixes applied

- Bass pickup ("and-of-4") originally targeted `next_root - 2` (a scale step
  below the next bar's root), which landed out-of-chord for 10 of 12 bars.
  Fixed: pickup snaps to the nearest chord tone of the **current** bar → STRICT
  discipline holds (scale + chord violations 0).
