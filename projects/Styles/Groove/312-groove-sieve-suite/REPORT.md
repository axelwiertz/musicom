# REPORT — 312-groove-sieve-suite

**Project:** 312-groove-sieve-suite · **Date:** 2026-11-19 · **Job:** nightly rework cron

## 1. Source selection + audit

| Field | Value |
|---|---|
| Chosen source | `Styles/Groove/274-groove-sieve-rework` |
| Genre | Groove |
| Primary MIDI | `MIDI/274-groove-sieve-rework-perfect.mid` |
| Audit | **ALL STANDARDS PASS** → extension (not redesign) |

**Standards:**

| Standard | Result |
|---|---|
| engine (UnitMatrixComposer, no raw mido) | ✅ PASS |
| zero-drift (6 voice tracks equal 61440 ticks) | ✅ PASS |
| rhythm-grid (0 off-grid pitched onsets) | ✅ PASS |
| track-setup (6 tracks, ch9 drums) | ✅ PASS |
| two-phase artifacts (`-phase1.mid` present) | ✅ PASS |
| provenance.json + index.html | ✅ PASS (3 sidecars + dashboard) |

Detailed audit: `../274-groove-sieve-rework/Analysis/rework_audit.json`.

## 2. Preserved musical identity (DNA)

- Key **G natural minor** (pcs `{7,9,10,0,2,3,5}`)
- **Xenakis Sieve** (Method 025): C = A (mod 8, res {0,2,5}) ∩ B (mod 7, res {0,1,4}),
  period 56, offsets `[0,8,18,21,29,32,42,50,53]`
- Tempo **110 BPM** 4/4 · 480 TPB
- Voices: Lead (Soprano Sax 65), Horns (Brass 61), Rhodes (EP 4), Bass (EB 33),
  Counter (Strings 48), Drums (ch9)

## 3. What changed (extension, seed from existing DNA)

- **Longer**: 40 bars / 10 sections (source was 32 bars / 8 sections; N+2 = 10).
- **More varied**: 8 variation techniques (3 new vs source).
- Chorus2 Counter voice now performs a **canon imitation** (echoes lead −12 at
  +1 beat, re-quantized to its own bar's chord).

## 4. Form (40 bars / 10 sections)

| # | Section | Bars | Progression | Variation technique |
|---|---|---|---|---|
| 1 | Intro | 4 | i — VII — i — VII | sieve exposed (sparse) |
| 2 | VerseA | 4 | i — III — iv — v | core sieve motif |
| 3 | VerseB | 4 | i — iv — v — VI | **transposition +12** |
| 4 | PreChorus | 4 | iv — VI — VII — v | **diminution** (16th feel) |
| 5 | Chorus | 4 | III — VII — i — iv | density rise + counterline |
| 6 | Bridge | 4 | VI — III — VII — v | **inversion** |
| 7 | VerseC | 4 | i — III — iv — v | **retrograde** |
| 8 | Chorus2 | 4 | III — VII — i — iv | transposition + **canon** |
| 9 | Break | 4 | VI — v — VI — VII | **register shift −12** (sparse) |
| 10 | Outro | 4 | i — VI — VII — i | **augmentation** + fade |

Section midpoint roots: G(7) C(0) D(2) F(5) G(7) F(5) C(0) G(7) Eb(3) F(5) —
varied across sections, no bar-0 tonic collapse.

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw sieve walk, single voice (LeadRaw 65),
  off-grid onsets, unquantized chromatic wander, no harmony. Own
  `UnitMatrixComposer` + `validate()` gate (PASS). 334 raw events.
- **Phase 2** (`-perfect.mid`): grid snap (16th) → scale quantize →
  chord-tone quantize per bar (`t // BAR`) → voice-leading (leap cap 9) →
  range-restricted (48–84) → 6-voice arrangement. `validate()` PASS.
- **Dual-version**: `export_dual` → `-perfect.mid` + `-humanized.mid`
  (seeded hz 81068).

## 6. Verification (read-only mido audit)

| Check | phase1 (raw) | perfect | humanized |
|---|---|---|---|
| File size > 40 B | 2991 ✓ | 11405 ✓ | 11364 ✓ |
| Zero-drift | 1 × 76800 ✓ | 6 × 76800 ✓ | 6 × 76800 ✓ |
| Pitched onsets | 334 | 849 | 849 |
| Off-grid | 259/334 (raw) | **0/849 ✓** | 735/849 (>0, jitter ran) |
| Scale violations | 66 (raw) | **0 ✓** | **0 ✓** |
| Chord violations | 226 (raw) | **0 ✓** | 20 (bar-line jitter ≤5 t) |

Humanized chord "violations" (20) are onset-jitter artifacts: every note is
in-scale and a valid chord tone of its **source** bar; onset jittered 1–5
ticks across a bar line. Perfect layer (compositional truth) is 0 / 0 / 0.

## 7. Humanization (style groove + per-instrument DNA, seed 81068)

Style groove profile: timing σ 3.0 ms, velocity σ 5.0, phrase_corr 0.15, layback 1.0 ms.

| Voice | mean\|Δshift\| (ticks) | max\|Δshift\| | mean vel Δ |
|---|---|---|---|
| Lead | 1.93 | 8 | 5.45 |
| Horns | 1.66 | 8 | 6.21 |
| Rhodes | 1.99 | 7 | 4.34 |
| Bass | 7.39 | 18 | 3.71 |
| Counter | 1.73 | 5 | 4.11 |
| Drums | 1.06 | 5 | 3.21 |

Drums tightest (anchors grid), bass lays back (+8 ms DNA). Zero-drift intact.

## 8. Render + master (FluidSynth → master() → Opus OGG)

Soundfont `FluidR3_GM.sf2` (via `discover_soundfont()`). Master to
`target_for_style("groove")` = **−14 LUFS**, ceiling **−1 dBTP**.

See `Analysis/render_report.json` for LUFS / true-peak / silence numbers.

## 9. Files

```
/opt/data/projects/Styles/Groove/312-groove-sieve-suite/
├── README.md, REPORT.md, index.html, composition_meta.json
├── compose.py, verify.py, render.py
├── MIDI/   312-groove-sieve-suite-{phase1,perfect,humanized}.mid (+ provenance.json)
├── Audio/  312-groove-sieve-suite-{phase1,perfect,humanized}.ogg + .wav
└── Analysis/ grid_visualization{,_phase1}.txt, verify.json, render_report.json
```
