# REPORT — 276-african-contour-suite

**Project:** 276-african-contour-suite
**Source:** 105-african-contour (extension — audit all-pass)
**Genre:** African (polyrhythmic, call-and-response, kalimba + flute + marimba + djembe)
**Method:** 095 Contour Theory Composition (CTC, abstract layer)
**Key:** C major pentatonic {0,2,4,7,9} · **BPM:** 112 · 4/4 · 480 TPB (bar 1920)
**Date:** 2026-10-31 (Nightly Rework Job)
**Seed:** 20261031 · **hz_seed:** 66700

---

## 1. Source selection & audit

Random pick from `/opt/data/projects/Styles/` (208 candidates, 15 excluded for
last-7-day mtime). Chosen: **African/105-african-contour** (Method 095 CTC,
6 sections × 4 bars = 24 bars, 5 voices).

Audit against current standards (all six PASS → **extension**, no redesign):

| # | Standard | Result |
|---|---|---|
| 1 | Engine, not hand-rolled | PASS — `UnitMatrixComposer` (no raw mido authoring) |
| 2 | Zero-drift | PASS — 5 voice tracks all 46080 ticks |
| 3 | Rhythm-grid sync | PASS — pitched off-grid = 0 |
| 4 | Valid track setup | PASS — 6 tracks (conductor + 5 voices) |
| 5 | Two-phase artifacts | PASS — `.mid` + `-phase1.mid` present |
| 6 | provenance + index.html | PASS — sidecars + dashboard present |

Identity preserved: C major pentatonic, 112 BPM, contour vocabulary
(oscillate/arch/valley/chaos/rising/falling CSegs + CAS), dihedral transforms
{id,I,R,RI}, and the Kalimba/Flute/Marimba/Bass/Djembe voice roster.

## 2. What changed (extension → longer + more varied)

- **Longer:** 24 bars → **32 bars / 8 sections** (Intro / Theme / Variation /
  Development / Bridge / Climax / Outro / Coda).
- **More varied:** 7 distinct variation techniques (see table below).
- **New voice:** Pan Flute **counterline** (ch4) in Bridge + Climax (6 voices).
- **Per-section harmonic regions:** each section its own 4-bar progression;
  section roots taken from the MIDPOINT chord (never bar-0 tonic):

| Section | Contour | Transform | Register | Mode | Progression | Midpoint |
|---|---|---|---|---|---|---|
| Intro | oscillate | id | 60 | sync | C G C C | G |
| Theme | arch | id | 60 | sync | C Am C G | Am |
| Variation | valley | **R (retrograde)** | 60 | sync | Am G D G | G |
| Development | chaos | **I (inversion)** | **72 (+12)** | sync | D G Am D | G |
| Bridge | arch | id | 48 | **aug** | Am D G Am | **D** |
| Climax | rising | RI | **72 (+12)** | **dense (diminution)** | G C D C | C |
| Outro | falling | id | **48 (-12)** | sync | C G Am C | G |
| Coda | oscillate | **R** | 48 | **aug** | C G C C | G |

### Variation techniques (7 distinct)

1. **Retrograde (R)** — Variation (valley contour reversed) + Coda.
2. **Inversion (I)** — Development (chaos contour inverted).
3. **Register shift +12** — Development & Climax (base 60 → 72).
4. **Rhythmic augmentation** — Bridge & Coda (quarter-note grid, motif slowed).
5. **Rhythmic diminution** — Climax (8th-note grid, double-time density).
6. **Counterline (Pan Flute)** — Bridge & Climax (new 6th voice, stepwise call).
7. **Density rise + thinning** — Climax (all 6 voices) vs Coda (3 voices).

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw whole-tone contour walk (rank → base+2·rank),
  single Kalimba, off-grid (±30 tick jitter), no harmony. 208 onsets, off-grid 205.
- **Phase 2** (`-perfect.mid`): 16th-grid snap → C-pentatonic scale quantize →
  per-bar palette (chord-tone) quantize → range enforce → dedup → voice-leading
  (adjacent leap ≤ 9 st) → full 6-voice African texture.

## 4. Dual-version export (humanization)

`export_dual` — grid-locked **perfect** layer + **humanized** layer
(style-derived, seeded `hz_seed=66700`, per-instrument DNA from the registry):

| Voice | mean shift (ticks) | max shift | vel delta |
|---|---|---|---|
| Kalimba | 4.4 | — | 4.7 |
| Flute | 4.3 | — | 6.1 |
| Marimba | 4.0 | — | 4.2 |
| Bass | 8.6 | 25 | 4.3 |
| Counter | 4.3 | 15 | 4.3 |
| Drums | **1.2** | 6 | 3.1 |

Drums anchor tightest, bass lays back most — the expected role-DNA pattern.

## 5. Verification (read-only mido)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| Voice tracks | 1 | 6 | 6 |
| Track length (ticks) | 61440 | 61440 | 61440 |
| Zero-drift | ✓ | ✓ | ✓ |
| Pitched onsets | 208 | 460 | 460 |
| Off-grid | 205 | **0** | **420** (>0 = jitter ran) |
| Scale violations | 52 | **0** | **0** |
| Chord violations | 96 | **0** | 5* |

\* humanized chord violations = 5 notes within ≤6 ticks of a bar seam, pushed
across by timing jitter and re-attributed to the adjacent bar's palette. Scale
stays 0 (key-wide). Perfect layer (the compositional truth) is 0/0/0.

## 6. Files

- `MIDI/276-african-contour-suite-phase1.mid` (+ provenance)
- `MIDI/276-african-contour-suite-perfect.mid` (+ provenance)
- `MIDI/276-african-contour-suite-humanized.mid` (+ provenance)
- `Audio/276-african-contour-suite-{phase1,perfect,humanized}.ogg` (FluidSynth → LUFS master → Opus)
- `Analysis/` grid visualizations, verify.json, render_report.json
- `composition_meta.json`, `index.html`, `README.md`
