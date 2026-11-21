# 316 · Soul Voice-Leading Suite

**Extension of** `229-soul-voiceleading-rework` (Soul, F natural minor, Method 007
Voice-Leading Graph Search). Chain: `078-soul-voiceleading` → `229-…-rework` → `316-…-suite`.

## Source audit (229-soul-voiceleading-rework)

| Standard | Result |
|---|---|
| 1 Engine (UnitMatrixComposer) | PASS |
| 2 Zero-drift | PASS (6 voice tracks × 61440) |
| 3 Rhythm-grid sync | PASS (0 off-grid pitched onsets) |
| 4 Track setup (≥4) | PASS (6) |
| 5 Two-phase artifacts | PASS (`.mid` + `-phase1.mid`) |
| 6 provenance.json + index.html | PASS |

**All 6 standards pass → extension path (no redesign).**

## Identity preserved

- Genre **Soul**, key **F natural minor** (F G Ab Bb C Db Eb), **96 BPM**, 4/4.
- Method **007 Voice-Leading Graph Search** (`TonalNetworkGenerator`, minor tonic).
- Arch hook motif `[65,68,72,68,65,63,60,63]` (F4 Ab4 C5 Ab4 F4 Eb4 C4 Eb4).
- 6-voice texture: Lead (Tenor Sax 66), Horns (Brass 61), Rhodes (EP 4),
  Violin (40) counterline, Bass (33), Drums (ch9).

## What changed (longer + more varied)

- **Longer**: 32 → **40 bars** (8 → **10 sections**). Two NEW sections:
  `PreChorus` and `PreChorus2` (rising builds).
- **More variation**: 8 techniques (source had 6) — see below.
- **Dual-version export**: now ships `-perfect` + `-humanized` (source predated
  the humanization contract; only had a single phase-2 `.mid`).
- **Correct Tenor Sax program** 66 (source used 65 = Soprano Sax).

## Variation techniques (8)

| # | Technique | Where |
|---|---|---|
| 1 | Inversion | Intro lead = diatonic inversion of hook around F4 |
| 2 | **Augmentation** (NEW) | PreChorus = hook half-time (480-tick onsets, legato) |
| 3 | **Diminution** (NEW) | PreChorus2 = hook 16th runs (120-tick onsets) |
| 4 | Register shift | Verse2 lead = tonal-network walk +1 octave |
| 5 | Transposition | Chorus2 = hook diatonic +2 scale steps |
| 6 | Retrograde | Bridge lead = retrograde hook |
| 7 | **Counterline** (NEW) | rising violin obbligato in PreChorus/PreChorus2 |
| 8 | Density curve | drum/horn density 0.3 → 1.0 → 0.3 across 10 sections |

## Form & per-section harmonic regions (each section own progression)

| # | Section | Bars | Progression | Anchor (midpoint) |
|---|---|---|---|---|
| 0 | Intro | 4 | i VI iv i | VI(Db) |
| 1 | Verse | 4 | i iv III v | iv(Bbm) |
| 2 | PreChorus | 4 | iv v VI VII | v(Cm) |
| 3 | Chorus | 4 | VI III iv v | III(Ab) |
| 4 | Verse2 | 4 | i iv ii v | iv(Bbm) |
| 5 | PreChorus2 | 4 | iv v VI VII | v(Cm) |
| 6 | Chorus2 | 4 | VI III v i | III(Ab) |
| 7 | Bridge | 4 | iv ii VI VII | ii(Gdim) |
| 8 | Chorus3 | 4 | VI III iv v | III(Ab) |
| 9 | Outro | 4 | i VII VI i | VII(Eb) |

Section roots come from the **midpoint chord** (bar 1), never bar 0 — avoids
the bar-0 tonic collapse bug.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw tonal-network graph walk — single voice,
  unquantized chromatic, off-grid onsets, no harmony.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): rules post-process — grid
  snap (120/240) → chord-tone quantization (floor bar attribution) →
  voice-leading check + octave-fold correction → full soul texture →
  humanize (style `soul`, seed `316096`) via `workflows.humanize.export_dual`.

## Verification (real read-only mido numbers)

| Check | perfect | humanized | phase1 |
|---|---|---|---|
| Voice tracks | 6 × 76800 (zero-drift) | 6 × 76800 (zero-drift) | 1 × 76800 |
| Pitched onsets | 1044 | 1044 | 240 |
| Off-grid | **0** | **983** (jitter ran) | 220 (raw) |
| Scale violations (non-ch9) | **0** | **0** | 73 (raw) |
| Chord violations (non-ch9) | **0** | 14 (bar-boundary jitter ≤11 ticks) | 177 (raw) |

Humanized 14 "chord violations" are all notes within 1–11 ticks of a bar line —
the humanizer's intended micro-timing jitter, not compositional errors (the
perfect layer is chord-clean, and every note's pitch-class stays in-key).

## Files

- `MIDI/316-soul-voiceleading-suite-phase1.mid` — phase 1 (raw draft)
- `MIDI/316-soul-voiceleading-suite-perfect.mid` — phase 2 (grid-locked)
- `MIDI/316-soul-voiceleading-suite-humanized.mid` — phase 2 (humanized)
- `Audio/316-soul-voiceleading-suite-perfect.ogg` — mastered Opus render
- `Audio/316-soul-voiceleading-suite-humanized.ogg` — mastered Opus render
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `render_report.json`
- `index.html`, `README.md`, `provenance.json`, `rework_audit.json`
