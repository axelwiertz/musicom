# 286-country-hoedown-suite — Rework Report

**Rework of:** `001-country-loop-seamless` (Country)
**New project:** `286-country-hoedown-suite`
**Date:** 2026-11-05

## 1. Source identity (preserved)

| Attribute | Value |
|---|---|
| Genre | Country |
| Key | G major |
| Tempo | 120 BPM |
| Progression | I-IV-V-I (G-C-G-D / C-G-D-G) with vi (Em) and ii (Am) added |
| Voices | Fiddle (violin 40), Acoustic Guitar (25), Acoustic Bass (32), Harmony Guitar (24), Drums (ch 9) |
| Core DNA | arpeggiated triads + neighbor tones (G-B-D-B fiddle contour), walking bass |
| Mood | upbeat, danceable, nostalgic |

## 2. Audit result (source: 001-country-loop-seamless)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, no raw mido authoring) | **FAIL** — hand-rolled music21 (`stream.Part`/`note.Note`) |
| 2. Zero-drift (all voice tracks equal length) | **FAIL** — 312480 / 322560 / 332640 / 1275120 ticks |
| 3. Rhythm-grid sync | n/a-pass (foreign 10080 tpb; onsets quantized) |
| 4. Track setup (>=4 voices) | **FAIL** — 4 tracks but drums on channel 3, not ch 9 |
| 5. Two-phase artifacts (`<id>.mid` + `<id>-phase1.mid`) | **FAIL** — no phase1 |
| 6. `provenance.json` + `index.html` | **FAIL** — no provenance.json; index.html is a trivial stub |

**Decision:** `redesign_required = True`. Full rebuild through the canonical
`UnitMatrixComposer` workflow, preserving only musical identity.

## 3. What changed (source → new)

- **Form extended**: 16-bar seamless loop → **7 sections / 32 bars**
  (Intro / Verse / Chorus / Verse2 / Bridge / Chorus2 / Outro).
- **Per-section harmonic regions**: source used one global G-C-G-D / C-G-D-G
  cycle (bar-0 tonic risk). New version gives each section its OWN progression;
  section root read from the **midpoint chord** (bar 1). Midpoint roots:
  `C Em G Am Em G C` (varied — no bar-0 tonic bug).
- **Dual-version export**: `-perfect.mid` + `-humanized.mid` (source: one MIDI).
- **`index.html` dashboard + root `provenance.json`** added.
- **Blanket chord-tone quantization**: every pitched note snaps to ITS OWN
  bar's chord (across octaves) — 0 scale violations, 0 chord violations.

## 4. Variation techniques (8 applied, per section)

| Section | Technique |
|---|---|
| Intro | **Augmentation** (longer notes, sparse) + register drop |
| Verse | baseline Country Contour Walk (arpeggio + neighbor tones) |
| Chorus | **Register shift** up (center 79) + **diminution** (denser 16th feel) |
| Verse2 | **Transposition** (center up a 4th) + **mode shade** (Am/Em region) |
| Bridge | **Inversion** (mirrored contour) + relative-minor region |
| Chorus2 | **Counterline** (harmony guitar sustains chord 3rd/5th above fiddle) |
| Outro | **Retrograde** (reversed contour) + register drop to resolve |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single-voice raw contour walk — arpeggio/neighbor
  interval pool, jittered off-grid onsets + unquantized pitch, no harmony.
  256 events, 252 off-grid, 122 scale / 214 chord violations (intentionally raw).
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): grid-lock to 16th (120 ticks)
  → blanket chord-tone quantization per bar → voice-leading cap (leap ≤ 9) →
  dedup → full 5-voice Country texture.

## 6. Dual-version note (humanization)

- `-perfect`: grid-locked compositional truth — **0 off-grid**, 0 scale
  violations, 0 chord violations, 0 strong-beat violations.
- `-humanized`: country style profile (9 ms timing, 6.5 velocity, 2 ms layback)
  + per-instrument DNA (bass +8 ms layback, drums anchor 2 ms). **640 off-grid**
  onsets prove jitter ran. 0 scale / 0 strong-beat violations. 17 blanket-chord
  "violations" are onset-boundary artifacts: notes shifted ≤3 ticks early at a
  bar line are attributed to the previous bar by the `t // BAR` audit, but their
  pitch is correct for the intended bar — a timing artifact, not harmonic error.

## 7. Verification (read-only mido readback)

| Layer | voices | track len (ticks) | off-grid | scale viol | chord viol |
|---|---|---|---|---|---|
| phase1 | 1 | 61440 | 252 | 122 (raw) | 214 (raw) |
| perfect | 5 | 61440 ×5 | **0** | **0** | **0** |
| humanized | 5 | 61440 ×5 | **640** | **0** | 17 (boundary artifact) |

Zero-drift: all 5 voice tracks length 61440 ticks (32 bars × 1920). ✓
All MIDI/WAV/OGG sizes > 40 B. ✓

## 8. Files

- `MIDI/286-country-hoedown-suite-phase1.mid`
- `MIDI/286-country-hoedown-suite-perfect.mid`
- `MIDI/286-country-hoedown-suite-humanized.mid`
- `Audio/286-country-hoedown-suite-perfect.ogg`
- `Audio/286-country-hoedown-suite-humanized.ogg`
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/verification.json`
- `index.html` (dashboard), `README.md`
