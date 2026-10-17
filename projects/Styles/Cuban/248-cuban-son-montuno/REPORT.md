# 248 — Cuban Son Montuno

**Rework of `005-cuban-son-clave-lift`** · autonomous nightly rework job · 2026-10-17 · seed 248.

---

## 1. Source identity (preserved)

| Field | Value |
|---|---|
| Source project | `Styles/Cuban/005-cuban-son-clave-lift` |
| Genre | Cuban son / rumba-clave |
| Key | D dorian (D E F G A B C) |
| Tempo | 104 BPM · 4/4 · 480 TPB |
| Actual source length | 2 bars (3840 ticks) — README "8-bar loop" claim is wrong |
| Lead contour | D E F G A G F D (arch, degrees 1 2 3 4 5 4 3 1) |
| Montuno | D F G A G F E D (dorian raised-6th color) |
| Bass | D D F D G F D C (root-5th, anticipatory) |
| Instrumentation | flute lead (73) · nylon-guitar montuno (24) · electric bass (33) · clave kit (ch9) |

## 2. Audit result (against current standards)

| # | Standard | Result |
|---|---|---|
| 1 | Engine, not hand-rolled (`UnitMatrixComposer`) | **FAIL** — raw `mido` MidiTrack/note_on |
| 2 | Zero-drift (voice tracks equal length) | **FAIL** — [3840,3840,3840,2880], drums 1.5 bars |
| 3 | Rhythm-grid sync (onsets %120==0) | PASS — 0 off-grid |
| 4 | ≥4 voice tracks | PASS — 4 voices |
| 5 | Two-phase artifacts (`-phase1.mid`) | **FAIL** — missing |
| 6 | provenance.json + index.html | **FAIL** — missing |

**Verdict: redesign required** (4/6 standards failed). Full record in
`005-cuban-son-clave-lift/Analysis/rework_audit.json`.

## 3. Redesign decision

Rebuilt **from scratch** through the canonical `UnitMatrixComposer` two-phase
workflow. Musical identity preserved (D dorian, 104 BPM, flute/nylon-guitar/
e-bass/clave), non-compliant hand-rolled code discarded.

## 4. New form — longer + more varied

18 bars, 5 sections (source had 2 bars / effectively 1 loop):

| Section | Bars | Harmony (per bar) | Role |
|---|---|---|---|
| Intro | 0-1 | Dm · Dm | clave + bass establish |
| Canto | 2-5 | Dm · G · Am · Dm | lead states DNA (Dm arpeggio rise) |
| Montuno | 6-9 | Dm · G · C · Dm | call–response, retrograde answer |
| Canto' | 10-13 | G · Dm · Am · G | inversion + register shift |
| Mambo | 14-17 | Dm · G · Am · Dm | augmentation + density rise, tonic land |

**Per-section harmonic regions** (midpoint-chord roots, not bar-0 tonic):
Intro→i(D) · Canto→IV(G) · Montuno→IV(G) · Canto'→i(D) · Mambo→IV(G).
Chord *quality* derived from each midpoint degree (Dm / G / G / Dm / G).

## 5. Variation techniques (5, mapped)

1. **Retrograde** — Montuno section answers the Canto Dm arpeggio reversed
   (74·69·65·62 instead of 62·65·69·74).
2. **Inversion** — Canto' bar 10 inverts the Dm arpeggio around D4:
   D F A D → D B G D, which re-harmonizes to a G-major sonority.
3. **Register shift** — Mambo raises lead an octave (E5/D5 top register).
4. **Augmentation** — Mambo lead half-notes/whole-note (2×/4× durations).
5. **Density rise** — Mambo adds a maracas eighth-note pulse over the clave +
   conga bed.

## 6. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single flute voice, raw random walk over the
  D-dorian pc pool, unquantized pitch + off-grid micro-timing, no harmony.
  144 grain events.
- **Phase 2** (`.mid`): chord-tone quantization per bar (`t // BAR`), 8th-grid
  onset snap, voice-leading check, full 4-voice texture, seeded humanization.

## 7. Verification (readback, mido read-only)

| Check | Result |
|---|---|
| File sizes | phase1 1309 B · phase2 3823 B (all > 40) |
| Zero-drift (phase 2) | **PASS** — 4 voice tracks × 34560 ticks, equal |
| Zero-drift (phase 1) | **PASS** — 1 track × 34560 ticks |
| Grid sync (pre-humanize, 16th) | **0 off-grid** across all pitched voices |
| Scale violations (D dorian) | **0** (readback, post-humanize) |
| Chord violations (per-bar `t//BAR`) | **0** (readback, post-humanize) |
| Voice-leading violations | 0 |
| Post-humanize micro-timing | 259/296 pitched onsets off-grid (intentional) |

Humanization (style-derived, seeded): Lead σ 8ms (mean 4.0t), Montuno σ 6ms
(2.8t), Bass σ 5ms +8ms layback (6.4t), Drums anchor σ 2ms (1.2t).

## 8. Audio

| File | Dur | Peak | RMS | Silence |
|---|---|---|---|---|
| phase-2 (FluidR3_GM) | 44.9 s | 0.791 | 0.134 | 7.2% ✓ |
| phase-1 | 43.9 s | 0.457 | 0.055 | 7.5% ✓ |

Silence ratios well under the 30% silent-render trap. OGG Opus renders attached.
